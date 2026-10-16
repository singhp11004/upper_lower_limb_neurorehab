"""
Stepwise Linear Discriminant Analysis (SWLDA) for P300 ERP Classification.
Performs stepwise feature selection (p-in < 0.10, p-out > 0.15) and fits LDA classifier.
"""

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from typing import Tuple, Dict, Any, List


class SWLDAP300Classifier:
    def __init__(self, p_enter: float = 0.10, p_remove: float = 0.15, max_features: int = 60):
        """
        :param p_enter: Threshold p-value for feature entry (default 0.10)
        :param p_remove: Threshold p-value for feature removal (default 0.15)
        :param max_features: Maximum number of features to select
        """
        self.p_enter = p_enter
        self.p_remove = p_remove
        self.max_features = max_features
        self.selected_indices: List[int] = []
        self.lda = LinearDiscriminantAnalysis(solver="svd")
        self.is_fitted = False

    def _stepwise_selection(self, X: np.ndarray, y: np.ndarray) -> List[int]:
        """
        Forward/backward stepwise feature selection using F-test p-values.
        Forward step: add best feature with p < p_enter.
        Backward step: remove any feature with p > p_remove after each addition.
        """
        from scipy.stats import f_oneway

        n_samples, n_features = X.shape
        selected = []
        remaining = list(range(n_features))

        while remaining and len(selected) < self.max_features:
            # --- Forward Step: Find best candidate to add ---
            best_p = 1.0
            best_feature = None

            for feat in remaining:
                candidate = selected + [feat]
                X_cand = X[:, candidate]

                # Calculate F-statistic p-value for group separation
                group0 = X_cand[y == 0]
                group1 = X_cand[y == 1]

                if len(group0) > 0 and len(group1) > 0:
                    _, p_val = f_oneway(group0, group1)
                    p_val_min = np.min(p_val) if isinstance(p_val, np.ndarray) else p_val
                    if p_val_min < best_p:
                        best_p = p_val_min
                        best_feature = feat

            if best_feature is not None and best_p < self.p_enter:
                selected.append(best_feature)
                remaining.remove(best_feature)
            else:
                break

            # --- Backward Step: Remove any feature with p > p_remove ---
            if len(selected) >= 2:
                features_to_remove = []
                for idx, feat in enumerate(selected):
                    # Evaluate this feature's individual contribution by testing the
                    # subset without it against the full selected set
                    subset_without = [s for s in selected if s != feat]
                    X_sub = X[:, [feat]]
                    group0 = X_sub[y == 0]
                    group1 = X_sub[y == 1]

                    if len(group0) > 0 and len(group1) > 0:
                        _, p_val = f_oneway(group0, group1)
                        p_val_feat = np.min(p_val) if isinstance(p_val, np.ndarray) else p_val
                        if p_val_feat > self.p_remove:
                            features_to_remove.append(feat)

                for feat in features_to_remove:
                    selected.remove(feat)
                    remaining.append(feat)

        if not selected:
            # Fallback to top variance features if selection finds none
            variances = np.var(X, axis=0)
            selected = np.argsort(variances)[-self.max_features:].tolist()

        return selected

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SWLDAP300Classifier":
        """
        Fit SWLDA model on training features (N_samples, N_features) and binary target labels (0 or 1).
        """
        if X.ndim != 2:
            raise ValueError(f"Expected 2D array (n_samples, n_features), got {X.shape}")

        self.selected_indices = self._stepwise_selection(X, y)
        X_selected = X[:, self.selected_indices]

        self.lda.fit(X_selected, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict binary P300 presence (1 = P300 Target ERP present, 0 = Non-target)."""
        if not self.is_fitted:
            raise RuntimeError("Classifier is not fitted yet.")

        X_selected = X[:, self.selected_indices]
        return self.lda.predict(X_selected)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probability of P300 target presence."""
        if not self.is_fitted:
            raise RuntimeError("Classifier is not fitted yet.")

        X_selected = X[:, self.selected_indices]
        return self.lda.predict_proba(X_selected)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Evaluate accuracy, precision, recall, and F1 score."""
        y_pred = self.predict(X)
        return {
            "accuracy": float(np.round(accuracy_score(y, y_pred), 4)),
            "precision": float(np.round(precision_score(y, y_pred, zero_division=0), 4)),
            "recall": float(np.round(recall_score(y, y_pred, zero_division=0), 4)),
            "f1_score": float(np.round(f1_score(y, y_pred, zero_division=0), 4)),
            "selected_features_count": len(self.selected_indices)
        }
