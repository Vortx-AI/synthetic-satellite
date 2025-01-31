def get_content():
    """Return content for basic usage notebook"""
    return [
        {
            "title": "Environment Setup",
            "description": """
            Set up the development environment for the Vortx AGI Memory System. This section covers:
            - Required dependencies
            - System configuration
            - GPU setup (if available)
            - Basic environment checks
            """,
            "code": """
            import os
            import numpy as np
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns
            import torch
            import networkx as nx
            from datetime import datetime, timedelta

            # Vortx imports
            from vortx import AGIMemorySystem
            from vortx.utils import setup_environment, ConfigManager
            from vortx.viz import CognitiveVisualizer, MemoryMapper
            from vortx.memory import (
                EpisodicMemory,
                SemanticMemory,
                ProceduralMemory,
                WorkingMemory
            )
            from vortx.cognitive import (
                ContextProcessor,
                TemporalReasoner,
                CausalEngine
            )
            from vortx.metrics import MemoryMetrics

            # Configure visualization settings
            plt.style.use('seaborn')
            sns.set_palette("husl")
            %matplotlib inline
            %config InlineBackend.figure_format = 'retina'

            # Check system configuration
            print("System Configuration:")
            print(f"PyTorch Version: {torch.__version__}")
            print(f"CUDA Available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
            """
        },
        {
            "title": "Memory System Architecture",
            "description": """
            Initialize and configure the Vortx AGI Memory System. This section demonstrates:
            - System initialization
            - Memory architecture configuration
            - Component setup
            - System visualization
            """,
            "code": """
            # Initialize system with advanced configuration
            config = ConfigManager()

            # Configure memory architecture
            memory_config = {
                "type": "hierarchical_cognitive",
                "layers": [
                    "sensory_buffer",
                    "working_memory",
                    "long_term_storage"
                ],
                "attention_mechanism": "adaptive",
                "compression_strategy": "semantic_lossless",
                "embedding_dimension": 1024,
                "batch_size": 256,
                "learning_rate": 0.001,
                "optimization": {
                    "memory_efficiency": True,
                    "processing_speed": True,
                    "power_consumption": "efficient"
                },
                "neural_architecture": {
                    "encoder_layers": 6,
                    "decoder_layers": 6,
                    "attention_heads": 8,
                    "feedforward_dim": 2048
                },
                "storage": {
                    "persistence": True,
                    "replication": 2,
                    "consistency": "eventual",
                    "compression_ratio": 0.4
                }
            }

            config.set_memory_architecture(memory_config)

            # Initialize the AGI Memory System
            system = AGIMemorySystem(
                config=config,
                features=[
                    "temporal_reasoning",
                    "spatial_analysis",
                    "causal_inference",
                    "pattern_recognition",
                    "semantic_embedding",
                    "multi_modal_fusion"
                ]
            )

            # Initialize memory components
            episodic = EpisodicMemory(
                system,
                temporal_resolution="1s",
                max_sequence_length=1000,
                compression_level="adaptive"
            )

            semantic = SemanticMemory(
                system,
                embedding_dim=512,
                knowledge_graph=True,
                reasoning_engine="neural"
            )

            procedural = ProceduralMemory(
                system,
                action_space_dim=100,
                learning_rate=0.01,
                exploration_rate=0.1
            )

            working = WorkingMemory(
                system,
                capacity=1000,
                attention_mechanism="multi_head",
                update_rate=0.1
            )

            # Initialize visualization
            viz = CognitiveVisualizer(system)
            mapper = MemoryMapper(system)

            # Display system architecture
            print("Memory System Architecture:")
            system.describe_architecture()

            # Visualize system architecture
            plt.figure(figsize=(15, 10))
            viz.plot_architecture()
            plt.title('Vortx AGI Memory System Architecture')
            plt.show()
            """
        },
        {
            "title": "Cognitive Data Processing",
            "description": """
            Process and analyze data using the AGI Memory System. This section covers:
            - Data ingestion
            - Memory formation
            - Context embedding
            - Pattern analysis
            """,
            "code": """
            # Generate sample Earth observation data
            def generate_earth_observation_data(n_samples=1000):
                # Generate timestamps with varying intervals
                base_timestamp = pd.Timestamp('2024-01-01')
                timestamps = [base_timestamp + pd.Timedelta(minutes=np.random.exponential(30)) 
                            for _ in range(n_samples)]
                timestamps.sort()
                
                # Generate spatial patterns
                def generate_spatial_pattern(t):
                    hour = t.hour
                    # Add daily and seasonal patterns
                    lat_bias = 15 * np.sin(2 * np.pi * t.dayofyear / 365)
                    lon_bias = 30 * np.sin(2 * np.pi * hour / 24)
                    return {
                        'latitude': lat_bias + np.random.normal(0, 20),
                        'longitude': lon_bias + np.random.normal(0, 30)
                    }
                
                # Generate environmental patterns
                def generate_environmental_data(t, lat):
                    hour = t.hour
                    day_factor = np.sin(2 * np.pi * hour / 24)
                    season_factor = np.sin(2 * np.pi * t.dayofyear / 365)
                    lat_factor = np.cos(np.radians(lat))
                    
                    return {
                        'temperature': 15 + 10 * day_factor + 15 * season_factor * lat_factor + np.random.normal(0, 2),
                        'humidity': 60 + 20 * day_factor + np.random.normal(0, 5),
                        'cloud_cover': max(0, min(1, 0.5 + 0.3 * day_factor + np.random.normal(0, 0.1))),
                        'precipitation': max(0, np.random.exponential(2) * (0.5 + 0.5 * day_factor)),
                        'wind_speed': max(0, 5 + 5 * day_factor + np.random.normal(0, 2)),
                        'solar_radiation': max(0, 1000 * day_factor * (1 - 0.7 * cloud_cover) + np.random.normal(0, 50))
                    }
                
                # Generate vegetation indices
                def generate_vegetation_data(t, lat, temp, precip):
                    season_factor = np.sin(2 * np.pi * t.dayofyear / 365)
                    lat_factor = np.cos(np.radians(lat))
                    
                    return {
                        'ndvi': max(0, min(1, 0.5 + 0.3 * season_factor * lat_factor + 0.1 * np.log1p(precip) + np.random.normal(0, 0.05))),
                        'evi': max(0, min(1, 0.4 + 0.4 * season_factor * lat_factor + 0.15 * np.log1p(precip) + np.random.normal(0, 0.05))),
                        'biomass': max(0, 100 + 50 * season_factor * lat_factor + 20 * np.log1p(precip) + np.random.normal(0, 10))
                    }
                
                # Combine all data
                data = []
                for t in timestamps:
                    spatial = generate_spatial_pattern(t)
                    environmental = generate_environmental_data(t, spatial['latitude'])
                    vegetation = generate_vegetation_data(
                        t, 
                        spatial['latitude'],
                        environmental['temperature'],
                        environmental['precipitation']
                    )
                    
                    data.append({
                        'timestamp': t,
                        **spatial,
                        **environmental,
                        **vegetation
                    })
                
                return pd.DataFrame(data)

            # Generate and display sample data
            data = generate_earth_observation_data()
            print("Sample Earth Observation Data:")
            display(data.head())

            # Process data through memory system
            context_processor = ContextProcessor(
                system,
                temporal_window=24,  # hours
                spatial_resolution=0.1,  # degrees
                feature_extraction="deep"
            )

            # Process and store data
            processed_data = context_processor.process_batch(
                data,
                batch_size=64,
                extract_features=True,
                compute_embeddings=True
            )

            memory_id = episodic.store(
                processed_data,
                context={
                    'source': 'earth_observation',
                    'resolution': 'high',
                    'processing_level': 'L2A'
                }
            )

            # Visualize data patterns
            fig = plt.figure(figsize=(20, 12))
            gs = fig.add_gridspec(3, 3)

            # Spatial distribution
            ax1 = fig.add_subplot(gs[0, 0])
            plt.scatter(data['longitude'], data['latitude'], 
                    c=data['temperature'], cmap='viridis', alpha=0.6)
            plt.colorbar(label='Temperature (°C)')
            ax1.set_title('Spatial Distribution')

            # Temperature vs Time
            ax2 = fig.add_subplot(gs[0, 1])
            plt.plot(data['timestamp'], data['temperature'])
            ax2.set_title('Temperature Time Series')
            plt.xticks(rotation=45)

            # NDVI Distribution
            ax3 = fig.add_subplot(gs[0, 2])
            sns.histplot(data['ndvi'], kde=True)
            ax3.set_title('NDVI Distribution')

            # Environmental Correlations
            ax4 = fig.add_subplot(gs[1, :])
            env_vars = ['temperature', 'humidity', 'precipitation', 'wind_speed', 'solar_radiation']
            sns.heatmap(data[env_vars].corr(), annot=True, cmap='coolwarm')
            ax4.set_title('Environmental Variable Correlations')

            # Vegetation Indices Time Series
            ax5 = fig.add_subplot(gs[2, :])
            plt.plot(data['timestamp'], data['ndvi'], label='NDVI')
            plt.plot(data['timestamp'], data['evi'], label='EVI')
            plt.legend()
            ax5.set_title('Vegetation Indices Time Series')
            plt.xticks(rotation=45)

            plt.tight_layout()
            plt.show()
            """
        }
    ] 