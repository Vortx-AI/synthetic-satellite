#!/usr/bin/env python3
"""
Example demonstrating satellite data processing with AGI memory integration.
"""

import os
import numpy as np
import rasterio
import pandas as pd
from datetime import datetime
from sentinelsat import SentinelAPI

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    EpisodicMemory,
    SpatialMemory,
    TemporalMemory
)
from vortx.processors import (
    SatelliteProcessor,
    ImageEnhancer,
    BandCombiner
)
from vortx.sustainability import EnergyMonitor

def setup_satellite_api():
    """Initialize Sentinel API with credentials."""
    user = os.getenv("SENTINEL_USER")
    password = os.getenv("SENTINEL_PASSWORD")
    return SentinelAPI(user, password, "https://scihub.copernicus.eu/dhus")

def process_satellite_data(system, api, area_of_interest, time_range):
    """Process satellite data and store as memories."""
    processor = SatelliteProcessor()
    enhancer = ImageEnhancer()
    band_combiner = BandCombiner()
    
    # Query satellite data
    products = api.query(
        area_of_interest,
        date=time_range,
        platformname="Sentinel-2",
        cloudcoverpercentage=(0, 20)
    )
    
    # Initialize memories
    episodic = EpisodicMemory(system)
    spatial = SpatialMemory(system)
    temporal = TemporalMemory(system)
    
    memories = []
    for product_id, product in products.items():
        # Download and process data
        api.download(product_id)
        
        with rasterio.open(product["title"] + ".SAFE") as src:
            # Process bands
            bands = processor.read_bands(src)
            enhanced = enhancer.enhance_bands(bands)
            combined = band_combiner.combine(enhanced)
            
            # Create memory attributes
            attributes = {
                "timestamp": product["beginposition"],
                "coordinates": product["footprint"],
                "cloud_cover": product["cloudcoverpercentage"],
                "satellite": "Sentinel-2",
                "processing_level": product["processinglevel"],
                "cognitive_context": processor.extract_context(combined)
            }
            
            # Store as episodic memory
            memory_id = episodic.store(
                data=combined,
                attributes=attributes,
                encoding_config={
                    "compression": "efficient",
                    "precision": "mixed"
                }
            )
            
            # Create spatial and temporal associations
            spatial.index_memory(memory_id, attributes["coordinates"])
            temporal.index_memory(memory_id, attributes["timestamp"])
            
            memories.append(memory_id)
    
    return memories

def analyze_memories(system, memory_ids):
    """Analyze stored satellite memories."""
    episodic = EpisodicMemory(system)
    
    analysis = {
        "coverage": [],
        "quality": [],
        "patterns": []
    }
    
    for memory_id in memory_ids:
        memory = episodic.get(memory_id)
        
        # Analyze coverage
        coverage = memory.get_attribute("coordinates")
        analysis["coverage"].append(coverage)
        
        # Assess quality
        quality = memory.get_attribute("cloud_cover")
        analysis["quality"].append(quality)
        
        # Extract patterns
        patterns = memory.extract_patterns(
            pattern_types=["spatial", "temporal", "spectral"]
        )
        analysis["patterns"].extend(patterns)
    
    return analysis

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "hierarchical_cognitive",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Initialize monitoring
    monitor = EnergyMonitor(system)
    
    # Define area and time range
    area_of_interest = "POLYGON((...))"  # Define your area
    time_range = ("20240101", "20240131")
    
    # Process satellite data
    api = setup_satellite_api()
    print("Processing satellite data...")
    memory_ids = process_satellite_data(
        system, api, area_of_interest, time_range
    )
    
    # Analyze memories
    print("\nAnalyzing memories...")
    analysis = analyze_memories(system, memory_ids)
    
    # Print results
    print("\nAnalysis Results:")
    print(f"Total memories created: {len(memory_ids)}")
    print(f"Unique patterns discovered: {len(analysis['patterns'])}")
    print(f"Average cloud cover: {np.mean(analysis['quality']):.2f}%")
    
    # Get sustainability metrics
    metrics = monitor.get_metrics()
    print("\nSustainability Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Cleanup
    system.cleanup()

if __name__ == "__main__":
    main() 