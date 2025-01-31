#!/usr/bin/env python3

import os
import json
import nbformat as nbf
from datetime import datetime
import importlib.util
import sys

def load_notebook_content():
    """Load notebook content from content modules"""
    content = {}
    content_dir = "examples/notebooks/content"
    
    # Create content directory if it doesn't exist
    os.makedirs(content_dir, exist_ok=True)
    
    # Add content directory to Python path
    sys.path.append(os.path.abspath(content_dir))
    
    # Define modern notebook types with earth memory synthesis focus
    notebooks = {
        "basic_usage": "Introduction to Earth Memory System",
        "synthetic_data": "Synthetic Earth Data Generation",
        "advanced_ml": "Advanced Machine Learning for Earth Memories",
        "climate_analysis": "Climate Pattern Analysis",
        "3d_visualization": "3D Earth Memory Visualization",
        "memory_optimization": "Memory Formation & Optimization",
        "privacy_security": "Privacy-Preserving Earth Data Processing",
        "distributed_computing": "Distributed Earth Memory Processing",
        "sustainability": "Sustainable Computing Practices"
    }
    
    # Try to import content modules
    for notebook, description in notebooks.items():
        try:
            module = importlib.import_module(f"{notebook}_content")
            content[notebook] = module.get_content()
        except ImportError:
            print(f"Warning: Content module for {notebook} not found")
            content[notebook] = {}
    
    return content

def update_notebook_metadata(notebook):
    """Update notebook metadata with modern configuration"""
    notebook.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.9.0"
        },
        "toc": {
            "base_numbering": 1,
            "nav_menu": {},
            "number_sections": True,
            "sideBar": True,
            "skip_h1_title": False,
            "title_cell": "Table of Contents",
            "title_sidebar": "Contents",
            "toc_cell": False,
            "toc_position": {},
            "toc_section_display": True,
            "toc_window_display": True
        },
        "accelerator": {
            "gpu_support": True,
            "distributed": True,
            "memory_optimization": True
        },
        "sustainability": {
            "energy_tracking": True,
            "resource_optimization": True,
            "carbon_awareness": True
        },
        "interactive_visualization": {
            "plotly": True,
            "bokeh": True,
            "ipywidgets": True,
            "ipyleaflet": True,
            "ipyvolume": True
        }
    }
    return notebook

def update_notebook_content(notebook, content):
    """Update notebook cells with rich content and modern features"""
    new_cells = []
    
    # Add setup and import cell with expanded dependencies
    setup_cell = nbf.v4.new_code_cell("""
    # Core dependencies
    import numpy as np
    import pandas as pd
    import torch
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Interactive visualization
    import plotly.express as px
    import plotly.graph_objects as go
    from bokeh.plotting import figure, show
    import ipywidgets as widgets
    from IPython.display import display, HTML
    import ipyleaflet as leaflet
    import ipyvolume as ipv
    import pyvista as pv
    import holoviews as hv
    import geoviews as gv
    
    # Earth data processing
    import rasterio
    import geopandas as gpd
    import xarray as xr
    import netCDF4
    import earthpy as et
    import earthpy.spatial as es
    import earthpy.plot as ep
    
    # Machine learning
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    import pytorch_lightning as pl
    from transformers import AutoModel, AutoTokenizer
    
    # Earth memory system
    from vortx import AGIMemorySystem
    from vortx.memory import (
        EpisodicMemory, 
        SemanticMemory, 
        WorkingMemory,
        SpatialMemory,
        TemporalMemory
    )
    from vortx.cognitive import (
        PatternSynthesizer,
        ContextProcessor,
        MemoryOptimizer,
        RelationshipExtractor
    )
    from vortx.sustainability import (
        EnergyMonitor,
        ResourceOptimizer,
        CarbonTracker,
        PowerProfiler
    )
    from vortx.visualization import (
        MemoryVisualizer,
        EarthVisualizer,
        NetworkVisualizer,
        TimeSeriesPlotter
    )
    from vortx.data import (
        SatelliteDataLoader,
        ClimateDataProcessor,
        TerrainAnalyzer,
        BiodiversityMetrics
    )
    
    # Set modern plotting style
    plt.style.use('seaborn')
    sns.set_palette("husl")
    hv.extension('bokeh')
    gv.extension('bokeh')
    
    # Configure notebook settings
    %matplotlib inline
    %config InlineBackend.figure_format = 'retina'
    
    # Enable notebook widgets
    widgets.init()
    
    # Initialize PyVista plotting
    pv.set_jupyter_backend('pythreejs')
    
    # Setup sustainability monitoring
    energy_monitor = EnergyMonitor()
    carbon_tracker = CarbonTracker()
    energy_monitor.start()
    carbon_tracker.start()
    
    # Apply notebook styling
    from IPython.core.display import HTML, display
    
    # Initialize styling
    display(HTML('''
        <script>
            // Function to periodically check and reapply styles
            function ensureStyles() {
                var styleElements = document.querySelectorAll('.section-header, .example-header, .visualization-header');
                styleElements.forEach(function(el) {
                    if (!el.style.background) {
                        el.style.cssText = window.getComputedStyle(el).cssText;
                    }
                });
            }
            
            // Run initially and every 2 seconds
            ensureStyles();
            setInterval(ensureStyles, 2000);
        </script>
    '''))
    """)
    new_cells.append(setup_cell)
    
    # Add helper functions cell
    helper_cell = nbf.v4.new_code_cell("""
    def load_earth_data(data_type='satellite', time_range=None, region=None):
        \"\"\"Load and preprocess Earth observation data\"\"\"
        loader = SatelliteDataLoader(
            cache_dir='examples/notebooks/data/cache',
            use_gpu=torch.cuda.is_available()
        )
        
        if data_type == 'satellite':
            data = loader.load_satellite_data(
                time_range=time_range,
                region=region,
                resolution='high',
                bands=['RGB', 'NIR', 'SWIR']
            )
        elif data_type == 'climate':
            data = loader.load_climate_data(
                time_range=time_range,
                region=region,
                variables=['temperature', 'precipitation', 'vegetation']
            )
        elif data_type == 'terrain':
            data = loader.load_terrain_data(
                region=region,
                resolution='30m',
                include_derivatives=True
            )
        
        return data
    
    def create_memory_pipeline(data_type='general'):
        \"\"\"Create memory processing pipeline\"\"\"
        if data_type == 'spatial':
            return SpatialMemory(
                resolution='adaptive',
                compression_ratio=0.8,
                indexing_method='quadtree'
            )
        elif data_type == 'temporal':
            return TemporalMemory(
                sequence_length=1000,
                sampling_rate='1h',
                interpolation='cubic'
            )
        else:
            return EpisodicMemory(
                capacity='adaptive',
                retention_policy='importance_based'
            )
    
    def visualize_earth_memory(memory_data, viz_type='3d'):
        \"\"\"Create interactive visualization of Earth memory data\"\"\"
        visualizer = EarthVisualizer(
            backend='pythreejs',
            resolution='high'
        )
        
        if viz_type == '3d':
            fig = visualizer.create_3d_viz(
                memory_data,
                colormap='earth',
                add_controls=True
            )
        elif viz_type == 'network':
            fig = visualizer.create_memory_network(
                memory_data,
                layout='force_directed',
                show_relationships=True
            )
        elif viz_type == 'temporal':
            fig = visualizer.create_temporal_viz(
                memory_data,
                animation_frame='time',
                color_by='intensity'
            )
        
        return fig
    
    def monitor_sustainability():
        \"\"\"Monitor and display sustainability metrics\"\"\"
        metrics = {
            'energy_usage': energy_monitor.get_usage(),
            'carbon_footprint': carbon_tracker.get_footprint(),
            'memory_efficiency': ResourceOptimizer.get_efficiency(),
            'computation_cost': PowerProfiler.get_cost()
        }
        
        # Create sustainability dashboard
        fig = go.Figure()
        for metric, value in metrics.items():
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': metric.replace('_', ' ').title()},
                domain={'row': 0, 'column': 0}
            ))
        
        fig.update_layout(
            grid={'rows': 2, 'columns': 2},
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    """)
    new_cells.append(helper_cell)
    
    # Continue with existing content handling...
    if content:
        for section in content:
            # Add section header with modern styling
            header = f"""
            <div class="section-header">
                <h2>{section['title']}</h2>
                <p class="description">{section['description']}</p>
            </div>
            """
            new_cells.append(nbf.v4.new_markdown_cell(header))
            
            # Add code cells with modern features
            if 'code' in section:
                new_cells.append(nbf.v4.new_code_cell(section['code']))
            
            # Add interactive examples
            if 'examples' in section:
                for example in section['examples']:
                    example_header = f"""
                    <div class="example-header">
                        <h3>🔍 Example: {example['title']}</h3>
                        <p class="description">{example['description']}</p>
                        <div class="sustainability-note">
                            🌱 Estimated resource usage: {example.get('resource_usage', 'Low')}
                        </div>
                    </div>
                    """
                    new_cells.append(nbf.v4.new_markdown_cell(example_header))
                    new_cells.append(nbf.v4.new_code_cell(example['code']))
            
            # Add interactive visualizations
            if 'visualizations' in section:
                for viz in section['visualizations']:
                    viz_header = f"""
                    <div class="visualization-header">
                        <h3>📊 Visualization: {viz['title']}</h3>
                        <p class="description">{viz['description']}</p>
                        <div class="viz-controls">
                            <span class="viz-type">Type: {viz.get('type', '2D')}</span>
                            <span class="viz-complexity">Complexity: {viz.get('complexity', 'Medium')}</span>
                        </div>
                    </div>
                    """
                    new_cells.append(nbf.v4.new_markdown_cell(viz_header))
                    new_cells.append(nbf.v4.new_code_cell(viz['code']))
    
    notebook.cells = new_cells
    return notebook

def update_notebook_style(notebook):
    """Add modern styling and formatting to the notebook"""
    style_cell = nbf.v4.new_code_cell("""
    from IPython.core.display import HTML

    HTML('''
    <style>
    /* Modern color scheme */
    div.cell.code_cell {
        background-color: #f8f9fa !important;
        border-radius: 8px !important;
        padding: 1em !important;
        margin: 1em 0 !important;
    }
    
    div.output_area {
        padding: 1em !important;
        border-radius: 8px !important;
        background: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    div.inner_cell {
        padding: 1em !important;
    }
    
    .rendered_html h1, .rendered_html h2, .rendered_html h3, 
    .rendered_html h4, .rendered_html h5, .rendered_html h6 {
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
        color: #2c3e50 !important;
    }
    
    .rendered_html h1 {
        font-size: 2.5em !important;
        border-bottom: 3px solid #3498db !important;
        padding-bottom: 0.5em !important;
        margin-bottom: 1em !important;
    }
    
    .rendered_html h2 {
        font-size: 2em !important;
        border-bottom: 2px solid #3498db !important;
        padding-bottom: 0.3em !important;
        margin: 1.5em 0 1em !important;
    }
    
    .rendered_html h3 {
        font-size: 1.5em !important;
        color: #34495e !important;
        margin: 1em 0 !important;
    }
    
    /* Section styling */
    .section-header {
        background: #ecf0f1 !important;
        padding: 1em !important;
        border-radius: 8px !important;
        margin: 1.5em 0 !important;
        border-left: 4px solid #3498db !important;
    }
    
    .example-header, .visualization-header {
        background: linear-gradient(to right, #ecf0f1, transparent) !important;
        padding: 0.8em !important;
        border-left: 4px solid #e74c3c !important;
        margin: 1em 0 !important;
    }
    
    /* Interactive elements */
    .widget-slider {
        width: 100% !important;
        margin: 1em 0 !important;
    }
    
    .widget-button {
        background: #3498db !important;
        color: white !important;
        border: none !important;
        padding: 0.5em 1em !important;
        border-radius: 4px !important;
        cursor: pointer !important;
    }
    
    /* Alerts and info boxes */
    .alert {
        padding: 1em !important;
        margin: 1em 0 !important;
        border-radius: 4px !important;
        border-left: 4px solid !important;
    }
    
    .alert-info {
        background: #d9edf7 !important;
        border-color: #3498db !important;
    }
    
    .alert-warning {
        background: #fcf8e3 !important;
        border-color: #e74c3c !important;
    }
    
    /* Sustainability indicator */
    .sustainability-indicator {
        position: fixed !important;
        top: 1em !important;
        right: 1em !important;
        background: #ecf0f1 !important;
        padding: 0.5em !important;
        border-radius: 4px !important;
        font-size: 0.8em !important;
        z-index: 1000 !important;
    }
    
    /* Code cell improvements */
    .highlight {
        background: #f8f9fa !important;
        border-radius: 4px !important;
        padding: 0.5em !important;
    }
    
    .highlight pre {
        font-family: 'Fira Code', 'Source Code Pro', monospace !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
    }
    
    /* Table styling */
    .rendered_html table {
        border-collapse: collapse !important;
        margin: 1em 0 !important;
        width: 100% !important;
    }
    
    .rendered_html th, .rendered_html td {
        padding: 0.5em 1em !important;
        border: 1px solid #ddd !important;
    }
    
    .rendered_html th {
        background: #f8f9fa !important;
        font-weight: bold !important;
    }
    
    /* Markdown cell improvements */
    div.text_cell_render {
        padding: 1em !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        color: #2c3e50 !important;
    }
    </style>
    ''')
    """)
    notebook.cells.insert(0, style_cell)
    return notebook

def add_interactive_features(notebook):
    """Add modern interactive widgets and features"""
    # Add widget initialization and helper functions
    setup_cell = nbf.v4.new_code_cell("""
    def create_interactive_plot(data, plot_type='scatter'):
        \"\"\"Create interactive plot with controls\"\"\"
        plot_types = ['scatter', 'line', 'heatmap', '3d']
        
        # Create widgets
        plot_selector = widgets.Dropdown(
            options=plot_types,
            value=plot_type,
            description='Plot Type:'
        )
        
        # Create plot container
        plot_output = widgets.Output()
        
        def update_plot(change):
            plot_output.clear_output()
            with plot_output:
                if change['new'] == 'scatter':
                    fig = px.scatter(data)
                elif change['new'] == 'line':
                    fig = px.line(data)
                elif change['new'] == 'heatmap':
                    fig = px.imshow(data)
                else:  # 3d
                    fig = px.scatter_3d(data)
                fig.show()
        
        plot_selector.observe(update_plot, names='value')
        
        # Create layout
        controls = widgets.VBox([plot_selector])
        return widgets.VBox([controls, plot_output])
    
    # Initialize sustainability monitoring
    energy_monitor = widgets.HTML(
        value='<div class="sustainability-indicator">🌱 Energy Usage: Monitoring...</div>'
    )
    display(energy_monitor)
    """)
    notebook.cells.insert(1, setup_cell)
    return notebook

def add_documentation(notebook):
    """Add comprehensive documentation and examples"""
    doc_cells = [
        nbf.v4.new_markdown_cell("""
        # Earth Memory Synthesis Notebook
        
        This notebook provides comprehensive examples and demonstrations of the Earth Memory Synthesis System.
        
        ## Features
        - 🌍 Advanced Earth data processing
        - 🧠 Memory formation and synthesis
        - 📊 Interactive visualizations
        - 🚀 GPU-accelerated computations
        - 🌱 Sustainable computing practices
        
        ## Usage Guidelines
        1. Run cells sequentially
        2. Experiment with parameters
        3. Monitor resource usage
        4. Explore interactive visualizations
        
        ## Performance Tips
        - Enable GPU acceleration when available
        - Use batch processing for large datasets
        - Monitor memory usage
        - Implement sustainable computing practices
        """),
        nbf.v4.new_markdown_cell("""
        ## Getting Started
        
        This notebook uses modern tools and practices for earth memory synthesis:
        
        - **Data Processing**: Advanced preprocessing and augmentation
        - **Memory Formation**: Efficient memory creation and storage
        - **Visualization**: Interactive 2D/3D visualizations
        - **Sustainability**: Energy-aware computing
        
        Let's begin by setting up our environment and importing required libraries.
        """)
    ]
    notebook.cells.extend(doc_cells)
    return notebook

def main():
    """Main function to update notebooks with modern features"""
    notebooks_dir = "examples/notebooks"
    
    # Load content
    content = load_notebook_content()
    
    # Update each notebook
    for notebook_file in os.listdir(notebooks_dir):
        if notebook_file.endswith('.ipynb'):
            notebook_path = os.path.join(notebooks_dir, notebook_file)
            
            # Read existing notebook
            with open(notebook_path, 'r') as f:
                notebook = nbf.read(f, as_version=4)
            
            # Get notebook name without extension
            notebook_name = notebook_file.split('.')[0].split('_', 1)[1]
            
            # Update notebook with modern features
            notebook = update_notebook_metadata(notebook)
            notebook = update_notebook_content(notebook, content.get(notebook_name, {}))
            notebook = update_notebook_style(notebook)
            notebook = add_interactive_features(notebook)
            notebook = add_documentation(notebook)
            
            # Save updated notebook
            with open(notebook_path, 'w') as f:
                nbf.write(notebook, f)
            
            print(f"Updated notebook: {notebook_path} with modern features")

if __name__ == "__main__":
    main() 