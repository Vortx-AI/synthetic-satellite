"""Atmospheric correction module for satellite imagery"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime

class AtmosphericCorrection:
    """Handles atmospheric correction of satellite imagery"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def correct_image(self, 
                     data: np.ndarray,
                     metadata: Dict[str, Any],
                     method: str = "dos") -> Tuple[np.ndarray, Dict[str, Any]]:
        """Apply atmospheric correction to image data"""
        self.logger.info(f"Applying {method} atmospheric correction")
        
        if method == "dos":
            return self._dark_object_subtraction(data, metadata)
        elif method == "6s":
            return self._six_s_correction(data, metadata)
        elif method == "modtran":
            return self._modtran_correction(data, metadata)
        else:
            raise ValueError(f"Unknown correction method: {method}")
    
    def _dark_object_subtraction(self, 
                               data: np.ndarray,
                               metadata: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Apply Dark Object Subtraction (DOS) correction"""
        # Find dark objects in each band
        dark_values = np.percentile(data, 1, axis=(0, 1))
        
        # Apply correction
        corrected_data = data - dark_values[None, None, :]
        corrected_data = np.clip(corrected_data, 0, None)
        
        # Update metadata
        metadata.update({
            "atmospheric_correction": {
                "method": "dos",
                "dark_values": dark_values.tolist(),
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return corrected_data, metadata
    
    def _six_s_correction(self,
                         data: np.ndarray,
                         metadata: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Apply 6S (Second Simulation of Satellite Signal in the Solar Spectrum) correction"""
        try:
            from Py6S import SixS, AtmosProfile, AeroProfile, Geometry
            
            # Initialize 6S model
            s = SixS()
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
            s.aero_profile = AeroProfile.Continental
            
            # Set geometry from metadata
            if "sun_azimuth" in metadata and "sun_elevation" in metadata:
                s.geometry = Geometry.User()
                s.geometry.solar_z = 90 - metadata["sun_elevation"]
                s.geometry.solar_a = metadata["sun_azimuth"]
            
            # Apply correction band by band
            corrected_data = np.zeros_like(data, dtype=np.float32)
            coefficients = []
            
            for band in range(data.shape[-1]):
                s.run()
                xa = s.outputs.coef_xa
                xb = s.outputs.coef_xb
                xc = s.outputs.coef_xc
                
                # Apply correction formula
                y = xa * data[:, :, band] - xb
                corrected_data[:, :, band] = y / (1 + xc * y)
                coefficients.append({"xa": xa, "xb": xb, "xc": xc})
            
            # Update metadata
            metadata.update({
                "atmospheric_correction": {
                    "method": "6s",
                    "coefficients": coefficients,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            return corrected_data, metadata
            
        except ImportError:
            self.logger.warning("Py6S not installed. Falling back to DOS correction.")
            return self._dark_object_subtraction(data, metadata)
    
    def _modtran_correction(self,
                          data: np.ndarray,
                          metadata: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Apply MODTRAN-based atmospheric correction"""
        try:
            import modtran
            
            # Initialize MODTRAN parameters
            params = {
                "altitude": metadata.get("altitude", 0),
                "latitude": metadata.get("latitude", 0),
                "longitude": metadata.get("longitude", 0),
                "date": metadata.get("acquisition_date", datetime.now().strftime("%Y-%m-%d")),
                "atmosphere": "midlatitude summer"
            }
            
            # Run MODTRAN simulation
            simulation = modtran.run(params)
            
            # Apply correction
            corrected_data = np.zeros_like(data, dtype=np.float32)
            for band in range(data.shape[-1]):
                transmission = simulation.get_transmission(band)
                path_radiance = simulation.get_path_radiance(band)
                corrected_data[:, :, band] = (data[:, :, band] - path_radiance) / transmission
            
            # Update metadata
            metadata.update({
                "atmospheric_correction": {
                    "method": "modtran",
                    "parameters": params,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            return corrected_data, metadata
            
        except ImportError:
            self.logger.warning("MODTRAN not installed. Falling back to DOS correction.")
            return self._dark_object_subtraction(data, metadata) 