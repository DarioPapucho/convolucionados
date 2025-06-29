from pydantic import BaseModel, Field

class DeepStrokeResponseDTO(BaseModel):
    """DTO para la respuesta de predicción de riesgo de ACV con DeepSTROKE"""
    id_paciente: str = Field(..., description="ID único del paciente")
    probabilidad_acv: float = Field(..., description="Probabilidad final de ACV (0.0-1.0)")
    score_clinico: float = Field(..., description="Score clínico basado en factores de riesgo (0.0-1.0)")
    score_modelo: float = Field(..., description="Score del modelo de análisis de imagen (0.0-1.0)")
    nivel_riesgo: str = Field(..., description="Nivel de riesgo: BAJO, MODERADO, ALTO, MUY ALTO")
    riesgo_alto: bool = Field(..., description="¿Riesgo alto? (True=Sí, False=No)")
    recomendacion: str = Field(..., description="Recomendación clínica básica")
    recomendaciones_medicas: str = Field(..., description="Recomendaciones médicas personalizadas generadas por IA")
    
    # Datos del paciente (booleanos para la API)
    genero: bool = Field(..., description="Género del paciente (True=Masculino, False=Femenino)")
    fumador_alguna_ocasion_basal: bool = Field(..., description="¿Ha fumado alguna vez? (True=Sí, False=No)")
    hipertension_basal: bool = Field(..., description="¿Tiene hipertensión? (True=Sí, False=No)")
    diabetes_mellitus_tipo_2_basal: bool = Field(..., description="¿Tiene diabetes tipo 2? (True=Sí, False=No)")
    
    # Datos numéricos
    edad_basal: int = Field(..., description="Edad del paciente (años)")
    pas_basal: float = Field(..., description="Presión arterial sistólica (mmHg)")
    hdl_c_basal: float = Field(..., description="HDL colesterol (mmol/L)")
    colesterol_total_basal: float = Field(..., description="Colesterol total (mmol/L)")
    imc_basal: float = Field(..., description="Índice de masa corporal (kg/m²)")

    @classmethod
    def from_backend_data(cls, backend_data: dict) -> 'DeepStrokeResponseDTO':
        """Crea el DTO desde datos del backend (convierte 0/1 a booleanos)"""
        # Convertir enteros a booleanos para la API
        api_data = backend_data.copy()
        api_data['genero'] = bool(backend_data.get('genero', 0))
        api_data['fumador_alguna_ocasion_basal'] = bool(backend_data.get('fumador_alguna_ocasion_basal', 0))
        api_data['hipertension_basal'] = bool(backend_data.get('hipertension_basal', 0))
        api_data['diabetes_mellitus_tipo_2_basal'] = bool(backend_data.get('diabetes_mellitus_tipo_2_basal', 0))
        
        return cls(**api_data)

    class Config:
        json_schema_extra = {
            "example": {
                "id_paciente": "PAC001",
                "probabilidad_acv": 0.65,
                "score_clinico": 0.7,
                "score_modelo": 0.5,
                "nivel_riesgo": "ALTO",
                "riesgo_alto": True,
                "recomendacion": "Consulta especialista",
                "recomendaciones_medicas": "Dr. Carlos: Su riesgo de ACV es ALTO (65%). Factores a mejorar: presión arterial elevada (140 mmHg) y diabetes. Recomendaciones: control estricto de glucemia, dieta baja en sal, ejercicio moderado 30 min/día. Consulte cardiólogo cada 3 meses. Esto no es diagnóstico médico, sino evaluación de IA.",
                "genero": True,
                "fumador_alguna_ocasion_basal": False,
                "hipertension_basal": False,
                "diabetes_mellitus_tipo_2_basal": True,
                "edad_basal": 60,
                "pas_basal": 140.0,
                "hdl_c_basal": 1.2,
                "colesterol_total_basal": 5.5,
                "imc_basal": 25.5
            }
        } 