import sys
import os
from flask import Flask, request, jsonify, send_file, send_from_directory, redirect, current_app
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from flasgger import Swagger, swag_from
import yaml

import threading
from werkzeug.utils import secure_filename
import torch
from io import BytesIO
# Cache for tile results
from cachetools import TTLCache

# Import model load functions

# Add this import for type annotations
from typing import Dict, Any, List, Optional, Tuple

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

# Use preloaded models directly
from vision.process_vis import extract_image_details
from pompei.process_pr import generate_prompt_from_caption
from syndrella.process_imgen import generate_image_from_text
from geo.helper import tile_coords_to_bbox, generate_tile

from vision.process_vis import load_blip_model, unload_blip_model, unload_transformer_model
from syndrella.process_imgen import load_stable_diffusion_model, unload_stable_diffusion_model
from pompei.process_pr import load_llama_model, unload_llama_model
from pathlib import Path

from privacy.secure_encoding import SecureAPILayer  # Ensure this exists in src/privacy/secure_encoding.py
from synthetic_data_generator import SyntheticConfig, SyntheticDataGenerator  # Ensure correct path
from geo.helper import generate_tile, tile_coords_to_bbox  # Ensure correct path

# Additional Imports for New Endpoints
from vortx.core.memory import EarthMemoryStore
from vortx.core.synthesis import (SynthesisPipeline, SatelliteDataSource)
from vortx.core.data_sources import (
    WeatherDataSource,
    ElevationDataSource,
    LandUseDataSource,
    ClimateDataSource,
    DataCenterDataSource,
    PowerInfrastructureDataSource,
    SatelliteTrafficDataSource,
    NightLightDataSource,
    SolarRadiationDataSource,
    AirQualityDataSource
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import json
import tempfile
from datetime import datetime, timedelta
import uuid
import logging
from logging.handlers import RotatingFileHandler
import rasterio
from rasterio.warp import transform_bounds
from rasterio.crs import CRS
import mercantile
import numpy as np
from PIL import Image
import io
from shapely.geometry import shape, mapping
from functools import wraps
from werkzeug.utils import secure_filename
from google.cloud import storage
import base64

service_account_path = os.getenv("GOOGLE_EARTH_CREDENTIALS")

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')  # Set upload folder in config

# Add a secret key for session management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Swagger configuration
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Synthetic Satellite API",
        "description": "API for generating and managing synthetic satellite imagery",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "url": "https://vortx.ai",
        }
    },
    "basePath": "/api/v1",
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header"
        }
    },
    "security": [
        {
            "ApiKeyAuth": []
        }
    ]
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

# Initialize Swagger
swagger = Swagger(app, template=swagger_template, config=swagger_config)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)

# Initialize secure API layer
secure_api = SecureAPILayer(os.getenv('MASTER_KEY', 'your-secure-master-key'))

# Register some API keys (in production, load from secure storage)
secure_api.register_api_key(
    os.getenv('API_KEY_FULL'),
    {'read', 'write', 'generate'}
)
secure_api.register_api_key(
    os.getenv('API_KEY_READ'),
    {'read'}
)

def require_api_key(permission):
    """Decorator to require API key with specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key or not secure_api.validate_api_key(api_key, permission):
                return jsonify({'error': 'Invalid or missing API key'}), 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Load configuration
config = SyntheticConfig.from_yaml('config.yaml')
generator = SyntheticDataGenerator(config)

tile_cache = TTLCache(
    maxsize=int(os.getenv('TILE_CACHE_SIZE', 1000)),
    ttl=int(os.getenv('TILE_CACHE_TTL', 3600))
)

def get_tile_key(z: int, x: int, y: int, params: Dict[str, Any]) -> str:
    """Generate unique key for tile caching"""
    param_str = json.dumps(params, sort_keys=True)
    return f"{z}_{x}_{y}_{param_str}"

# ====================
# + Existing Routes
# ====================

@app.route('/')
def index():
    """
    Redirect to API documentation.
    ---
    responses:
      302:
        description: Redirect to /apidocs/
    """
    return redirect('/apidocs/')

@app.route('/health')
@limiter.exempt
def health_check():
    """
    Health Check Endpoint
    ---
    responses:
      200:
        description: Server is healthy.
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            timestamp:
              type: string
              format: date-time
              example: "2025-01-31T12:00:00Z"
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/v1/generate', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def generate_synthetic():
    """
    Generate Synthetic Image with Geo-Privacy Protection
    ---
    tags:
      - Generation
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - image_parameters
          properties:
            image_parameters:
              type: object
              required:
                - resolution
                - format
              properties:
                resolution:
                  type: integer
                  example: 1024
                format:
                  type: string
                  enum: ['png', 'jpg', 'jpeg']
                  example: png
    responses:
      200:
        description: Successfully generated synthetic image.
        schema:
          type: object
          properties:
            image_url:
              type: string
              example: "http://34.45.181.99:5000/api/v1/download/generated_image.png"
      400:
        description: Bad Request - Missing 'image_parameters' in request body.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing 'image_parameters' in request body"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - An unexpected error occurred.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to generate image"
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        prompt = request.form.get('prompt', 'A satellite view of terrain')
        negative_prompt = request.form.get('negative_prompt', '')
        protection_level = request.form.get('protection_level', 'high')
        layout_type = request.form.get('layout_type', 'grid')
        fractal_type = request.form.get('fractal_type')

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp:
            file.save(temp.name)

        # Process image
        result = generator.process_large_image(
            input_path=temp.name,
            output_path=None,  # Don't save to disk
            prompt=prompt,
            negative_prompt=negative_prompt,
            return_array=True  # Return numpy array instead of saving
        )

        # Get geometry from input image
        with rasterio.open(temp.name) as src:
            bounds = src.bounds
            geometry = shape({
                'type': 'Polygon',
                'coordinates': [[
                    [bounds.left, bounds.bottom],
                    [bounds.right, bounds.bottom],
                    [bounds.right, bounds.top],
                    [bounds.left, bounds.top],
                    [bounds.left, bounds.bottom]
                ]]
            })

        # Cleanup
        os.unlink(temp.name)

        if result is None:
            return jsonify({'error': 'Failed to generate image'}), 500

        # Encode with geo-privacy protection
        encrypted_data, secure_metadata = secure_api.encode_tile_with_geo_privacy(
            result['image'],
            geometry,
            {
                'prompt': prompt,
                'negative_prompt': negative_prompt,
                'timestamp': datetime.utcnow().isoformat()
            },
            protection_level,
            layout_type,
            fractal_type
        )

        # Save encrypted result
        output_path = Path('outputs') / f"{uuid.uuid4()}.enc"
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)

        return jsonify({
            'status': 'success',
            'output_path': str(output_path),
            'metadata': secure_metadata
        })

    except Exception as e:
        logger.error(f"Error in generation: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/tiles/<int:z>/<int:x>/<int:y>.png', methods=['GET'])
@require_api_key('read')
def get_tile(z: int, x: int, y: int):
    """
    Serve Encrypted XYZ Tiles with Geo-Privacy Protection
    ---
    tags:
      - Tiles
    parameters:
      - name: z
        in: path
        type: integer
        required: true
        description: Zoom level
      - name: x
        in: path
        type: integer
        required: true
        description: Tile X coordinate
      - name: y
        in: path
        type: integer
        required: true
        description: Tile Y coordinate
      - name: image_url
        in: query
        type: string
        required: true
        description: URL of the source image
      - name: X-Access-Token
        in: header
        type: string
        required: true
        description: Access token for decoding the tile
    responses:
      200:
        description: Successfully retrieved the tile image.
        content:
          image/png:
            schema:
              type: string
              format: binary
      400:
        description: Bad Request - Missing 'image_url' parameter.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "image_url parameter is required"
      401:
        description: Unauthorized - Missing or invalid access token.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unauthorized"
      500:
        description: Internal Server Error - An unexpected error occurred.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to generate tile"
    """
    try:
        # Get parameters
        image_url = request.args.get('image_url')
        if not image_url:
            return jsonify({'error': 'image_url parameter is required'}), 400

        access_token = request.headers.get('X-Access-Token')
        if not access_token:
            return jsonify({'error': 'Access token required'}), 401

        # Check cache
        cache_key = get_tile_key(z, x, y, request.args)
        if cache_key in tile_cache:
            encrypted_data, secure_metadata = tile_cache[cache_key]

            # Decode tile with geo-privacy
            tile_data, geometry = secure_api.decode_tile_with_geo_privacy(
                encrypted_data,
                secure_metadata,
                access_token
            )

            if tile_data is None:
                return jsonify({'error': 'Unauthorized'}), 401

            # Convert to PNG
            img_byte_arr = io.BytesIO()
            Image.fromarray(tile_data).save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            return send_file(
                img_byte_arr,
                mimetype='image/png'
            )

        # Calculate tile bounds
        tile = mercantile.Tile(x, y, z)
        bounds = mercantile.bounds(tile)

        # Process tile
        with rasterio.open(image_url) as src:
            # Transform bounds to image CRS
            bounds_transformed = transform_bounds(
                CRS.from_epsg(4326),
                src.crs,
                *bounds
            )

            # Create geometry from bounds
            geometry = shape({
                'type': 'Polygon',
                'coordinates': [[
                    [bounds.west, bounds.south],
                    [bounds.east, bounds.south],
                    [bounds.east, bounds.north],
                    [bounds.west, bounds.north],
                    [bounds.west, bounds.south]
                ]]
            })

            # Generate tile
            result = generator.generate_synthetic_image(
                input_image=src.read(),
                prompt=request.args.get('prompt', 'A satellite view of terrain'),
                negative_prompt=request.args.get('negative_prompt', '')
            )

            if result is None:
                return jsonify({'error': 'Failed to generate tile'}), 500

            # Encode tile with geo-privacy
            encrypted_data, secure_metadata = secure_api.encode_tile_with_geo_privacy(
                result['image'],
                geometry,
                {
                    'z': z,
                    'x': x,
                    'y': y,
                    'bounds': bounds._asdict(),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )

            # Cache result
            tile_cache[cache_key] = (encrypted_data, secure_metadata)

            # Decode for response
            tile_data, _ = secure_api.decode_tile_with_geo_privacy(
                encrypted_data,
                secure_metadata,
                access_token
            )

            if tile_data is None:
                return jsonify({'error': 'Unauthorized'}), 401

            # Convert to PNG
            img_byte_arr = io.BytesIO()
            Image.fromarray(tile_data).save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            return send_file(
                img_byte_arr,
                mimetype='image/png'
            )

    except Exception as e:
        logger.error(f"Error serving tile: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/map', methods=['GET'])
def map_viewer():
    """
    Serve Map Viewer HTML Interface
    ---
    tags:
      - Map Viewer
    responses:
      200:
        description: Successfully retrieved the map viewer HTML.
        content:
          text/html:
            schema:
              type: string
              example: "<html>...</html>"
      500:
        description: Internal Server Error - Failed to retrieve map viewer.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to retrieve map viewer."
    """
    try:
        return send_from_directory('templates', 'map.html')
    except Exception as e:
        logger.error(f"Error in map_viewer: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/capabilities', methods=['GET'])
def get_capabilities():
    """
    Retrieve Server Capabilities and Configuration
    ---
    tags:
      - Capabilities
    responses:
      200:
        description: Successfully retrieved server capabilities.
        schema:
          type: object
          properties:
            version:
              type: string
              example: "1.0.0"
            supported_formats:
              type: array
              items:
                type: string
              example: ["png", "tiff"]
            max_image_size:
              type: integer
              example: 100000000
            tile_size:
              type: integer
              example: 256
            models:
              type: object
              properties:
                stable_diffusion:
                  type: string
                  example: "stable_diffusion_v1"
                controlnet:
                  type: string
                  example: "controlnet_v2"
                segmentation:
                  type: string
                  example: "segmentation_v3"
            endpoints:
              type: object
              properties:
                generate:
                  type: string
                  example: "/api/v1/generate"
                tiles:
                  type: string
                  example: "/api/v1/tiles/{z}/{x}/{y}.png"
                map:
                  type: string
                  example: "/api/v1/map"
      500:
        description: Internal Server Error - Failed to retrieve capabilities.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to retrieve capabilities."
    """
    try:
        return jsonify({
            'version': '1.0.0',
            'supported_formats': ['png', 'tiff'],
            'max_image_size': 10000 * 10000,
            'tile_size': config.tile_size,
            'models': {
                'stable_diffusion': config.stable_diffusion_model,
                'controlnet': config.controlnet_model,
                'segmentation': config.segmentation_model
            },
            'endpoints': {
                'generate': '/api/v1/generate',
                'tiles': '/api/v1/tiles/{z}/{x}/{y}.png',
                'map': '/api/v1/map'
            }
        })
    except Exception as e:
        logger.error(f"Error in get_capabilities: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/download/<path:filename>', methods=['GET'])
@require_api_key('read')
def download_result(filename):
    """
    Download Encrypted Results with Geo-Privacy Protection
    ---
    tags:
      - Download
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: Name of the file to download
      - name: X-Access-Token
        in: header
        type: string
        required: true
        description: Access token for decoding the file
    responses:
      200:
        description: Successfully downloaded the file.
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
      400:
        description: Bad Request - Missing metadata in request.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Metadata required"
      401:
        description: Unauthorized - Missing or invalid access token.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unauthorized"
      404:
        description: Not Found - File does not exist.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "File not found"
      500:
        description: Internal Server Error - Failed to download file.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to download file."
    """
    try:
        # Read encrypted data
        with open(Path('outputs') / filename, 'rb') as f:
            encrypted_data = f.read()

        # Get metadata from request
        secure_metadata = request.get_json()
        if not secure_metadata:
            return jsonify({'error': 'Metadata required'}), 400

        # Decode data with geo-privacy
        image_data, geometry = secure_api.decode_tile_with_geo_privacy(
            encrypted_data,
            secure_metadata,
            request.headers.get('X-Access-Token')
        )

        if image_data is None:
            return jsonify({'error': 'Unauthorized'}), 401

        # Convert to PNG
        img_byte_arr = io.BytesIO()
        Image.fromarray(image_data).save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return send_file(
            img_byte_arr,
            mimetype='image/png',
            as_attachment=True,
            download_name=f"{Path(filename).stem}.png"
        )

    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/locen', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def locen():
    """
    Handle Generation of Synthetic Images with Geo-Privacy Protection
    ---
    tags:
      - Location Retraction
    consumes:
      - multipart/form-data
    parameters:
      - name: Secret-Key
        in: query
        type: string
        required: true
        description: User Secret Key for authentication
      - name: image
        in: formData
        type: file
        required: true
        description: Image file to upload
    responses:
      200:
        description: Successfully generated synthetic image.
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 200
            message:
              type: string
              example: "Success"
            description:
              type: string
              example: "Description extracted from image"
            text1:
              type: string
              example: "Generated text from LLaMA model"
            scene:
              type: string
              example: "Scene description for Stable Diffusion"
            image:
              type: string
              example: "https://storage.cloud.google.com/appimage/geni1_20231005_123456.png"
      400:
        description: Bad Request - Invalid input or missing parameters.
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 400
            message:
              type: string
              example: "Invalid file type."
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 401
            message:
              type: string
              example: "Unauthorized"
      500:
        description: Internal Server Error - An unexpected error occurred.
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 500
            message:
              type: string
              example: "Internal Server Error"
    """
    try:
        # Clear GPU cache if needed
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Received a request to /locen")

        # === Authentication ===
        secret_key = request.args.get("Secret-Key")


        # === Image Validation ===
        if "image" not in request.files:
            logger.warning("No image part in the request")
            return jsonify({"status": 400, "message": "No image part in request"}), 400

        image = request.files["image"]
        if image.filename == "":
            logger.warning("No selected image")
            return jsonify({"status": 400, "message": "No selected image"}), 400

        if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            logger.warning("Invalid file type uploaded")
            return jsonify({"status": 400, "message": "Invalid file type. Only PNG, JPG, and JPEG are allowed."}), 400

        # === Load Models ===
        load_stable_diffusion_model()  # Load Stable Diffusion model
        load_llama_model()             # Load LLaMA model

        # === Save Uploaded Image ===
        upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(image.filename)
        upload_path = os.path.join(upload_folder, filename)
        image.save(upload_path)
        logger.info(f"Image saved to {upload_path}")

        # === Image Description (BLIP Model) ===
        description = extract_image_details(upload_path)
        logger.info(f"Extracted description: {description}")

        # === Generate Response (LLaMA Model) ===
        prompt = (
            f"From the sentence: \"{description}\", extract all living objects such as plants, animals, or any living entities. "
            f"Respond ONLY json containing comma separated living object names, without any additional text or examples."
        )
        generated_text = generate_prompt_from_caption(prompt)
        logger.info(f"Generated text: {generated_text}")

        # Extract JSON portion
        json_start = generated_text.find("{")
        if json_start == -1:
            raise ValueError("No JSON found in generated text")
        json_part = generated_text[json_start:].strip()
        response_dict = json.loads(json_part)

        # Extract based on the structure of the JSON
        living_objects = []
        for key, value in response_dict.items():
            if isinstance(value, str) and key.strip():  # Extract value if it's a string
                living_objects.append(key.strip())       # Extract the key (e.g., "tomatoes")
            elif isinstance(value, list):               # Handle lists if present
                living_objects.extend([item.strip() for item in value if isinstance(item, str)])

        # Ensure unique items
        living_objects = list(set(living_objects))

        logger.info(f"Extracted living objects: {living_objects}")

        # Create a description for Stable Diffusion
        prompt1 = (
            f"Create a description for a stable diffusion prompt where \"{living_objects}\" are seen in a farm. "
            f"Respond with only a descriptive sentence suitable for generating an image, without any extra text."
        )
        scene = generate_prompt_from_caption(prompt1)
        logger.info(f"Scene description for Stable Diffusion: {scene}")

        # === Generate Image (Stable Diffusion Model) ===
        generated_image = generate_image_from_text(scene, None)

        # === Save Generated Image ===
        image_byte_array = io.BytesIO()
        generated_image.save(image_byte_array, format='PNG', optimize=True, quality=85)

        image_byte_array.seek(0)
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        unique_filename = f"geni1_{timestamp}.png"
        unique_filename1 = f"up1_{timestamp}.png"

        # === Set Up Google Cloud Storage ===
        service_account_path = "/home/jaya/syn_project/peak-sorter-432307-p8-c68a06a6da43.json"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path

        bucket_name = "appimage"
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)

        # Upload original image if provided
        if upload_path:
            blob = bucket.blob(unique_filename1)
            with open(upload_path, "rb") as image_file:
                blob.upload_from_file(image_file, content_type='image/png')

            image_url1 = f"https://storage.cloud.google.com/{bucket_name}/{unique_filename1}"
        else:
            image_url1 = None

        # === Upload Generated Image to Google Cloud Storage ===
        blob = bucket.blob(unique_filename)
        blob.upload_from_string(image_byte_array.getvalue(), content_type='image/png')

        # Generate public URL
        image_url = f"https://storage.cloud.google.com/{bucket_name}/{unique_filename}"

        logger.info(f"Image uploaded successfully to: {image_url}")

        # Unload models after use to free memory
        unload_stable_diffusion_model()
        unload_llama_model()

        return jsonify({
            "status": 200,
            "message": "Success",
            "description": description,
            "text1": generated_text,
            "scene": scene,
            "image": image_url,
            "uploaded_image_url": image_url1
        }), 200

    except ValueError as e:
        logger.error(f"Value error: {e}")
        return jsonify({"status": 400, "message": str(e)}), 400
    except json.JSONDecodeError as e:
        logger.error(f"JSON error: {e}")
        return jsonify({"status": 400, "message": "Failed to parse JSON response"}), 400
    except Exception as e:
        logger.error(f"Error processing /locen: {e}")
        return jsonify({"status": 500, "message": "Internal Server Error"}), 500

@app.route('/tileformer', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def tileformer():
    """
    Generate and Serve Tile Images Based on Provided Band Images and Bounding Boxes
    ---
    tags:
      - Tile Generation
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - band_images
          properties:
            band_images:
              type: object
              required:
                - B04
                - B08
              properties:
                B04:
                  type: string
                  description: URL for the B04 band image
                  example: "http://example.com/b04_image.png"
                B08:
                  type: string
                  description: URL for the B08 band image
                  example: "http://example.com/b08_image.png"
            bounding_box:
              type: object
              properties:
                minx:
                  type: number
                  example: -118.5
                miny:
                  type: number
                  example: 33.9
                maxx:
                  type: number
                  example: -118.0
                maxy:
                  type: number
                  example: 34.2
            tile_size:
              type: integer
              example: 256
            algorithm:
              type: string
              description: Processing algorithm
              example: "transformer"
    responses:
      200:
        description: Successfully generated tile image.
        content:
          image/png:
            schema:
              type: string
              format: binary
      400:
        description: Bad Request - Missing required parameters or unsupported algorithm.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Both 'B04' and 'B08' image URLs are required"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - Failed to generate tile.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to generate tile"
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request payload must be in JSON format"}), 400

        # Validate band image URLs
        band_images = data.get("band_images")
        if not band_images or 'B04' not in band_images or 'B08' not in band_images:
            return jsonify({"error": "Both 'B04' and 'B08' image URLs are required"}), 400

        b04_url = band_images['B04']
        b08_url = band_images['B08']

        # Validate and parse bounding box parameters
        bounding_box = data.get("bounding_box", {})
        try:
            minx = float(bounding_box.get("minx", -180))
            miny = float(bounding_box.get("miny", -90))
            maxx = float(bounding_box.get("maxx", 180))
            maxy = float(bounding_box.get("maxy", 90))
        except ValueError:
            return jsonify({"error": "Bounding box parameters must be numeric"}), 400

        tile_size = int(data.get('tile_size', 256))
        algorithm = data.get('algorithm', 'transformer')

        bbox = [minx, miny, maxx, maxy]

        # Generate and serve the tile
        img_byte_arr = generate_tile(b04_url, b08_url, bbox, tile_size, algorithm)

        if img_byte_arr:
            img_byte_arr.seek(0)
            return send_file(img_byte_arr, mimetype='image/png')
        else:
            return jsonify({"error": f"Unsupported algorithm '{algorithm}'"}), 400

    except Exception as e:
        logger.error(f"Error in tileformer: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ====================
# + New Advanced Analysis Endpoints
# ====================

# Initialize services for advanced APIs
data_sources_memory = {
    "datacenter": DataCenterDataSource(),
    "power": PowerInfrastructureDataSource(),
    "satellite": SatelliteTrafficDataSource(),
    "nightlight": NightLightDataSource(),
    "solar": SolarRadiationDataSource(),
    "air": AirQualityDataSource()
}

pipeline_memory = SynthesisPipeline(
    data_sources=list(data_sources_memory.values()),
    memory_store=EarthMemoryStore(Path("/app/data/memories"))
)

@app.route('/api/v1/advanced/analyze_datacenters', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def analyze_datacenters():
    """
    Analyze Data Centers and Their Infrastructure
    ---
    tags:
      - Advanced Analysis
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
          properties:
            latitude:
              type: number
              example: 34.05
            longitude:
              type: number
              example: -118.25
            radius_km:
              type: number
              example: 50.0
            include_power:
              type: boolean
              example: true
            include_climate:
              type: boolean
              example: true
    responses:
      200:
        description: Successfully analyzed data centers.
        schema:
          type: object
          properties:
            data_centers:
              type: object
              properties:
                count:
                  type: integer
                total_area_km2:
                  type: number
                average_distance_km:
                  type: number
            power_infrastructure:
              type: object
              properties:
                transmission_lines:
                  type: integer
                power_stations:
                  type: integer
                substations:
                  type: integer
                power_plants:
                  type: integer
                towers:
                  type: integer
            environmental_impact:
              type: object
              properties:
                air_quality:
                  type: object
                  properties:
                    pm25:
                      type: number
                    pm10:
                      type: number
                    no2:
                      type: number
                    o3:
                      type: number
                    so2:
                      type: number
                    co:
                      type: number
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - An unexpected error occurred.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to analyze data centers."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        radius_km = data.get('radius_km', 50.0)
        include_power = data.get('include_power', True)
        include_climate = data.get('include_climate', True)

        results = {}

        # Analyze Data Centers
        dc_data = data_sources_memory['datacenter'].load_data(
            coordinates=(latitude, longitude),
            timestamp=datetime.now()
        )
        results["data_centers"] = {
            "count": int(dc_data[0, 0, 0]),
            "total_area_km2": float(dc_data[1, 0, 0]),
            "average_distance_km": float(dc_data[2, 0, 0])
        }

        if include_power:
            # Analyze Power Infrastructure
            power_data = data_sources_memory['power'].load_data(
                coordinates=(latitude, longitude),
                timestamp=datetime.now()
            )
            results["power_infrastructure"] = {
                "transmission_lines": int(power_data[0, 0, 0]),
                "power_stations": int(power_data[1, 0, 0]),
                "substations": int(power_data[2, 0, 0]),
                "power_plants": int(power_data[3, 0, 0]),
                "towers": int(power_data[4, 0, 0])
            }

        if include_climate:
            # Analyze Environmental Impact
            air_data = data_sources_memory['air'].load_data(
                coordinates=(latitude, longitude),
                timestamp=datetime.now()
            )
            results["environmental_impact"] = {
                "air_quality": {
                    "pm25": float(air_data[0, 0, 0]),
                    "pm10": float(air_data[1, 0, 0]),
                    "no2": float(air_data[2, 0, 0]),
                    "o3": float(air_data[3, 0, 0]),
                    "so2": float(air_data[4, 0, 0]),
                    "co": float(air_data[5, 0, 0])
                }
            }

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error in analyze_datacenters: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/advanced/analyze_energy', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def analyze_energy():
    """
    Analyze Energy Infrastructure and Potential
    ---
    tags:
      - Advanced Analysis
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
          properties:
            latitude:
              type: number
              example: 34.05
            longitude:
              type: number
              example: -118.25
            radius_km:
              type: number
              example: 50.0
            analyze_solar_potential:
              type: boolean
              example: true
            include_consumption:
              type: boolean
              example: true
    responses:
      200:
        description: Successfully analyzed energy infrastructure.
        schema:
          type: object
          properties:
            infrastructure:
              type: object
              properties:
                transmission_lines:
                  type: integer
                power_stations:
                  type: integer
                substations:
                  type: integer
                power_plants:
                  type: integer
                towers:
                  type: integer
            estimated_consumption:
              type: object
              properties:
                night_light_intensity:
                  type: number
            solar_potential:
              type: object
              properties:
                global_horizontal_irradiance:
                  type: number
                direct_normal_irradiance:
                  type: number
                diffuse_horizontal_irradiance:
                  type: number
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - An unexpected error occurred.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to analyze energy infrastructure."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        radius_km = data.get('radius_km', 50.0)
        analyze_solar_potential = data.get('analyze_solar_potential', True)
        include_consumption = data.get('include_consumption', True)

        results = {}

        # Analyze Power Infrastructure
        power_data = data_sources_memory['power'].load_data(
            coordinates=(latitude, longitude),
            timestamp=datetime.now()
        )
        results["infrastructure"] = {
            "transmission_lines": int(power_data[0, 0, 0]),
            "power_stations": int(power_data[1, 0, 0]),
            "substations": int(power_data[2, 0, 0]),
            "power_plants": int(power_data[3, 0, 0]),
            "towers": int(power_data[4, 0, 0])
        }

        if include_consumption:
            # Analyze Estimated Consumption
            night_data = data_sources_memory['nightlight'].load_data(
                coordinates=(latitude, longitude),
                timestamp=datetime.now()
            )
            results["estimated_consumption"] = {
                "night_light_intensity": float(night_data[0, 0, 0])
            }

        if analyze_solar_potential:
            # Analyze Solar Potential
            solar_data = data_sources_memory['solar'].load_data(
                coordinates=(latitude, longitude),
                timestamp=datetime.now()
            )
            results["solar_potential"] = {
                "global_horizontal_irradiance": float(solar_data[0, 0, 0]),
                "direct_normal_irradiance": float(solar_data[1, 0, 0]),
                "diffuse_horizontal_irradiance": float(solar_data[2, 0, 0])
            }

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error in analyze_energy: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/advanced/analyze_spacetech', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def analyze_spacetech():
    """
    Analyze Satellite Coverage and Space Infrastructure
    ---
    tags:
      - Advanced Analysis
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
          properties:
            latitude:
              type: number
              example: 34.05
            longitude:
              type: number
              example: -118.25
            time_window_hours:
              type: integer
              example: 24
            include_coverage:
              type: boolean
              example: true
            include_interference:
              type: boolean
              example: true
    responses:
      200:
        description: Successfully analyzed space technology.
        schema:
          type: object
          properties:
            satellite_traffic:
              type: object
              properties:
                total_satellites:
                  type: integer
                starlink_satellites:
                  type: integer
                onewweb_satellites:
                  type: integer
                other_satellites:
                  type: integer
            coverage_analysis:
              type: object
              properties:
                estimated_coverage_hours:
                  type: number
                coverage_percentage:
                  type: number
            interference_analysis:
              type: object
              properties:
                satellite_density:
                  type: number
                potential_interference_level:
                  type: string
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - An unexpected error occurred.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to analyze space technology."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        time_window_hours = data.get('time_window_hours', 24)
        include_coverage = data.get('include_coverage', True)
        include_interference = data.get('include_interference', True)

        results = {}

        # Analyze Satellite Traffic
        sat_data = data_sources_memory['satellite'].load_data(
            coordinates=(latitude, longitude),
            timestamp=datetime.now()
        )
        results["satellite_traffic"] = {
            "total_satellites": int(sat_data[0, 0, 0]),
            "starlink_satellites": int(sat_data[1, 0, 0]),
            "oneweb_satellites": int(sat_data[2, 0, 0]),
            "other_satellites": int(sat_data[3, 0, 0])
        }

        if include_coverage:
            # Calculate Coverage Analysis
            coverage_hours = min(sat_data[1, 0, 0] + sat_data[2, 0, 0], 24) * 0.8
            results["coverage_analysis"] = {
                "estimated_coverage_hours": float(coverage_hours),
                "coverage_percentage": float(coverage_hours / 24 * 100)
            }

        if include_interference:
            # Analyze Potential Interference
            satellite_density = float(sat_data[0, 0, 0] / 100)  # per 100 km²
            if sat_data[0, 0, 0] > 100:
                interference_level = "high"
            elif sat_data[0, 0, 0] > 50:
                interference_level = "medium"
            else:
                interference_level = "low"
            results["interference_analysis"] = {
                "satellite_density": satellite_density,
                "potential_interference_level": interference_level
            }

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error in analyze_spacetech: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/advanced/analyze_agi_infrastructure', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def analyze_agi_infrastructure():
    """
    Analyze Infrastructure Relevant for AGI Deployment
    ---
    tags:
      - Advanced Analysis
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
          properties:
            latitude:
              type: number
              example: 34.05
            longitude:
              type: number
              example: -118.25
            radius_km:
              type: number
              example: 50.0
            include_compute:
              type: boolean
              example: true
            include_network:
              type: boolean
              example: true
            include_power:
              type: boolean
              example: true
    responses:
      200:
        description: Successfully analyzed AGI infrastructure.
        schema:
          type: object
          properties:
            location:
              type: object
              properties:
                coordinates:
                  type: array
                  items:
                    type: number
                  example: [34.05, -118.25]
                radius_km:
                  type: number
                  example: 50.0
            compute_infrastructure:
              type: object
              properties:
                data_centers:
                  type: object
                  properties:
                    count:
                      type: integer
                    total_area_km2:
                      type: number
                    average_distance_km:
                      type: number
            network_infrastructure:
              type: object
              properties:
                development_level:
                  type: string
                night_light_intensity:
                  type: number
            power_infrastructure:
              type: object
              properties:
                transmission_lines:
                  type: integer
                power_stations:
                  type: integer
                substations:
                  type: integer
                power_plants:
                  type: integer
                estimated_capacity_mw:
                  type: number
            agi_suitability:
              type: object
              properties:
                score:
                  type: number
                level:
                  type: string
                limiting_factors:
                  type: array
                  items:
                    type: string
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - An unexpected error occurred.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to analyze AGI infrastructure."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        radius_km = data.get('radius_km', 50.0)
        include_compute = data.get('include_compute', True)
        include_network = data.get('include_network', True)
        include_power = data.get('include_power', True)

        results = {
            "location": {
                "coordinates": [latitude, longitude],
                "radius_km": radius_km
            }
        }

        # Analyze Compute Infrastructure
        if include_compute:
            dc_data = data_sources_memory['datacenter'].load_data(
                coordinates=(latitude, longitude),
                timestamp=datetime.now()
            )
            results["compute_infrastructure"] = {
                "data_centers": {
                    "count": int(dc_data[0, 0, 0]),
                    "total_area_km2": float(dc_data[1, 0, 0]),
                    "average_distance_km": float(dc_data[2, 0, 0])
                }
            }

        # Analyze Network Infrastructure
        if include_network:
            night_data = data_sources_memory['nightlight'].load_data(
                coordinates=(latitude, longitude),
                timestamp=datetime.now()
            )
            development_level = "high" if night_data[0, 0, 0] > 50 else "medium" if night_data[0, 0, 0] > 20 else "low"
            results["network_infrastructure"] = {
                "development_level": development_level,
                "night_light_intensity": float(night_data[0, 0, 0])
            }

        # Analyze Power Infrastructure
        if include_power:
            power_data = data_sources_memory['power'].load_data(
                coordinates=(latitude, longitude),
                timestamp=datetime.now()
            )
            results["power_infrastructure"] = {
                "transmission_lines": int(power_data[0, 0, 0]),
                "power_stations": int(power_data[1, 0, 0]),
                "substations": int(power_data[2, 0, 0]),
                "power_plants": int(power_data[3, 0, 0]),
                "estimated_capacity_mw": float(power_data[3, 0, 0] * 100)  # Rough estimate
            }

        # Calculate Overall AGI Suitability Score
        if include_compute and include_network and include_power:
            compute_score = min(dc_data[0, 0, 0] / 10, 1.0)  # Normalize by 10 data centers
            network_score = night_data[0, 0, 0] / 100  # Normalize by 100 intensity
            power_score = min(power_data[3, 0, 0] / 5, 1.0)  # Normalize by 5 power plants

            overall_score = (compute_score + network_score + power_score) / 3
            level = "high" if overall_score > 0.7 else "medium" if overall_score > 0.4 else "low"

            limiting_factors = []
            if compute_score < 0.3:
                limiting_factors.append("compute_infrastructure")
            if network_score < 0.3:
                limiting_factors.append("network_infrastructure")
            if power_score < 0.3:
                limiting_factors.append("power_infrastructure")

            results["agi_suitability"] = {
                "score": float(overall_score),
                "level": level,
                "limiting_factors": limiting_factors
            }

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error in analyze_agi_infrastructure: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ====================
# + New Analysis Endpoints
# ====================

@app.route('/api/v1/analysis/detect_changes', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def detect_environmental_changes():
    """
    Detect and Analyze Environmental Changes Over Time
    ---
    tags:
      - Analysis
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
            - start_time
            - end_time
          properties:
            latitude:
              type: number
              example: 34.05
            longitude:
              type: number
              example: -118.25
            start_time:
              type: string
              format: date-time
              example: "2023-01-01T00:00:00Z"
            end_time:
              type: string
              format: date-time
              example: "2023-12-31T23:59:59Z"
            interval_days:
              type: integer
              example: 30
            change_threshold:
              type: number
              example: 0.1
    responses:
      200:
        description: Successfully detected environmental changes.
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            total_intervals:
              type: integer
              example: 12
            significant_changes:
              type: array
              items:
                type: object
                properties:
                  timestamp:
                    type: string
                    format: date-time
                  change_magnitude:
                    type: number
                  previous_state:
                    type: object
                  current_state:
                    type: object
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - Failed to detect environmental changes.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to detect environmental changes."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude', 'start_time', 'end_time']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        start_time_str = data['start_time']
        end_time_str = data['end_time']
        interval_days = data.get('interval_days', 30)
        change_threshold = data.get('change_threshold', 0.1)

        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid datetime format"}), 400

        # Process time series data
        results = pipeline_memory.process_time_series(
            coordinates=(latitude, longitude),
            time_range=(start_time, end_time),
            interval_days=interval_days
        )

        # Analyze changes
        changes = []
        for i in range(1, len(results)):
            prev_data = results[i-1]["data"]
            curr_data = results[i]["data"]

            # Calculate change metrics
            diff = np.mean(np.abs(curr_data - prev_data))
            if diff > change_threshold:
                changes.append({
                    "timestamp": results[i]["metadata"]["timestamp"].isoformat(),
                    "change_magnitude": float(diff),
                    "previous_state": results[i-1]["metadata"],
                    "current_state": results[i]["metadata"]
                })

        return jsonify({
            "status": "success",
            "total_intervals": len(results),
            "significant_changes": changes
        }), 200

    except Exception as e:
        logger.error(f"Error in detect_environmental_changes: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/analysis/find_similar', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def find_similar_locations():
    """
    Find Locations with Similar Environmental Characteristics
    ---
    tags:
      - Analysis
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
            - timestamp
          properties:
            latitude:
              type: number
              example: 34.05
            longitude:
              type: number
              example: -118.25
            timestamp:
              type: string
              format: date-time
              example: "2023-06-15T12:00:00Z"
            radius_km:
              type: number
              example: 100.0
            limit:
              type: integer
              example: 5
    responses:
      200:
        description: Successfully found similar locations.
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            reference_location:
              type: object
              properties:
                coordinates:
                  type: array
                  items:
                    type: number
                  example: [34.05, -118.25]
                metadata:
                  type: object
            similar_locations:
              type: array
              items:
                type: object
                properties:
                  coordinates:
                    type: array
                    items:
                      type: number
                    example: [34.10, -118.20]
                  distance_km:
                    type: number
                    example: 5.0
                  similarity_score:
                    type: number
                    example: 0.95
                  metadata:
                    type: object
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude', 'timestamp']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - Failed to find similar locations.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to find similar locations."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude', 'timestamp']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        timestamp_str = data['timestamp']
        radius_km = data.get('radius_km', 100.0)
        limit = data.get('limit', 5)

        # Parse datetime string
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid datetime format"}), 400

        # Process reference location
        reference = pipeline_memory.process_location(
            coordinates=(latitude, longitude),
            timestamp=timestamp
        )

        # Query similar locations from memory store
        similar = pipeline_memory.memory_store.query_memories(
            coordinates=(latitude, longitude),
            time_range=None,  # Assuming no time range filter
            k=limit
        )

        # Calculate similarity scores
        results = []
        for mem in similar:
            # Calculate distance
            dist_km = np.sqrt(
                (mem["coordinates"][0] - latitude)**2 +
                (mem["coordinates"][1] - longitude)**2
            ) * 111  # Rough km conversion

            if dist_km <= radius_km:
                # Calculate feature similarity
                similarity = np.dot(
                    reference["embedding"].flatten(),
                    mem["embedding"].flatten()
                )
                similarity /= (np.linalg.norm(reference["embedding"].flatten()) * np.linalg.norm(mem["embedding"].flatten()) + 1e-8)  # Normalize

                results.append({
                    "coordinates": mem["coordinates"],
                    "distance_km": float(dist_km),
                    "similarity_score": float(similarity),
                    "metadata": mem["metadata"]
                })

        # Sort by similarity score descending
        sorted_results = sorted(
            results,
            key=lambda x: x["similarity_score"],
            reverse=True
        )

        return jsonify({
            "status": "success",
            "reference_location": {
                "coordinates": (latitude, longitude),
                "metadata": reference["metadata"]
            },
            "similar_locations": sorted_results
        }), 200

    except Exception as e:
        logger.error(f"Error in find_similar_locations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/analysis/get_context', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def get_location_context():
    """
    Get Comprehensive Context for a Location
    ---
    tags:
      - Analysis
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
            - timestamp
          properties:
            latitude:
              type: number
              example: 34.05
            longitude:
              type: number
              example: -118.25
            timestamp:
              type: string
              format: date-time
              example: "2023-06-15T12:00:00Z"
            context_window_days:
              type: integer
              example: 365
    responses:
      200:
        description: Successfully retrieved location context.
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            current_state:
              type: object
              properties:
                timestamp:
                  type: string
                  format: date-time
                metadata:
                  type: object
            historical_trends:
              type: object
              additionalProperties:
                type: object
                properties:
                  mean:
                    type: number
                  std:
                    type: number
                  min:
                    type: number
                  max:
                    type: number
            temporal_context:
              type: object
              properties:
                window_days:
                  type: integer
                data_points:
                  type: integer
                first_observation:
                  type: string
                  format: date-time
                last_observation:
                  type: string
                  format: date-time
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude', 'timestamp']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - Failed to retrieve location context.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to retrieve location context."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude', 'timestamp']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        timestamp_str = data['timestamp']
        context_window_days = data.get('context_window_days', 365)

        # Parse datetime string
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid datetime format"}), 400

        # Get current state
        current = pipeline_memory.process_location(
            coordinates=(latitude, longitude),
            timestamp=timestamp
        )

        # Get historical context
        start_time = timestamp - timedelta(days=context_window_days)
        historical = pipeline_memory.process_time_series(
            coordinates=(latitude, longitude),
            time_range=(start_time, timestamp),
            interval_days=30
        )

        # Analyze trends
        trends = {}
        for source in data_sources_memory.values():
            source_name = source.name  # Assuming each data source has a 'name' attribute
            source_data = [
                result["metadata"].get(f"{source_name}_resolution")
                for result in historical
                if f"{source_name}_resolution" in result["metadata"]
            ]
            if source_data:
                trends[source_name] = {
                    "mean": float(np.mean(source_data)),
                    "std": float(np.std(source_data)),
                    "min": float(np.min(source_data)),
                    "max": float(np.max(source_data))
                }

        # Prepare temporal context
        temporal_context = {
            "window_days": context_window_days,
            "data_points": len(historical),
            "first_observation": historical[0]["metadata"]["timestamp"].isoformat() if historical else None,
            "last_observation": historical[-1]["metadata"]["timestamp"].isoformat() if historical else None
        }

        return jsonify({
            "status": "success",
            "current_state": {
                "timestamp": current["metadata"]["timestamp"],
                "metadata": current["metadata"]
            },
            "historical_trends": trends,
            "temporal_context": temporal_context
        }), 200

    except Exception as e:
        logger.error(f"Error in get_location_context: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/analysis/decision_support', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def decision_support():
    """
    Get Decision Support Analysis for a Location
    ---
    tags:
      - Analysis
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
            - analysis_type
          properties:
            latitude:
              type: number
              example: 34.05
            longitude:
              type: number
              example: -118.25
            analysis_type:
              type: string
              description: "Type of analysis to perform"
              example: "land_use_change"
            parameters:
              type: object
              additionalProperties:
                type: any
    responses:
      200:
        description: Successfully performed decision support analysis.
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            analysis_results:
              type: object
      400:
        description: Invalid input parameters or unsupported analysis type.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unsupported analysis type: unknown_type"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - Failed to perform analysis.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to perform analysis."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude', 'analysis_type']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        analysis_type = data['analysis_type']
        parameters = data.get('parameters', {})

        # Prepare a mock request object or extract additional parameters as needed
        request_payload = {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.now().isoformat()
        }

        if analysis_type == "land_use_change":
            # Analyze land use changes and their implications
            return analyze_land_use_impact(data)
        elif analysis_type == "climate_risk":
            # Assess climate-related risks
            return analyze_climate_risk(data)
        elif analysis_type == "environmental_impact":
            # Evaluate environmental impact
            return analyze_environmental_impact(data)
        else:
            return jsonify({
                "error": f"Unsupported analysis type: {analysis_type}"
            }), 400

    except Exception as e:
        logger.error(f"Error in decision_support: {str(e)}")
        return jsonify({"error": str(e)}), 500

def analyze_land_use_impact(data: Dict[str, Any]):
    """Analyze land use changes and their implications."""
    try:
        # Implement the specific logic for land use impact analysis
        # Placeholder implementation
        results = {
            "land_use_changes": [
                {"type": "deforestation", "magnitude": 0.2, "implications": "loss of biodiversity"},
                {"type": "urbanization", "magnitude": 0.3, "implications": "increased pollution"}
            ],
            "overall_impact": "significant"
        }
        return jsonify({
            "status": "success",
            "analysis_results": results
        }), 200
    except Exception as e:
        logger.error(f"Error in analyze_land_use_impact: {str(e)}")
        return jsonify({"error": str(e)}), 500

def analyze_climate_risk(data: Dict[str, Any]):
    """Assess climate-related risks for a location."""
    try:
        # Implement the specific logic for climate risk assessment
        # Placeholder implementation
        results = {
            "risks": {
                "flooding": {"probability": 0.3, "impact": "moderate"},
                "drought": {"probability": 0.2, "impact": "low"},
                "hurricane": {"probability": 0.1, "impact": "high"}
            },
            "overall_risk_level": "medium"
        }
        return jsonify({
            "status": "success",
            "analysis_results": results
        }), 200
    except Exception as e:
        logger.error(f"Error in analyze_climate_risk: {str(e)}")
        return jsonify({"error": str(e)}), 500

def analyze_environmental_impact(data: Dict[str, Any]):
    """Evaluate environmental impact of changes."""
    try:
        # Implement the specific logic for environmental impact evaluation
        # Placeholder implementation
        results = {
            "impact_factors": {
                "air_quality": {"pm25_increase": 5.0, "pm10_increase": 10.0},
                "water_quality": {"contaminants": ["lead", "mercury"], "levels": [0.05, 0.02]},
                "soil_quality": {"erosion_rate": 0.1}
            },
            "overall_impact": "high"
        }
        return jsonify({
            "status": "success",
            "analysis_results": results
        }), 200
    except Exception as e:
        logger.error(f"Error in analyze_environmental_impact: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ====================
# + Memory Analysis Endpoints
# ====================

@app.route('/api/v1/memory/query', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def query_memories_endpoint():
    """
    Query Memories by Location and Time Range
    ---
    tags:
      - Memory
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
          properties:
            latitude:
              type: number
              format: float
              example: 34.05
            longitude:
              type: number
              format: float
              example: -118.25
            start_time:
              type: string
              format: date-time
              example: "2023-01-01T00:00:00Z"
            end_time:
              type: string
              format: date-time
              example: "2023-12-31T23:59:59Z"
            limit:
              type: integer
              example: 5
    responses:
      200:
        description: Successfully queried memories.
        schema:
          type: array
          items:
            type: object
            properties:
              coordinates:
                type: array
                items:
                  type: number
                example: [34.05, -118.25]
              timestamp:
                type: string
                format: date-time
              metadata:
                type: object
              embedding:
                type: array
                items:
                  type: number
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - Failed to query memories.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to query memories."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        limit = data.get('limit', 5)

        # Parse datetime strings if provided
        time_range = None
        if start_time_str and end_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                time_range = (start_time, end_time)
            except ValueError:
                return jsonify({"error": "Invalid datetime format"}), 400

        # Query memories
        memories = pipeline_memory.memory_store.query_memories(
            coordinates=(latitude, longitude),
            time_range=time_range,
            k=limit
        )

        # Prepare response
        response = []
        for mem in memories:
            response.append({
                "coordinates": mem["coordinates"],
                "timestamp": mem["timestamp"].isoformat(),
                "metadata": mem["metadata"],
                "embedding": mem["embedding"].tolist()
            })

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in query_memories_endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/memory/process', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def process_location_endpoint():
    """
    Process a New Location and Store It in Memory
    ---
    tags:
      - Memory
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
            - timestamp
          properties:
            latitude:
              type: number
              format: float
              example: 34.05
            longitude:
              type: number
              format: float
              example: -118.25
            timestamp:
              type: string
              format: date-time
              example: "2023-06-15T12:00:00Z"
            metadata:
              type: object
              example: {"additional_info": "Sample metadata"}
    responses:
      200:
        description: Successfully processed location.
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            embedding:
              type: array
              items:
                type: number
            metadata:
              type: object
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude', 'timestamp']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - Failed to process location.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to process location."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude', 'timestamp']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        timestamp_str = data['timestamp']
        metadata = data.get('metadata')

        # Parse datetime string
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid datetime format"}), 400

        # Process location
        result = pipeline_memory.process_location(
            coordinates=(latitude, longitude),
            timestamp=timestamp,
            metadata=metadata
        )

        return jsonify({
            "status": "success",
            "embedding": result["embedding"].tolist(),
            "metadata": result["metadata"]
        }), 200

    except Exception as e:
        logger.error(f"Error in process_location_endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/memory/process_time_series', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key('generate')
def process_time_series_endpoint():
    """
    Process a Location Across a Time Range and Store the Time Series Data in Memory
    ---
    tags:
      - Memory
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - latitude
            - longitude
            - start_time
            - end_time
          properties:
            latitude:
              type: number
              format: float
              example: 34.05
            longitude:
              type: number
              format: float
              example: -118.25
            start_time:
              type: string
              format: date-time
              example: "2023-01-01T00:00:00Z"
            end_time:
              type: string
              format: date-time
              example: "2023-12-31T23:59:59Z"
            interval_days:
              type: integer
              example: 1
    responses:
      200:
        description: Successfully processed time series.
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            count:
              type: integer
              example: 365
            results:
              type: array
              items:
                type: object
                properties:
                  timestamp:
                    type: string
                    format: date-time
                  embedding:
                    type: array
                    items:
                      type: number
                  metadata:
                    type: object
      400:
        description: Invalid input parameters.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['latitude', 'longitude', 'start_time', 'end_time']"
      401:
        description: Unauthorized - Invalid or missing API key.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error - Failed to process time series.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to process time series."
    """
    try:
        data = request.get_json()
        required_fields = ['latitude', 'longitude', 'start_time', 'end_time']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

        latitude = data['latitude']
        longitude = data['longitude']
        start_time_str = data['start_time']
        end_time_str = data['end_time']
        interval_days = data.get('interval_days', 1)

        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid datetime format"}), 400

        # Process time series data
        results = pipeline_memory.process_time_series(
            coordinates=(latitude, longitude),
            time_range=(start_time, end_time),
            interval_days=interval_days
        )

        return jsonify({
            "status": "success",
            "count": len(results),
            "results": [
                {
                    "timestamp": result["metadata"]["timestamp"].isoformat(),
                    "embedding": result["embedding"].tolist(),
                    "metadata": result["metadata"]
                }
                for result in results
            ]
        }), 200

    except Exception as e:
        logger.error(f"Error in process_time_series_endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/memory/health', methods=['GET'])
@limiter.exempt
def memory_health_check():
    """
    Check the Health of the Memory Service
    ---
    tags:
      - Memory
    responses:
      200:
        description: Returns the health status of the memory service.
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            memory_count:
              type: integer
              example: 1500
      500:
        description: Internal Server Error - Failed to check memory health.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to check memory health."
    """
    try:
        return jsonify({
            "status": "healthy",
            "memory_count": len(pipeline_memory.memory_store.memory_index)
        }), 200
    except Exception as e:
        logger.error(f"Error in memory_health_check: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ====================
# + Finalizing the App
# ====================

if __name__ == '__main__':
    # Create necessary directories
    Path('outputs').mkdir(exist_ok=True)

    # Run app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False
    )
