"""
Script to generate Jupyter notebooks for the Vortx Earth Memory System examples.
"""

import nbformat as nbf
import os

def create_basic_usage_notebook():
    nb = nbf.v4.new_notebook()
    
    # Title and introduction
    nb.cells.append(nbf.v4.new_markdown_cell(
        "# Basic Usage of Vortx Earth Memory System\n\n"
        "This notebook demonstrates the basic usage of the Vortx Earth Memory System.\n\n"
        "## Contents\n"
        "1. System Setup\n"
        "2. Loading Sample Data\n"
        "3. Creating Earth Memories\n"
        "4. Basic Operations\n"
        "5. Visualization\n\n"
        "Author: Vortx Team  \n"
        "License: MIT"
    ))
    
    # Imports
    nb.cells.append(nbf.v4.new_code_cell(
        "# Import required libraries\n"
        "import os\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "import matplotlib.pyplot as plt\n"
        "from datetime import datetime, timedelta\n\n"
        "from vortx import EarthMemorySystem\n"
        "from vortx.utils import setup_environment\n"
        "from vortx.viz import MemoryVisualizer"
    ))
    
    # System Setup section
    nb.cells.append(nbf.v4.new_markdown_cell(
        "## 1. System Setup\n\n"
        "First, let's set up the Earth Memory System with basic configurations."
    ))
    
    nb.cells.append(nbf.v4.new_code_cell(
        "# Configure environment\n"
        "setup_environment(\n"
        "    api_key=os.getenv(\"VORTX_API_KEY\", \"demo-key\"),\n"
        "    log_level=\"INFO\"\n"
        ")\n\n"
        "# Initialize system\n"
        "system = EarthMemorySystem(\n"
        "    memory_config={\n"
        "        \"architecture\": \"hierarchical\",\n"
        "        \"compression\": \"adaptive\"\n"
        "    }\n"
        ")\n\n"
        "print(\"System initialized successfully!\")"
    ))
    
    # Data Loading section
    nb.cells.append(nbf.v4.new_markdown_cell(
        "## 2. Loading Sample Data\n\n"
        "Let's generate some sample Earth observation data for demonstration."
    ))
    
    nb.cells.append(nbf.v4.new_code_cell(
        "def generate_sample_data(n_samples=1000):\n"
        "    \"\"\"Generate synthetic Earth observation data.\"\"\"\n"
        "    start_date = datetime(2024, 1, 1)\n"
        "    \n"
        "    data = {\n"
        "        \"timestamp\": [start_date + timedelta(hours=i) for i in range(n_samples)],\n"
        "        \"latitude\": np.random.uniform(30, 45, n_samples),\n"
        "        \"longitude\": np.random.uniform(-120, -100, n_samples),\n"
        "        \"temperature\": np.random.normal(25, 5, n_samples),\n"
        "        \"precipitation\": np.random.exponential(2, n_samples),\n"
        "        \"cloud_cover\": np.random.uniform(0, 1, n_samples)\n"
        "    }\n"
        "    \n"
        "    return pd.DataFrame(data)\n\n"
        "# Generate and display sample data\n"
        "sample_data = generate_sample_data()\n"
        "print(\"Sample data shape:\", sample_data.shape)\n"
        "sample_data.head()"
    ))
    
    # Memory Creation section
    nb.cells.append(nbf.v4.new_markdown_cell(
        "## 3. Creating Earth Memories\n\n"
        "Now, let's create Earth memories from our sample data."
    ))
    
    nb.cells.append(nbf.v4.new_code_cell(
        "# Create memory from sample data\n"
        "memory = system.create_memory(\n"
        "    data=sample_data,\n"
        "    memory_params={\n"
        "        \"spatial_resolution\": \"1km\",\n"
        "        \"temporal_resolution\": \"1h\",\n"
        "        \"compression_level\": \"medium\"\n"
        "    }\n"
        ")\n\n"
        "print(\"Memory created successfully!\")\n"
        "print(f\"Memory size: {memory.size_mb:.2f} MB\")"
    ))
    
    # Basic Operations section
    nb.cells.append(nbf.v4.new_markdown_cell(
        "## 4. Basic Operations\n\n"
        "Let's perform some basic operations on our Earth memory."
    ))
    
    nb.cells.append(nbf.v4.new_code_cell(
        "# Query memory\n"
        "query_results = memory.query(\n"
        "    bbox=[-115, 35, -105, 40],  # [min_lon, min_lat, max_lon, max_lat]\n"
        "    time_range=[datetime(2024, 1, 1), datetime(2024, 1, 7)],\n"
        "    variables=[\"temperature\", \"precipitation\"]\n"
        ")\n\n"
        "print(\"Query results shape:\", query_results.shape)\n"
        "query_results.head()"
    ))
    
    # Visualization section
    nb.cells.append(nbf.v4.new_markdown_cell(
        "## 5. Visualization\n\n"
        "Finally, let's visualize our Earth memory data."
    ))
    
    nb.cells.append(nbf.v4.new_code_cell(
        "# Initialize visualizer\n"
        "visualizer = MemoryVisualizer()\n\n"
        "# Create visualization\n"
        "fig = visualizer.plot_memory(\n"
        "    memory=memory,\n"
        "    variable=\"temperature\",\n"
        "    time=datetime(2024, 1, 1),\n"
        "    plot_type=\"heatmap\"\n"
        ")\n\n"
        "plt.show()"
    ))
    
    # Cleanup section
    nb.cells.append(nbf.v4.new_markdown_cell(
        "## Cleanup\n\n"
        "Always clean up system resources when done."
    ))
    
    nb.cells.append(nbf.v4.new_code_cell(
        "# Cleanup\n"
        "system.cleanup()\n"
        "print(\"Cleanup complete!\")"
    ))
    
    return nb

def create_synthetic_data_notebook():
    nb = nbf.v4.new_notebook()
    
    # Title and introduction
    nb.cells.append(nbf.v4.new_markdown_cell(
        "# Synthetic Data Generation with Vortx\n\n"
        "This notebook demonstrates how to generate synthetic Earth observation data.\n\n"
        "## Contents\n"
        "1. Setup and Configuration\n"
        "2. Basic Synthetic Data Generation\n"
        "3. Advanced Generation Techniques\n"
        "4. Validation and Quality Checks\n"
        "5. Export and Visualization\n\n"
        "Author: Vortx Team  \n"
        "License: MIT"
    ))
    
    # Imports
    nb.cells.append(nbf.v4.new_code_cell(
        "# Import required libraries\n"
        "import os\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "import matplotlib.pyplot as plt\n"
        "from datetime import datetime, timedelta\n\n"
        "from vortx import EarthMemorySystem\n"
        "from vortx.utils import setup_environment\n"
        "from vortx.synthetic import DataGenerator, QualityChecker\n"
        "from vortx.viz import SyntheticVisualizer"
    ))
    
    # Setup section
    nb.cells.append(nbf.v4.new_markdown_cell(
        "## 1. Setup and Configuration\n\n"
        "First, let's set up the system and configure the synthetic data generator."
    ))
    
    nb.cells.append(nbf.v4.new_code_cell(
        "# Configure environment\n"
        "setup_environment(\n"
        "    api_key=os.getenv(\"VORTX_API_KEY\", \"demo-key\"),\n"
        "    log_level=\"INFO\"\n"
        ")\n\n"
        "# Initialize generator\n"
        "generator = DataGenerator(\n"
        "    config={\n"
        "        \"resolution\": \"1km\",\n"
        "        \"time_step\": \"1h\",\n"
        "        \"noise_level\": \"low\",\n"
        "        \"complexity\": \"medium\"\n"
        "    }\n"
        ")\n\n"
        "print(\"Generator initialized successfully!\")"
    ))
    
    return nb

def create_ml_notebook():
    nb = nbf.v4.new_notebook()
    
    # Title and introduction
    nb.cells.append(nbf.v4.new_markdown_cell(
        "# Advanced ML Processing with Vortx\n\n"
        "This notebook demonstrates advanced machine learning capabilities.\n\n"
        "## Contents\n"
        "1. Setup and Data Loading\n"
        "2. Feature Engineering\n"
        "3. Model Training\n"
        "4. Advanced Analysis\n"
        "5. Performance Evaluation\n\n"
        "Author: Vortx Team  \n"
        "License: MIT"
    ))
    
    # Imports
    nb.cells.append(nbf.v4.new_code_cell(
        "# Import required libraries\n"
        "import os\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "import torch\n"
        "import matplotlib.pyplot as plt\n"
        "from sklearn.model_selection import train_test_split\n"
        "from datetime import datetime, timedelta\n\n"
        "from vortx import EarthMemorySystem\n"
        "from vortx.utils import setup_environment\n"
        "from vortx.ml import (\n"
        "    FeatureProcessor,\n"
        "    ModelTrainer,\n"
        "    PerformanceEvaluator\n"
        ")\n"
        "from vortx.viz import MLVisualizer"
    ))
    
    return nb

def create_3d_ar_vr_notebook():
    nb = nbf.v4.new_notebook()
    
    # Title and introduction
    nb.cells.append(nbf.v4.new_markdown_cell(
        "# 3D, AR, and VR Visualization with Vortx\n\n"
        "This notebook demonstrates advanced visualization capabilities.\n\n"
        "## Contents\n"
        "1. Setup and Data Preparation\n"
        "2. 3D Visualization\n"
        "3. AR Scene Generation\n"
        "4. VR Environment Creation\n"
        "5. Interactive Visualization\n\n"
        "Author: Vortx Team  \n"
        "License: MIT"
    ))
    
    # Imports
    nb.cells.append(nbf.v4.new_code_cell(
        "# Import required libraries\n"
        "import os\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "import plotly.graph_objects as go\n"
        "from datetime import datetime\n\n"
        "from vortx import EarthMemorySystem\n"
        "from vortx.utils import setup_environment\n"
        "from vortx.viz import (\n"
        "    Scene3DGenerator,\n"
        "    ARSceneCreator,\n"
        "    VREnvironmentBuilder,\n"
        "    InteractiveVisualizer\n"
        ")"
    ))
    
    return nb

def create_gpu_notebook():
    nb = nbf.v4.new_notebook()
    
    # Title and introduction
    nb.cells.append(nbf.v4.new_markdown_cell(
        "# Advanced GPU Processing with Vortx\n\n"
        "This notebook demonstrates advanced GPU processing capabilities.\n\n"
        "## Contents\n"
        "1. Setup and GPU Configuration\n"
        "2. Data Preparation\n"
        "3. Parallel Processing\n"
        "4. Memory Management\n"
        "5. Performance Optimization\n\n"
        "Author: Vortx Team  \n"
        "License: MIT"
    ))
    
    # Imports
    nb.cells.append(nbf.v4.new_code_cell(
        "# Import required libraries\n"
        "import os\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "import torch\n"
        "import cupy as cp\n"
        "from datetime import datetime\n\n"
        "from vortx import EarthMemorySystem\n"
        "from vortx.utils import setup_environment\n"
        "from vortx.gpu import (\n"
        "    GPUProcessor,\n"
        "    MemoryManager,\n"
        "    StreamHandler,\n"
        "    Profiler\n"
        ")"
    ))
    
    return nb

def main():
    # Create notebooks directory if it doesn't exist
    os.makedirs("examples/notebooks", exist_ok=True)
    
    # Create notebooks
    notebooks = {
        "01_basic_usage.ipynb": create_basic_usage_notebook(),
        "02_synthetic_data.ipynb": create_synthetic_data_notebook(),
        "03_advanced_ml.ipynb": create_ml_notebook(),
        "04_3d_ar_vr.ipynb": create_3d_ar_vr_notebook(),
        "05_gpu_processing.ipynb": create_gpu_notebook()
    }
    
    # Save notebooks
    for filename, nb in notebooks.items():
        with open(f"examples/notebooks/{filename}", "w") as f:
            nbf.write(nb, f)
        print(f"Created {filename}")

if __name__ == "__main__":
    main() 