import io
from typing import Optional
from fastapi import UploadFile
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from src.domain.interfaces.vision_classifier_service_interface import VisionClassifierServiceInterface

class HuggingFaceDentalService(VisionClassifierServiceInterface):
    """
    Implementation of a dental diagnostic image classification service using a Hugging Face model.
    
    This service loads a pretrained transformer model to analyze dental images and 
    predict possible dental conditions such as caries, periodontitis, impacted teeth, 
    or apical infections.
    """
    
    def __init__(self, model_name: str = "vishnu027/dental_classification_model_010424"):
        """
        Initialize the dental classification service.
        
        Args:
            model_name: The name of the Hugging Face model to load.
        """
        self.model_name = model_name
        self.processor = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the image processor and classification model from Hugging Face."""
        try:
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            # Retry with the same default model
            self.model_name = "vishnu027/dental_classification_model_010424"
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
    
    async def classify_image(
        self,
        image: UploadFile,
        description: Optional[str] = None
    ) -> str:
        """
        Classify a dental image to detect possible dental diseases.
        
        Args:
            image: The uploaded dental image (e.g., X-ray, intraoral photo).
            description: Optional description or notes about the image.
        
        Returns:
            str: Predicted dental condition with a brief message.
        """
        try:
            # Load image from request
            image_data = await image.read()
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Preprocess input
            inputs = self.processor(pil_image, return_tensors="pt")
            
            # Run prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                predicted_class = logits.argmax().item()
                label = self.model.config.id2label[predicted_class]
                
                return f"The image may indicate: **{label}**"
        
        except Exception as e:
            print(f"Error classifying image: {str(e)}")
            return "Error during dental diagnosis (Confidence: 0%)"
