#!/usr/bin/env python3
"""
Example demonstrating knowledge graph integration with AGI memory systems.
"""

import os
import numpy as np
import networkx as nx
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

from vortx import AGIMemorySystem
from vortx.utils import setup_environment
from vortx.memory import (
    KnowledgeMemory,
    SemanticMemory,
    RelationalMemory
)
from vortx.processors import (
    KnowledgeProcessor,
    SemanticAnalyzer,
    RelationExtractor
)
from vortx.optimization import (
    GraphOptimizer,
    QueryOptimizer,
    ResourceOptimizer
)
from vortx.visualization import (
    GraphVisualizer,
    KnowledgeMapper
)
from vortx.analytics import (
    PatternMiner,
    InferenceEngine
)
from vortx.sustainability import (
    EnergyMonitor,
    MemoryMonitor
)

class KnowledgeGraphSystem:
    """Knowledge graph system with AGI memory integration."""
    
    def __init__(self, system):
        self.system = system
        
        # Initialize memory components
        self.knowledge = KnowledgeMemory(system)
        self.semantic = SemanticMemory(system)
        self.relational = RelationalMemory(system)
        
        # Initialize processors
        self.knowledge_processor = KnowledgeProcessor()
        self.semantic_analyzer = SemanticAnalyzer()
        self.relation_extractor = RelationExtractor()
        
        # Initialize optimizers
        self.graph_optimizer = GraphOptimizer()
        self.query_optimizer = QueryOptimizer()
        self.resource_optimizer = ResourceOptimizer()
        
        # Initialize visualization
        self.graph_viz = GraphVisualizer()
        self.knowledge_mapper = KnowledgeMapper()
        
        # Initialize analytics
        self.pattern_miner = PatternMiner()
        self.inference_engine = InferenceEngine()
        
        # Initialize monitoring
        self.energy_monitor = EnergyMonitor(system)
        self.memory_monitor = MemoryMonitor(system)
        
        # Initialize graph
        self.graph = nx.DiGraph()
        
        # Configure system parameters
        self.config = {
            "similarity_threshold": 0.8,
            "relation_confidence": 0.7,
            "max_inference_depth": 3,
            "memory_limit": "8GB"
        }
    
    def add_entity(self, entity: Dict):
        """Add entity to knowledge graph."""
        # Process entity
        processed_entity = self.knowledge_processor.process_entity(entity)
        
        # Extract semantic information
        semantics = self.semantic_analyzer.analyze(
            processed_entity,
            threshold=self.config["similarity_threshold"]
        )
        
        # Store in memory
        entity_id = self.knowledge.store_entity(
            data={
                "entity": processed_entity,
                "semantics": semantics
            },
            context={
                "timestamp": datetime.now(),
                "confidence": semantics["confidence"]
            }
        )
        
        # Add to graph
        self.graph.add_node(
            entity_id,
            **processed_entity,
            semantics=semantics
        )
        
        return entity_id
    
    def add_relation(self, source_id: str, target_id: str,
                    relation_type: str, metadata: Optional[Dict] = None):
        """Add relation between entities."""
        # Extract relation
        relation = self.relation_extractor.extract(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            metadata=metadata,
            confidence_threshold=self.config["relation_confidence"]
        )
        
        if relation["confidence"] >= self.config["relation_confidence"]:
            # Store in memory
            relation_id = self.relational.store(
                data=relation,
                context={
                    "timestamp": datetime.now(),
                    "source": source_id,
                    "target": target_id
                }
            )
            
            # Add to graph
            self.graph.add_edge(
                source_id,
                target_id,
                relation_id=relation_id,
                **relation
            )
            
            return relation_id
        return None
    
    def query_knowledge(self, query: Dict):
        """Query knowledge graph."""
        # Optimize query
        optimized_query = self.query_optimizer.optimize(
            query,
            graph=self.graph
        )
        
        # Execute query
        results = self.knowledge.query(
            optimized_query,
            context={
                "timestamp": datetime.now()
            }
        )
        
        return results
    
    def infer_knowledge(self, entity_id: str):
        """Infer new knowledge from existing relations."""
        # Get entity neighborhood
        subgraph = nx.ego_graph(
            self.graph,
            entity_id,
            radius=self.config["max_inference_depth"]
        )
        
        # Run inference
        inferences = self.inference_engine.infer(
            graph=subgraph,
            root_id=entity_id,
            confidence_threshold=self.config["relation_confidence"]
        )
        
        # Store and add new relations
        new_relations = []
        for inference in inferences:
            relation_id = self.add_relation(
                source_id=inference["source"],
                target_id=inference["target"],
                relation_type=inference["type"],
                metadata=inference["metadata"]
            )
            if relation_id:
                new_relations.append(relation_id)
        
        return new_relations
    
    def mine_patterns(self):
        """Mine patterns in knowledge graph."""
        # Find patterns
        patterns = self.pattern_miner.find_patterns(
            graph=self.graph,
            min_support=0.1,
            min_confidence=self.config["relation_confidence"]
        )
        
        # Store patterns
        pattern_ids = []
        for pattern in patterns:
            pattern_id = self.knowledge.store_pattern(
                data=pattern,
                context={
                    "timestamp": datetime.now(),
                    "support": pattern["support"],
                    "confidence": pattern["confidence"]
                }
            )
            pattern_ids.append(pattern_id)
        
        return pattern_ids
    
    def visualize_graph(self, focus_entity_id: Optional[str] = None):
        """Generate visualization of knowledge graph."""
        if focus_entity_id:
            # Visualize neighborhood of focus entity
            subgraph = nx.ego_graph(
                self.graph,
                focus_entity_id,
                radius=2
            )
            return self.graph_viz.visualize(
                graph=subgraph,
                focus_node=focus_entity_id
            )
        else:
            # Visualize entire graph
            return self.graph_viz.visualize(graph=self.graph)
    
    def get_statistics(self):
        """Get knowledge graph statistics."""
        return {
            "num_entities": self.graph.number_of_nodes(),
            "num_relations": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "avg_degree": sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
            "memory_usage": self.memory_monitor.get_usage(),
            "energy_metrics": self.energy_monitor.get_metrics()
        }

def generate_sample_data():
    """Generate sample knowledge graph data."""
    # Sample entities
    entities = [
        {
            "type": "person",
            "name": "Alice Smith",
            "attributes": {
                "age": 30,
                "occupation": "Data Scientist",
                "skills": ["Python", "Machine Learning", "Data Analysis"]
            }
        },
        {
            "type": "organization",
            "name": "Tech Corp",
            "attributes": {
                "industry": "Technology",
                "location": "San Francisco",
                "founded": 2010
            }
        },
        {
            "type": "project",
            "name": "AI Initiative",
            "attributes": {
                "status": "active",
                "start_date": "2023-01-01",
                "technologies": ["Machine Learning", "Neural Networks"]
            }
        }
    ]
    
    # Sample relations
    relations = [
        {
            "source": 0,  # Alice Smith
            "target": 1,  # Tech Corp
            "type": "works_for",
            "metadata": {
                "start_date": "2020-03-15",
                "role": "Senior Data Scientist"
            }
        },
        {
            "source": 0,  # Alice Smith
            "target": 2,  # AI Initiative
            "type": "leads",
            "metadata": {
                "start_date": "2023-01-01",
                "responsibility": "Technical Lead"
            }
        },
        {
            "source": 1,  # Tech Corp
            "target": 2,  # AI Initiative
            "type": "sponsors",
            "metadata": {
                "investment": 1000000,
                "duration": "2 years"
            }
        }
    ]
    
    return entities, relations

def main():
    # Initialize environment
    setup_environment(
        api_key=os.getenv("VORTX_API_KEY", "demo-key"),
        log_level="INFO"
    )
    
    # Create AGI memory system
    system = AGIMemorySystem(
        config={
            "architecture": "knowledge_graph_optimized",
            "sustainability": {
                "enabled": True,
                "mode": "efficient"
            }
        }
    )
    
    # Create knowledge graph system
    kg_system = KnowledgeGraphSystem(system)
    
    try:
        print("Building knowledge graph...")
        
        # Generate sample data
        entities, relations = generate_sample_data()
        
        # Add entities
        print("\nAdding entities...")
        entity_ids = []
        for entity in entities:
            entity_id = kg_system.add_entity(entity)
            entity_ids.append(entity_id)
            print(f"Added entity: {entity['name']}")
        
        # Add relations
        print("\nAdding relations...")
        for relation in relations:
            source_id = entity_ids[relation["source"]]
            target_id = entity_ids[relation["target"]]
            relation_id = kg_system.add_relation(
                source_id,
                target_id,
                relation["type"],
                relation["metadata"]
            )
            if relation_id:
                print(f"Added relation: {relation['type']}")
        
        # Infer new knowledge
        print("\nInferring new knowledge...")
        for entity_id in entity_ids:
            new_relations = kg_system.infer_knowledge(entity_id)
            print(f"Inferred {len(new_relations)} new relations")
        
        # Mine patterns
        print("\nMining patterns...")
        patterns = kg_system.mine_patterns()
        print(f"Found {len(patterns)} patterns")
        
        # Generate visualization
        print("\nGenerating visualization...")
        visualization = kg_system.visualize_graph()
        
        # Print statistics
        stats = kg_system.get_statistics()
        print("\nKnowledge Graph Statistics:")
        print(f"Number of Entities: {stats['num_entities']}")
        print(f"Number of Relations: {stats['num_relations']}")
        print(f"Graph Density: {stats['density']:.4f}")
        print(f"Average Degree: {stats['avg_degree']:.2f}")
        
        print("\nMemory Usage:")
        for key, value in stats["memory_usage"].items():
            print(f"  {key}: {value}")
        
        print("\nSustainability Metrics:")
        for key, value in stats["energy_metrics"].items():
            print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"\nError building knowledge graph: {str(e)}")
    
    finally:
        # Cleanup
        system.cleanup()
        print("\nKnowledge graph processing completed")

if __name__ == "__main__":
    main() 