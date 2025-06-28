from typing import Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile

class DeepStrokeRequestDTO(BaseModel):
    """DTO para la petición de predicción de riesgo de ACV con DeepSTROKE"""
    id_paciente: str = Field(..., description="ID del paciente")
    genero: int = Field(..., description="Género del paciente (0=femenino, 1=masculino)")
    fumador_alguna_ocasion_basal: int = Field(..., description="Fumador alguna vez (0=no, 1=sí)")
    hipertension_basal: int = Field(..., description="Hipertensión basal (0=no, 1=sí)")
    diabetes_mellitus_tipo_2_basal: int = Field(..., description="Diabetes tipo 2 basal (0=no, 1=sí)")
    edad_basal: int = Field(..., description="Edad del paciente")
    pas_basal: int = Field(..., description="Presión arterial sistólica basal")
    hdl_c_basal: float = Field(..., description="HDL colesterol basal")
    colesterol_total_basal: float = Field(..., description="Colesterol total basal")
    imc_basal: float = Field(..., description="IMC basal")
    ojo1: UploadFile = Field(..., description="Imagen de fondo de ojo derecho")
    ojo2: UploadFile = Field(..., description="Imagen de fondo de ojo izquierdo")

    class Config:
        json_schema_extra = {
            "example": {
                "id_paciente": "1",
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