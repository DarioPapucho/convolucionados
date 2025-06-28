import io
from typing import Optional
from fastapi import UploadFile
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from src.domain.interfaces.vision_classifier_service_interface import VisionClassifierServiceInterface

class HuggingFaceVisionService(VisionClassifierServiceInterface):
    """Implementation of image classification service using Hugging Face"""
    
    def __init__(self, model_name: str = "Anwarkh1/Skin_Cancer-Image_Classification"):
        """
        Initialize the classification service
        
        Args:
            model_name: Hugging Face model name to use
        """
        self.model_name = model_name
        self.processor = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Hugging Face model and processor"""
        try:
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            # Fallback to a simpler model
            self.model_name = "Anwarkh1/Skin_Cancer-Image_Classification"
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
    
    async def classify_image(
        self,
        image: UploadFile,
        description: Optional[str] = None
    ) -> str:
        """
        Classify an image using the Hugging Face model
        
        Args:
            image: Image to classify
            description: Optional description of the image
            
        Returns:
            str: Classified category with confidence level
        """
        try:
            # Read the image
            image_data = await image.read()
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Preprocess the image
            inputs = self.processor(pil_image, return_tensors="pt")
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                
                # Get the class with highest probability
                predicted_class_id = logits.argmax().item()
                confidence = probabilities[0][predicted_class_id].item()
                
                # Get the class name
                predicted_class = self.model.config.id2label[predicted_class_id]
                
                # Format result
                result = f"{predicted_class} (Confidence: {confidence:.1%})"
                
                return result
                
        except Exception as e:
            print(f"Error classifying image: {str(e)}")
            return "Classification error (Confidence: 0%)" 