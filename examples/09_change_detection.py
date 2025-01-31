#!/usr/bin/env python3
"""
Example demonstrating change detection with AGI memory integration.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    TemporalMemory,
    DifferentialMemory,
    EpisodicMemory
)
from vortx.processors import (
    ChangeDetector,
    TrendAnalyzer,
    StateEstimator
)
from vortx.sustainability import (
    EnergyMonitor,
    ResourceOptimizer
)

class ChangeDetectionSystem:
    """Change detection system with AGI memory integration."""
    
    def __init__(self, system):
        self.system = system
        self.temporal = TemporalMemory(system)
        self.differential = DifferentialMemory(system)
        self.episodic = EpisodicMemory(system)
        
        self.detector = ChangeDetector()
        self.analyzer = TrendAnalyzer()
        self.estimator = StateEstimator()
        
        # Configure detection parameters
        self.config = {
            "detection_window": "7d",
            "min_change_threshold": 0.1,
            "confidence_level": 0.95,
            "memory_depth": "30d"
        }
    
    def process_historical_data(self, data):
        """Process historical data to establish baseline."""
        # Initialize baseline state
        baseline = self.estimator.compute_baseline(
            data,
            window=self.config["detection_window"]
        )
        
        # Store baseline in memory
        self.temporal.store_baseline(
            baseline,
            context={
                "timestamp": datetime.now(),
                "parameters": self.config
            }
        )
        
        return baseline
    
    def detect_changes(self, current_data, baseline=None):
        """Detect changes in current data compared to baseline."""
        if baseline is None:
            baseline = self.temporal.get_latest_baseline()
        
        # Detect changes
        changes = self.detector.detect(
            current_data,
            baseline,
            threshold=self.config["min_change_threshold"],
            confidence=self.config["confidence_level"]
        )
        
        # Analyze trends in changes
        trends = self.analyzer.analyze_changes(
            changes,
            history=self.temporal.get_window(
                self.config["memory_depth"]
            )
        )
        
        # Store in differential memory
        memory_id = self.differential.store(
            changes=changes,
            trends=trends,
            context={
                "timestamp": datetime.now(),
                "baseline_id": baseline["id"],
                "confidence": self.config["confidence_level"]
            }
        )
        
        return memory_id, changes, trends
    
    def analyze_significance(self, changes, trends):
        """Analyze the significance of detected changes."""
        significance = {
            "changes": {},
            "trends": {},
            "patterns": []
        }
        
        # Analyze change significance
        for metric, change in changes.items():
            significance["changes"][metric] = \
                self.analyzer.compute_significance(change)
        
        # Analyze trend significance
        for metric, trend in trends.items():
            significance["trends"][metric] = \
                self.analyzer.compute_trend_significance(trend)
        
        # Detect patterns
        patterns = self.analyzer.detect_patterns(
            changes, trends,
            history=self.temporal.get_window(
                self.config["memory_depth"]
            )
        )
        significance["patterns"] = patterns
        
        return significance
    
    def store_significant_changes(self, changes, significance):
        """Store significant changes in episodic memory."""
        # Filter significant changes
        significant_changes = {
            metric: change
            for metric, change in changes.items()
            if significance["changes"][metric] > 0.8  # High significance
        }
        
        if significant_changes:
            # Store in episodic memory
            self.episodic.store(
                data=significant_changes,
                context={
                    "timestamp": datetime.now(),
                    "significance": significance,
                    "detection_params": self.config
                },
                priority="high"
            )
    
    def get_change_history(self):
        """Get history of significant changes."""
        return self.episodic.get_window(
            window=self.config["memory_depth"],
            filter_criteria={
                "priority": "high"
            }
        )

def generate_sample_data(days=30, frequency="1h"):
    """Generate sample time series data with known changes."""
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=days),
        end=datetime.now(),
        freq=frequency
    )
    
    n_samples = len(dates)
    base_temp = 25 + np.sin(np.linspace(0, 4*np.pi, n_samples))
    
    # Add trend and anomalies
    data = pd.DataFrame({
        "timestamp": dates,
        "temperature": base_temp + np.random.normal(0, 0.5, n_samples),
        "humidity": 60 + np.random.normal(0, 5, n_samples),
        "pressure": 1013 + np.random.normal(0, 2, n_samples)
    })
    
    # Introduce artificial changes
    change_point = n_samples // 2
    data.loc[change_point:, "temperature"] += 5  # Temperature increase
    data.loc[change_point:, "humidity"] *= 1.2   # Humidity increase
    
    return data

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "change_detection_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Initialize monitoring
    monitor = EnergyMonitor(system)
    optimizer = ResourceOptimizer()
    
    # Optimize system for change detection
    optimizer.optimize_for_detection(
        system,
        config={
            "memory_allocation": "dynamic",
            "processing_mode": "batch",
            "power_mode": "balanced"
        }
    )
    
    # Create change detection system
    detector = ChangeDetectionSystem(system)
    
    # Generate and process data
    print("Generating sample data...")
    data = generate_sample_data(days=30)
    
    print("Processing historical data...")
    baseline = detector.process_historical_data(
        data[:-7]  # Use all but last week as historical
    )
    
    print("\nDetecting changes...")
    memory_id, changes, trends = detector.detect_changes(
        data[-7:],  # Last week as current data
        baseline
    )
    
    # Analyze significance
    significance = detector.analyze_significance(changes, trends)
    
    # Store significant changes
    detector.store_significant_changes(changes, significance)
    
    # Print results
    print("\nChange Detection Results:")
    print("-------------------------")
    print("Detected Changes:")
    for metric, change in changes.items():
        sig = significance["changes"][metric]
        print(f"{metric}: {change:.2f} (significance: {sig:.2f})")
    
    print("\nIdentified Trends:")
    for metric, trend in trends.items():
        sig = significance["trends"][metric]
        print(f"{metric}: {trend} (significance: {sig:.2f})")
    
    print("\nDetected Patterns:")
    for pattern in significance["patterns"]:
        print(f"- {pattern}")
    
    # Get sustainability metrics
    metrics = monitor.get_metrics()
    print("\nSustainability Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Cleanup
    system.cleanup()

if __name__ == "__main__":
    main() 