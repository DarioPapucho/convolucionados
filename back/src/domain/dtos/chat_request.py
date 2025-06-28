from typing import Optional
from pydantic import BaseModel, Field

class ChatRequestDTO(BaseModel):
    """DTO for chat requests with Gemini"""
    
    system_prompt: str = Field(..., description="Instructions on how the model should respond")
    user_prompt: str = Field(..., description="User's question or prompt")
    context: Optional[str] = Field(None, description="Optional additional context for the conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "system_prompt": "You are a helpful assistant that responds clearly and concisely.",
                "user_prompt": "What is the capital of France?",
                "context": "The user is studying European geography."
            }
        } 