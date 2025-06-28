from abc import ABC, abstractmethod
from typing import Optional
from fastapi import UploadFile

class CoughClassifierServiceInterface(ABC):
    """Interface for cough classification services"""
    
    @abstractmethod
    async def classify_audio(
        self,
        audio: UploadFile,
        description: Optional[str] = None
    ) -> str:
        """
        Classifies an audio and returns the category with confidence
        
        Args:
            audio: Audio to classify
            description: Optional description
            
        Returns:
            str: Classified category with confidence level
        """
        pass
