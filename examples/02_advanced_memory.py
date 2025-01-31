#!/usr/bin/env python3
"""
Advanced example demonstrating complex memory operations and sustainability features.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    EpisodicMemory,
    SemanticMemory,
    WorkingMemory
)
from vortx.cognitive import (
    PatternSynthesizer,
    ContextProcessor
)
from vortx.sustainability import (
    EnergyMonitor,
    ResourceOptimizer
)

def create_synthetic_memories(size=1000):
    """Generate synthetic memory data with cognitive attributes."""
    base_time = datetime.now()
    
    # Generate temporal sequence
    times = [base_time + timedelta(minutes=i) for i in range(size)]
    
    # Generate cognitive features
    data = {
        "timestamp": times,
        "cognitive_load": np.random.uniform(0, 1, size),
        "attention_level": np.random.uniform(0.5, 1, size),
        "emotional_valence": np.random.normal(0, 1, size),
        "context_embedding": [
            np.random.normal(0, 1, 128) for _ in range(size)
        ],
        "memory_strength": np.random.exponential(0.5, size)
    }
    
    return pd.DataFrame(data)

def optimize_memory_usage(system, resource_optimizer):
    """Optimize memory usage for sustainability."""
    config = {
        "memory_limits": {
            "working_memory": "1GB",
            "episodic_buffer": "4GB",
            "semantic_store": "8GB"
        },
        "optimization": {
            "compression_level": "adaptive",
            "cleanup_threshold": 0.75,
            "cache_strategy": "lru"
        },
        "power_settings": {
            "mode": "efficiency",
            "max_power": "50W",
            "idle_optimization": True
        }
    }
    
    return resource_optimizer.apply_optimization(system, config)

def process_memories(system, data):
    """Process and store memories with cognitive processing."""
    # Initialize components
    episodic = EpisodicMemory(system)
    semantic = SemanticMemory(system)
    working = WorkingMemory(system)
    
    # Initialize processors
    pattern_synth = PatternSynthesizer()
    context_proc = ContextProcessor()
    
    # Process in batches for efficiency
    batch_size = 100
    memory_ids = []
    
    for i in range(0, len(data), batch_size):
        batch = data.iloc[i:i + batch_size]
        
        # Process context and patterns
        contexts = context_proc.process_batch(batch)
        patterns = pattern_synth.analyze_batch(batch)
        
        # Store in working memory first
        working_id = working.store(batch, contexts)
        
        # Transfer to long-term memory
        episodic_id = episodic.store(
            working.get(working_id),
            patterns=patterns,
            contexts=contexts
        )
        
        # Extract semantic information
        semantic.process_episodic_memory(episodic_id)
        
        memory_ids.append(episodic_id)
        
        # Cleanup working memory
        working.clear(working_id)
    
    return memory_ids

def analyze_sustainability(monitor, memory_ids):
    """Analyze sustainability metrics for processed memories."""
    metrics = monitor.get_detailed_metrics()
    
    # Calculate per-memory metrics
    memory_metrics = {
        memory_id: monitor.analyze_memory_impact(memory_id)
        for memory_id in memory_ids
    }
    
    # Get optimization recommendations
    recommendations = monitor.get_optimization_recommendations()
    
    return {
        "system_metrics": metrics,
        "memory_metrics": memory_metrics,
        "recommendations": recommendations
    }

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create system with sustainability focus
    system = AGIMemorySystem(
        config={
            "architecture": "hierarchical_cognitive",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Initialize sustainability components
    monitor = EnergyMonitor(system)
    optimizer = ResourceOptimizer()
    
    # Generate and process memories
    print("Generating synthetic memories...")
    data = create_synthetic_memories(size=1000)
    
    print("Optimizing system configuration...")
    optimize_memory_usage(system, optimizer)
    
    print("Processing memories...")
    memory_ids = process_memories(system, data)
    
    print("Analyzing sustainability metrics...")
    analysis = analyze_sustainability(monitor, memory_ids)
    
    # Print results
    print("\nSustainability Analysis:")
    print("------------------------")
    print("System Metrics:")
    for metric, value in analysis["system_metrics"].items():
        print(f"{metric}: {value}")
    
    print("\nOptimization Recommendations:")
    for rec in analysis["recommendations"]:
        print(f"- {rec}")
    
    # Cleanup
    system.cleanup()

if __name__ == "__main__":
    main() 