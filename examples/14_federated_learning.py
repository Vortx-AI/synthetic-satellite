#!/usr/bin/env python3
"""
Example demonstrating federated learning with AGI memory systems.
"""

import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from datetime import datetime
from typing import Dict, List, Tuple
import asyncio
from pathlib import Path

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    FederatedMemory,
    ModelMemory,
    GradientMemory
)
from vortx.processors import (
    ModelAggregator,
    GradientProcessor,
    PrivacyGuard
)
from vortx.optimization import (
    FederatedOptimizer,
    CommunicationOptimizer,
    ResourceOptimizer
)
from vortx.security import (
    DifferentialPrivacy,
    SecureAggregation
)
from vortx.sustainability import (
    EnergyMonitor,
    CommunicationMonitor
)

class SimpleModel(nn.Module):
    """Simple neural network for demonstration."""
    def __init__(self, input_size=784, hidden_size=128, output_size=10):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
    
    def forward(self, x):
        return self.network(x)

class FederatedLearningSystem:
    """Federated learning system with AGI memory integration."""
    
    def __init__(self, system, num_clients=10):
        self.system = system
        self.num_clients = num_clients
        
        # Initialize memory components
        self.federated = FederatedMemory(system)
        self.model = ModelMemory(system)
        self.gradient = GradientMemory(system)
        
        # Initialize processors
        self.aggregator = ModelAggregator()
        self.gradient_processor = GradientProcessor()
        self.privacy_guard = PrivacyGuard()
        
        # Initialize optimizers
        self.fed_optimizer = FederatedOptimizer()
        self.comm_optimizer = CommunicationOptimizer()
        self.resource_optimizer = ResourceOptimizer()
        
        # Initialize security components
        self.diff_privacy = DifferentialPrivacy()
        self.secure_agg = SecureAggregation()
        
        # Initialize monitoring
        self.energy_monitor = EnergyMonitor(system)
        self.comm_monitor = CommunicationMonitor(system)
        
        # Configure system parameters
        self.config = {
            "rounds": 100,
            "local_epochs": 5,
            "batch_size": 32,
            "learning_rate": 0.01,
            "privacy_budget": 1.0,
            "communication_threshold": 1e-3
        }
        
        # Initialize global model
        self.global_model = SimpleModel()
        self.save_global_model()
    
    def save_global_model(self):
        """Save global model state."""
        model_id = self.model.store(
            data={
                "state_dict": self.global_model.state_dict(),
                "architecture": "simple_nn"
            },
            context={
                "timestamp": datetime.now(),
                "version": "global"
            }
        )
        return model_id
    
    async def train_client(self, client_id: int, data: torch.Tensor,
                          labels: torch.Tensor):
        """Train model on client data."""
        # Get global model
        local_model = SimpleModel()
        local_model.load_state_dict(self.global_model.state_dict())
        
        # Setup training
        optimizer = optim.SGD(
            local_model.parameters(),
            lr=self.config["learning_rate"]
        )
        criterion = nn.CrossEntropyLoss()
        
        # Local training
        for epoch in range(self.config["local_epochs"]):
            for i in range(0, len(data), self.config["batch_size"]):
                batch_data = data[i:i + self.config["batch_size"]]
                batch_labels = labels[i:i + self.config["batch_size"]]
                
                optimizer.zero_grad()
                outputs = local_model(batch_data)
                loss = criterion(outputs, batch_labels)
                loss.backward()
                optimizer.step()
        
        # Compute gradients
        gradients = {}
        for name, param in local_model.named_parameters():
            gradients[name] = param.grad.clone()
        
        # Apply differential privacy
        private_gradients = self.diff_privacy.apply(
            gradients,
            epsilon=self.config["privacy_budget"]
        )
        
        # Store gradients
        gradient_id = self.gradient.store(
            data={
                "gradients": private_gradients,
                "client_id": client_id
            },
            context={
                "timestamp": datetime.now(),
                "round": self.current_round
            }
        )
        
        return gradient_id, loss.item()
    
    async def aggregate_gradients(self, gradient_ids: List[str]):
        """Aggregate gradients from clients."""
        # Collect gradients
        gradients = []
        for grad_id in gradient_ids:
            grad_data = self.gradient.get(grad_id)
            gradients.append(grad_data["gradients"])
        
        # Secure aggregation
        secure_gradients = self.secure_agg.aggregate(gradients)
        
        # Process and apply gradients
        processed_gradients = self.gradient_processor.process(
            secure_gradients,
            threshold=self.config["communication_threshold"]
        )
        
        # Update global model
        for name, param in self.global_model.named_parameters():
            if name in processed_gradients:
                param.data.add_(processed_gradients[name])
        
        # Save updated model
        return self.save_global_model()
    
    async def train_federated(self, data: List[torch.Tensor],
                            labels: List[torch.Tensor]):
        """Run federated training process."""
        self.current_round = 0
        training_stats = []
        
        for round in range(self.config["rounds"]):
            self.current_round = round
            print(f"\nFederated Round {round + 1}/{self.config['rounds']}")
            
            # Train on each client
            gradient_ids = []
            round_losses = []
            
            for client_id in range(self.num_clients):
                gradient_id, loss = await self.train_client(
                    client_id,
                    data[client_id],
                    labels[client_id]
                )
                gradient_ids.append(gradient_id)
                round_losses.append(loss)
            
            # Aggregate results
            model_id = await self.aggregate_gradients(gradient_ids)
            
            # Optimize communication
            self.comm_optimizer.optimize(
                round_stats={
                    "gradients": len(gradient_ids),
                    "model_size": self.model.get_size(model_id)
                }
            )
            
            # Store round statistics
            stats = {
                "round": round,
                "average_loss": np.mean(round_losses),
                "model_id": model_id,
                "gradient_ids": gradient_ids,
                "timestamp": datetime.now()
            }
            training_stats.append(stats)
            
            # Print progress
            print(f"Average Loss: {stats['average_loss']:.4f}")
            
            # Get sustainability metrics
            energy_metrics = self.energy_monitor.get_metrics()
            comm_metrics = self.comm_monitor.get_metrics()
            
            print("\nSustainability Metrics:")
            for key, value in energy_metrics.items():
                print(f"  {key}: {value}")
            
            print("\nCommunication Metrics:")
            for key, value in comm_metrics.items():
                print(f"  {key}: {value}")
        
        return training_stats

def generate_sample_data(num_clients: int = 10):
    """Generate sample data for federated learning."""
    # Generate synthetic data for each client
    data = []
    labels = []
    
    for _ in range(num_clients):
        # Generate random data (MNIST-like)
        client_data = torch.randn(1000, 784)  # 1000 samples per client
        client_labels = torch.randint(0, 10, (1000,))  # 10 classes
        
        data.append(client_data)
        labels.append(client_labels)
    
    return data, labels

async def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "federated_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Create federated learning system
    fed_system = FederatedLearningSystem(system, num_clients=10)
    
    try:
        print("Starting federated learning...")
        
        # Generate sample data
        print("\nGenerating sample data...")
        data, labels = generate_sample_data(num_clients=10)
        
        # Run federated training
        training_stats = await fed_system.train_federated(data, labels)
        
        # Print final results
        print("\nTraining Complete!")
        print(f"Final Loss: {training_stats[-1]['average_loss']:.4f}")
        
        # Get final metrics
        energy_metrics = fed_system.energy_monitor.get_metrics()
        comm_metrics = fed_system.comm_monitor.get_metrics()
        
        print("\nFinal Sustainability Metrics:")
        for key, value in energy_metrics.items():
            print(f"  {key}: {value}")
        
        print("\nFinal Communication Metrics:")
        for key, value in comm_metrics.items():
            print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"\nError during training: {str(e)}")
    
    finally:
        # Cleanup
        system.cleanup()
        print("\nFederated learning completed")

if __name__ == "__main__":
    asyncio.run(main()) 