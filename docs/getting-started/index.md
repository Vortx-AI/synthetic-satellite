# Getting Started with Vortx

Welcome to Vortx Synthetic Satellite! This section will help you get up and running quickly with our advanced Earth Memory System.

## Quick Navigation

### Essential Setup
1. [Installation Guide](installation.md)
   - System requirements
   - Installation from source
   - Environment setup
   - Verification steps

2. [Quick Start Guide](quickstart.md)
   - Basic usage
   - First memory formation
   - Simple inference
   - Example workflows

3. [Configuration](configuration.md)
   - Basic settings
   - Advanced options
   - Performance tuning
   - Security setup

### Next Steps
- [Core Concepts](../core-concepts/overview.md)
- [Tutorials](../guides/tutorials/basic.md)
- [API Reference](../technical/api/rest.md)

## Common Tasks

### Memory Formation
```python
from vortx import Vortx
from vortx.memory import EarthMemoryStore

# Initialize Vortx
vx = Vortx()

# Create memories
memories = vx.create_memories(
    location=(37.7749, -122.4194),
    time_range=("2020-01-01", "2024-01-01")
)
```

### Basic Inference
```python
# Run inference
results = vx.infer(
    query="Analyze urban development",
    context=memories
)
```

## Support Resources
- [Documentation Home](../index.md)
- [Community Forums](https://community.vortx.ai)
- [GitHub Repository](https://github.com/vortx-ai/synthetic-satellite)
- [Issue Tracker](https://github.com/vortx-ai/synthetic-satellite/issues) 