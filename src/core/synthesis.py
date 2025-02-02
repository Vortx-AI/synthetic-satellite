"""Knowledge synthesis module for combining and analyzing data"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from datetime import datetime
from pathlib import Path
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import xarray as xr
import pandas as pd

from ..core.memory import MemorySystem

class KnowledgeSynthesis:
    """Knowledge synthesis and reasoning system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.memory = MemorySystem(config)
        self.scaler = StandardScaler()
    
    def synthesize(self,
                  data_sources: List[Dict[str, Any]],
                  parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize knowledge from multiple data sources"""
        try:
            # Extract features from each data source
            features = []
            metadata = []
            
            for source in data_sources:
                source_features, source_metadata = self._extract_features(source)
                features.append(source_features)
                metadata.append(source_metadata)
            
            # Combine features
            combined_features = np.concatenate(features, axis=1)
            
            # Scale features
            scaled_features = self.scaler.fit_transform(combined_features)
            
            # Analyze patterns
            patterns = self._analyze_patterns(scaled_features, parameters)
            
            # Generate insights
            insights = self._generate_insights(patterns, metadata)
            
            # Store results in memory
            result = {
                "patterns": patterns,
                "insights": insights,
                "metadata": {
                    "sources": metadata,
                    "parameters": parameters,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            memory_id = self.memory.store(
                data=result,
                metadata={
                    "type": "synthesis",
                    "sources": len(data_sources),
                    "parameters": parameters
                }
            )
            
            result["memory_id"] = memory_id
            return result
            
        except Exception as e:
            self.logger.error(f"Error in knowledge synthesis: {e}")
            raise
    
    def _extract_features(self,
                         data_source: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Extract features from a data source"""
        try:
            if data_source["type"] == "raster":
                return self._extract_raster_features(data_source)
            elif data_source["type"] == "vector":
                return self._extract_vector_features(data_source)
            elif data_source["type"] == "timeseries":
                return self._extract_timeseries_features(data_source)
            else:
                raise ValueError(f"Unknown data source type: {data_source['type']}")
                
        except Exception as e:
            self.logger.error(f"Error extracting features: {e}")
            raise
    
    def _extract_raster_features(self,
                               data_source: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Extract features from raster data"""
        data = np.load(data_source["path"])
        
        # Calculate statistical features
        features = np.array([
            data.mean(axis=(0, 1)),
            data.std(axis=(0, 1)),
            data.min(axis=(0, 1)),
            data.max(axis=(0, 1))
        ]).T
        
        metadata = {
            "type": "raster",
            "shape": data.shape,
            "bands": data_source.get("bands", [f"band_{i}" for i in range(data.shape[-1])])
        }
        
        return features, metadata
    
    def _extract_vector_features(self,
                               data_source: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Extract features from vector data"""
        df = pd.read_parquet(data_source["path"])
        
        # Calculate statistical features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        features = np.array([
            df[numeric_cols].mean(),
            df[numeric_cols].std(),
            df[numeric_cols].min(),
            df[numeric_cols].max()
        ]).T
        
        metadata = {
            "type": "vector",
            "columns": list(numeric_cols),
            "rows": len(df)
        }
        
        return features, metadata
    
    def _extract_timeseries_features(self,
                                   data_source: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Extract features from time series data"""
        ds = xr.open_dataset(data_source["path"])
        
        # Calculate temporal features
        features = []
        for var in ds.data_vars:
            data = ds[var].values
            # Flatten percentiles into separate features
            features.extend([
                data.mean(),
                data.std(),
                data.min(),
                data.max(),
                np.percentile(data, 25),  # Split percentiles into separate values
                np.percentile(data, 50),
                np.percentile(data, 75)
            ])
        
        metadata = {
            "type": "timeseries",
            "variables": list(ds.data_vars),
            "time_range": [str(ds.time[0].values), str(ds.time[-1].values)]
        }
        
        # Convert features to 2D array
        features_array = np.array(features, dtype=np.float32).reshape(-1, 1)
        return features_array, metadata
    
    def _analyze_patterns(self,
                         features: np.ndarray,
                         parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in the combined features"""
        # Train a random forest to identify feature importance
        rf = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        
        # Use first feature as target (can be modified based on use case)
        X = features[:, 1:]
        y = features[:, 0]
        
        rf.fit(X, y)
        
        # Get feature importance
        importance = rf.feature_importances_
        
        # Identify clusters
        from sklearn.cluster import KMeans
        kmeans = KMeans(
            n_clusters=parameters.get("n_clusters", 3),
            random_state=42
        )
        clusters = kmeans.fit_predict(features)
        
        return {
            "feature_importance": importance.tolist(),
            "clusters": clusters.tolist(),
            "cluster_centers": kmeans.cluster_centers_.tolist()
        }
    
    def _generate_insights(self,
                          patterns: Dict[str, Any],
                          metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate insights from patterns"""
        insights = []
        
        # Analyze feature importance
        top_features = np.argsort(patterns["feature_importance"])[-3:]
        insights.append({
            "type": "feature_importance",
            "description": "Top 3 most important features identified",
            "features": top_features.tolist()
        })
        
        # Analyze clusters
        cluster_sizes = np.bincount(patterns["clusters"])
        insights.append({
            "type": "clustering",
            "description": "Data cluster analysis",
            "cluster_sizes": cluster_sizes.tolist()
        })
        
        # Generate temporal insights if time series data present
        if any(m["type"] == "timeseries" for m in metadata):
            insights.append({
                "type": "temporal",
                "description": "Temporal pattern analysis",
                "time_ranges": [
                    m["time_range"] for m in metadata
                    if m["type"] == "timeseries"
                ]
            })
        
        return insights 