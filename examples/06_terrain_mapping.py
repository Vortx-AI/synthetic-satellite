#!/usr/bin/env python3
"""
Example demonstrating terrain mapping with AGI memory integration.
"""

import os
import numpy as np
import rasterio
import geopandas as gpd
from shapely.geometry import box
from rasterio.warp import calculate_default_transform

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    SpatialMemory,
    TerrainMemory,
    EpisodicMemory
)
from vortx.processors import (
    TerrainProcessor,
    ElevationAnalyzer,
    LandformClassifier
)
from vortx.sustainability import (
    EnergyMonitor,
    ResourceOptimizer
)

def load_terrain_data(dem_path, region_bounds=None):
    """Load and preprocess terrain data."""
    with rasterio.open(dem_path) as src:
        if region_bounds:
            # Clip to region of interest
            window = src.window(*region_bounds)
            elevation = src.read(1, window=window)
            transform = src.window_transform(window)
        else:
            elevation = src.read(1)
            transform = src.transform
        
        return elevation, transform, src.crs

def create_terrain_memories(system, elevation, transform, crs):
    """Create cognitive memories from terrain data."""
    processor = TerrainProcessor()
    analyzer = ElevationAnalyzer()
    classifier = LandformClassifier()
    
    # Initialize memory components
    spatial = SpatialMemory(system)
    terrain = TerrainMemory(system)
    episodic = EpisodicMemory(system)
    
    # Process terrain in tiles for efficiency
    tile_size = 1024
    height, width = elevation.shape
    memories = []
    
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            # Extract tile
            tile = elevation[y:y+tile_size, x:x+tile_size]
            if tile.size == 0:
                continue
            
            # Calculate tile bounds
            tile_bounds = box(
                *rasterio.transform.xy(
                    transform, y, x,
                    y+tile.shape[0], x+tile.shape[1]
                )
            )
            
            # Process terrain features
            features = processor.extract_features(tile, transform)
            landforms = classifier.classify(features)
            patterns = analyzer.detect_patterns(features)
            
            # Create cognitive context
            context = {
                "elevation_stats": analyzer.compute_statistics(tile),
                "landform_distribution": classifier.get_distribution(landforms),
                "terrain_complexity": analyzer.compute_complexity(features),
                "spatial_patterns": patterns
            }
            
            # Store as terrain memory
            memory_id = terrain.store(
                data=tile,
                features=features,
                landforms=landforms,
                context=context,
                encoding_config={
                    "compression": "lossless",
                    "precision": "elevation_optimized"
                }
            )
            
            # Create spatial indexing
            spatial.index_terrain(
                memory_id,
                bounds=tile_bounds,
                crs=crs
            )
            
            # Store in episodic memory
            episodic.link_terrain_memory(
                memory_id,
                context=context,
                timestamp=datetime.now()
            )
            
            memories.append(memory_id)
    
    return memories

def analyze_terrain_patterns(system, memory_ids):
    """Analyze terrain patterns from stored memories."""
    terrain = TerrainMemory(system)
    
    analysis = {
        "landforms": {},
        "elevation_profiles": [],
        "terrain_features": [],
        "spatial_patterns": []
    }
    
    for memory_id in memory_ids:
        memory = terrain.get(memory_id)
        
        # Analyze landforms
        landforms = memory.get_landforms()
        for landform, count in landforms.items():
            analysis["landforms"][landform] = \
                analysis["landforms"].get(landform, 0) + count
        
        # Collect elevation profiles
        analysis["elevation_profiles"].append(
            memory.get_elevation_profile()
        )
        
        # Extract terrain features
        analysis["terrain_features"].extend(
            memory.get_terrain_features()
        )
        
        # Analyze spatial patterns
        analysis["spatial_patterns"].extend(
            memory.get_spatial_patterns()
        )
    
    return analysis

def optimize_terrain_processing(system, optimizer):
    """Optimize system for terrain data processing."""
    config = {
        "memory_config": {
            "terrain_compression": "adaptive",
            "spatial_indexing": "efficient",
            "feature_cache_size": "4GB"
        },
        "processing_config": {
            "tile_size": "adaptive",
            "precision": "elevation_optimized",
            "parallel_processing": True
        },
        "sustainability": {
            "power_mode": "efficient",
            "storage_optimization": True,
            "compute_scheduling": "green"
        }
    }
    
    return optimizer.optimize_for_terrain(system, config)

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "terrain_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Initialize monitoring
    monitor = EnergyMonitor(system)
    optimizer = ResourceOptimizer()
    
    # Optimize system
    print("Optimizing system for terrain processing...")
    optimize_terrain_processing(system, optimizer)
    
    # Load terrain data
    print("Loading terrain data...")
    elevation, transform, crs = load_terrain_data(
        "path/to/dem.tif",
        region_bounds=None  # Optional region bounds
    )
    
    # Process terrain
    print("Creating terrain memories...")
    memory_ids = create_terrain_memories(
        system, elevation, transform, crs
    )
    
    # Analyze patterns
    print("\nAnalyzing terrain patterns...")
    analysis = analyze_terrain_patterns(system, memory_ids)
    
    # Print results
    print("\nAnalysis Results:")
    print("Landform Distribution:")
    for landform, count in analysis["landforms"].items():
        print(f"  {landform}: {count}")
    print(f"Elevation profiles analyzed: {len(analysis['elevation_profiles'])}")
    print(f"Terrain features detected: {len(analysis['terrain_features'])}")
    print(f"Spatial patterns identified: {len(analysis['spatial_patterns'])}")
    
    # Get sustainability metrics
    metrics = monitor.get_metrics()
    print("\nSustainability Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Cleanup
    system.cleanup()

if __name__ == "__main__":
    main() 