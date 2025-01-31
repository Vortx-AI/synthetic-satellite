#!/usr/bin/env python3
"""
Example demonstrating real-time monitoring with AGI memory integration.
"""

import os
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread, Event

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    StreamingMemory,
    WorkingMemory,
    EpisodicMemory
)
from vortx.processors import (
    StreamProcessor,
    AnomalyDetector,
    PatternMatcher
)
from vortx.sustainability import (
    EnergyMonitor,
    ResourceOptimizer
)

class RealTimeMonitor:
    """Real-time monitoring system with AGI memory integration."""
    
    def __init__(self, system):
        self.system = system
        self.streaming = StreamingMemory(system)
        self.working = WorkingMemory(system)
        self.episodic = EpisodicMemory(system)
        
        self.processor = StreamProcessor()
        self.anomaly_detector = AnomalyDetector()
        self.pattern_matcher = PatternMatcher()
        
        self.data_queue = Queue()
        self.stop_event = Event()
        
        # Configure memory windows
        self.memory_config = {
            "stream_window": "5m",
            "working_window": "1h",
            "episodic_interval": "1d"
        }
    
    def start_data_collection(self):
        """Simulate real-time data collection."""
        def generate_data():
            while not self.stop_event.is_set():
                # Simulate sensor data
                data = {
                    "timestamp": datetime.now(),
                    "temperature": np.random.normal(25, 2),
                    "humidity": np.random.uniform(40, 60),
                    "pressure": np.random.normal(1013, 5),
                    "air_quality": np.random.uniform(0, 100)
                }
                
                self.data_queue.put(data)
                time.sleep(1)  # 1 second interval
        
        self.collector_thread = Thread(target=generate_data)
        self.collector_thread.start()
    
    def process_stream(self):
        """Process incoming data stream."""
        def process_data():
            while not self.stop_event.is_set():
                if not self.data_queue.empty():
                    data = self.data_queue.get()
                    
                    # Process streaming data
                    processed = self.processor.process(data)
                    
                    # Store in streaming memory
                    stream_id = self.streaming.store(
                        processed,
                        window=self.memory_config["stream_window"]
                    )
                    
                    # Check for anomalies
                    anomalies = self.anomaly_detector.check(
                        self.streaming.get_window(stream_id)
                    )
                    
                    if anomalies:
                        self.handle_anomalies(anomalies)
                    
                    # Update working memory
                    self.update_working_memory(processed)
                    
                    # Periodically update episodic memory
                    self.update_episodic_memory()
                
                time.sleep(0.1)  # Prevent CPU overload
        
        self.processor_thread = Thread(target=process_data)
        self.processor_thread.start()
    
    def handle_anomalies(self, anomalies):
        """Handle detected anomalies."""
        for anomaly in anomalies:
            # Create anomaly context
            context = {
                "type": anomaly["type"],
                "severity": anomaly["severity"],
                "timestamp": datetime.now(),
                "affected_metrics": anomaly["metrics"]
            }
            
            # Store anomaly in episodic memory
            self.episodic.store(
                data=anomaly["data"],
                context=context,
                priority="high"
            )
            
            # Log anomaly
            print(f"Anomaly detected: {context}")
    
    def update_working_memory(self, data):
        """Update working memory with recent data."""
        # Get current working memory window
        working_data = self.working.get_window(
            self.memory_config["working_window"]
        )
        
        # Update patterns
        patterns = self.pattern_matcher.update(
            working_data,
            new_data=data
        )
        
        # Store in working memory
        self.working.store(
            data=data,
            patterns=patterns,
            window=self.memory_config["working_window"]
        )
    
    def update_episodic_memory(self):
        """Periodically update episodic memory."""
        current_time = datetime.now()
        last_update = getattr(self, '_last_episodic_update', None)
        
        if (not last_update or 
            current_time - last_update > 
            timedelta(days=1)):
            
            # Get working memory data
            working_data = self.working.get_window(
                self.memory_config["working_window"]
            )
            
            # Create episodic memory
            self.episodic.store(
                data=working_data,
                context={
                    "timestamp": current_time,
                    "patterns": self.pattern_matcher.get_patterns(),
                    "statistics": self.processor.compute_statistics(working_data)
                }
            )
            
            self._last_episodic_update = current_time
    
    def stop(self):
        """Stop monitoring."""
        self.stop_event.set()
        self.collector_thread.join()
        self.processor_thread.join()
        
        # Final memory update
        self.update_episodic_memory()

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "streaming_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Initialize monitoring
    monitor = EnergyMonitor(system)
    optimizer = ResourceOptimizer()
    
    # Configure system for streaming
    optimizer.optimize_for_streaming(
        system,
        config={
            "memory_allocation": "dynamic",
            "stream_processing": "real_time",
            "power_mode": "balanced"
        }
    )
    
    # Create and start monitor
    print("Starting real-time monitoring...")
    rtm = RealTimeMonitor(system)
    rtm.start_data_collection()
    rtm.process_stream()
    
    try:
        # Run for some time
        time.sleep(300)  # 5 minutes
        
        # Get monitoring metrics
        metrics = monitor.get_metrics()
        print("\nMonitoring Metrics:")
        for key, value in metrics.items():
            print(f"{key}: {value}")
    
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
    
    finally:
        # Cleanup
        rtm.stop()
        system.cleanup()

if __name__ == "__main__":
    main() 