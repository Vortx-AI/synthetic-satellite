#!/usr/bin/env python3
"""
Example demonstrating disaster response coordination with AGI memory systems.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Tuple

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    EmergencyMemory,
    ResourceMemory,
    CoordinationMemory
)
from vortx.processors import (
    RiskAnalyzer,
    ResourceAllocator,
    ResponseCoordinator
)
from vortx.optimization import (
    RouteOptimizer,
    ResourceOptimizer
)
from vortx.visualization import (
    EmergencyVisualizer,
    ResourceMapper
)
from vortx.sustainability import EnergyMonitor

class DisasterResponseSystem:
    """Disaster response system with AGI memory integration."""
    
    def __init__(self, system):
        self.system = system
        
        # Initialize memory components
        self.emergency = EmergencyMemory(system)
        self.resources = ResourceMemory(system)
        self.coordination = CoordinationMemory(system)
        
        # Initialize processors
        self.risk_analyzer = RiskAnalyzer()
        self.resource_allocator = ResourceAllocator()
        self.coordinator = ResponseCoordinator()
        
        # Initialize optimizers
        self.route_optimizer = RouteOptimizer()
        self.resource_optimizer = ResourceOptimizer()
        
        # Initialize visualizers
        self.emergency_viz = EmergencyVisualizer()
        self.resource_mapper = ResourceMapper()
        
        # Configure system parameters
        self.config = {
            "update_interval": 30,  # seconds
            "risk_threshold": 0.7,
            "resource_buffer": 0.2,
            "coordination_radius": 5000  # meters
        }
    
    async def process_emergency(self, emergency_data: Dict):
        """Process incoming emergency data."""
        # Analyze risk levels
        risk_analysis = self.risk_analyzer.analyze(
            emergency_data,
            threshold=self.config["risk_threshold"]
        )
        
        # Store emergency information
        emergency_id = self.emergency.store(
            data={
                "raw": emergency_data,
                "analysis": risk_analysis
            },
            context={
                "timestamp": datetime.now(),
                "priority": "high" if risk_analysis["risk_level"] > 0.8 else "medium"
            }
        )
        
        return emergency_id, risk_analysis
    
    async def allocate_resources(self, emergency_id: str, risk_analysis: Dict):
        """Allocate resources based on emergency needs."""
        # Get available resources
        available_resources = self.resources.get_available(
            radius=self.config["coordination_radius"],
            location=risk_analysis["location"]
        )
        
        # Optimize resource allocation
        allocation = self.resource_allocator.allocate(
            emergency=risk_analysis,
            resources=available_resources,
            buffer=self.config["resource_buffer"]
        )
        
        # Optimize routes
        routes = self.route_optimizer.optimize(
            resources=allocation["assigned_resources"],
            target=risk_analysis["location"],
            constraints=allocation["constraints"]
        )
        
        # Store allocation plan
        allocation_id = self.resources.store_allocation(
            emergency_id=emergency_id,
            allocation=allocation,
            routes=routes,
            context={
                "timestamp": datetime.now(),
                "priority": risk_analysis["priority"]
            }
        )
        
        return allocation_id, allocation, routes
    
    async def coordinate_response(self, emergency_id: str, allocation_id: str):
        """Coordinate response activities."""
        # Get emergency and allocation details
        emergency = self.emergency.get(emergency_id)
        allocation = self.resources.get_allocation(allocation_id)
        
        # Generate coordination plan
        plan = self.coordinator.generate_plan(
            emergency=emergency,
            allocation=allocation,
            config={
                "update_interval": self.config["update_interval"],
                "coordination_radius": self.config["coordination_radius"]
            }
        )
        
        # Store coordination plan
        plan_id = self.coordination.store_plan(
            emergency_id=emergency_id,
            allocation_id=allocation_id,
            plan=plan,
            context={
                "timestamp": datetime.now(),
                "status": "active"
            }
        )
        
        return plan_id, plan
    
    async def monitor_response(self, plan_id: str):
        """Monitor and update response progress."""
        while True:
            # Get current plan status
            plan = self.coordination.get_plan(plan_id)
            if plan["status"] == "completed":
                break
            
            # Update progress
            updates = self.coordinator.update_progress(plan)
            
            # Store updates
            self.coordination.update_plan(
                plan_id=plan_id,
                updates=updates,
                context={
                    "timestamp": datetime.now()
                }
            )
            
            # Generate visualization
            viz_data = self.emergency_viz.generate(
                plan=plan,
                updates=updates
            )
            
            # Generate resource map
            resource_map = self.resource_mapper.generate(
                plan=plan,
                updates=updates
            )
            
            yield {
                "plan": plan,
                "updates": updates,
                "visualization": viz_data,
                "resource_map": resource_map
            }
            
            await asyncio.sleep(self.config["update_interval"])

async def simulate_emergency(duration: int = 300):
    """Generate simulated emergency data for testing."""
    start_time = datetime.now()
    
    while (datetime.now() - start_time).total_seconds() < duration:
        # Generate emergency data
        emergency_data = {
            "type": np.random.choice(["fire", "flood", "earthquake"]),
            "location": {
                "lat": np.random.uniform(35.0, 36.0),
                "lon": np.random.uniform(-119.0, -118.0)
            },
            "severity": np.random.uniform(0.5, 1.0),
            "affected_area": np.random.uniform(100, 1000),  # square meters
            "population_density": np.random.uniform(50, 500)  # people per sq km
        }
        
        yield emergency_data
        await asyncio.sleep(30)  # Update every 30 seconds

async def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "emergency_response_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "balanced"
            }
        }
    )
    
    # Initialize monitoring
    monitor = EnergyMonitor(system)
    
    # Create disaster response system
    response_system = DisasterResponseSystem(system)
    
    print("Starting disaster response simulation...")
    emergency_count = 0
    active_responses = {}
    
    try:
        async for emergency_data in simulate_emergency(duration=300):
            emergency_count += 1
            print(f"\nProcessing emergency #{emergency_count}")
            print(f"Type: {emergency_data['type']}")
            print(f"Severity: {emergency_data['severity']:.2f}")
            
            # Process emergency
            emergency_id, risk_analysis = await response_system.process_emergency(
                emergency_data
            )
            
            # Allocate resources
            allocation_id, allocation, routes = await response_system.allocate_resources(
                emergency_id,
                risk_analysis
            )
            
            # Coordinate response
            plan_id, plan = await response_system.coordinate_response(
                emergency_id,
                allocation_id
            )
            
            # Start monitoring
            active_responses[emergency_id] = asyncio.create_task(
                monitor_response_wrapper(
                    response_system,
                    plan_id
                )
            )
            
            # Print sustainability metrics
            metrics = monitor.get_metrics()
            print("\nSustainability Metrics:")
            for key, value in metrics.items():
                print(f"{key}: {value}")
    
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    
    finally:
        # Cancel active monitoring tasks
        for task in active_responses.values():
            task.cancel()
        
        # Cleanup
        system.cleanup()
        print(f"\nSimulation completed. Processed {emergency_count} emergencies")

async def monitor_response_wrapper(response_system, plan_id):
    """Wrapper function for monitoring response progress."""
    async for update in response_system.monitor_response(plan_id):
        # Process updates as needed
        pass

if __name__ == "__main__":
    asyncio.run(main()) 