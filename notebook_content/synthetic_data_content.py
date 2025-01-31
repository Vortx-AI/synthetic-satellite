def get_content():
    """Return content for synthetic data generation notebook"""
    return [
        {
            "title": "Memory Pattern Architecture",
            "description": """
            Define and implement various memory pattern types and templates for synthetic data generation.
            This section covers:
            - Pattern type definitions
            - Memory templates
            - Cognitive schemas
            - Pattern relationships
            """,
            "code": """
            # Initialize pattern generation components
            template_engine = TemplateEngine()
            schema_builder = SchemaBuilder()

            # Define memory pattern templates
            pattern_templates = {
                'spatial': {
                    'dimensions': 3,
                    'resolution': 'high',
                    'coordinate_system': 'geodetic',
                    'patterns': ['clustering', 'dispersion', 'gradient']
                },
                'temporal': {
                    'sequence_length': 100,
                    'time_resolution': '1s',
                    'causality_preservation': True,
                    'patterns': ['periodic', 'trend', 'anomaly']
                },
                'semantic': {
                    'embedding_dim': 256,
                    'vocabulary_size': 10000,
                    'context_window': 50,
                    'patterns': ['hierarchical', 'associative', 'analogical']
                }
            }

            # Create cognitive schemas
            schemas = schema_builder.build_schemas(pattern_templates)

            # Visualize schema structure
            plt.figure(figsize=(12, 8))
            schema_builder.visualize_schemas(schemas)
            plt.title('Cognitive Schema Architecture')
            plt.show()
            """
        },
        {
            "title": "Advanced Generation Techniques",
            "description": """
            Implement sophisticated memory generation techniques using probabilistic models and neural networks.
            This section demonstrates:
            - Probabilistic memory synthesis
            - Temporal pattern creation
            - Causal chain generation
            - Pattern composition
            """,
            "code": """
            # Initialize generation components
            generator = MemoryGenerator()
            synthesizer = PatternSynthesizer()
            causal_gen = CausalGenerator()

            # Generate synthetic memories
            def generate_synthetic_memories(n_samples=1000):
                # Generate spatial patterns
                spatial_patterns = synthesizer.generate_spatial_patterns(
                    n_samples=n_samples,
                    dimensions=3,
                    distribution='gaussian_mixture',
                    n_clusters=5
                )
                
                # Generate temporal patterns
                temporal_patterns = synthesizer.generate_temporal_patterns(
                    n_samples=n_samples,
                    sequence_length=100,
                    pattern_types=['cyclic', 'trend', 'anomaly'],
                    noise_level=0.1
                )
                
                # Generate causal chains
                causal_chains = causal_gen.generate_causal_chains(
                    n_chains=10,
                    chain_length=5,
                    branching_factor=2,
                    noise_type='gaussian'
                )
                
                return {
                    'spatial': spatial_patterns,
                    'temporal': temporal_patterns,
                    'causal': causal_chains
                }

            # Generate memories
            synthetic_memories = generate_synthetic_memories()

            # Visualize generated patterns
            fig = plt.figure(figsize=(15, 5))
            gs = fig.add_gridspec(1, 3)

            # Spatial patterns
            ax1 = fig.add_subplot(gs[0], projection='3d')
            synthesizer.plot_spatial_patterns(synthetic_memories['spatial'], ax=ax1)
            ax1.set_title('Spatial Patterns')

            # Temporal patterns
            ax2 = fig.add_subplot(gs[1])
            synthesizer.plot_temporal_patterns(synthetic_memories['temporal'], ax=ax2)
            ax2.set_title('Temporal Patterns')

            # Causal chains
            ax3 = fig.add_subplot(gs[2])
            causal_gen.plot_causal_chains(synthetic_memories['causal'], ax=ax3)
            ax3.set_title('Causal Chains')

            plt.tight_layout()
            plt.show()
            """
        },
        {
            "title": "Memory Quality and Validation",
            "description": """
            Implement comprehensive validation and quality assurance for synthetic memories.
            This section covers:
            - Coherence checking
            - Pattern verification
            - Semantic consistency
            - Quality metrics
            """,
            "code": """
            # Initialize validation components
            coherence_checker = CoherenceChecker()
            semantic_validator = SemanticValidator()
            integrity_tester = IntegrityTester()

            # Validate synthetic memories
            def validate_memories(memories):
                # Check coherence
                coherence_scores = coherence_checker.check_coherence(
                    memories,
                    metrics=['spatial', 'temporal', 'causal']
                )
                
                # Validate semantics
                semantic_scores = semantic_validator.validate_semantics(
                    memories,
                    aspects=['consistency', 'relevance', 'completeness']
                )
                
                # Test integrity
                integrity_scores = integrity_tester.test_integrity(
                    memories,
                    tests=['structure', 'relationships', 'constraints']
                )
                
                return {
                    'coherence': coherence_scores,
                    'semantic': semantic_scores,
                    'integrity': integrity_scores
                }

            # Perform validation
            validation_results = validate_memories(synthetic_memories)

            # Visualize validation results
            plt.figure(figsize=(12, 6))
            validation_df = pd.DataFrame(validation_results)

            sns.boxplot(data=validation_df)
            plt.title('Memory Quality Metrics')
            plt.ylabel('Score')
            plt.show()

            # Display summary statistics
            print("\\nValidation Summary:")
            print(validation_df.describe())
            """
        }
    ] 