from typing import Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile

class LesionEvaluationRequestDTO(BaseModel):
    """DTO for dermatological lesion evaluation requests"""
    
    image: UploadFile = Field(..., description="Dermatological lesion image")
    description: Optional[str] = Field(None, description="Optional description of the lesion")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Lesion on right arm, brown color, small size"
            }
        } 