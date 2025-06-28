from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from typing import Optional
from src.domain.dtos.lesion_evaluation_request import LesionEvaluationRequestDTO
from src.domain.dtos.lesion_evaluation_response import LesionEvaluationResponseDTO
from src.domain.interfaces.cough_classifier_service_interface import CoughClassifierServiceInterface
from src.domain.interfaces.dialog_system_service import DialogSystemServiceInterface
from src.infrastructure.services.huggingface_cough_classification import CoughClassificationService
from src.infrastructure.services.gemini_service import GeminiService

router = APIRouter(prefix="/cough", tags=["cough"])

def get_vision_service() -> CoughClassifierServiceInterface:
    """Dependency injection for the image classification service"""
    return CoughClassificationService()

def get_dialog_service() -> DialogSystemServiceInterface:
    """Dependency injection for the dialog service"""
    return GeminiService()

@router.post("/evaluate", response_model=LesionEvaluationResponseDTO)
async def evaluate_cough(
    audio: UploadFile = File(..., description="Cough Audio"),
    description: Optional[str] = Form(None, description="Optional description of the cough symptoms"),
    vision_service: CoughClassifierServiceInterface = Depends(get_vision_service),
    dialog_service: DialogSystemServiceInterface = Depends(get_dialog_service)
) -> LesionEvaluationResponseDTO:
    """
    Evaluate a dermatological lesion using image classification and medical advice
    
    Args:
        audio: Lesion image
        description: Optional description of the lesion
        vision_service: Image classification service
        dialog_service: Dialog service for medical advice
        
    Returns:
        LesionEvaluationResponseDTO: Classification and medical advice
    """
    try:
        classification = await vision_service.classify_audio(audio, description)
        
        system_prompt = """You are an expert medical assistant specialized in analyzing cough sounds. Based on the classification of a cough audio sample, 
        provide professional, clear, and useful medical guidance. Address the following:
        - Whether the cough is likely associated with COVID-19, general symptoms, or is normal
        - Whether medical consultation is advised
        - Possible causes or conditions related to the detected cough type
        - Recommendations for monitoring symptoms or seeking care
        - A reminder that this is not a medical diagnosis, but an AI-based assessment to support decision-making

        Respond with clarity and empathy for the patient."""

        user_prompt = f"""
        Cough classification: {classification}

        Additional patient description: {description or 'Not provided'}

        Please provide medical advice based on this information.
        """

        medical_advice = await dialog_service.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=f"Classification: {classification}"
        )
        
        return LesionEvaluationResponseDTO(
            classification=classification,
            medical_advice=medical_advice
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating lesion: {str(e)}"
        ) 