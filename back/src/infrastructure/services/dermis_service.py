from src.infrastructure.services.roboflow_dermi_service import RoboflowDermisService

class DermisService:
    """
    Service for dermatological disease classification using RoboflowDermisService.
    """
    def __init__(self, roboflow_service: RoboflowDermisService):
        """
        Initializes the DermisService with a RoboflowDermisService instance.
        :param roboflow_service: Instance of RoboflowDermisService
        """
        self.roboflow_service = roboflow_service

    async def classify_disease(self, image_input):
        """
        Classifies a dermatological disease from the given image input.
        :param image_input: Path or URL to the image to classify
        :return: Classification result as a dictionary
        """
        return await self.roboflow_service.classify_image(image_input)
