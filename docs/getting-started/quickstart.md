# Quick Start Guide

## Basic Usage

### Prerequisites
- Python 3.9 or higher
- Virtual environment (recommended)
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/vortx-ai/synthetic-satellite.git
cd synthetic-satellite

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Basic Example
```python
from vortx import Vortx
from vortx.models import DeepSeekR1, DeepSeekV3
from vortx.memory import EarthMemoryStore

# Initialize with advanced models
vx = Vortx(
    models={
        "reasoning": DeepSeekR1(),
        "vision": DeepSeekV3()
    },
    use_gpu=True
)

# Create Earth memories
memory_store = EarthMemoryStore()
memories = vx.create_memories(
    location=(37.7749, -122.4194),
    time_range=("2020-01-01", "2024-01-01"),
    modalities=["satellite", "climate", "social"]
)
```

## Next Steps

- [Configuration Guide](configuration.md)
- [Advanced Features](../guides/tutorials/advanced.md)
- [API Reference](../technical/api/python.md)
- [Example Projects](../guides/examples/) 