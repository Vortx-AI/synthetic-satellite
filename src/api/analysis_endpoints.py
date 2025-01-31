"""Basic analysis endpoints for the Vortx API"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import numpy as np
from pathlib import Path
import tempfile
import shutil

from ..core.processor import Processor
from ..utils.satellite_utils import setup_logging

router = APIRouter()

class ProcessingRequest(BaseModel):
    input_path: str
    output_path: str
    parameters: Dict[str, Any]

class ProcessingResponse(BaseModel):
    status: str
    output_path: str
    metadata: Dict[str, Any]

@router.post("/process", response_model=ProcessingResponse)
async def process_data(request: ProcessingRequest):
    """Process satellite data with basic analysis"""
    try:
        processor = Processor()
        result = processor.process_file(
            Path(request.input_path),
            Path(request.output_path),
            **request.parameters
        )
        
        return ProcessingResponse(
            status="success",
            output_path=request.output_path,
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for processing"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        return {
            "filename": file.filename,
            "temp_path": temp_path,
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/parameters")
async def get_parameters():
    """Get available processing parameters"""
    return {
        "parameters": {
            "preprocessing": [
                "radiometric_correction",
                "atmospheric_correction",
                "cloud_masking"
            ],
            "analysis": [
                "ndvi",
                "ndwi",
                "savi"
            ],
            "output_formats": [
                "GeoTIFF",
                "COG",
                "PNG"
            ]
        }
    } 