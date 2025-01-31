"""
Quick Start Guide for Vortx Earth Memory System
=============================================

This example demonstrates basic initialization and simple operations using the Vortx Earth Memory System.
It covers:
1. System initialization
2. Loading sample data
3. Creating Earth memories
4. Basic queries and analysis
5. Visualization

Author: Vortx Team
License: MIT
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from vortx import EarthMemorySystem
from vortx.utils import setup_environment, DataLoader
from vortx.viz import plot_memory_formation
from vortx.metrics import MemoryMetrics

def setup_system():
    """Initialize the Earth Memory System with basic configuration."""
    try:
        # Initialize environment
        setup_environment(
            api_key=os.getenv("VORTX_API_KEY", "demo-key"),
            log_level="INFO"
        )
        
        # Create system instance with optimal defaults
        system = EarthMemorySystem(
            memory_config={
                "compression_level": "balanced",
                "cache_size": "2GB",
                "precision": "float32"
            },
            compute_config={
                "device": "auto",  # Automatically select CPU/GPU
                "num_threads": -1,  # Use all available threads
                "optimize_memory": True
            }
        )
        
        return system
    except Exception as e:
        print(f"Error initializing system: {e}")
        raise

def load_sample_data():
    """Load sample Earth observation data."""
    loader = DataLoader()
    
    # Load sample satellite imagery
    data = loader.load_sample(
        dataset_type="satellite",
        region="california",
        time_range=["2024-01-01", "2024-01-07"],
        resolution="medium"
    )
    
    return data

def create_memory(system, data):
    """Create Earth memories from the loaded data."""
    try:
        # Configure memory formation
        memory_params = {
            "spatial_resolution": 30,  # 30 meters
            "temporal_resolution": "1D",  # Daily
            "compression_ratio": 0.8,
            "feature_extraction": True
        }
        
        # Create memory with progress tracking
        with system.memory_formation(params=memory_params) as memory:
            for timestamp, image in data.items():
                memory.add_observation(
                    data=image,
                    timestamp=timestamp,
                    metadata={
                        "source": "sample_data",
                        "quality": "high"
                    }
                )
                
        return memory
    except Exception as e:
        print(f"Error in memory formation: {e}")
        raise

def analyze_memory(memory):
    """Perform basic analysis on the formed memory."""
    # Calculate basic statistics
    stats = memory.compute_statistics()
    
    # Detect patterns
    patterns = memory.detect_patterns(
        method="temporal_correlation",
        threshold=0.8
    )
    
    # Extract features
    features = memory.extract_features(
        feature_types=["ndvi", "water", "urban"],
        aggregation="mean"
    )
    
    return {
        "statistics": stats,
        "patterns": patterns,
        "features": features
    }

def visualize_results(memory, analysis_results):
    """Create visualizations of the memory and analysis results."""
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot memory formation process
    plot_memory_formation(memory, ax=axes[0, 0])
    axes[0, 0].set_title("Memory Formation Process")
    
    # Plot feature extraction results
    features = analysis_results["features"]
    for i, (feature_name, values) in enumerate(features.items()):
        axes[0, 1].plot(values, label=feature_name)
    axes[0, 1].set_title("Feature Trends")
    axes[0, 1].legend()
    
    # Plot pattern detection
    patterns = analysis_results["patterns"]
    memory.visualize_patterns(patterns, ax=axes[1, 0])
    axes[1, 0].set_title("Detected Patterns")
    
    # Plot statistics
    stats = analysis_results["statistics"]
    memory.plot_statistics(stats, ax=axes[1, 1])
    axes[1, 1].set_title("Statistical Analysis")
    
    plt.tight_layout()
    return fig

def main():
    """Main execution function."""
    try:
        # Step 1: Setup
        print("Initializing Earth Memory System...")
        system = setup_system()
        
        # Step 2: Load Data
        print("Loading sample data...")
        data = load_sample_data()
        
        # Step 3: Create Memory
        print("Forming Earth memory...")
        memory = create_memory(system, data)
        
        # Step 4: Analysis
        print("Analyzing memory...")
        analysis_results = analyze_memory(memory)
        
        # Step 5: Visualization
        print("Creating visualizations...")
        fig = visualize_results(memory, analysis_results)
        
        # Save results
        output_dir = "examples/output"
        os.makedirs(output_dir, exist_ok=True)
        
        fig.savefig(f"{output_dir}/quickstart_results.png")
        print(f"Results saved to {output_dir}/quickstart_results.png")
        
        # Print performance metrics
        metrics = MemoryMetrics.get_metrics(memory)
        print("\nPerformance Metrics:")
        print(f"Memory Size: {metrics['memory_size']:.2f} MB")
        print(f"Compression Ratio: {metrics['compression_ratio']:.2f}")
        print(f"Formation Time: {metrics['formation_time']:.2f} seconds")
        print(f"Query Latency: {metrics['query_latency']:.2f} ms")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        raise
    finally:
        # Cleanup
        plt.close('all')
        if 'system' in locals():
            system.cleanup()

if __name__ == "__main__":
    main() 