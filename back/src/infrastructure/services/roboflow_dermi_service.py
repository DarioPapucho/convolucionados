from inference_sdk import InferenceHTTPClient
from PIL import Image
import os
import requests
from io import BytesIO

class RoboflowDermisService:
    """
    Service for interacting with the Roboflow inference API for dermatological images.
    """
    def __init__(self):
        """
        Initializes the RoboflowDermisService with API credentials and model information.
        """
        self.client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=os.getenv("ROBOFLOW_API_KEY")
        )
        self.project_id = "skin-scanner-2.2"
        self.model_version = 2

    async def classify_image(self, image_input):
        """
        Classifies a dermatological image using the Roboflow API.
        :param image_input: Path or URL to the image to classify
        :return: Classification result as a dictionary
        """
        if isinstance(image_input, str) and image_input.startswith("http"):
            response = requests.get(image_input)
            pil_image = Image.open(BytesIO(response.content))
        else:
            pil_image = Image.open(image_input)
        results = self.client.infer(pil_image, model_id=f"{self.project_id}/{self.model_version}")
        return results
