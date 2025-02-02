import torch
import gc
import psutil
import os
import subprocess
from typing import Optional

class GPUMemoryManager:
    @staticmethod
    def reset_gpu():
        """Reset GPU completely"""
        try:
            # Try nvidia-smi reset
            subprocess.run(['nvidia-smi', '--gpu-reset'], check=True)
        except:
            pass
        
        # Set memory allocation strategy
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True,garbage_collection_threshold:0.6'
        torch.cuda.empty_cache()
        gc.collect()
    
    @staticmethod
    def get_free_memory() -> Optional[float]:
        """Get free GPU memory in MB"""
        if torch.cuda.is_available():
            return torch.cuda.get_device_properties(0).total_memory / 1024**2 - torch.cuda.memory_allocated() / 1024**2
        return None
    
    @staticmethod
    def print_memory_stats():
        """Print detailed memory statistics"""
        if torch.cuda.is_available():
            print("\nGPU Memory Statistics:")
            print(f"Total: {torch.cuda.get_device_properties(0).total_memory / 1024**2:.2f} MB")
            print(f"Allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
            print(f"Cached: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")
            print(f"Free: {GPUMemoryManager.get_free_memory():.2f} MB")
    
    @staticmethod
    def force_memory_cleanup():
        """Aggressive memory cleanup"""
        # Delete all tensors
        for obj in gc.get_objects():
            try:
                if torch.is_tensor(obj) or (hasattr(obj, 'data') and torch.is_tensor(obj.data)):
                    del obj
            except:
                pass
        
        # Multiple rounds of cleanup
        for _ in range(3):
            gc.collect()
            torch.cuda.empty_cache()
        
        torch.cuda.reset_peak_memory_stats()