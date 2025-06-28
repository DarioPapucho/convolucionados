from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from typing import Optional
from src.domain.dtos.lesion_evaluation_request import LesionEvaluationRequestDTO
from src.domain.dtos.lesion_evaluation_response import LesionEvaluationResponseDTO
from src.domain.interfaces.cough_classifier_service_interface import CoughClassifierServiceInterface
from src.domain.interfaces.dialog_system_service import DialogSystemServiceInterface
from src.infrastructure.services.huggingface_cough_classification import CoughClassificationService
from src.infrastructure.services.gemini_service import GeminiService

router = APIRouter(prefix="/cough", tags=["Cough"])

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
        
        system_prompt = """Eres un asistente médico experto en el análisis de sonidos de tos. Tu función es ofrecer orientación médica clara, útil y profesional 
        basada en la clasificación de una muestra de tos. Solo puedes responder sobre los siguientes tres casos: COVID-19, tos normal o tos con síntomas (sintomática).
        No debes mencionar ni diagnosticar otras enfermedades o condiciones.

        Debes abordar exclusivamente lo siguiente:
        - Si la tos está posiblemente asociada a COVID-19, si presenta síntomas generales (sintomática), o si se trata de una tos normal
        - Si es recomendable acudir a una consulta médica
        - Posibles causas o condiciones relacionadas con uno de los tres tipos de tos permitidos
        - Recomendaciones para observar la evolución, monitorear síntomas o buscar atención
        - Un recordatorio claro de que esto no es un diagnóstico médico, sino una evaluación basada en inteligencia artificial para apoyar la toma de decisiones

        Responde con empatía, sencillez y precisión. Nunca inventes o especules fuera de los tres casos definidos."""

        user_prompt = f"""
        Clasificación de la tos: {classification}

        Descripción adicional del paciente: {description or 'No proporcionada'}

        Por favor, proporciona una orientación médica basada en esta información.
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