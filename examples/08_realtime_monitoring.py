"""
Real-time Earth Monitoring with Vortx
===================================

This example demonstrates real-time Earth observation monitoring capabilities using the Vortx Earth Memory System.
It showcases:
1. Real-time data streaming
2. Live visualization
3. Anomaly detection
4. Alert generation
5. Performance optimization

Author: Vortx Team
License: MIT
"""

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from threading import Thread, Event
from queue import Queue

from vortx import EarthMemorySystem
from vortx.utils import setup_environment
from vortx.streaming import DataStreamer
from vortx.monitoring import (
    RealTimeMonitor,
    AlertManager,
    PerformanceTracker
)
from vortx.viz import DynamicVisualizer

class RealTimeMonitoringExample:
    def __init__(self):
        """Initialize the real-time monitoring system."""
        self.system = self._setup_system()
        self.streamer = DataStreamer()
        self.monitor = RealTimeMonitor()
        self.alert_manager = AlertManager()
        self.visualizer = DynamicVisualizer()
        self.performance_tracker = PerformanceTracker()
        
        # Data management
        self.data_queue = Queue(maxsize=1000)
        self.alert_queue = Queue(maxsize=100)
        self.stop_event = Event()
        
        # Visualization
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 12))
        plt.ion()  # Enable interactive mode
    
    def _setup_system(self):
        """Configure the Earth Memory System for real-time monitoring."""
        setup_environment(
            api_key=os.getenv("VORTX_API_KEY", "demo-key"),
            log_level="INFO"
        )
        
        return EarthMemorySystem(
            memory_config={
                "compression_level": "low",  # Optimize for speed
                "cache_size": "8GB",
                "precision": "float32"
            },
            compute_config={
                "device": "auto",
                "num_threads": -1,
                "optimize_memory": True,
                "stream_processing": True
            }
        )
    
    def start_data_stream(self):
        """Initialize and start the data streaming process."""
        def stream_worker():
            try:
                while not self.stop_event.is_set():
                    # Get real-time Earth observation data
                    data = self.streamer.get_next_observation(
                        variables=[
                            "temperature",
                            "precipitation",
                            "cloud_cover",
                            "vegetation"
                        ],
                        region="global",
                        resolution="medium"
                    )
                    
                    # Add timestamp
                    data['timestamp'] = datetime.now()
                    
                    # Put data in queue
                    if not self.data_queue.full():
                        self.data_queue.put(data)
                    
                    # Control streaming rate
                    time.sleep(1)  # 1 second interval
                    
            except Exception as e:
                print(f"Error in stream worker: {e}")
                self.stop_event.set()
        
        # Start streaming thread
        stream_thread = Thread(target=stream_worker)
        stream_thread.daemon = True
        stream_thread.start()
    
    def process_data(self):
        """Process incoming data stream."""
        def process_worker():
            try:
                while not self.stop_event.is_set():
                    # Get data from queue
                    if not self.data_queue.empty():
                        data = self.data_queue.get()
                        
                        # Process data
                        processed_data = self.monitor.process_observation(
                            data,
                            analysis_types=[
                                "anomaly_detection",
                                "trend_analysis",
                                "pattern_recognition"
                            ]
                        )
                        
                        # Check for alerts
                        alerts = self.alert_manager.check_alerts(
                            processed_data,
                            alert_types=[
                                "anomaly",
                                "threshold",
                                "trend"
                            ]
                        )
                        
                        # Add alerts to queue
                        for alert in alerts:
                            if not self.alert_queue.full():
                                self.alert_queue.put(alert)
                        
                        # Track performance
                        self.performance_tracker.update(
                            data_size=len(data),
                            processing_time=time.time() - data['timestamp'].timestamp()
                        )
                    
                    time.sleep(0.1)  # Small delay to prevent CPU overload
                    
            except Exception as e:
                print(f"Error in process worker: {e}")
                self.stop_event.set()
        
        # Start processing thread
        process_thread = Thread(target=process_worker)
        process_thread.daemon = True
        process_thread.start()
    
    def update_visualization(self):
        """Update the real-time visualization."""
        def viz_worker():
            try:
                while not self.stop_event.is_set():
                    # Clear previous plots
                    for ax in self.axes.flat:
                        ax.clear()
                    
                    # Get latest monitoring data
                    monitoring_data = self.monitor.get_latest_data()
                    
                    # 1. Real-time observations
                    self.visualizer.plot_realtime_data(
                        data=monitoring_data,
                        ax=self.axes[0, 0],
                        variables=['temperature', 'precipitation']
                    )
                    self.axes[0, 0].set_title("Real-time Observations")
                    
                    # 2. Anomaly detection
                    self.visualizer.plot_anomalies(
                        data=monitoring_data,
                        ax=self.axes[0, 1],
                        threshold=0.95
                    )
                    self.axes[0, 1].set_title("Anomaly Detection")
                    
                    # 3. Alert timeline
                    alerts = list(self.alert_queue.queue)
                    self.visualizer.plot_alert_timeline(
                        alerts=alerts,
                        ax=self.axes[1, 0]
                    )
                    self.axes[1, 0].set_title("Recent Alerts")
                    
                    # 4. Performance metrics
                    performance_metrics = self.performance_tracker.get_metrics()
                    self.visualizer.plot_performance(
                        metrics=performance_metrics,
                        ax=self.axes[1, 1]
                    )
                    self.axes[1, 1].set_title("System Performance")
                    
                    # Update display
                    plt.tight_layout()
                    plt.draw()
                    plt.pause(0.1)
                    
                    time.sleep(1)  # Update every second
                    
            except Exception as e:
                print(f"Error in visualization worker: {e}")
                self.stop_event.set()
        
        # Start visualization thread
        viz_thread = Thread(target=viz_worker)
        viz_thread.daemon = True
        viz_thread.start()
    
    def run_monitoring(self, duration_seconds=60):
        """Run the real-time monitoring system."""
        try:
            print("Starting real-time Earth monitoring...")
            
            # Start all components
            self.start_data_stream()
            self.process_data()
            self.update_visualization()
            
            # Run for specified duration
            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                if self.stop_event.is_set():
                    break
                time.sleep(1)
            
            # Print summary
            performance_metrics = self.performance_tracker.get_summary()
            print("\nMonitoring Summary:")
            print(f"Total Observations: {performance_metrics['total_observations']}")
            print(f"Average Processing Time: {performance_metrics['avg_processing_time']:.2f}ms")
            print(f"Alert Count: {performance_metrics['alert_count']}")
            print(f"System Uptime: {performance_metrics['uptime']:.1f}s")
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
        except Exception as e:
            print(f"Error in monitoring: {e}")
        finally:
            # Cleanup
            self.stop_event.set()
            plt.ioff()
            plt.close('all')
            self.system.cleanup()

def main():
    """Main execution function."""
    monitor = RealTimeMonitoringExample()
    monitor.run_monitoring(duration_seconds=300)  # Run for 5 minutes

if __name__ == "__main__":
    main() 