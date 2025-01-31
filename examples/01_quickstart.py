#!/usr/bin/env python3
"""
Quickstart example demonstrating basic usage of the Vortx AGI Memory System.
"""

import os
import numpy as np
from datetime import datetime, timedelta

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import EpisodicMemory, SemanticMemory
from vortx.sustainability import EnergyMonitor

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )

    # Create memory system with sustainability features
    system = AGIMemorySystem(
        config={
            "architecture": "hierarchical_cognitive",
            "compression": "adaptive",
            "sustainability": {
                "power_mode": "efficient",
                "memory_optimization": "dynamic"
            }
        }
    )

    # Generate sample data
    timestamps = [datetime.now() + timedelta(hours=i) for i in range(100)]
    data = {
        "timestamp": timestamps,
        "temperature": np.random.normal(25, 5, 100),
        "humidity": np.random.uniform(0, 100, 100),
        "pressure": np.random.normal(1013, 10, 100),
        "location": [(lat, lon) for lat, lon in zip(
            np.random.uniform(30, 45, 100),
            np.random.uniform(-120, -100, 100)
        )]
    }

    # Create memories
    episodic = EpisodicMemory(system)
    semantic = SemanticMemory(system)

    # Store data as memories
    memory_id = episodic.store(data)
    patterns = semantic.extract_patterns(memory_id)

    # Monitor resource usage
    monitor = EnergyMonitor(system)
    metrics = monitor.get_metrics()

    # Print results
    print("\nMemory System Status:")
    print(f"Memory ID: {memory_id}")
    print(f"Discovered Patterns: {len(patterns)}")
    print("\nSustainability Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main() 