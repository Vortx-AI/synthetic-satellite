#!/usr/bin/env python3
"""
Example demonstrating climate data analysis with AGI memory integration.
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    EpisodicMemory,
    SemanticMemory,
    TemporalMemory
)
from vortx.processors import (
    ClimateProcessor,
    PatternDetector,
    AnomalyDetector
)
from vortx.sustainability import (
    EnergyMonitor,
    ResourceOptimizer
)

def load_climate_data(data_path):
    """Load and preprocess climate data."""
    # Load data using xarray
    ds = xr.open_dataset(data_path)
    
    # Basic preprocessing
    ds = ds.sel(time=slice("2000", "2024"))  # Select time range
    ds = ds.resample(time="1M").mean()  # Monthly averages
    
    return ds

def create_climate_memories(system, data):
    """Create memories from climate data with cognitive processing."""
    processor = ClimateProcessor()
    pattern_detector = PatternDetector()
    anomaly_detector = AnomalyDetector()
    
    # Initialize memory components
    episodic = EpisodicMemory(system)
    semantic = SemanticMemory(system)
    temporal = TemporalMemory(system)
    
    memories = []
    
    # Process data in temporal chunks
    for year in data.time.dt.year.unique():
        year_data = data.sel(time=str(year))
        
        # Process climate patterns
        patterns = pattern_detector.detect(year_data)
        anomalies = anomaly_detector.detect(year_data)
        
        # Create cognitive context
        context = processor.create_context(
            data=year_data,
            patterns=patterns,
            anomalies=anomalies
        )
        
        # Store as episodic memory
        memory_id = episodic.store(
            data=year_data,
            context=context,
            encoding_config={
                "compression": "efficient",
                "precision": "climate_optimized"
            }
        )
        
        # Create semantic associations
        semantic.process_climate_patterns(
            memory_id,
            patterns,
            anomalies
        )
        
        # Index in temporal memory
        temporal.index_memory(
            memory_id,
            year_data.time.values
        )
        
        memories.append(memory_id)
    
    return memories

def analyze_climate_trends(system, memory_ids):
    """Analyze climate trends using stored memories."""
    episodic = EpisodicMemory(system)
    semantic = SemanticMemory(system)
    
    trends = {
        "temperature": [],
        "precipitation": [],
        "extreme_events": [],
        "patterns": []
    }
    
    for memory_id in memory_ids:
        # Retrieve memory
        memory = episodic.get(memory_id)
        
        # Extract climate indicators
        trends["temperature"].extend(
            memory.get_temperature_trends()
        )
        trends["precipitation"].extend(
            memory.get_precipitation_patterns()
        )
        trends["extreme_events"].extend(
            memory.get_extreme_events()
        )
        
        # Get semantic patterns
        patterns = semantic.get_patterns(memory_id)
        trends["patterns"].extend(patterns)
    
    return trends

def optimize_processing(system, optimizer):
    """Optimize system for climate data processing."""
    config = {
        "memory_config": {
            "climate_data_compression": True,
            "temporal_indexing": "efficient",
            "pattern_cache_size": "2GB"
        },
        "processing_config": {
            "batch_size": "adaptive",
            "precision": "mixed",
            "parallel_processing": True
        },
        "sustainability": {
            "power_mode": "efficient",
            "storage_optimization": True,
            "compute_scheduling": "green"
        }
    }
    
    return optimizer.optimize_for_climate(system, config)

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "climate_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Initialize components
    monitor = EnergyMonitor(system)
    optimizer = ResourceOptimizer()
    
    # Optimize system
    print("Optimizing system for climate analysis...")
    optimize_processing(system, optimizer)
    
    # Load and process data
    print("Loading climate data...")
    data = load_climate_data("path/to/climate_data.nc")
    
    print("Creating climate memories...")
    memory_ids = create_climate_memories(system, data)
    
    # Analyze trends
    print("\nAnalyzing climate trends...")
    trends = analyze_climate_trends(system, memory_ids)
    
    # Print results
    print("\nAnalysis Results:")
    print(f"Temperature trends analyzed: {len(trends['temperature'])}")
    print(f"Precipitation patterns found: {len(trends['precipitation'])}")
    print(f"Extreme events detected: {len(trends['extreme_events'])}")
    print(f"Climate patterns identified: {len(trends['patterns'])}")
    
    # Get sustainability metrics
    metrics = monitor.get_metrics()
    print("\nSustainability Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Cleanup
    system.cleanup()

if __name__ == "__main__":
    main() 