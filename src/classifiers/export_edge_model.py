"""Exports trained scikit-learn SWLDA model into lightweight JSON weights for real-time Jetson edge execution.
"""

import os
import sys
import json
import joblib
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, BASE_DIR)
MODELS_DIR = os.path.join(BASE_DIR, "models")


def export_edge_model():
    model_path = os.path.join(MODELS_DIR, "swlda_p300_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at {model_path}")

    swlda = joblib.load(model_path)

    # SWLDA wrapper stores selected_indices and inner LDA
    selected_indices = getattr(swlda, "selected_indices", list(range(len(swlda.lda.coef_[0]))))
    weights = swlda.lda.coef_[0].tolist()
    intercept = float(swlda.lda.intercept_[0])

    edge_config = {
        "model_type": "SWLDA_P300_EDGE",
        "version": "1.0.0",
        "selected_feature_indices": selected_indices,
        "weights": weights,
        "intercept": intercept,
        "p300_confidence_threshold": 0.65,
        "eog_blink_threshold_uv": 80.0,
        "eog_max_blink_interval_sec": 0.5,
        "jaw_clench_gamma_threshold_db": 8.0,
        "sample_rate": 250,
        "bandpass_low": 0.5,
        "bandpass_high": 45.0,
        "notch_freq": 50.0,
        "notch_q": 30.0,
        "erp_window_start_sample": 62,
        "erp_window_end_sample": 125,
        "downsample_factor": 4,
    }

    out_file = os.path.join(MODELS_DIR, "edge_swlda_weights.json")
    with open(out_file, "w") as f:
        json.dump(edge_config, f, indent=2)

    print(f"✓ Edge model exported to {out_file}")
    print(f"  Weights: {len(weights)}, Features: {len(selected_indices)}, Intercept: {intercept:.4f}")


if __name__ == "__main__":
    export_edge_model()
