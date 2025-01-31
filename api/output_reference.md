#tileformer
    
#health check api: """
    Health Check Endpoint
    ---
    responses:
      200:
        description: Returns the health status of the application
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            timestamp:
              type: string
              format: date-time
    """

#generate synthetic :  """
    Generate Synthetic Satellite Image
    ---
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
                  example: png
                # Add other relevant parameters as needed
    responses:
      200:
        description: Successfully generated synthetic image
        schema:
          type: object
          properties:
            image_url:
              type: string
              example: http://34.45.181.99:5000/api/v1/download/generated_image.png
      400:
        description: Invalid input parameters
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing 'image_parameters' in request body"
      401:
        description: Unauthorized - Invalid or missing API key
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Detailed error message"
    """

#get tile api : """
    Retrieve Encrypted XYZ Tile
    ---
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
        description: Tile's X coordinate
      - name: y
        in: path
        type: integer
        required: true
        description: Tile's Y coordinate
    responses:
      200:
        description: Returns the encrypted tile image
        content:
          image/png:
            schema:
              type: string
              format: binary
      401:
        description: Unauthorized - Invalid or missing API key
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      404:
        description: Tile not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Tile not found"
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Detailed error message"
    """

#map api : """
    Serve Map Viewer HTML
    ---
    responses:
      200:
        description: Returns the map viewer HTML page
        content:
          text/html:
            schema:
              type: string
              example: "<!DOCTYPE html>..."
      404:
        description: HTML template not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Template not found"
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Detailed error message"
    """

#capabilities api : """
    Get Server Capabilities and Configuration
    ---
    responses:
      200:
        description: Returns the server capabilities and configuration
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
                  example: "stable_diffusion_model_v1"
                controlnet:
                  type: string
                  example: "controlnet_model_v2"
                segmentation:
                  type: string
                  example: "segmentation_model_v3"
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
        description: Internal Server Error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Detailed error message"
    """

#"""
    Download Encrypted Results with Geo-Privacy Protection
    ---
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: Name of the file to download
    responses:
      200:
        description: Returns the encrypted file for download
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
      401:
        description: Unauthorized - Invalid or missing API key
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or missing API key"
      404:
        description: File not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "File not found"
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Detailed error message"
    """

#locen api : """
    Handle Generation of Synthetic Images with Geo-Privacy Protection
    ---
    responses:
      200:
        description: Successfully processed location
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
            description:
              type: string
            text1:
              type: string
            scene:
              type: string
            image:
              type: string
            uploaded_image_url:
              type: string
      400:
        description: Invalid input parameters
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Unauthorized - Invalid or missing API key
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            error:
              type: string
    """
