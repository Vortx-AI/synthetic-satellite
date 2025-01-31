#!/usr/bin/env python3
"""
Example demonstrating data pipeline integration with AGI memory systems.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Generator
import asyncio
from pathlib import Path

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    StreamingMemory,
    ProcessingMemory,
    AnalyticalMemory
)
from vortx.processors import (
    DataProcessor,
    StreamAnalyzer,
    BatchProcessor
)
from vortx.optimization import (
    PipelineOptimizer,
    MemoryOptimizer,
    ResourceOptimizer
)
from vortx.analytics import (
    DataAnalyzer,
    PatternDetector,
    AnomalyDetector
)
from vortx.sustainability import (
    EnergyMonitor,
    ResourceMonitor
)

class DataPipelineSystem:
    """Data pipeline system with AGI memory integration."""
    
    def __init__(self, system):
        self.system = system
        
        # Initialize memory components
        self.streaming = StreamingMemory(system)
        self.processing = ProcessingMemory(system)
        self.analytical = AnalyticalMemory(system)
        
        # Initialize processors
        self.data_processor = DataProcessor()
        self.stream_analyzer = StreamAnalyzer()
        self.batch_processor = BatchProcessor()
        
        # Initialize optimizers
        self.pipeline_optimizer = PipelineOptimizer()
        self.memory_optimizer = MemoryOptimizer()
        self.resource_optimizer = ResourceOptimizer()
        
        # Initialize analytics
        self.data_analyzer = DataAnalyzer()
        self.pattern_detector = PatternDetector()
        self.anomaly_detector = AnomalyDetector()
        
        # Initialize monitoring
        self.energy_monitor = EnergyMonitor(system)
        self.resource_monitor = ResourceMonitor(system)
        
        # Configure system parameters
        self.config = {
            "batch_size": 1000,
            "processing_window": "1h",
            "memory_limit": "10GB",
            "optimization_interval": 300  # seconds
        }
    
    async def process_stream(self, data_stream: Generator):
        """Process incoming data stream."""
        batch = []
        results = []
        
        async for data in data_stream:
            # Add to batch
            batch.append(data)
            
            # Process batch if full
            if len(batch) >= self.config["batch_size"]:
                batch_result = await self.process_batch(batch)
                results.append(batch_result)
                batch = []
        
        # Process remaining data
        if batch:
            batch_result = await self.process_batch(batch)
            results.append(batch_result)
        
        return results
    
    async def process_batch(self, batch: List[Dict]):
        """Process a batch of data."""
        # Preprocess data
        processed_data = self.data_processor.process(
            batch,
            config={
                "window": self.config["processing_window"]
            }
        )
        
        # Store in processing memory
        batch_id = self.processing.store(
            data=processed_data,
            context={
                "timestamp": datetime.now(),
                "size": len(batch)
            }
        )
        
        # Analyze batch
        analysis = self.stream_analyzer.analyze(
            processed_data,
            window=self.config["processing_window"]
        )
        
        # Detect patterns and anomalies
        patterns = self.pattern_detector.detect(processed_data)
        anomalies = self.anomaly_detector.detect(processed_data)
        
        # Store analytical results
        analysis_id = self.analytical.store(
            data={
                "analysis": analysis,
                "patterns": patterns,
                "anomalies": anomalies
            },
            context={
                "batch_id": batch_id,
                "timestamp": datetime.now()
            }
        )
        
        return {
            "batch_id": batch_id,
            "analysis_id": analysis_id,
            "size": len(batch),
            "patterns": len(patterns),
            "anomalies": len(anomalies)
        }
    
    async def optimize_pipeline(self):
        """Optimize pipeline performance and resource usage."""
        while True:
            # Get current metrics
            memory_usage = self.memory_optimizer.get_usage()
            resource_usage = self.resource_optimizer.get_usage()
            
            # Check if optimization is needed
            if (memory_usage > self.config["memory_limit"] or
                resource_usage["cpu"] > 0.8):
                
                # Optimize pipeline
                optimization = self.pipeline_optimizer.optimize(
                    memory_usage=memory_usage,
                    resource_usage=resource_usage,
                    constraints={
                        "memory_limit": self.config["memory_limit"],
                        "cpu_limit": 0.8
                    }
                )
                
                # Apply optimization
                self.apply_optimization(optimization)
            
            # Wait for next optimization interval
            await asyncio.sleep(self.config["optimization_interval"])
    
    def apply_optimization(self, optimization: Dict):
        """Apply pipeline optimization settings."""
        if "batch_size" in optimization:
            self.config["batch_size"] = optimization["batch_size"]
        
        if "processing_window" in optimization:
            self.config["processing_window"] = optimization["processing_window"]
        
        if "memory_settings" in optimization:
            self.memory_optimizer.apply_settings(
                optimization["memory_settings"]
            )
        
        if "resource_settings" in optimization:
            self.resource_optimizer.apply_settings(
                optimization["resource_settings"]
            )
    
    def get_pipeline_stats(self):
        """Get pipeline statistics and metrics."""
        return {
            "memory_usage": self.memory_optimizer.get_usage(),
            "resource_usage": self.resource_optimizer.get_usage(),
            "processing_stats": self.processing.get_stats(),
            "analytical_stats": self.analytical.get_stats(),
            "sustainability_metrics": self.energy_monitor.get_metrics()
        }

async def generate_sample_data(duration: int = 3600):
    """Generate sample data stream for testing."""
    start_time = datetime.now()
    
    while (datetime.now() - start_time).total_seconds() < duration:
        # Generate sample data point
        data = {
            "timestamp": datetime.now().isoformat(),
            "sensor_id": np.random.randint(1, 100),
            "temperature": np.random.normal(25, 5),
            "humidity": np.random.uniform(30, 70),
            "pressure": np.random.normal(1013, 10),
            "wind_speed": np.random.exponential(5),
            "battery_level": np.random.uniform(0, 100)
        }
        
        yield data
        await asyncio.sleep(0.1)  # Simulate 10 Hz data stream

async def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "pipeline_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Create data pipeline system
    pipeline = DataPipelineSystem(system)
    
    try:
        print("Starting data pipeline...")
        
        # Start optimization task
        optimization_task = asyncio.create_task(
            pipeline.optimize_pipeline()
        )
        
        # Process data stream
        print("\nProcessing data stream...")
        results = await pipeline.process_stream(
            generate_sample_data(duration=3600)  # 1 hour of data
        )
        
        # Print summary
        total_records = sum(r["size"] for r in results)
        total_patterns = sum(r["patterns"] for r in results)
        total_anomalies = sum(r["anomalies"] for r in results)
        
        print("\nPipeline Summary:")
        print("----------------")
        print(f"Total Records Processed: {total_records}")
        print(f"Total Patterns Detected: {total_patterns}")
        print(f"Total Anomalies Detected: {total_anomalies}")
        
        # Get pipeline stats
        stats = pipeline.get_pipeline_stats()
        
        print("\nPipeline Statistics:")
        print("Memory Usage:")
        for key, value in stats["memory_usage"].items():
            print(f"  {key}: {value}")
        
        print("\nResource Usage:")
        for key, value in stats["resource_usage"].items():
            print(f"  {key}: {value}")
        
        print("\nSustainability Metrics:")
        for key, value in stats["sustainability_metrics"].items():
            print(f"  {key}: {value}")
    
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
    
    except Exception as e:
        print(f"\nError in pipeline: {str(e)}")
    
    finally:
        # Cancel optimization task
        optimization_task.cancel()
        try:
            await optimization_task
        except asyncio.CancelledError:
            pass
        
        # Cleanup
        system.cleanup()
        print("\nPipeline completed")

if __name__ == "__main__":
    asyncio.run(main()) 