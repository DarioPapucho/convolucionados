from typing import Optional
from pydantic import BaseModel, Field, validator
from fastapi import UploadFile

class DeepStrokeRequestDTO(BaseModel):
    """DTO para la petición de predicción de riesgo de ACV con DeepSTROKE"""
    id_paciente: str = Field(..., description="ID único del paciente")
    genero: bool = Field(..., description="Género del paciente (True=Masculino, False=Femenino)")
    fumador_alguna_ocasion_basal: bool = Field(..., description="¿Ha fumado alguna vez? (True=Sí, False=No)")
    hipertension_basal: bool = Field(..., description="¿Tiene hipertensión? (True=Sí, False=No)")
    diabetes_mellitus_tipo_2_basal: bool = Field(..., description="¿Tiene diabetes tipo 2? (True=Sí, False=No)")
    edad_basal: int = Field(..., description="Edad del paciente (años)", ge=18, le=120)
    pas_basal: float = Field(..., description="Presión arterial sistólica (mmHg)", ge=80, le=250)
    hdl_c_basal: float = Field(..., description="HDL colesterol (mmol/L)", ge=0.1, le=10.0)
    colesterol_total_basal: float = Field(..., description="Colesterol total (mmol/L)", ge=1.0, le=20.0)
    imc_basal: float = Field(..., description="Índice de masa corporal (kg/m²)", ge=15.0, le=50.0)
    ojo1: UploadFile = Field(..., description="Imagen de fondo de ojo derecho")
    ojo2: UploadFile = Field(..., description="Imagen de fondo de ojo izquierdo")

    def to_backend_format(self) -> dict:
        """Convierte los datos a formato compatible con el backend (0/1)"""
        return {
            'id_paciente': self.id_paciente,
            'genero': 1 if self.genero else 0,
            'fumador_alguna_ocasion_basal': 1 if self.fumador_alguna_ocasion_basal else 0,
            'hipertension_basal': 1 if self.hipertension_basal else 0,
            'diabetes_mellitus_tipo_2_basal': 1 if self.diabetes_mellitus_tipo_2_basal else 0,
            'edad_basal': self.edad_basal,
            'pas_basal': self.pas_basal,
            'hdl_c_basal': self.hdl_c_basal,
            'colesterol_total_basal': self.colesterol_total_basal,
            'imc_basal': self.imc_basal
        }

    class Config:
        json_schema_extra = {
            "example": {
                "id_paciente": "PAC001",
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