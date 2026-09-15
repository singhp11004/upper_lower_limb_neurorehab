"""
Model Manager for Model Persistence, Model Weights Saving/Loading, and Cross-Validation.
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, Optional
from sklearn.model_selection import StratifiedKFold, cross_val_score


class ModelManager:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)

    def save_model(self, model: Any, model_name: str) -> str:
        """
        Save trained model object to models_dir as .joblib file.
        """
        if not model_name.endswith(".joblib"):
            model_name += ".joblib"

        file_path = os.path.join(self.models_dir, model_name)
        joblib.dump(model, file_path)
        print(f"[ModelManager] Model successfully saved to '{file_path}'.")
        return file_path

    def load_model(self, model_name: str) -> Any:
        """
        Load trained model object from models_dir.
        """
        if not model_name.endswith(".joblib"):
            model_name += ".joblib"

        file_path = os.path.join(self.models_dir, model_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file '{file_path}' does not exist.")

        model = joblib.load(file_path)
        print(f"[ModelManager] Model successfully loaded from '{file_path}'.")
        return model

    def evaluate_cross_validation(self, estimator: Any, X: np.ndarray, y: np.ndarray, n_splits: int = 5) -> Dict[str, float]:
        """
        Perform 5-fold Stratified Cross-Validation.
        """
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        scores = cross_val_score(estimator, X, y, cv=cv, scoring="accuracy")

        return {
            "mean_accuracy": float(np.round(np.mean(scores), 4)),
            "std_accuracy": float(np.round(np.std(scores), 4)),
            "fold_scores": np.round(scores, 4).tolist()
        }
