#!/usr/bin/env python3
"""
Example demonstrating machine learning integration with AGI memory system.
"""

import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    EpisodicMemory,
    SemanticMemory,
    WorkingMemory
)
from vortx.ml import (
    MemoryNetwork,
    TransferLearner,
    ContinualLearner
)
from vortx.sustainability import (
    EnergyMonitor,
    ResourceOptimizer
)

class MemoryEnhancedModel(nn.Module):
    """Neural network with AGI memory integration."""
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.memory_net = MemoryNetwork(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            memory_size=1000
        )
        self.transfer = TransferLearner(hidden_dim)
        self.continual = ContinualLearner(hidden_dim)
        
        self.layers = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x, memory_context=None):
        # Process through memory network
        memory_features = self.memory_net(x, memory_context)
        
        # Apply transfer learning
        transferred = self.transfer(memory_features)
        
        # Update continual learning
        enhanced = self.continual(transferred)
        
        # Final processing
        return self.layers(enhanced)

def create_memory_dataset(system, data, labels):
    """Create memory-enhanced dataset."""
    episodic = EpisodicMemory(system)
    semantic = SemanticMemory(system)
    working = WorkingMemory(system)
    
    memory_enhanced_data = []
    memory_contexts = []
    
    # Process data in batches
    batch_size = 32
    for i in range(0, len(data), batch_size):
        batch_data = data[i:i + batch_size]
        batch_labels = labels[i:i + batch_size]
        
        # Store in working memory
        working_id = working.store(
            data=batch_data,
            labels=batch_labels
        )
        
        # Create episodic memory
        episodic_id = episodic.store(
            data=batch_data,
            context={
                "labels": batch_labels,
                "timestamp": datetime.now()
            }
        )
        
        # Extract semantic features
        semantic_features = semantic.extract_features(episodic_id)
        
        # Combine memory information
        memory_context = {
            "working": working.get_context(working_id),
            "episodic": episodic.get_context(episodic_id),
            "semantic": semantic_features
        }
        
        memory_enhanced_data.append(batch_data)
        memory_contexts.append(memory_context)
        
        # Cleanup working memory
        working.clear(working_id)
    
    return np.vstack(memory_enhanced_data), memory_contexts

def train_memory_model(model, train_data, train_contexts, train_labels, 
                      val_data, val_contexts, val_labels, monitor):
    """Train model with memory enhancement and sustainability monitoring."""
    optimizer = torch.optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss()
    
    # Create data loaders
    train_loader = DataLoader(
        list(zip(train_data, train_contexts, train_labels)),
        batch_size=32,
        shuffle=True
    )
    val_loader = DataLoader(
        list(zip(val_data, val_contexts, val_labels)),
        batch_size=32
    )
    
    best_val_loss = float('inf')
    patience = 5
    patience_counter = 0
    
    for epoch in range(100):
        # Training
        model.train()
        train_loss = 0
        for batch_data, batch_contexts, batch_labels in train_loader:
            optimizer.zero_grad()
            
            # Forward pass with memory context
            outputs = model(batch_data, batch_contexts)
            loss = criterion(outputs, batch_labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch_data, batch_contexts, batch_labels in val_loader:
                outputs = model(batch_data, batch_contexts)
                val_loss += criterion(outputs, batch_labels).item()
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}")
                break
        
        # Monitor resource usage
        metrics = monitor.get_training_metrics()
        print(f"Epoch {epoch}: Train Loss = {train_loss:.4f}, "
              f"Val Loss = {val_loss:.4f}")
        print("Resource Usage:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "ml_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Initialize monitoring
    monitor = EnergyMonitor(system)
    optimizer = ResourceOptimizer()
    
    # Generate sample data
    data = np.random.randn(1000, 128)
    labels = np.random.randint(0, 10, 1000)
    
    # Create memory-enhanced dataset
    print("Creating memory-enhanced dataset...")
    enhanced_data, memory_contexts = create_memory_dataset(
        system, data, labels
    )
    
    # Split data
    (train_data, val_data, train_labels, val_labels, 
     train_contexts, val_contexts) = train_test_split(
        enhanced_data, labels, memory_contexts, test_size=0.2
    )
    
    # Create and train model
    print("\nTraining memory-enhanced model...")
    model = MemoryEnhancedModel(
        input_dim=128,
        hidden_dim=256,
        output_dim=10
    )
    
    train_memory_model(
        model, train_data, train_contexts, train_labels,
        val_data, val_contexts, val_labels, monitor
    )
    
    # Save model and memory contexts
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)
    
    torch.save({
        'model_state': model.state_dict(),
        'memory_config': system.get_memory_config()
    }, f"{output_dir}/memory_enhanced_model.pth")
    
    # Print final metrics
    metrics = monitor.get_metrics()
    print("\nFinal Sustainability Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Cleanup
    system.cleanup()

if __name__ == "__main__":
    main() 