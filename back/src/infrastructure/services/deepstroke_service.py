import os
import torch
import torch.nn as nn
import io
from PIL import Image
from fastapi import UploadFile
from typing import Dict
import torchvision.transforms as transforms
from src.domain.weights import RETFOUND_WEIGHTS_PATH
from DeepSTROKE.inference_solo_retfound import load_retfound_model, calcular_score_clinico, ModelWrapper
from src.infrastructure.services.gemini_service import GeminiService

class DeepStrokeService:
    """Servicio para inferencia del modelo DeepSTROKE"""
    _instance = None
    _model = None
    _device = 'cuda' if torch.cuda.is_available() else 'cpu'
    _weights_path = RETFOUND_WEIGHTS_PATH
    _gemini_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
            cls._instance._gemini_service = GeminiService()
        return cls._instance

    def _load_model(self):
        if self._model is None:
            original_model = load_retfound_model(self._weights_path, num_classes=2)
            self._model = ModelWrapper(original_model)
            self._model.eval()
            self._model.to(self._device)

    async def _generate_medical_recommendations(self, prediction_result: Dict) -> str:
        """Genera recomendaciones médicas personalizadas usando Gemini"""
        system_prompt = """Eres el Dr. Carlos, un neurólogo especialista en prevención de ACV con 15 años de experiencia. 
        Tu misión es ayudar a pacientes a reducir su riesgo de accidente cerebrovascular con recomendaciones prácticas y personalizadas.
        
        IMPORTANTE: Solo responde sobre prevención de ACV y factores de riesgo cardiovascular. 
        Si te preguntan sobre otros temas médicos, redirige amablemente al tema de ACV.
        
        Tu estilo es:
        - Cálido pero profesional
        - Directo y práctico
        - Usas analogías simples cuando es útil
        - Siempre empático con el paciente
        
        Incluye SOLO:
        1. **Recomendación principal** (1-2 líneas)
        2. **2-3 cambios específicos** en estilo de vida
        3. **1-2 valores a mejorar** si están fuera de rango
        4. **Frecuencia de control médico** recomendada
        
        Máximo 150 palabras. Sé directo y práctico."""

        user_prompt = f"""
        Paciente: {prediction_result['edad_basal']} años, {'M' if prediction_result['genero'] == 1 else 'F'}
        Factores: {'Fumador' if prediction_result['fumador_alguna_ocasion_basal'] == 1 else ''} {'Hipertensión' if prediction_result['hipertension_basal'] == 1 else ''} {'Diabetes' if prediction_result['diabetes_mellitus_tipo_2_basal'] == 1 else ''}
        PAS: {prediction_result['pas_basal']} mmHg, HDL: {prediction_result['hdl_c_basal']}, IMC: {prediction_result['imc_basal']}
        Riesgo: {prediction_result['nivel_riesgo']} ({prediction_result['probabilidad_acv']:.1%})
        
        Dr. Carlos, ¿qué recomendaciones tienes para este paciente?"""

        try:
            recommendations = await self._gemini_service.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                context=f"ACV - Paciente {prediction_result['id_paciente']}"
            )
            return recommendations
        except Exception as e:
            print(f"Error generando recomendaciones con Gemini: {str(e)}")
            return "No se pudieron generar recomendaciones personalizadas en este momento."

    async def predict(self, data: Dict, ojo1: UploadFile, ojo2: UploadFile) -> Dict:
        # Procesar imágenes directamente desde UploadFile
        image1 = Image.open(io.BytesIO(await ojo1.read())).convert('RGB')
        image2 = Image.open(io.BytesIO(await ojo2.read())).convert('RGB')
        transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        image1 = transform(image1).unsqueeze(0).to(self._device)
        image2 = transform(image2).unsqueeze(0).to(self._device)

        # Score clínico
        datos_clinicos = {
            'genero': data['genero'],
            'fumador': data['fumador_alguna_ocasion_basal'],
            'hipertension': data['hipertension_basal'],
            'diabetes': data['diabetes_mellitus_tipo_2_basal'],
            'edad': data['edad_basal'],
            'pas': data['pas_basal'],
            'hdl_c': data['hdl_c_basal'],
            'colesterol': data['colesterol_total_basal'],
            'imc': data['imc_basal']
        }
        score_clinico = calcular_score_clinico(datos_clinicos)

        # Predicción modelo
        with torch.no_grad():
            def get_features(image):
                output = self._model(image)
                if isinstance(output, tuple):
                    return output[0]
                return output
            features1 = get_features(image1)
            features2 = get_features(image2)
            if features1.shape != features2.shape:
                features1 = features1.mean(dim=[2, 3], keepdim=True).squeeze()
                features2 = features2.mean(dim=[2, 3], keepdim=True).squeeze()
            combined_features = (features1 + features2) / 2
            if combined_features.dim() == 1:
                combined_features = combined_features.unsqueeze(0)
            probabilities = torch.softmax(combined_features, dim=1)
            prob_modelo = probabilities[0, 1].item()

        # Combinar score clínico y modelo
        peso_clinico = 0.7
        peso_modelo = 0.3
        probabilidad_final = (peso_clinico * score_clinico) + (peso_modelo * prob_modelo)
        riesgo_alto = probabilidad_final > 0.5
        nivel_riesgo = "MUY ALTO" if probabilidad_final > 0.75 else \
                      "ALTO" if probabilidad_final > 0.5 else \
                      "MODERADO" if probabilidad_final > 0.3 else "BAJO"
        recomendacion = 'Consulta especialista' if riesgo_alto else 'Seguimiento rutinario'

        # Crear resultado base
        result = {
            'id_paciente': data['id_paciente'],
            'probabilidad_acv': round(float(probabilidad_final), 4),
            'score_clinico': round(float(score_clinico), 4),
            'score_modelo': round(float(prob_modelo), 4),
            'nivel_riesgo': nivel_riesgo,
            'riesgo_alto': riesgo_alto,
            'recomendacion': recomendacion,
            **data
        }

        # Generar recomendaciones médicas personalizadas
        medical_recommendations = await self._generate_medical_recommendations(result)
        result['recomendaciones_medicas'] = medical_recommendations

        return result 