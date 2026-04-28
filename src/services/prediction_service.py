"""
Service de prédiction ML — Singleton qui charge les modèles une seule fois.
Utilisé par les routes FastAPI pour les prédictions.
"""

import os
import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_PATH = os.path.join(BASE_DIR, "models")


class MLService:
    """Charge les modèles ML au démarrage et expose des méthodes de prédiction."""

    def __init__(self):
        self._models = {}
        self._scaler = None
        self._feature_names = None
        self._metrics = None
        self._loaded = False

    def load(self):
        """Charge tous les modèles depuis le disque (appelé une seule fois)."""
        if self._loaded:
            return

        for name in ("RandomForest", "LogisticRegression", "SVM"):
            path = os.path.join(MODELS_PATH, f"{name}.pkl")
            if os.path.exists(path):
                self._models[name] = joblib.load(path)

        scaler_path = os.path.join(MODELS_PATH, "scaler.pkl")
        if os.path.exists(scaler_path):
            self._scaler = joblib.load(scaler_path)

        fn_path = os.path.join(MODELS_PATH, "feature_names.pkl")
        if os.path.exists(fn_path):
            self._feature_names = joblib.load(fn_path)

        metrics_path = os.path.join(MODELS_PATH, "metrics.pkl")
        if os.path.exists(metrics_path):
            self._metrics = joblib.load(metrics_path)

        self._loaded = True
        print(f"[MLService] {len(self._models)} modèle(s) chargé(s)")

    @property
    def is_ready(self) -> bool:
        return self._loaded and len(self._models) > 0

    @property
    def available_models(self) -> list:
        return list(self._models.keys())

    def get_metrics(self) -> dict:
        """Retourne les métriques sauvegardées lors de l'entraînement."""
        if self._metrics:
            return self._metrics
        return {}

    def get_model(self, name: str):
        return self._models.get(name)

    @property
    def scaler(self):
        return self._scaler

    @property
    def feature_names(self):
        return self._feature_names


# Instance singleton — importable partout
ml_service = MLService()
