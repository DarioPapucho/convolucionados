import pickle
import librosa
import numpy as np
import pandas as pd
import io
import os
from typing import Optional
from fastapi import UploadFile
from src.domain.interfaces.cough_classifier_service_interface import CoughClassifierServiceInterface

class CoughClassificationService(CoughClassifierServiceInterface):
    """Service to classify cough audio using a pre-trained sklearn model."""

    def __init__(self, path_model: str = 'domain/weights/hugging_face/cough_classification_model.pkl'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_rel_path = '../../domain/weights/hugging_face/cough_classification_model.pkl'
        self.path_model = os.path.normpath(os.path.join(base_dir, model_rel_path))
        self._load_model()

    def _load_model(self):
        with open(self.path_model, 'rb') as f:
            components = pickle.load(f)

        self.model = components['model']
        self.scaler = components['scaler']
        self.label_encoder = components['label_encoder']
        self.feature_names = components['feature_names']

    def extract_all_features_from_audio(self, y: np.ndarray, sr: int) -> dict:
        features_dict = {}

        features_dict['duration'] = librosa.get_duration(y=y, sr=sr)
        rms = librosa.feature.rms(y=y)
        features_dict['rms_mean'] = np.mean(rms)
        features_dict['rms_std'] = np.std(rms)
        zcr = librosa.feature.zero_crossing_rate(y)
        features_dict['zcr_mean'] = np.mean(zcr)
        features_dict['zcr_std'] = np.std(zcr)
        sc = librosa.feature.spectral_centroid(y=y, sr=sr)
        features_dict['spectral_centroid_mean'] = np.mean(sc)
        features_dict['spectral_centroid_std'] = np.std(sc)
        sb = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        features_dict['spectral_bandwidth_mean'] = np.mean(sb)
        features_dict['spectral_bandwidth_std'] = np.std(sb)
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        features_dict['spectral_contrast_mean'] = np.mean(contrast)
        features_dict['spectral_contrast_std'] = np.std(contrast)
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        features_dict['rolloff_mean'] = np.mean(rolloff)
        features_dict['rolloff_std'] = np.std(rolloff)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        for i in range(13):
            features_dict[f'mfcc{i+1}_mean'] = np.mean(mfccs[i])
            features_dict[f'mfcc{i+1}_std'] = np.std(mfccs[i])
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        features_dict['chroma_mean'] = np.mean(chroma)
        features_dict['chroma_std'] = np.std(chroma)

        return features_dict

    async def classify_audio(
        self,
        audio: UploadFile,
        description: Optional[str] = None
    ) -> str:
        try:
            audio_bytes = await audio.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)

            features_dict = self.extract_all_features_from_audio(y, sr)
            features_df = pd.DataFrame([features_dict])[self.feature_names]
            features_scaled = self.scaler.transform(features_df)

            prediction_idx = self.model.predict(features_scaled)[0]
            prediction = self.label_encoder.inverse_transform([prediction_idx])[0]
            probabilities_array = self.model.predict_proba(features_scaled)[0]
            confidence = max(probabilities_array)

            print(prediction)
            print(confidence)

            return f"{prediction} (Confidence: {confidence:.1%})"

        except Exception as e:
            return f"Classification error: {str(e)}"
