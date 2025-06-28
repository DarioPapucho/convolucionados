from abc import ABC, abstractmethod
from typing import Optional
from fastapi import UploadFile

class VisionClassifierServiceInterface(ABC):
    """Interface for image classification services"""
    
    @abstractmethod
    async def classify_image(
        self,
        image: UploadFile,
        description: Optional[str] = None
    ) -> str:
        """
        Classifies an image and returns the category with confidence
        
        Args:
            image: Image to classify
            description: Optional description of the image
            
        Returns:
            str: Classified category with confidence level
        """
        pass 