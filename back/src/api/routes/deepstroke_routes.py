from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from typing import Optional
from src.domain.dtos.deepstroke_request import DeepStrokeRequestDTO
from src.domain.dtos.deepstroke_response import DeepStrokeResponseDTO
from src.infrastructure.services.deepstroke_service import DeepStrokeService
from src.infrastructure.services.gemini_service import GeminiService

router = APIRouter(prefix="/deepstroke", tags=["DeepSTROKE - Retinal Fundus Analysis"])

def get_deepstroke_service() -> DeepStrokeService:
    """Dependency to get DeepStroke service instance"""
    return DeepStrokeService()

def get_dialog_service() -> GeminiService:
    """Dependency injection for the dialog service"""
    return GeminiService()

@router.post("/predict", response_model=DeepStrokeResponseDTO)
async def predict_stroke_risk(
    id_paciente: str = Form(..., description="ID único del paciente"),
    genero: bool = Form(..., description="Género del paciente (True=Masculino, False=Femenino)"),
    fumador_alguna_ocasion_basal: bool = Form(..., description="¿Ha fumado alguna vez? (True=Sí, False=No)"),
    hipertension_basal: bool = Form(..., description="¿Tiene hipertensión? (True=Sí, False=No)"),
    diabetes_mellitus_tipo_2_basal: bool = Form(..., description="¿Tiene diabetes tipo 2? (True=Sí, False=No)"),
    edad_basal: int = Form(..., description="Edad del paciente (años)", ge=18, le=120),
    pas_basal: float = Form(..., description="Presión arterial sistólica (mmHg)", ge=80, le=250),
    hdl_c_basal: float = Form(..., description="HDL colesterol (mmol/L)", ge=0.1, le=10.0),
    colesterol_total_basal: float = Form(..., description="Colesterol total (mmol/L)", ge=1.0, le=20.0),
    imc_basal: float = Form(..., description="Índice de masa corporal (kg/m²)", ge=15.0, le=50.0),
    ojo1: UploadFile = File(..., description="Imagen de fondo de ojo derecho"),
    ojo2: UploadFile = File(..., description="Imagen de fondo de ojo izquierdo"),
    deepstroke_service: DeepStrokeService = Depends(get_deepstroke_service),
    dialog_service: GeminiService = Depends(get_dialog_service)
):
    """
    Predice el riesgo de accidente cerebrovascular usando análisis de fondo de ojo con RETFound
    
    **Parámetros:**
    - **id_paciente**: ID único del paciente
    - **genero**: Género (True=Masculino, False=Femenino)
    - **fumador_alguna_ocasion_basal**: ¿Ha fumado alguna vez? (True=Sí, False=No)
    - **hipertension_basal**: ¿Tiene hipertensión? (True=Sí, False=No)
    - **diabetes_mellitus_tipo_2_basal**: ¿Tiene diabetes tipo 2? (True=Sí, False=No)
    - **edad_basal**: Edad del paciente (18-120 años)
    - **pas_basal**: Presión arterial sistólica (80-250 mmHg)
    - **hdl_c_basal**: HDL colesterol (0.1-10.0 mmol/L)
    - **colesterol_total_basal**: Colesterol total (1.0-20.0 mmol/L)
    - **imc_basal**: Índice de masa corporal (15.0-50.0 kg/m²)
    - **ojo1**: Imagen del fondo de ojo derecho
    - **ojo2**: Imagen del fondo de ojo izquierdo
    
    **Retorna:**
    - Probabilidad de ACV
    - Nivel de riesgo (BAJO, MODERADO, ALTO, MUY ALTO)
    - Recomendaciones médicas personalizadas
    """
    try:
        # Validar tipos de archivo
        if not ojo1.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="ojo1 debe ser una imagen")
        if not ojo2.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="ojo2 debe ser una imagen")
        
        # Crear DTO con datos de la API (booleanos)
        request_dto = DeepStrokeRequestDTO(
            id_paciente=id_paciente,
            genero=genero,
            fumador_alguna_ocasion_basal=fumador_alguna_ocasion_basal,
            hipertension_basal=hipertension_basal,
            diabetes_mellitus_tipo_2_basal=diabetes_mellitus_tipo_2_basal,
            edad_basal=edad_basal,
            pas_basal=pas_basal,
            hdl_c_basal=hdl_c_basal,
            colesterol_total_basal=colesterol_total_basal,
            imc_basal=imc_basal,
            ojo1=ojo1,
            ojo2=ojo2
        )
        
        # Convertir a formato del backend (0/1)
        backend_data = request_dto.to_backend_format()
        
        # Realizar predicción
        result = await deepstroke_service.predict(backend_data, ojo1, ojo2)
        
        # Generar recomendaciones médicas con prompt específico
        system_prompt = """Eres el Dr. Carlos, un neurólogo especialista en prevención de accidentes cerebrovasculares (ACV) con 15 años de experiencia. 
        Tu función es ofrecer orientación médica clara, útil y profesional basada en el análisis de riesgo de ACV.
        
        IMPORTANTE: Solo puedes responder sobre prevención de ACV y factores de riesgo cardiovascular. 
        No debes mencionar ni diagnosticar otras enfermedades o condiciones médicas.
        
        Debes abordar exclusivamente lo siguiente:
        - Evaluación del nivel de riesgo de ACV (BAJO, MODERADO, ALTO, MUY ALTO)
        - Factores de riesgo específicos del paciente que pueden mejorarse
        - Recomendaciones prácticas para reducir el riesgo de ACV
        - Si es recomendable acudir a una consulta médica especializada
        - Frecuencia de controles médicos recomendada
        - Un recordatorio claro de que esto no es un diagnóstico médico, sino una evaluación basada en inteligencia artificial para apoyar la toma de decisiones
        
        Responde con empatía, sencillez y precisión. Máximo 120 palabras. Sé directo y práctico."""

        user_prompt = f"""
        Paciente: {result['edad_basal']} años, {'Masculino' if result['genero'] == 1 else 'Femenino'}
        
        Factores de riesgo:
        - Fumador: {'Sí' if result['fumador_alguna_ocasion_basal'] == 1 else 'No'}
        - Hipertensión: {'Sí' if result['hipertension_basal'] == 1 else 'No'}
        - Diabetes: {'Sí' if result['diabetes_mellitus_tipo_2_basal'] == 1 else 'No'}
        - Presión arterial: {result['pas_basal']} mmHg
        - HDL colesterol: {result['hdl_c_basal']} mmol/L
        - Colesterol total: {result['colesterol_total_basal']} mmol/L
        - IMC: {result['imc_basal']} kg/m²
        
        Resultado del análisis:
        - Nivel de riesgo: {result['nivel_riesgo']}
        - Probabilidad de ACV: {result['probabilidad_acv']:.1%}
        
        Dr. Carlos, ¿qué recomendaciones específicas tienes para este paciente?
        """

        medical_advice = await dialog_service.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=f"ACV - Paciente {result['id_paciente']}"
        )
        
        # Actualizar el resultado con las recomendaciones médicas
        result['recomendaciones_medicas'] = medical_advice
        
        # Convertir respuesta del backend a formato de API (booleanos)
        return DeepStrokeResponseDTO.from_backend_data(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(e)}")

@router.get("/health")
async def health_check():
    """Verificar el estado del servicio DeepSTROKE"""
    return {
        "status": "healthy",
        "service": "DeepSTROKE RETFound",
        "description": "Servicio de análisis de fondo de ojo para predicción de riesgo de ACV"
    } 