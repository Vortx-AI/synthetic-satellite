"""
Climate Analysis with Vortx Earth Memory System
============================================

This example demonstrates advanced climate analysis capabilities using the Vortx Earth Memory System.
It showcases:
1. Loading and processing climate data
2. Temperature trend analysis
3. Extreme weather event detection
4. Climate pattern visualization
5. Predictive modeling

Author: Vortx Team
License: MIT
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

from vortx import EarthMemorySystem
from vortx.utils import setup_environment, ClimateDataLoader
from vortx.analysis import ClimateAnalyzer
from vortx.viz import ClimateVisualizer
from vortx.models import ClimatePredictor

class ClimateAnalysisExample:
    def __init__(self):
        """Initialize the climate analysis example."""
        self.system = self._setup_system()
        self.analyzer = ClimateAnalyzer()
        self.visualizer = ClimateVisualizer()
        self.predictor = ClimatePredictor()
        
    def _setup_system(self):
        """Configure the Earth Memory System for climate analysis."""
        setup_environment(
            api_key=os.getenv("VORTX_API_KEY", "demo-key"),
            log_level="INFO"
        )
        
        return EarthMemorySystem(
            memory_config={
                "compression_level": "high",
                "cache_size": "4GB",
                "precision": "float32"
            },
            compute_config={
                "device": "auto",
                "num_threads": -1,
                "optimize_memory": True
            }
        )
    
    def load_climate_data(self):
        """Load historical climate data for analysis."""
        loader = ClimateDataLoader()
        
        # Load temperature, precipitation, and weather events data
        climate_data = loader.load_climate_data(
            variables=["temperature", "precipitation", "pressure"],
            region="north_america",
            time_range=["2000-01-01", "2024-01-01"],
            resolution="daily"
        )
        
        # Load extreme weather events
        events_data = loader.load_weather_events(
            event_types=["hurricane", "drought", "flood"],
            region="north_america",
            time_range=["2000-01-01", "2024-01-01"]
        )
        
        return climate_data, events_data
    
    def analyze_temperature_trends(self, climate_data):
        """Analyze long-term temperature trends."""
        return self.analyzer.analyze_temperature(
            data=climate_data,
            analysis_types=[
                "trend",
                "seasonality",
                "anomalies"
            ],
            baseline_period=["2000-01-01", "2010-01-01"]
        )
    
    def detect_extreme_events(self, climate_data, events_data):
        """Detect and analyze extreme weather events."""
        # Configure detection parameters
        detection_params = {
            "temperature_threshold": 95,  # 95th percentile
            "precipitation_threshold": 90,  # 90th percentile
            "min_duration": "3D",
            "spatial_extent": "100km"
        }
        
        # Detect events
        detected_events = self.analyzer.detect_extreme_events(
            climate_data=climate_data,
            known_events=events_data,
            params=detection_params
        )
        
        return detected_events
    
    def predict_climate_patterns(self, climate_data, forecast_horizon="1Y"):
        """Predict future climate patterns."""
        return self.predictor.forecast_climate(
            historical_data=climate_data,
            horizon=forecast_horizon,
            variables=["temperature", "precipitation"],
            uncertainty=True
        )
    
    def visualize_analysis(self, temp_trends, events, predictions):
        """Create comprehensive visualizations of the analysis results."""
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Temperature Trends
        ax1 = plt.subplot(3, 2, 1)
        self.visualizer.plot_temperature_trends(
            trends=temp_trends,
            ax=ax1,
            include_confidence=True
        )
        
        # 2. Temperature Anomalies
        ax2 = plt.subplot(3, 2, 2)
        self.visualizer.plot_anomalies(
            anomalies=temp_trends["anomalies"],
            ax=ax2,
            cmap="RdBu_r"
        )
        
        # 3. Extreme Events Timeline
        ax3 = plt.subplot(3, 2, (3, 4))
        self.visualizer.plot_event_timeline(
            events=events,
            ax=ax3,
            include_intensity=True
        )
        
        # 4. Climate Predictions
        ax4 = plt.subplot(3, 2, 5)
        self.visualizer.plot_predictions(
            predictions=predictions,
            variable="temperature",
            ax=ax4,
            include_uncertainty=True
        )
        
        # 5. Prediction Uncertainty
        ax5 = plt.subplot(3, 2, 6)
        self.visualizer.plot_prediction_uncertainty(
            predictions=predictions,
            ax=ax5,
            include_scenarios=True
        )
        
        plt.tight_layout()
        return fig
    
    def run_analysis(self):
        """Execute the complete climate analysis workflow."""
        try:
            # 1. Load Data
            print("Loading climate data...")
            climate_data, events_data = self.load_climate_data()
            
            # 2. Analyze Temperature Trends
            print("Analyzing temperature trends...")
            temp_trends = self.analyze_temperature_trends(climate_data)
            
            # 3. Detect Extreme Events
            print("Detecting extreme events...")
            detected_events = self.detect_extreme_events(climate_data, events_data)
            
            # 4. Predict Future Patterns
            print("Predicting future patterns...")
            predictions = self.predict_climate_patterns(climate_data)
            
            # 5. Visualize Results
            print("Creating visualizations...")
            fig = self.visualize_analysis(temp_trends, detected_events, predictions)
            
            # Save results
            output_dir = "examples/output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save visualization
            fig.savefig(f"{output_dir}/climate_analysis_results.png")
            print(f"Results saved to {output_dir}/climate_analysis_results.png")
            
            # Save numerical results
            results = {
                "temperature_trends": temp_trends,
                "extreme_events": detected_events,
                "predictions": predictions
            }
            
            pd.to_pickle(results, f"{output_dir}/climate_analysis_results.pkl")
            print(f"Analysis results saved to {output_dir}/climate_analysis_results.pkl")
            
            # Print summary statistics
            print("\nAnalysis Summary:")
            print(f"Temperature Trend: {temp_trends['trend_magnitude']:.2f}°C/decade")
            print(f"Extreme Events Detected: {len(detected_events)}")
            print(f"Prediction Confidence: {predictions['confidence_score']:.2%}")
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            raise
        finally:
            # Cleanup
            plt.close('all')
            self.system.cleanup()

def main():
    """Main execution function."""
    analyzer = ClimateAnalysisExample()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 