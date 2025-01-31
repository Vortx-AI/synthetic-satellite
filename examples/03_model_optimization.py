#!/usr/bin/env python3
"""
Example demonstrating model optimization and efficiency tuning for AGI memory systems.
"""

import os
import numpy as np
import torch
import torch.nn as nn
from datetime import datetime

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.optimization import (
    ModelOptimizer,
    QuantizationEngine,
    PruningEngine
)
from vortx.sustainability import (
    EnergyMonitor,
    PerformanceProfiler
)
from vortx.models import (
    MemoryEncoder,
    ContextualAttention,
    TemporalProcessor
)

class MemoryNetwork(nn.Module):
    """Example memory network architecture."""
    def __init__(self, input_dim=256, hidden_dim=512):
        super().__init__()
        self.encoder = MemoryEncoder(input_dim, hidden_dim)
        self.attention = ContextualAttention(hidden_dim)
        self.temporal = TemporalProcessor(hidden_dim)
        
        self.layers = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim // 4)
        )

def optimize_model(model, data, energy_monitor):
    """Optimize model for efficiency and performance."""
    optimizer = ModelOptimizer()
    quantizer = QuantizationEngine()
    pruner = PruningEngine()
    
    print("Starting model optimization...")
    
    # Profile baseline performance
    baseline_metrics = energy_monitor.profile_model(model, data)
    print("\nBaseline Metrics:")
    for metric, value in baseline_metrics.items():
        print(f"{metric}: {value}")
    
    # Quantization optimization
    print("\nOptimizing with quantization...")
    quantization_config = {
        "precision": "int8",
        "scheme": "dynamic",
        "calibration_method": "histogram"
    }
    quantized_model = quantizer.optimize(
        model,
        config=quantization_config,
        calibration_data=data
    )
    
    # Model pruning
    print("\nApplying model pruning...")
    pruning_config = {
        "method": "magnitude",
        "sparsity_target": 0.5,
        "schedule": "gradual"
    }
    pruned_model = pruner.optimize(
        quantized_model,
        config=pruning_config
    )
    
    # Architecture optimization
    print("\nOptimizing architecture...")
    arch_config = {
        "search_space": "efficiency_focused",
        "constraints": {
            "max_params": 1e6,
            "max_memory": "2GB",
            "target_latency": "10ms"
        }
    }
    optimized_model = optimizer.optimize_architecture(
        pruned_model,
        config=arch_config
    )
    
    return optimized_model

def evaluate_efficiency(model, data, energy_monitor):
    """Evaluate model efficiency and sustainability metrics."""
    profiler = PerformanceProfiler()
    
    metrics = {
        "inference_latency": profiler.measure_latency(model, data),
        "memory_usage": profiler.measure_memory(model),
        "energy_consumption": energy_monitor.measure_consumption(model),
        "carbon_footprint": energy_monitor.estimate_carbon_impact(model)
    }
    
    recommendations = profiler.generate_recommendations(metrics)
    
    return metrics, recommendations

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create system
    system = AGIMemorySystem()
    energy_monitor = EnergyMonitor(system)
    
    # Create sample model and data
    model = MemoryNetwork()
    data = torch.randn(100, 256)  # Sample input data
    
    # Optimize model
    optimized_model = optimize_model(model, data, energy_monitor)
    
    # Evaluate efficiency
    metrics, recommendations = evaluate_efficiency(
        optimized_model,
        data,
        energy_monitor
    )
    
    # Print results
    print("\nOptimization Results:")
    print("--------------------")
    print("\nEfficiency Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")
    
    print("\nOptimization Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # Save optimized model
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)
    torch.save(optimized_model.state_dict(), 
              f"{output_dir}/optimized_memory_model.pth")
    
    print(f"\nOptimized model saved to {output_dir}/optimized_memory_model.pth")

if __name__ == "__main__":
    main() 