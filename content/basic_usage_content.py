"""Content module for basic usage notebook."""

def get_content():
    """Return content for basic usage notebook."""
    return [
        {
            'title': 'Introduction to Earth Memory System',
            'description': 'Learn the fundamentals of the Earth Memory System and its core components.',
            'code': '''
# Initialize the Earth Memory System
system = AGIMemorySystem(
    config={
        'memory_type': 'hierarchical',
        'compression': 'adaptive',
        'sustainability': {
            'energy_efficient': True,
            'resource_optimized': True
        }
    }
)

# Create memory components
episodic = create_memory_pipeline('general')
spatial = create_memory_pipeline('spatial')
temporal = create_memory_pipeline('temporal')

# Display system configuration
print("System Configuration:")
print(system.get_config())
'''
        },
        {
            'title': 'Loading Earth Data',
            'description': 'Learn how to load and preprocess different types of Earth observation data.',
            'examples': [
                {
                    'title': 'Loading Satellite Data',
                    'description': 'Load and process high-resolution satellite imagery.',
                    'resource_usage': 'Medium',
                    'code': '''
# Load satellite data for a specific region
satellite_data = load_earth_data(
    data_type='satellite',
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
                },
                {
                    'title': 'Loading Climate Data',
                    'description': 'Load and analyze climate patterns.',
                    'resource_usage': 'Low',
                    'code': '''
# Load climate data
climate_data = load_earth_data(
    data_type='climate',
    time_range=['2024-01-01', '2024-01-31'],
    region='global'
)

# Create interactive climate visualization
fig = visualize_earth_memory(climate_data, viz_type='temporal')
fig.show()
'''
                }
            ]
        },
        {
            'title': 'Memory Formation',
            'description': 'Understanding how memories are formed and stored.',
            'code': '''
# Process and store satellite data as memories
memory_id = episodic.store(
    data=satellite_data,
    context={
        'source': 'sentinel-2',
        'region': 'portland',
        'time': '2024-01'
    }
)

# Create spatial memory index
spatial_index = spatial.create_index(
    data=satellite_data,
    resolution='10m',
    index_type='quadtree'
)

# Store temporal patterns
temporal_patterns = temporal.extract_patterns(
    data=climate_data,
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
dashboard = monitor_sustainability()
dashboard.show()

# Display detailed metrics
print("\\nDetailed Sustainability Metrics:")
print(f"Energy Efficiency: {ResourceOptimizer.get_efficiency_score():.2f}")
print(f"Memory Utilization: {ResourceOptimizer.get_memory_utilization():.2f}")
print(f"Carbon Footprint: {CarbonTracker.get_total_emissions():.2f} kgCO2e")
'''
                }
            ]
        }
    ] 