"""
Data Privacy and Encoding with Vortx
==================================

This example demonstrates advanced data privacy and encoding capabilities of the Vortx Earth Memory System.
It showcases:
1. Earth Information Identifier (EII) detection and removal
2. Data encoding and encryption
3. Privacy-preserving analytics
4. Secure memory formation
5. Compliance validation

Author: Vortx Team
License: MIT
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime
from cryptography.fernet import Fernet

from vortx import EarthMemorySystem
from vortx.utils import setup_environment
from vortx.privacy import (
    EIIDetector,
    PrivacyEncoder,
    ComplianceValidator
)
from vortx.security import (
    MemoryEncryptor,
    SecureProcessor
)

class DataPrivacyExample:
    def __init__(self):
        """Initialize the data privacy example."""
        self.system = self._setup_system()
        self.eii_detector = EIIDetector()
        self.privacy_encoder = PrivacyEncoder()
        self.validator = ComplianceValidator()
        self.encryptor = MemoryEncryptor()
        self.processor = SecureProcessor()
        
    def _setup_system(self):
        """Configure the Earth Memory System with privacy settings."""
        setup_environment(
            api_key=os.getenv("VORTX_API_KEY", "demo-key"),
            log_level="INFO",
            privacy_mode="strict"
        )
        
        return EarthMemorySystem(
            memory_config={
                "encryption_level": "high",
                "privacy_preserving": True,
                "secure_processing": True
            },
            security_config={
                "key_rotation": True,
                "audit_logging": True,
                "compliance_check": True
            }
        )
    
    def detect_eii(self, data):
        """Detect Earth Information Identifiers in the data."""
        # Configure detection parameters
        detection_params = {
            "sensitivity": "high",
            "identifiers": [
                "location",
                "timestamp",
                "sensor_id",
                "facility_info",
                "personnel_data"
            ],
            "context_aware": True
        }
        
        # Detect EII
        detected_eii = self.eii_detector.scan(
            data=data,
            params=detection_params
        )
        
        return detected_eii
    
    def encode_data(self, data, detected_eii):
        """Encode data with privacy preservation."""
        encoding_config = {
            "method": "differential_privacy",
            "epsilon": 0.1,  # Privacy budget
            "delta": 1e-5,   # Privacy loss parameter
            "mechanism": "gaussian"
        }
        
        # Encode sensitive information
        encoded_data = self.privacy_encoder.encode(
            data=data,
            eii=detected_eii,
            config=encoding_config
        )
        
        return encoded_data
    
    def create_secure_memory(self, encoded_data):
        """Create secure, privacy-preserving Earth memory."""
        # Configure secure memory parameters
        security_params = {
            "encryption_algorithm": "AES-256-GCM",
            "key_derivation": "PBKDF2HMAC",
            "secure_deletion": True
        }
        
        # Create encrypted memory
        secure_memory = self.encryptor.create_memory(
            data=encoded_data,
            params=security_params
        )
        
        return secure_memory
    
    def validate_compliance(self, secure_memory):
        """Validate compliance with privacy regulations."""
        compliance_checks = [
            "GDPR",
            "CCPA",
            "HIPAA",
            "ISO27001"
        ]
        
        validation_results = self.validator.check_compliance(
            memory=secure_memory,
            standards=compliance_checks
        )
        
        return validation_results
    
    def perform_secure_analysis(self, secure_memory):
        """Perform privacy-preserving analysis on secure memory."""
        analysis_config = {
            "homomorphic_encryption": True,
            "secure_aggregation": True,
            "k_anonymity": 5
        }
        
        # Analyze data securely
        results = self.processor.analyze(
            memory=secure_memory,
            config=analysis_config,
            operations=[
                "aggregate_statistics",
                "pattern_detection",
                "anomaly_analysis"
            ]
        )
        
        return results
    
    def run_privacy_test(self, test_data):
        """Execute complete privacy test workflow."""
        try:
            print("Starting privacy and encoding test...")
            
            # Step 1: Detect EII
            print("Detecting Earth Information Identifiers...")
            detected_eii = self.detect_eii(test_data)
            print(f"Found {len(detected_eii)} potential identifiers")
            
            # Step 2: Encode Data
            print("Encoding sensitive data...")
            encoded_data = self.encode_data(test_data, detected_eii)
            
            # Step 3: Create Secure Memory
            print("Creating secure memory...")
            secure_memory = self.create_secure_memory(encoded_data)
            
            # Step 4: Validate Compliance
            print("Validating compliance...")
            compliance_results = self.validate_compliance(secure_memory)
            
            # Step 5: Perform Secure Analysis
            print("Performing secure analysis...")
            analysis_results = self.perform_secure_analysis(secure_memory)
            
            # Save results
            output_dir = "examples/output/privacy_test"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save compliance report
            compliance_report = pd.DataFrame(compliance_results)
            compliance_report.to_csv(f"{output_dir}/compliance_report.csv")
            
            # Save analysis results (encrypted)
            self.encryptor.save_encrypted(
                data=analysis_results,
                filepath=f"{output_dir}/secure_analysis.enc"
            )
            
            # Print summary
            print("\nPrivacy Test Summary:")
            print(f"EII Detected: {len(detected_eii)}")
            print(f"Encoding Success: {encoded_data['success_rate']:.2%}")
            print(f"Compliance Score: {compliance_results['overall_score']:.2%}")
            print(f"Security Level: {secure_memory.security_rating}")
            
            return {
                "eii_count": len(detected_eii),
                "encoding_rate": encoded_data['success_rate'],
                "compliance_score": compliance_results['overall_score'],
                "security_rating": secure_memory.security_rating
            }
            
        except Exception as e:
            print(f"Error in privacy test: {e}")
            raise
        finally:
            # Secure cleanup
            if 'secure_memory' in locals():
                secure_memory.secure_delete()
            self.system.cleanup()

def generate_test_data():
    """Generate sample test data with synthetic identifiers."""
    np.random.seed(42)
    
    # Generate synthetic Earth observation data
    n_samples = 1000
    test_data = {
        "timestamp": pd.date_range(start="2024-01-01", periods=n_samples, freq="H"),
        "location": [f"SITE_{i:03d}" for i in range(n_samples)],
        "sensor_id": [f"SENSOR_{i:04d}" for i in range(n_samples)],
        "temperature": np.random.normal(25, 5, n_samples),
        "humidity": np.random.normal(60, 10, n_samples),
        "pressure": np.random.normal(1013, 10, n_samples),
        "facility_info": [f"FAC_{i%10:02d}" for i in range(n_samples)],
        "personnel_id": [f"EMP_{i%50:03d}" for i in range(n_samples)]
    }
    
    return pd.DataFrame(test_data)

def main():
    """Main execution function."""
    # Generate test data
    test_data = generate_test_data()
    
    # Run privacy test
    privacy_tester = DataPrivacyExample()
    results = privacy_tester.run_privacy_test(test_data)
    
    # Print results
    print("\nTest Results:")
    for key, value in results.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main() 