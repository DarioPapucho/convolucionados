from pydantic import BaseModel, Field

class DeepStrokeResponseDTO(BaseModel):
    """DTO para la respuesta de predicción de riesgo de ACV con DeepSTROKE"""
    id_paciente: str = Field(..., description="ID del paciente")
    probabilidad_acv: float = Field(..., description="Probabilidad final de ACV")
    score_clinico: float = Field(..., description="Score clínico")
    score_modelo: float = Field(..., description="Score del modelo de imagen")
    nivel_riesgo: str = Field(..., description="Nivel de riesgo (BAJO, MODERADO, ALTO, MUY ALTO)")
    riesgo_alto: bool = Field(..., description="¿Riesgo alto?")
    recomendacion: str = Field(..., description="Recomendación clínica básica")
    recomendaciones_medicas: str = Field(..., description="Recomendaciones médicas personalizadas generadas por IA")
    genero: int = Field(..., description="Género del paciente")
    fumador_alguna_ocasion_basal: int = Field(..., description="Fumador alguna vez")
    hipertension_basal: int = Field(..., description="Hipertensión basal")
    diabetes_mellitus_tipo_2_basal: int = Field(..., description="Diabetes tipo 2 basal")
    edad_basal: int = Field(..., description="Edad del paciente")
    pas_basal: int = Field(..., description="Presión arterial sistólica basal")
    hdl_c_basal: float = Field(..., description="HDL colesterol basal")
    colesterol_total_basal: float = Field(..., description="Colesterol total basal")
    imc_basal: float = Field(..., description="IMC basal")

    class Config:
        json_schema_extra = {
            "example": {
                "id_paciente": "1",
                "probabilidad_acv": 0.65,
                "score_clinico": 0.7,
                "score_modelo": 0.5,
                "nivel_riesgo": "ALTO",
                "riesgo_alto": True,
                "recomendacion": "Consulta especialista",
                "recomendaciones_medicas": "Basado en su análisis, se recomienda consultar con un neurólogo...",
                "genero": 1,
                "fumador_alguna_ocasion_basal": 0,
                "hipertension_basal": 0,
                "diabetes_mellitus_tipo_2_basal": 1,
                "edad_basal": 60,
                "pas_basal": 140,
                "hdl_c_basal": 1.2,
                "colesterol_total_basal": 1.5,
                "imc_basal": 20.0
            }
        } 