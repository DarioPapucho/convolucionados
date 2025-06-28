from fastapi import APIRouter, HTTPException, Depends
from src.domain.dtos.chat_request import ChatRequestDTO
from src.domain.dtos.chat_response import ChatResponseDTO
from src.domain.interfaces.dialog_system_service import DialogSystemServiceInterface
from src.infrastructure.services.gemini_service import GeminiService

router = APIRouter(prefix="/chat", tags=["Chat"])

def get_ai_service() -> DialogSystemServiceInterface:
    """Dependency injection for the AI service"""
    return GeminiService()

@router.post("/generate", response_model=ChatResponseDTO)
async def generate_response(
    request: ChatRequestDTO,
    ai_service: DialogSystemServiceInterface = Depends(get_ai_service)
) -> ChatResponseDTO:
    """
    Generate a response using the AI service
    
    Args:
        request: DTO with system_prompt, user_prompt and optional context
        ai_service: Injected AI service
        
    Returns:
        ChatResponseDTO: Generated response
    """
    try:
        response = await ai_service.generate_response(
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            context=request.context
        )
        
        return ChatResponseDTO(response=response)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        ) 