#!/usr/bin/env python3
"""
Example demonstrating urban planning with AGI memory systems.
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    UrbanMemory,
    InfrastructureMemory,
    SustainabilityMemory
)
from vortx.processors import (
    UrbanAnalyzer,
    InfrastructurePlanner,
    SustainabilityOptimizer
)
from vortx.optimization import (
    ZoningOptimizer,
    TransportOptimizer,
    ResourceOptimizer
)
from vortx.visualization import (
    UrbanVisualizer,
    InfrastructureMapper
)
from vortx.sustainability import (
    EnergyMonitor,
    CarbonFootprintAnalyzer
)

class UrbanPlanningSystem:
    """Urban planning system with AGI memory integration."""
    
    def __init__(self, system):
        self.system = system
        
        # Initialize memory components
        self.urban = UrbanMemory(system)
        self.infrastructure = InfrastructureMemory(system)
        self.sustainability = SustainabilityMemory(system)
        
        # Initialize processors
        self.urban_analyzer = UrbanAnalyzer()
        self.infra_planner = InfrastructurePlanner()
        self.sustain_optimizer = SustainabilityOptimizer()
        
        # Initialize optimizers
        self.zoning_optimizer = ZoningOptimizer()
        self.transport_optimizer = TransportOptimizer()
        self.resource_optimizer = ResourceOptimizer()
        
        # Initialize visualizers
        self.urban_viz = UrbanVisualizer()
        self.infra_mapper = InfrastructureMapper()
        
        # Initialize sustainability components
        self.energy_monitor = EnergyMonitor(system)
        self.carbon_analyzer = CarbonFootprintAnalyzer()
        
        # Configure system parameters
        self.config = {
            "planning_horizon": "20y",
            "update_interval": "1y",
            "sustainability_target": 0.8,
            "density_threshold": 0.7
        }
    
    def analyze_urban_area(self, area_data: Dict):
        """Analyze urban area characteristics."""
        # Analyze urban patterns
        analysis = self.urban_analyzer.analyze(
            area_data,
            config={
                "density_threshold": self.config["density_threshold"],
                "horizon": self.config["planning_horizon"]
            }
        )
        
        # Store analysis results
        analysis_id = self.urban.store(
            data={
                "raw": area_data,
                "analysis": analysis
            },
            context={
                "timestamp": datetime.now(),
                "horizon": self.config["planning_horizon"]
            }
        )
        
        return analysis_id, analysis
    
    def plan_infrastructure(self, analysis_id: str, analysis: Dict):
        """Plan infrastructure based on urban analysis."""
        # Get current infrastructure state
        current_infra = self.infrastructure.get_current_state()
        
        # Generate infrastructure plan
        infra_plan = self.infra_planner.generate_plan(
            urban_analysis=analysis,
            current_infrastructure=current_infra,
            horizon=self.config["planning_horizon"]
        )
        
        # Optimize transportation network
        transport_plan = self.transport_optimizer.optimize(
            infrastructure_plan=infra_plan,
            urban_analysis=analysis,
            constraints={
                "sustainability_target": self.config["sustainability_target"]
            }
        )
        
        # Store infrastructure plan
        plan_id = self.infrastructure.store_plan(
            analysis_id=analysis_id,
            infrastructure_plan=infra_plan,
            transport_plan=transport_plan,
            context={
                "timestamp": datetime.now(),
                "horizon": self.config["planning_horizon"]
            }
        )
        
        return plan_id, infra_plan, transport_plan
    
    def optimize_sustainability(self, analysis_id: str, plan_id: str):
        """Optimize urban plan for sustainability."""
        # Get urban analysis and infrastructure plan
        analysis = self.urban.get(analysis_id)
        infra_plan = self.infrastructure.get_plan(plan_id)
        
        # Optimize zoning
        zoning_plan = self.zoning_optimizer.optimize(
            urban_analysis=analysis,
            infrastructure_plan=infra_plan,
            sustainability_target=self.config["sustainability_target"]
        )
        
        # Optimize resource usage
        resource_plan = self.resource_optimizer.optimize(
            zoning_plan=zoning_plan,
            infrastructure_plan=infra_plan,
            constraints={
                "sustainability_target": self.config["sustainability_target"]
            }
        )
        
        # Calculate sustainability metrics
        sustainability_analysis = self.sustain_optimizer.analyze(
            zoning_plan=zoning_plan,
            resource_plan=resource_plan,
            infrastructure_plan=infra_plan
        )
        
        # Store sustainability plan
        sustain_id = self.sustainability.store_plan(
            analysis_id=analysis_id,
            plan_id=plan_id,
            zoning_plan=zoning_plan,
            resource_plan=resource_plan,
            sustainability_analysis=sustainability_analysis,
            context={
                "timestamp": datetime.now(),
                "horizon": self.config["planning_horizon"]
            }
        )
        
        return sustain_id, sustainability_analysis
    
    def generate_visualizations(self, analysis_id: str, plan_id: str, sustain_id: str):
        """Generate visualizations of urban plans."""
        # Get all relevant data
        analysis = self.urban.get(analysis_id)
        infra_plan = self.infrastructure.get_plan(plan_id)
        sustain_plan = self.sustainability.get_plan(sustain_id)
        
        # Generate urban visualization
        urban_viz = self.urban_viz.generate(
            urban_analysis=analysis,
            infrastructure_plan=infra_plan,
            sustainability_plan=sustain_plan
        )
        
        # Generate infrastructure map
        infra_map = self.infra_mapper.generate(
            infrastructure_plan=infra_plan,
            sustainability_analysis=sustain_plan["sustainability_analysis"]
        )
        
        return {
            "urban_visualization": urban_viz,
            "infrastructure_map": infra_map
        }

def generate_sample_data():
    """Generate sample urban planning data for testing."""
    # Generate sample urban area data
    area_data = {
        "region": {
            "name": "Sample City",
            "bounds": {
                "north": 34.5,
                "south": 34.0,
                "east": -118.0,
                "west": -118.5
            }
        },
        "population": {
            "current": 500000,
            "growth_rate": 0.02,
            "density": {
                "residential": 5000,  # people per sq km
                "commercial": 2000,
                "industrial": 1000
            }
        },
        "land_use": {
            "residential": 0.4,
            "commercial": 0.3,
            "industrial": 0.2,
            "green_space": 0.1
        },
        "infrastructure": {
            "transport_network": {
                "roads": 1500,  # km
                "public_transit": 100  # km
            },
            "utilities": {
                "water": 0.8,  # coverage ratio
                "power": 0.9,
                "internet": 0.85
            }
        },
        "sustainability": {
            "green_space_ratio": 0.15,
            "renewable_energy_ratio": 0.3,
            "water_recycling_ratio": 0.4
        }
    }
    
    return area_data

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "urban_planning_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Create urban planning system
    planning_system = UrbanPlanningSystem(system)
    
    try:
        print("Starting urban planning analysis...")
        
        # Generate sample data
        area_data = generate_sample_data()
        
        # Analyze urban area
        print("\nAnalyzing urban area...")
        analysis_id, analysis = planning_system.analyze_urban_area(area_data)
        
        # Plan infrastructure
        print("\nGenerating infrastructure plan...")
        plan_id, infra_plan, transport_plan = planning_system.plan_infrastructure(
            analysis_id,
            analysis
        )
        
        # Optimize for sustainability
        print("\nOptimizing for sustainability...")
        sustain_id, sustainability_analysis = planning_system.optimize_sustainability(
            analysis_id,
            plan_id
        )
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        visualizations = planning_system.generate_visualizations(
            analysis_id,
            plan_id,
            sustain_id
        )
        
        # Print summary
        print("\nUrban Planning Summary:")
        print("----------------------")
        print(f"Population Growth: {analysis['population_projection']:.2f}%")
        print(f"Density Optimization: {analysis['density_score']:.2f}")
        print(f"Infrastructure Coverage: {infra_plan['coverage_ratio']:.2f}")
        print(f"Sustainability Score: {sustainability_analysis['overall_score']:.2f}")
        
        # Print sustainability metrics
        metrics = planning_system.energy_monitor.get_metrics()
        print("\nSustainability Metrics:")
        for key, value in metrics.items():
            print(f"{key}: {value}")
        
        # Calculate carbon footprint
        carbon_footprint = planning_system.carbon_analyzer.analyze(
            sustainability_analysis
        )
        print("\nCarbon Footprint Analysis:")
        for key, value in carbon_footprint.items():
            print(f"{key}: {value}")
    
    except Exception as e:
        print(f"\nError during planning: {str(e)}")
    
    finally:
        # Cleanup
        system.cleanup()
        print("\nPlanning completed")

if __name__ == "__main__":
    main() 