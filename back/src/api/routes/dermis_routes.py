from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Optional
import os
from src.domain.dtos.lesion_evaluation_response import LesionEvaluationResponseDTO
from src.infrastructure.container import Container
from src.infrastructure.services.dermis_service import DermisService
from io import BytesIO
from src.infrastructure.services.gemini_service import GeminiService
from src.domain.interfaces.dialog_system_service import DialogSystemServiceInterface

router = APIRouter(prefix="/dermis", tags=["Dermis"])

def get_dermis_service() -> DermisService:
    """
    Provides the singleton instance of DermisService for dependency injection.
    """
    return Container.dermis_service()

def get_dialog_service() -> DialogSystemServiceInterface:
    """
    Provides the singleton instance of GeminiService for dependency injection as a dialog system service.
    """
    return Container.gemini_service()

@router.post("/evaluate", response_model=LesionEvaluationResponseDTO, tags=["Dermis"])
async def evaluate_dermis_condition(
    image: UploadFile = File(..., description="Dermatological image"),
    description: Optional[str] = Form(None, description="Optional description of the symptoms"),
    dermis_service: DermisService = Depends(get_dermis_service),
    dialog_service: DialogSystemServiceInterface = Depends(get_dialog_service)
) -> LesionEvaluationResponseDTO:
    """
    Evaluates a dermatological condition using image classification and generates expert medical advice.
    Receives an image and an optional description, classifies the condition, and returns a response DTO with the classification and advice.
    """
    try:
        image_bytes = await image.read()
        classification_result = await dermis_service.classify_disease(BytesIO(image_bytes))
        predicted_classes = classification_result.get("predicted_classes", [])
        if predicted_classes:
            classification = ", ".join(predicted_classes)
        else:
            classification = "No se detectó ninguna condición conocida. La imagen está limpia o el problema no está en nuestro dataset."
        system_prompt = (
            "Eres un dermatólogo experto. Siempre responde en español. "
            "Solo puedes responder preguntas relacionadas con condiciones dermatológicas, piel, uñas o cabello. "
            "Si la pregunta o el contexto no está relacionado con temas dermatológicos, rechaza la consulta educadamente diciendo: "
            "'Lo siento, solo puedo responder preguntas relacionadas con dermatología, piel, uñas o cabello.'\n"
            "Si recibes un diagnóstico, explica de manera clara y profesional en qué consiste la enfermedad o condición detectada, "
            "cuáles son sus implicaciones, y qué puede hacer el paciente para aliviar, tratar o curar la enfermedad. "
            "Incluye recomendaciones sobre:\n"
            "- Si es necesario consultar a un especialista\n"
            "- Posibles tratamientos\n"
            "- Síntomas o señales de alerta que requieren atención urgente\n"
            "- Medidas preventivas y consejos de cuidado de la piel\n"
            "Sé profesional pero fácil de entender para un paciente no especialista."
        )
        user_prompt = f"""
        Dermatological condition classification: {classification}
        
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
            detail=f"Error evaluating dermatological condition: {str(e)}"
        )