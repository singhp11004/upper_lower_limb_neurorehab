"""
Linear Discriminant Analysis (LDA) Classifier for Cognitive Workload / Alpha Bandpower Discrimination.
"""

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import accuracy_score, confusion_matrix
from typing import Dict, Any, Tuple


class WorkloadLDAClassifier:
    def __init__(self, solver: str = "svd"):
        self.lda = LinearDiscriminantAnalysis(solver=solver)
        self.is_fitted = False

    def fit(self, X_alpha: np.ndarray, y_workload: np.ndarray) -> "WorkloadLDAClassifier":
        """
        Fit LDA on alpha bandpower features X_alpha (N_samples, N_channels) and discrete workload states y (0=Low, 1=High).
        """
        self.lda.fit(X_alpha, y_workload)
        self.is_fitted = True
        return self

    def predict(self, X_alpha: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Workload LDA classifier is not fitted yet.")
        return self.lda.predict(X_alpha)

    def predict_proba(self, X_alpha: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Workload LDA classifier is not fitted yet.")
        return self.lda.predict_proba(X_alpha)

    def evaluate(self, X_alpha: np.ndarray, y_workload: np.ndarray) -> Dict[str, Any]:
        y_pred = self.predict(X_alpha)
        acc = accuracy_score(y_workload, y_pred)
        cm = confusion_matrix(y_workload, y_pred)
        return {
            "accuracy": float(np.round(acc, 4)),
            "confusion_matrix": cm.tolist()
        }
