from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from typing import Optional
from src.domain.dtos.lesion_evaluation_request import LesionEvaluationRequestDTO
from src.domain.dtos.lesion_evaluation_response import LesionEvaluationResponseDTO
from src.domain.interfaces.vision_classifier_service_interface import VisionClassifierServiceInterface
from src.domain.interfaces.dialog_system_service import DialogSystemServiceInterface
from src.infrastructure.services.huggingface_dental_service import HuggingFaceDentalService
from src.infrastructure.services.gemini_service import GeminiService

router = APIRouter(prefix="/dental", tags=["Dental"])

def get_vision_service() -> VisionClassifierServiceInterface:
    """Dependency injection for the dental image classification service"""
    return HuggingFaceDentalService()

def get_dialog_service() -> DialogSystemServiceInterface:
    """Dependency injection for the dental advice dialog system"""
    return GeminiService()

@router.post("/evaluate", response_model=LesionEvaluationResponseDTO)
async def evaluate_dental_condition(
    image: UploadFile = File(..., description="Oral or dental image (e.g., X-ray, intraoral photo)"),
    description: Optional[str] = Form(None, description="Optional description of the patient’s symptoms"),
    vision_service: VisionClassifierServiceInterface = Depends(get_vision_service),
    dialog_service: DialogSystemServiceInterface = Depends(get_dialog_service)
) -> LesionEvaluationResponseDTO:
    """
    Evaluate an oral or dental condition using image classification and expert medical advice.
    
    Args:
        image: Image of the oral cavity or dental structure
        description: Optional patient-provided description or symptoms
        vision_service: Dental image classification service
        dialog_service: Dialog system for expert dental guidance
    
    Returns:
        LesionEvaluationResponseDTO: Dental condition and advice
    """
    try:
        # Step 1: Classify the dental condition
        classification = await vision_service.classify_image(image, description)
        
        system_prompt = """Eres un dentista experto. Basado en una clasificación preliminar de una posible condición dental u oral, 
        brinda consejos profesionales, claros y útiles. Tu objetivo es orientar al paciente, pero siempre dejando en claro que este análisis es solo una guía inicial y no reemplaza una consulta médica.

        Incluye en tu respuesta:
        - Una recomendación clara de acudir al dentista u odontólogo, explicando por qué es importante una revisión presencial
        - Posibles tratamientos que un profesional podría sugerir (como conducto, extracción, restauración), sin recetar medicamentos ni sugerir automedicación
        - Síntomas comunes relacionados con la condición que podrían empeorar si no se atienden
        - Consejos de prevención e higiene bucal para mantener una buena salud dental

        Usa un tono amigable y sencillo, para que cualquier persona pueda entenderlo fácilmente. Limita tu respuesta a solo dos párrafos. Aclara que esta información es solo orientativa y no reemplaza el diagnóstico profesional.
        """

        user_prompt = f"""
        Clasificación preliminar de la condición dental: {classification}

        Descripción adicional del paciente: {description or 'No proporcionada'}

        Por favor, brinda una orientación dental basada en esta información, recordando que no es un diagnóstico médico definitivo.
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
            detail=f"Error evaluating dental condition: {str(e)}"
        )
