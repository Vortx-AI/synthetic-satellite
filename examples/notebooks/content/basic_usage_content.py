"""Content module for basic usage notebook."""

import torch

def get_content():
    """Return content for basic usage notebook."""
    return [
        {
            'title': 'Introduction to Satellite Synthesis System',
            'description': 'Learn the fundamentals of the Satellite Synthesis System and its core components.',
            'code': '''
# Initialize the Satellite Synthesis System
system = SynthesisSystem(
    config={
        'memory_type': 'hierarchical',
        'compression': 'adaptive',
        'sustainability': {
            'energy_efficient': True,
            'resource_optimized': True
        }
    }
)

# Create processing pipelines
data_pipeline = DataProcessor('satellite')
spatial_pipeline = SpatialMemory('high_resolution')
temporal_pipeline = TemporalMemory('pattern_analysis')

# Display system configuration
print("System Configuration:")
print(system.get_config())
'''
        },
        {
            'title': 'Loading Satellite Data',
            'description': 'Learn how to load and preprocess different types of satellite data.',
            'examples': [
                {
                    'title': 'Loading Observation Data',
                    'description': 'Load and process high-resolution satellite imagery.',
                    'resource_usage': 'Medium',
                    'code': '''
# Initialize data loader with correct paths
loader = SatelliteDataLoader(
    cache_dir='data/cache',
    raw_dir='data/raw',
    processed_dir='data/processed',
    use_gpu=torch.cuda.is_available()
)

# Load satellite data for a specific region
satellite_data = loader.load_data(
    data_type='observation',
    time_range=['2024-01-01', '2024-01-31'],
    region={
        'lat': (45.5, 46.5),
        'lon': (-122.7, -122.5)
    }
)

# Display data summary
print("Satellite Data Summary:")
print(satellite_data.info())
'''
                }
            ]
        },
        {
            'title': 'Memory Formation',
            'description': 'Understanding how memories are formed and stored.',
            'code': '''
# Process and store satellite data
memory_id = data_pipeline.process(
    data=satellite_data,
    context={
        'source': 'sentinel-2',
        'region': 'portland',
        'time': '2024-01'
    }
)

# Create spatial memory index
spatial_index = spatial_pipeline.create_index(
    data=satellite_data,
    resolution='10m',
    index_type='quadtree'
)

# Extract temporal patterns
temporal_patterns = temporal_pipeline.extract_patterns(
    data=satellite_data,
    window_size='1M',
    pattern_type=['trend', 'seasonality', 'anomaly']
)
'''
        },
        {
            'title': 'Sustainability Monitoring',
            'description': 'Monitor and optimize resource usage.',
            'visualizations': [
                {
                    'title': 'Resource Usage Dashboard',
                    'description': 'Interactive dashboard showing sustainability metrics.',
                    'type': '2D',
                    'complexity': 'Medium',
                    'code': '''
# Create and display sustainability dashboard
dashboard = SystemMetrics.create_dashboard()
dashboard.show()

# Display detailed metrics
print("\\nDetailed Sustainability Metrics:")
print(f"Energy Efficiency: {SystemMetrics.get_efficiency_score():.2f}")
print(f"Memory Utilization: {SystemMetrics.get_memory_utilization():.2f}")
print(f"Carbon Footprint: {SystemMetrics.get_carbon_emissions():.2f} kgCO2e")
'''
                }
            ]
        }
    ] 