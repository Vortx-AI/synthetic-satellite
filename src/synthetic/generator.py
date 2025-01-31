"""Synthetic satellite data generation module"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from pathlib import Path
import rasterio
from rasterio.transform import from_origin
from datetime import datetime
import json
from noise import snoise2, snoise3
import cv2
from scipy import ndimage
import random
from dataclasses import dataclass

@dataclass
class TerrainParams:
    """Parameters for terrain generation"""
    elevation_scale: float = 1000.0
    roughness: float = 0.5
    persistence: float = 0.5
    octaves: int = 6
    base_frequency: float = 0.02

@dataclass
class AtmosphericParams:
    """Parameters for atmospheric effects"""
    cloud_coverage: float = 0.3
    haze_intensity: float = 0.2
    aerosol_density: float = 0.1
    shadow_intensity: float = 0.4

@dataclass
class SpectralParams:
    """Parameters for spectral characteristics"""
    band_correlations: Dict[str, float]
    spectral_noise: float = 0.1
    sensor_gain: float = 1.0
    quantization_bits: int = 12

class SyntheticGenerator:
    """Generator for synthetic satellite imagery"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Set default parameters
        self.image_size = self.config.get("image_size", (1024, 1024))
        self.num_bands = self.config.get("num_bands", 4)  # RGBN by default
        self.resolution = self.config.get("resolution", 10)  # meters/pixel
        
        # Initialize random seed
        np.random.seed(self.config.get("random_seed", 42))
    
    def generate_scene(self,
                      output_path: Path,
                      terrain_params: Optional[TerrainParams] = None,
                      atmospheric_params: Optional[AtmosphericParams] = None,
                      spectral_params: Optional[SpectralParams] = None) -> Dict[str, Any]:
        """Generate a synthetic satellite scene"""
        try:
            # Use default parameters if not provided
            terrain_params = terrain_params or TerrainParams()
            atmospheric_params = atmospheric_params or AtmosphericParams()
            spectral_params = spectral_params or SpectralParams(
                band_correlations={
                    "red": 1.0,
                    "green": 0.8,
                    "blue": 0.6,
                    "nir": 0.4
                }
            )
            
            # Generate base terrain
            terrain = self._generate_terrain(terrain_params)
            
            # Generate spectral bands
            bands = self._generate_spectral_bands(
                terrain,
                spectral_params
            )
            
            # Apply atmospheric effects
            bands = self._apply_atmospheric_effects(
                bands,
                atmospheric_params
            )
            
            # Save as GeoTIFF
            metadata = self._save_geotiff(bands, output_path)
            
            # Return metadata
            return {
                "metadata": metadata,
                "parameters": {
                    "terrain": vars(terrain_params),
                    "atmospheric": vars(atmospheric_params),
                    "spectral": vars(spectral_params)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating synthetic scene: {e}")
            raise
    
    def _generate_terrain(self, params: TerrainParams) -> np.ndarray:
        """Generate synthetic terrain using Perlin noise"""
        height, width = self.image_size
        terrain = np.zeros((height, width))
        
        # Generate multiple octaves of noise
        for octave in range(params.octaves):
            frequency = params.base_frequency * (2 ** octave)
            amplitude = params.elevation_scale * (params.persistence ** octave)
            
            # Generate noise layer
            noise_layer = np.zeros((height, width))
            for y in range(height):
                for x in range(width):
                    noise_layer[y, x] = snoise2(
                        x * frequency,
                        y * frequency,
                        octave=1,
                        persistence=params.persistence,
                        lacunarity=2.0,
                        repeatx=width,
                        repeaty=height,
                        base=random.randint(0, 1000)
                    )
            
            terrain += noise_layer * amplitude
        
        # Normalize terrain
        terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
        
        # Apply roughness
        if params.roughness > 0:
            terrain = ndimage.gaussian_filter(
                terrain,
                sigma=1.0 / params.roughness
            )
        
        return terrain
    
    def _generate_spectral_bands(self,
                               terrain: np.ndarray,
                               params: SpectralParams) -> np.ndarray:
        """Generate spectral bands based on terrain"""
        height, width = terrain.shape
        bands = np.zeros((self.num_bands, height, width))
        
        # Generate correlated noise for each band
        base_noise = np.random.normal(0, params.spectral_noise, (height, width))
        
        for i, (band_name, correlation) in enumerate(params.band_correlations.items()):
            # Combine terrain and noise with band-specific correlation
            band = (terrain * correlation +
                   base_noise * (1 - correlation)) * params.sensor_gain
            
            # Apply quantization
            if params.quantization_bits:
                steps = 2 ** params.quantization_bits
                band = np.round(band * steps) / steps
            
            bands[i] = band
        
        return bands
    
    def _apply_atmospheric_effects(self,
                                 bands: np.ndarray,
                                 params: AtmosphericParams) -> np.ndarray:
        """Apply atmospheric effects to the bands"""
        num_bands, height, width = bands.shape
        
        # Generate cloud mask
        clouds = self._generate_clouds(
            (height, width),
            coverage=params.cloud_coverage
        )
        
        # Generate haze
        haze = self._generate_haze(
            (height, width),
            intensity=params.haze_intensity
        )
        
        # Apply effects to each band
        for i in range(num_bands):
            # Apply clouds
            bands[i] = bands[i] * (1 - clouds) + clouds
            
            # Apply haze
            bands[i] = bands[i] * (1 - haze) + haze * params.aerosol_density
            
            # Apply shadows
            if params.shadow_intensity > 0:
                shadows = ndimage.gaussian_filter(
                    clouds,
                    sigma=5.0
                ) * params.shadow_intensity
                bands[i] = bands[i] * (1 - shadows)
        
        return np.clip(bands, 0, 1)
    
    def _generate_clouds(self,
                        shape: Tuple[int, int],
                        coverage: float = 0.3,
                        scale: float = 100.0) -> np.ndarray:
        """Generate cloud patterns"""
        height, width = shape
        
        # Generate base noise
        clouds = np.zeros(shape)
        for y in range(height):
            for x in range(width):
                clouds[y, x] = snoise3(
                    x / scale,
                    y / scale,
                    random.random(),
                    octaves=4,
                    persistence=0.5
                )
        
        # Normalize and threshold
        clouds = (clouds - clouds.min()) / (clouds.max() - clouds.min())
        clouds = np.where(clouds > (1 - coverage), clouds, 0)
        
        # Smooth edges
        return ndimage.gaussian_filter(clouds, sigma=2.0)
    
    def _generate_haze(self,
                      shape: Tuple[int, int],
                      intensity: float = 0.2,
                      scale: float = 200.0) -> np.ndarray:
        """Generate atmospheric haze"""
        height, width = shape
        
        # Generate smooth noise
        haze = np.zeros(shape)
        for y in range(height):
            for x in range(width):
                haze[y, x] = snoise2(
                    x / scale,
                    y / scale,
                    octaves=2,
                    persistence=0.5
                )
        
        # Normalize and scale by intensity
        haze = (haze - haze.min()) / (haze.max() - haze.min())
        return haze * intensity
    
    def _save_geotiff(self,
                     bands: np.ndarray,
                     output_path: Path) -> Dict[str, Any]:
        """Save the synthetic scene as a GeoTIFF"""
        num_bands, height, width = bands.shape
        
        # Create transform (assuming upper-left corner at 0,0)
        transform = from_origin(0, 0, self.resolution, self.resolution)
        
        # Prepare metadata
        metadata = {
            "driver": "GTiff",
            "height": height,
            "width": width,
            "count": num_bands,
            "dtype": "float32",
            "crs": "EPSG:4326",
            "transform": transform,
            "compress": "deflate",
            "nodata": None,
            "tiled": True,
            "blockxsize": 256,
            "blockysize": 256
        }
        
        # Save file
        with rasterio.open(output_path, "w", **metadata) as dst:
            dst.write(bands.astype(np.float32))
            
            # Add custom metadata
            dst.update_tags(
                TIFFTAG_DATETIME=datetime.now().isoformat(),
                SYNTHETIC_DATA="True",
                RESOLUTION=str(self.resolution),
                NUM_BANDS=str(num_bands)
            )
        
        return metadata 