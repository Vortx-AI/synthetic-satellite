def get_content():
    """Return content for advanced machine learning notebook"""
    return [
        {
            "title": "Neural Memory Architectures",
            "description": """
            Implement advanced neural architectures for memory processing.
            This section covers:
            - Memory Networks
            - Attention Mechanisms
            - Transformer Models
            - Neural Memory Operations
            """,
            "code": """
            # Define memory network architecture
            class AdvancedMemoryNetwork(nn.Module):
                def __init__(self, input_dim=256, hidden_dim=512, num_layers=6, num_heads=8):
                    super().__init__()
                    
                    # Embedding layer
                    self.embedding = nn.Linear(input_dim, hidden_dim)
                    
                    # Transformer layers
                    encoder_layer = nn.TransformerEncoderLayer(
                        d_model=hidden_dim,
                        nhead=num_heads,
                        dim_feedforward=hidden_dim*4,
                        dropout=0.1,
                        activation='gelu'
                    )
                    self.transformer = nn.TransformerEncoder(
                        encoder_layer,
                        num_layers=num_layers,
                        norm=nn.LayerNorm(hidden_dim)
                    )
                    
                    # Memory readout
                    self.readout = nn.Sequential(
                        nn.Linear(hidden_dim, hidden_dim),
                        nn.GELU(),
                        nn.Dropout(0.1),
                        nn.Linear(hidden_dim, input_dim)
                    )
                    
                def forward(self, x, mask=None):
                    # x shape: (batch_size, sequence_length, input_dim)
                    embedded = self.embedding(x)
                    transformed = self.transformer(
                        embedded.transpose(0, 1),
                        src_key_padding_mask=mask
                    ).transpose(0, 1)
                    output = self.readout(transformed)
                    return output

            # Initialize network
            memory_net = AdvancedMemoryNetwork().to(device)
            print(memory_net)

            # Generate sample data
            def generate_memory_data(n_samples=1000):
                x = torch.randn(n_samples, 10, 256)  # (batch_size, sequence_length, features)
                y = torch.randn(n_samples, 10, 256)  # Target memories
                return x, y

            # Create data loaders
            train_x, train_y = generate_memory_data(1000)
            val_x, val_y = generate_memory_data(200)

            train_loader = DataLoader(
                list(zip(train_x, train_y)),
                batch_size=32,
                shuffle=True,
                num_workers=4
            )
            val_loader = DataLoader(
                list(zip(val_x, val_y)),
                batch_size=32,
                num_workers=4
            )

            # Training configuration
            optimizer = optim.AdamW(
                memory_net.parameters(),
                lr=0.001,
                weight_decay=0.01
            )
            criterion = nn.MSELoss()
            scheduler = optim.lr_scheduler.CosineAnnealingLR(
                optimizer,
                T_max=10,
                eta_min=1e-5
            )

            # Training loop
            def train_epoch(model, loader, optimizer, criterion):
                model.train()
                total_loss = 0
                
                for x, y in loader:
                    x, y = x.to(device), y.to(device)
                    optimizer.zero_grad()
                    
                    output = model(x)
                    loss = criterion(output, y)
                    
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
                    
                    total_loss += loss.item()
                
                return total_loss / len(loader)

            # Train model
            n_epochs = 10
            train_losses = []
            val_losses = []

            for epoch in range(n_epochs):
                train_loss = train_epoch(memory_net, train_loader, optimizer, criterion)
                train_losses.append(train_loss)
                
                # Validation
                memory_net.eval()
                with torch.no_grad():
                    val_loss = sum(criterion(memory_net(x.to(device)), y.to(device)).item()
                                for x, y in val_loader) / len(val_loader)
                val_losses.append(val_loss)
                
                # Update learning rate
                scheduler.step()
                
                print(f'Epoch {epoch+1}: Train Loss = {train_loss:.4f}, Val Loss = {val_loss:.4f}')

            # Plot training progress
            plt.figure(figsize=(10, 6))
            plt.plot(train_losses, label='Train Loss')
            plt.plot(val_losses, label='Validation Loss')
            plt.xlabel('Epoch')
            plt.ylabel('Loss')
            plt.title('Training Progress')
            plt.legend()
            plt.grid(True)
            plt.show()
            """
        },
        {
            "title": "Feature Engineering",
            "description": """
            Implement advanced feature extraction and embedding techniques.
            This section demonstrates:
            - Memory Embeddings
            - Temporal Features
            - Cognitive Attributes
            - Feature Fusion
            """,
            "code": """
            # Initialize feature extractors
            feature_extractor = MemoryFeatureExtractor()
            temporal_encoder = TemporalEncoder()
            cognitive_embedding = CognitiveEmbedding()

            # Generate sample memory data
            def generate_complex_memory_data(n_samples=1000):
                return {
                    'content': np.random.randn(n_samples, 512),  # Raw memory content
                    'temporal': pd.date_range('2024-01-01', periods=n_samples, freq='H'),
                    'metadata': {
                        'importance': np.random.uniform(0, 1, n_samples),
                        'complexity': np.random.uniform(0, 1, n_samples),
                        'context': np.random.randint(0, 10, n_samples)
                    }
                }

            # Generate and process data
            memory_data = generate_complex_memory_data()

            # Extract features
            content_features = feature_extractor.extract_features(
                memory_data['content'],
                method='deep',
                layers=['low', 'mid', 'high']
            )
            
            temporal_features = temporal_encoder.encode_temporal(
                memory_data['temporal'],
                resolution='1h',
                window_size=24
            )
            
            cognitive_features = cognitive_embedding.embed_memories(
                memory_data,
                embedding_dim=256,
                context_window=5
            )

            # Visualize feature distributions
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))

            # Content features
            axes[0].hist(content_features[:, 0], bins=50, density=True)
            axes[0].set_title('Content Feature Distribution')
            axes[0].set_xlabel('Feature Value')
            axes[0].set_ylabel('Density')

            # Temporal features
            axes[1].hist(temporal_features[:, 0], bins=50, density=True)
            axes[1].set_title('Temporal Feature Distribution')
            axes[1].set_xlabel('Feature Value')

            # Cognitive features
            axes[2].hist(cognitive_features[:, 0], bins=50, density=True)
            axes[2].set_title('Cognitive Feature Distribution')
            axes[2].set_xlabel('Feature Value')

            plt.tight_layout()
            plt.show()

            # Feature correlation analysis
            combined_features = np.hstack([
                content_features[:, :5],
                temporal_features[:, :5],
                cognitive_features[:, :5]
            ])

            plt.figure(figsize=(10, 8))
            sns.heatmap(
                pd.DataFrame(combined_features).corr(),
                annot=True,
                cmap='coolwarm',
                center=0,
                vmin=-1,
                vmax=1
            )
            plt.title('Feature Correlation Matrix')
            plt.show()
            """
        },
        {
            "title": "Advanced Learning Techniques",
            "description": """
            Implement memory consolidation and transfer learning.
            This section covers:
            - Memory Consolidation
            - Transfer Learning
            - Meta-Learning
            - Continual Learning
            """,
            "code": """
            # Initialize learning components
            transfer_learner = CognitiveTransfer()
            meta_learner = MetaLearner()

            # Define meta-learning task
            class MemoryConsolidationTask:
                def __init__(self, n_tasks=10, n_samples_per_task=100):
                    self.tasks = [
                        generate_complex_memory_data(n_samples_per_task)
                        for _ in range(n_tasks)
                    ]
                
                def sample_task(self):
                    return np.random.choice(self.tasks)

            # Create tasks
            consolidation_tasks = MemoryConsolidationTask()

            # Train meta-learner
            meta_results = meta_learner.train(
                tasks=consolidation_tasks,
                n_epochs=100,
                n_inner_steps=5,
                learning_rate=0.01,
                meta_batch_size=4
            )

            # Perform transfer learning
            transfer_results = transfer_learner.transfer_knowledge(
                source_data=memory_data,
                target_data=generate_complex_memory_data(500),
                n_epochs=50,
                adaptation_rate=0.1
            )

            # Visualize learning progress
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

            # Meta-learning progress
            ax1.plot(meta_results['train_loss'], label='Train')
            ax1.plot(meta_results['val_loss'], label='Validation')
            ax1.set_title('Meta-Learning Progress')
            ax1.set_xlabel('Iteration')
            ax1.set_ylabel('Loss')
            ax1.legend()
            ax1.grid(True)

            # Transfer learning progress
            ax2.plot(transfer_results['source_performance'], label='Source')
            ax2.plot(transfer_results['target_performance'], label='Target')
            ax2.set_title('Transfer Learning Progress')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Performance')
            ax2.legend()
            ax2.grid(True)

            plt.tight_layout()
            plt.show()
            """
        }
    ] 