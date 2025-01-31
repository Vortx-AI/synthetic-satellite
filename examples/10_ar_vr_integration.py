#!/usr/bin/env python3
"""
Example demonstrating AR/VR integration with AGI memory systems.
"""

import os
import numpy as np
import json
from datetime import datetime
import asyncio
import websockets

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    SpatialMemory,
    PerceptualMemory,
    InteractionMemory
)
from vortx.processors import (
    SpatialProcessor,
    SceneAnalyzer,
    InteractionHandler
)
from vortx.visualization import (
    ARRenderer,
    VRRenderer,
    MemoryVisualizer
)
from vortx.sustainability import (
    EnergyMonitor,
    ResourceOptimizer
)

class ARVRMemorySystem:
    """AR/VR system with AGI memory integration."""
    
    def __init__(self, system, mode="ar"):
        self.system = system
        self.mode = mode.lower()
        
        # Initialize memory components
        self.spatial = SpatialMemory(system)
        self.perceptual = PerceptualMemory(system)
        self.interaction = InteractionMemory(system)
        
        # Initialize processors
        self.spatial_processor = SpatialProcessor()
        self.scene_analyzer = SceneAnalyzer()
        self.interaction_handler = InteractionHandler()
        
        # Initialize renderers
        self.renderer = ARRenderer() if mode == "ar" else VRRenderer()
        self.visualizer = MemoryVisualizer()
        
        # Configure system parameters
        self.config = {
            "update_rate": 60,  # Hz
            "memory_retention": "1h",
            "spatial_resolution": 0.01,  # meters
            "interaction_threshold": 0.5
        }
    
    async def process_scene(self, scene_data):
        """Process incoming scene data."""
        # Process spatial information
        spatial_info = self.spatial_processor.process(
            scene_data["spatial"],
            resolution=self.config["spatial_resolution"]
        )
        
        # Analyze scene contents
        scene_analysis = self.scene_analyzer.analyze(
            scene_data["visual"],
            spatial_context=spatial_info
        )
        
        # Store in memory
        await self.store_scene_memory(
            spatial_info,
            scene_analysis
        )
        
        return spatial_info, scene_analysis
    
    async def store_scene_memory(self, spatial_info, scene_analysis):
        """Store scene information in memory."""
        # Store spatial information
        self.spatial.store(
            data=spatial_info,
            context={
                "timestamp": datetime.now(),
                "mode": self.mode,
                "resolution": self.config["spatial_resolution"]
            }
        )
        
        # Store perceptual information
        self.perceptual.store(
            data=scene_analysis,
            context={
                "timestamp": datetime.now(),
                "spatial_ref": spatial_info["id"]
            }
        )
    
    async def handle_interaction(self, interaction_data):
        """Process and store user interactions."""
        # Process interaction
        processed = self.interaction_handler.process(
            interaction_data,
            threshold=self.config["interaction_threshold"]
        )
        
        if processed["significance"] > self.config["interaction_threshold"]:
            # Store significant interactions
            self.interaction.store(
                data=processed,
                context={
                    "timestamp": datetime.now(),
                    "mode": self.mode
                }
            )
        
        return processed
    
    async def render_frame(self, spatial_info, scene_analysis):
        """Render AR/VR frame with memory integration."""
        # Get relevant memories
        recent_spatial = self.spatial.get_window(
            window=self.config["memory_retention"]
        )
        recent_perceptual = self.perceptual.get_window(
            window=self.config["memory_retention"]
        )
        
        # Generate memory visualization
        memory_vis = self.visualizer.generate(
            spatial=recent_spatial,
            perceptual=recent_perceptual,
            mode=self.mode
        )
        
        # Render frame
        frame = await self.renderer.render(
            spatial_info=spatial_info,
            scene_analysis=scene_analysis,
            memory_visualization=memory_vis,
            config={
                "mode": self.mode,
                "resolution": self.config["spatial_resolution"]
            }
        )
        
        return frame

async def simulate_ar_vr_data(duration=10):
    """Generate simulated AR/VR data for testing."""
    for _ in range(duration * 60):  # 60 fps
        # Generate sample data
        scene_data = {
            "spatial": {
                "position": np.random.rand(3),
                "orientation": np.random.rand(4),
                "points": np.random.rand(100, 3)
            },
            "visual": {
                "objects": [
                    {
                        "type": "cube",
                        "position": np.random.rand(3),
                        "color": np.random.rand(3)
                    }
                    for _ in range(5)
                ]
            }
        }
        
        # Generate interaction data
        interaction_data = {
            "type": "gesture",
            "position": np.random.rand(3),
            "confidence": np.random.rand()
        }
        
        yield scene_data, interaction_data
        await asyncio.sleep(1/60)  # Simulate 60 fps

async def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "ar_vr_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "balanced"
            }
        }
    )
    
    # Initialize monitoring
    monitor = EnergyMonitor(system)
    optimizer = ResourceOptimizer()
    
    # Optimize system for AR/VR
    optimizer.optimize_for_realtime(
        system,
        config={
            "target_fps": 60,
            "memory_policy": "sliding_window",
            "power_mode": "performance"
        }
    )
    
    # Create AR/VR system (default to AR mode)
    ar_vr = ARVRMemorySystem(system, mode="ar")
    
    print("Starting AR/VR simulation...")
    frame_count = 0
    
    try:
        async for scene_data, interaction_data in simulate_ar_vr_data(duration=10):
            # Process scene
            spatial_info, scene_analysis = await ar_vr.process_scene(scene_data)
            
            # Handle interaction
            interaction_result = await ar_vr.handle_interaction(interaction_data)
            
            # Render frame
            frame = await ar_vr.render_frame(spatial_info, scene_analysis)
            
            frame_count += 1
            if frame_count % 60 == 0:  # Print stats every second
                print(f"Processed {frame_count} frames")
                
                # Get sustainability metrics
                metrics = monitor.get_metrics()
                print("\nSustainability Metrics:")
                for key, value in metrics.items():
                    print(f"{key}: {value}")
    
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    
    finally:
        # Cleanup
        system.cleanup()
        print(f"\nSimulation completed. Processed {frame_count} frames")

if __name__ == "__main__":
    asyncio.run(main()) 