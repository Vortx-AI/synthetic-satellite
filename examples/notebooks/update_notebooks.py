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
    content_dir = "content"
    
    # Create content directory if it doesn't exist
    os.makedirs(content_dir, exist_ok=True)
    
    # Add content directory to Python path
    sys.path.append(os.path.abspath(content_dir))
    
    # Try to import content modules
    for notebook in ["basic_usage", "synthetic_data", "advanced_ml", "3d_ar_vr", "gpu_processing", "sustainable_deployment"]:
        try:
            module = importlib.import_module(f"{notebook}_content")
            content[notebook] = module.get_content()
        except ImportError:
            print(f"Warning: Content module for {notebook} not found")
            content[notebook] = {}
    
    return content

def update_notebook_metadata(notebook):
    """Update notebook metadata"""
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
        }
    }
    return notebook

def update_notebook_content(notebook, content):
    """Update notebook cells with rich content"""
    # Update existing cells or add new ones
    new_cells = []
    
    # Add content if available
    if content:
        for section in content:
            # Add section header
            new_cells.append(nbf.v4.new_markdown_cell(f"## {section['title']}\n\n{section['description']}"))
            
            # Add code cells
            if 'code' in section:
                new_cells.append(nbf.v4.new_code_cell(section['code']))
            
            # Add example cells
            if 'examples' in section:
                for example in section['examples']:
                    new_cells.append(nbf.v4.new_markdown_cell(f"### Example: {example['title']}\n\n{example['description']}"))
                    new_cells.append(nbf.v4.new_code_cell(example['code']))
            
            # Add visualization cells
            if 'visualizations' in section:
                for viz in section['visualizations']:
                    new_cells.append(nbf.v4.new_markdown_cell(f"### Visualization: {viz['title']}\n\n{viz['description']}"))
                    new_cells.append(nbf.v4.new_code_cell(viz['code']))
    
    notebook.cells = new_cells
    return notebook

def update_notebook_style(notebook):
    """Add styling and formatting to the notebook"""
    # Add custom CSS
    style_cell = nbf.v4.new_markdown_cell("""
    <style>
    h1 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    h2 {
        color: #34495e;
        border-bottom: 1px solid #bdc3c7;
        padding-bottom: 5px;
    }
    h3 {
        color: #7f8c8d;
    }
    .alert {
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid transparent;
        border-radius: 4px;
    }
    .alert-info {
        color: #31708f;
        background-color: #d9edf7;
        border-color: #bce8f1;
    }
    .alert-warning {
        color: #8a6d3b;
        background-color: #fcf8e3;
        border-color: #faebcc;
    }
    </style>
    """)
    notebook.cells.insert(0, style_cell)
    return notebook

def add_interactive_features(notebook):
    """Add interactive widgets and features"""
    # Add ipywidgets import
    import_cell = nbf.v4.new_code_cell("""
    import ipywidgets as widgets
    from IPython.display import display, HTML
    """)
    notebook.cells.insert(1, import_cell)
    return notebook

def add_documentation(notebook):
    """Add comprehensive documentation and examples"""
    # Add documentation cells
    doc_cells = [
        nbf.v4.new_markdown_cell("""
        ## Documentation
        
        This notebook provides comprehensive examples and demonstrations of the Vortx AGI Memory System.
        Each section includes:
        - Detailed explanations
        - Code examples
        - Interactive visualizations
        - Performance metrics
        
        ### Usage Guidelines
        1. Run cells in sequence
        2. Modify parameters as needed
        3. Experiment with different configurations
        4. Monitor system performance
        """),
        nbf.v4.new_markdown_cell("""
        ### Performance Tips
        - Use GPU acceleration when available
        - Monitor memory usage
        - Optimize batch sizes
        - Enable caching for repeated operations
        """)
    ]
    notebook.cells.extend(doc_cells)
    return notebook

def main():
    """Main function to update notebooks"""
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
            
            # Update notebook
            notebook = update_notebook_metadata(notebook)
            notebook = update_notebook_content(notebook, content.get(notebook_name, {}))
            notebook = update_notebook_style(notebook)
            notebook = add_interactive_features(notebook)
            notebook = add_documentation(notebook)
            
            # Save updated notebook
            with open(notebook_path, 'w') as f:
                nbf.write(notebook, f)
            
            print(f"Updated notebook: {notebook_path}")

if __name__ == "__main__":
    main() 