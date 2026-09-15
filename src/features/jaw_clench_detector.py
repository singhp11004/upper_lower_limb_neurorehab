"""
High-Gamma Burst (30–45 Hz) Jaw-Clench Spike Detector.
Detects deliberate jaw-clench trigger events with configurable power threshold.
"""

import numpy as np
from typing import Tuple, Dict, Any


class JawClenchDetector:
    def __init__(self, sample_rate: int = 250, threshold_db: float = 8.0, window_sec: float = 0.2):
        """
        :param sample_rate: Sampling frequency in Hz (250 Hz)
        :param threshold_db: High-gamma power spike threshold in dB (default 8.0 dB above baseline)
        :param window_sec: Detection window duration in seconds
        """
        self.sample_rate = sample_rate
        self.threshold_db = threshold_db
        self.window_sec = window_sec

    def detect_clench(self, gamma_signal: np.ndarray) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Evaluate high-gamma filtered signal array (n_channels, n_samples) for jaw-clench spike.

        :return: Tuple (is_clench_triggered, max_gamma_db, details_dict)
        """
        if gamma_signal.ndim == 1:
            gamma_signal = gamma_signal[np.newaxis, :]

        # Calculate high-gamma envelope power across temporal periauricular channels
        gamma_power = np.var(gamma_signal, axis=1) + 1e-6
        mean_power = np.mean(gamma_power)
        gamma_db = 10 * np.log10(mean_power)

        is_clench = bool(gamma_db > self.threshold_db)

        details = {
            "is_clench": is_clench,
            "gamma_power_db": float(np.round(gamma_db, 2)),
            "threshold_db": self.threshold_db,
            "channel_powers_db": (10 * np.log10(gamma_power)).tolist()
        }

        return is_clench, float(gamma_db), details
