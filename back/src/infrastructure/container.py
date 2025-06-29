from dependency_injector import containers, providers
from src.infrastructure.services.roboflow_dermi_service import RoboflowDermisService
from src.infrastructure.services.dermis_service import DermisService
from src.infrastructure.services.gemini_service import GeminiService

class Container(containers.DeclarativeContainer):
    roboflow_service = providers.Singleton(RoboflowDermisService)
    dermis_service = providers.Singleton(DermisService, roboflow_service=roboflow_service)
    gemini_service = providers.Singleton(GeminiService)
