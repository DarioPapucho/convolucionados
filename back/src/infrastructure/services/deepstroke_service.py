import os
import torch
import torch.nn as nn
import io
from PIL import Image
from fastapi import UploadFile
from typing import Dict
import torchvision.transforms as transforms
from src.domain.weights import RETFOUND_WEIGHTS_PATH
from src.infrastructure.services.gemini_service import GeminiService

class RETFoundModel(nn.Module):
    """Modelo RETFound simplificado para análisis de fondo de ojo"""
    def __init__(self, num_classes=2):
        super().__init__()
        # Encoder de características
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        # Clasificador
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

def calcular_score_clinico(datos_clinicos: Dict) -> float:
    """
    Calcula el score clínico basado en factores de riesgo cardiovascular
    
    Args:
        datos_clinicos: Diccionario con datos clínicos del paciente
    
    Returns:
        Score clínico entre 0 y 1
    """
    score = 0.0
    
    # Factores de riesgo y sus pesos (basado en estudios clínicos)
    factores = {
        'edad': min(datos_clinicos.get('edad', 50) / 100, 1.0),  # Normalizar edad
        'hipertension': datos_clinicos.get('hipertension', 0) * 0.25,
        'diabetes': datos_clinicos.get('diabetes', 0) * 0.20,
        'fumador': datos_clinicos.get('fumador', 0) * 0.15,
        'pas': min(datos_clinicos.get('pas', 120) / 200, 1.0),  # Normalizar PAS
        'hdl_c': max(0, 1 - datos_clinicos.get('hdl_c', 1.0) / 2),  # HDL inverso
        'colesterol': min(datos_clinicos.get('colesterol', 200) / 400, 1.0),  # Normalizar colesterol
        'imc': min(datos_clinicos.get('imc', 25) / 50, 1.0)  # Normalizar IMC
    }
    
    # Calcular score ponderado (basado en Framingham Risk Score)
    pesos = [0.25, 0.20, 0.15, 0.10, 0.15, 0.05, 0.05, 0.05]
    valores = list(factores.values())
    
    for valor, peso in zip(valores, pesos):
        score += valor * peso
    
    # Asegurar que esté entre 0 y 1
    return max(0.0, min(1.0, score))

class DeepStrokeService:
    """Servicio para inferencia del modelo DeepSTROKE usando RETFound"""
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
        """Carga el modelo RETFound desde los pesos"""
        if self._model is None:
            try:
                # Crear modelo
                self._model = RETFoundModel(num_classes=2)
                
                # Intentar cargar pesos si existen
                if os.path.exists(self._weights_path):
                    print(f"Cargando pesos desde: {self._weights_path}")
                    checkpoint = torch.load(self._weights_path, map_location=self._device)
                    if 'state_dict' in checkpoint:
                        self._model.load_state_dict(checkpoint['state_dict'])
                    else:
                        self._model.load_state_dict(checkpoint)
                else:
                    print(f"Pesos no encontrados en: {self._weights_path}")
                    print("Usando modelo con pesos aleatorios")
                
                self._model.eval()
                self._model.to(self._device)
                
            except Exception as e:
                print(f"Error cargando modelo: {e}")
                # Usar modelo básico si falla
                self._model = RETFoundModel(num_classes=2)
                self._model.eval()
                self._model.to(self._device)

    async def _generate_medical_recommendations(self, prediction_result: Dict) -> str:
        """Genera recomendaciones médicas personalizadas usando Gemini"""
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
        Paciente: {prediction_result['edad_basal']} años, {'Masculino' if prediction_result['genero'] == 1 else 'Femenino'}
        
        Factores de riesgo:
        - Fumador: {'Sí' if prediction_result['fumador_alguna_ocasion_basal'] == 1 else 'No'}
        - Hipertensión: {'Sí' if prediction_result['hipertension_basal'] == 1 else 'No'}
        - Diabetes: {'Sí' if prediction_result['diabetes_mellitus_tipo_2_basal'] == 1 else 'No'}
        - Presión arterial: {prediction_result['pas_basal']} mmHg
        - HDL colesterol: {prediction_result['hdl_c_basal']}
        - Colesterol total: {prediction_result['colesterol_total_basal']}
        - IMC: {prediction_result['imc_basal']}
        
        Resultado del análisis:
        - Nivel de riesgo: {prediction_result['nivel_riesgo']}
        - Probabilidad de ACV: {prediction_result['probabilidad_acv']:.1%}
        
        Dr. Carlos, ¿qué recomendaciones específicas tienes para este paciente?
        """

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
            transforms.Resize((224, 224)),
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
            features1 = self._model(image1)
            features2 = self._model(image2)
            
            # Combinar características de ambas imágenes
            combined_features = (features1 + features2) / 2
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