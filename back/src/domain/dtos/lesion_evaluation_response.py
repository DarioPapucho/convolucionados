from pydantic import BaseModel, Field

class LesionEvaluationResponseDTO(BaseModel):
    """DTO for dermatological lesion evaluation responses"""
    
    classification: str = Field(..., description="Lesion classification with confidence")
    medical_advice: str = Field(..., description="Medical advice based on classification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "classification": "Melanoma (Confidence: 85%)",
                "medical_advice": "Based on the classification, immediate consultation with a dermatologist is recommended for professional evaluation and possible biopsy."
            }
        } 