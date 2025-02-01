"""Advanced analysis endpoints for the Vortx API"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..core.processor import Processor
from ..core.memory import MemorySystem
from ..utils.satellite_utils import setup_logging

router = APIRouter()

class AnalysisRequest(BaseModel):
    data_path: str
    analysis_type: str
    parameters: Dict[str, Any]
    use_memory: bool = True

class AnalysisResponse(BaseModel):
    results: Dict[str, Any]
    metadata: Dict[str, Any]
    memory_id: Optional[str]

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest):
    """Perform advanced analysis on satellite data"""
    try:
        processor = Processor()
        memory = MemorySystem() if request.use_memory else None
        
        # Process the analysis request
        results = processor.analyze(
            data_path=request.data_path,
            analysis_type=request.analysis_type,
            parameters=request.parameters
        )
        
        # Store in memory if requested
        memory_id = None
        if memory and results:
            memory_id = memory.store(
                data=results,
                metadata={
                    "type": "analysis",
                    "analysis_type": request.analysis_type,
                    "parameters": request.parameters
                }
            )
        
        return AnalysisResponse(
            results=results,
            metadata={
                "analysis_type": request.analysis_type,
                "parameters": request.parameters
            },
            memory_id=memory_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis-types")
async def get_analysis_types():
    """Get available analysis types"""
    return {
        "types": [
            {
                "name": "spectral",
                "description": "Spectral analysis of satellite imagery",
                "parameters": ["bands", "indices"]
            },
            {
                "name": "temporal",
                "description": "Time series analysis of satellite data",
                "parameters": ["start_date", "end_date", "interval"]
            },
            {
                "name": "spatial",
                "description": "Spatial pattern analysis",
                "parameters": ["resolution", "patterns"]
            },
            {
                "name": "change_detection",
                "description": "Change detection analysis",
                "parameters": ["baseline_date", "comparison_date"]
            }
        ]
    } 