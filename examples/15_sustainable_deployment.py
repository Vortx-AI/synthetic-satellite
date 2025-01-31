"""
Sustainable Deployment with Vortx
==============================

This example demonstrates sustainable deployment practices using the Vortx Earth Memory System.
It showcases:
1. Energy-efficient deployment strategies
2. Resource optimization
3. Carbon footprint monitoring
4. Adaptive scaling
5. Green computing practices

Author: Vortx Team
License: MIT
"""

import os
import time
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

from vortx import EarthMemorySystem
from vortx.utils import setup_environment
from vortx.deployment import (
    SustainableDeployer,
    ResourceMonitor,
    CarbonTracker,
    GreenScheduler
)
from vortx.optimization import EnergyOptimizer
from vortx.viz import SustainabilityDashboard

class SustainableDeploymentExample:
    def __init__(self):
        """Initialize the sustainable deployment example."""
        self.system = self._setup_system()
        self.deployer = SustainableDeployer()
        self.monitor = ResourceMonitor()
        self.tracker = CarbonTracker()
        self.scheduler = GreenScheduler()
        self.optimizer = EnergyOptimizer()
        self.dashboard = SustainabilityDashboard()
        
    def _setup_system(self):
        """Configure the Earth Memory System for sustainable deployment."""
        setup_environment(
            api_key=os.getenv("VORTX_API_KEY", "demo-key"),
            log_level="INFO"
        )
        
        return EarthMemorySystem(
            deployment_config={
                "energy_efficiency": "high",
                "resource_optimization": True,
                "carbon_aware": True
            },
            sustainability_config={
                "power_management": "dynamic",
                "cooling_optimization": True,
                "workload_scheduling": "green"
            }
        )
    
    def configure_deployment(self):
        """Configure sustainable deployment parameters."""
        config = {
            "compute": {
                "cpu_power_limit": 0.8,  # 80% of max power
                "gpu_power_limit": 0.7,  # 70% of max power
                "memory_optimization": True,
                "thermal_management": True
            },
            "storage": {
                "tiered_storage": True,
                "compression_enabled": True,
                "deduplication": True
            },
            "network": {
                "bandwidth_optimization": True,
                "latency_requirements": "flexible",
                "caching_strategy": "adaptive"
            },
            "scheduling": {
                "carbon_intensity_aware": True,
                "workload_batching": True,
                "peak_avoidance": True
            }
        }
        
        return self.deployer.configure(config)
    
    def monitor_resources(self):
        """Monitor resource usage and efficiency."""
        metrics = {
            "compute": self.monitor.track_compute(),
            "memory": self.monitor.track_memory(),
            "storage": self.monitor.track_storage(),
            "network": self.monitor.track_network()
        }
        
        return metrics
    
    def track_carbon_footprint(self):
        """Track carbon emissions and energy usage."""
        return self.tracker.calculate_footprint(
            metrics=self.monitor_resources(),
            include_scope3=True
        )
    
    def optimize_energy_usage(self, deployment_config):
        """Optimize energy consumption across the system."""
        optimization_targets = {
            "power_usage": {
                "target": "minimize",
                "constraint": "performance"
            },
            "cooling_efficiency": {
                "target": "maximize",
                "constraint": "temperature"
            },
            "resource_utilization": {
                "target": "optimize",
                "constraint": "availability"
            }
        }
        
        return self.optimizer.optimize(
            config=deployment_config,
            targets=optimization_targets
        )
    
    def schedule_workloads(self, workloads):
        """Schedule workloads for optimal energy efficiency."""
        scheduling_params = {
            "carbon_intensity": self.tracker.get_grid_intensity(),
            "power_availability": self.monitor.get_power_status(),
            "thermal_conditions": self.monitor.get_thermal_status()
        }
        
        return self.scheduler.schedule(
            workloads=workloads,
            params=scheduling_params
        )
    
    def monitor_deployment(self, duration_seconds=3600):
        """Monitor deployment sustainability metrics."""
        metrics_history = []
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration_seconds:
                # Collect current metrics
                current_metrics = {
                    "timestamp": datetime.now(),
                    "resources": self.monitor_resources(),
                    "carbon": self.track_carbon_footprint(),
                    "energy": self.optimizer.get_energy_metrics()
                }
                
                metrics_history.append(current_metrics)
                
                # Update dashboard
                self.dashboard.update(current_metrics)
                
                # Adaptive optimization
                if self.should_optimize(current_metrics):
                    self.optimize_deployment()
                
                time.sleep(60)  # Monitor every minute
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            
        return metrics_history
    
    def should_optimize(self, metrics):
        """Determine if deployment optimization is needed."""
        thresholds = {
            "energy_efficiency": 0.8,
            "resource_utilization": 0.9,
            "carbon_intensity": 100  # gCO2/kWh
        }
        
        return any([
            metrics["energy"]["efficiency"] < thresholds["energy_efficiency"],
            metrics["resources"]["utilization"] > thresholds["resource_utilization"],
            metrics["carbon"]["intensity"] > thresholds["carbon_intensity"]
        ])
    
    def optimize_deployment(self):
        """Perform deployment optimization."""
        current_config = self.deployer.get_current_config()
        optimized_config = self.optimize_energy_usage(current_config)
        self.deployer.apply_config(optimized_config)
    
    def generate_sustainability_report(self, metrics_history):
        """Generate comprehensive sustainability report."""
        report = {
            "energy_efficiency": {
                "average_pue": np.mean([m["energy"]["pue"] for m in metrics_history]),
                "power_savings": self.calculate_power_savings(metrics_history),
                "optimization_events": self.count_optimization_events(metrics_history)
            },
            "carbon_footprint": {
                "total_emissions": sum([m["carbon"]["emissions"] for m in metrics_history]),
                "emission_intensity": np.mean([m["carbon"]["intensity"] for m in metrics_history]),
                "reduction_percentage": self.calculate_emission_reduction(metrics_history)
            },
            "resource_utilization": {
                "compute_efficiency": np.mean([m["resources"]["compute"]["efficiency"] for m in metrics_history]),
                "memory_efficiency": np.mean([m["resources"]["memory"]["efficiency"] for m in metrics_history]),
                "storage_efficiency": np.mean([m["resources"]["storage"]["efficiency"] for m in metrics_history])
            }
        }
        
        return report
    
    def run_sustainable_deployment(self):
        """Execute complete sustainable deployment workflow."""
        try:
            print("Starting sustainable deployment test...")
            
            # Step 1: Configure Deployment
            print("Configuring deployment parameters...")
            deployment_config = self.configure_deployment()
            
            # Step 2: Initial Optimization
            print("Performing initial optimization...")
            optimized_config = self.optimize_energy_usage(deployment_config)
            
            # Step 3: Apply Configuration
            print("Applying optimized configuration...")
            self.deployer.apply_config(optimized_config)
            
            # Step 4: Monitor Deployment
            print("Monitoring deployment (1 hour)...")
            metrics_history = self.monitor_deployment(duration_seconds=3600)
            
            # Step 5: Generate Report
            print("Generating sustainability report...")
            report = self.generate_sustainability_report(metrics_history)
            
            # Save results
            output_dir = "examples/output/sustainable_deployment"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save metrics history
            pd.DataFrame(metrics_history).to_csv(
                f"{output_dir}/metrics_history.csv"
            )
            
            # Save report
            pd.DataFrame(report).to_csv(
                f"{output_dir}/sustainability_report.csv"
            )
            
            # Save visualizations
            self.dashboard.save_snapshot(
                f"{output_dir}/final_dashboard.png"
            )
            
            # Print summary
            print("\nDeployment Summary:")
            print(f"Average PUE: {report['energy_efficiency']['average_pue']:.2f}")
            print(f"Power Savings: {report['energy_efficiency']['power_savings']:.1f}%")
            print(f"Carbon Reduction: {report['carbon_footprint']['reduction_percentage']:.1f}%")
            print(f"Resource Efficiency: {report['resource_utilization']['compute_efficiency']:.1f}%")
            
            return report
            
        except Exception as e:
            print(f"Error in sustainable deployment: {e}")
            raise
        finally:
            self.system.cleanup()
    
    def calculate_power_savings(self, metrics_history):
        """Calculate power savings percentage."""
        baseline = metrics_history[0]["energy"]["power_usage"]
        final = metrics_history[-1]["energy"]["power_usage"]
        return ((baseline - final) / baseline) * 100
    
    def calculate_emission_reduction(self, metrics_history):
        """Calculate emission reduction percentage."""
        baseline = metrics_history[0]["carbon"]["emissions"]
        final = metrics_history[-1]["carbon"]["emissions"]
        return ((baseline - final) / baseline) * 100
    
    def count_optimization_events(self, metrics_history):
        """Count number of optimization events."""
        return sum(1 for i in range(1, len(metrics_history))
                  if metrics_history[i]["energy"]["optimization_triggered"])

def main():
    """Main execution function."""
    # Create sustainable deployment manager
    deployment = SustainableDeploymentExample()
    
    # Run deployment test
    results = deployment.run_sustainable_deployment()
    
    # Print detailed results
    print("\nDetailed Deployment Results:")
    print("==========================")
    for category, metrics in results.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for key, value in metrics.items():
            print(f"  {key.replace('_', ' ').title()}: {value:.2f}")

if __name__ == "__main__":
    main() 