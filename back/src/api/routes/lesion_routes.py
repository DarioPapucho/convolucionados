from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from typing import Optional
from src.domain.dtos.lesion_evaluation_request import LesionEvaluationRequestDTO
from src.domain.dtos.lesion_evaluation_response import LesionEvaluationResponseDTO
from src.domain.interfaces.vision_classifier_service_interface import VisionClassifierServiceInterface
from src.domain.interfaces.dialog_system_service import DialogSystemServiceInterface
from src.infrastructure.services.huggingface_vision_service import HuggingFaceVisionService
from src.infrastructure.services.gemini_service import GeminiService

router = APIRouter(prefix="/lesion", tags=["lesion"])

def get_vision_service() -> VisionClassifierServiceInterface:
    """Dependency injection for the image classification service"""
    return HuggingFaceVisionService()

def get_dialog_service() -> DialogSystemServiceInterface:
    """Dependency injection for the dialog service"""
    return GeminiService()

@router.post("/evaluate", response_model=LesionEvaluationResponseDTO)
async def evaluate_lesion(
    image: UploadFile = File(..., description="Dermatological lesion image"),
    description: Optional[str] = Form(None, description="Optional description of the lesion"),
    vision_service: VisionClassifierServiceInterface = Depends(get_vision_service),
    dialog_service: DialogSystemServiceInterface = Depends(get_dialog_service)
) -> LesionEvaluationResponseDTO:
    """
    Evaluate a dermatological lesion using image classification and medical advice
    
    Args:
        image: Lesion image
        description: Optional description of the lesion
        vision_service: Image classification service
        dialog_service: Dialog service for medical advice
        
    Returns:
        LesionEvaluationResponseDTO: Classification and medical advice
    """
    try:
        # Step 1: Classify the image
        classification = await vision_service.classify_image(image, description)
        
        # Step 2: Generate medical advice using Gemini
        system_prompt = """You are an expert dermatologist. Based on the classification of a dermatological lesion, 
        provide professional, clear and useful medical advice. Include recommendations on:
        - Whether specialist consultation is necessary
        - Possible treatments
        - Warning signs to watch for
        - Preventive measures
        
        Respond professionally but understandably for the patient."""
        
        user_prompt = f"""
        Lesion classification: {classification}
        
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