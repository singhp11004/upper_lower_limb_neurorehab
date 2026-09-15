"""
Periauricular EOG Peak & Double-Blink Detector for Safety Interlock Veto (<100ms latency).
Method adapted from King et al. (Nature Scientific Reports 2025).
"""

import numpy as np
from scipy.signal import find_peaks
from typing import Tuple, Dict, Any


class EOGBlinkDetector:
    def __init__(self, sample_rate: int = 250, peak_threshold_uv: float = 80.0, max_blink_interval_sec: float = 0.5):
        """
        :param sample_rate: Sampling frequency in Hz (250 Hz)
        :param peak_threshold_uv: Differential EOG peak amplitude threshold (default 80 uV)
        :param max_blink_interval_sec: Maximum time delta between two consecutive blinks for double-blink veto (0.5s)
        """
        self.sample_rate = sample_rate
        self.peak_threshold_uv = peak_threshold_uv
        self.max_blink_interval_samples = int(max_blink_interval_sec * sample_rate)

    def detect_blinks(self, eeg_signal: np.ndarray) -> Tuple[bool, int, Dict[str, Any]]:
        """
        Detect double-blink emergency veto flag on differential temporal/periauricular channels.

        :param eeg_signal: 2D array (n_channels, n_samples)
        :return: Tuple (is_veto_active, blink_count, details_dict)
        """
        if eeg_signal.ndim == 1:
            eeg_signal = eeg_signal[np.newaxis, :]

        # Derive differential EOG channel signal (Front-Periauricular minus Back-Periauricular)
        diff_eog = eeg_signal[0, :] - eeg_signal[-1, :]

        # Find positive amplitude peaks corresponding to eye blinks
        peaks, properties = find_peaks(
            diff_eog,
            height=self.peak_threshold_uv,
            distance=int(0.15 * self.sample_rate)  # Min 150ms between blinks
        )

        blink_count = len(peaks)
        is_double_blink_veto = False

        if blink_count >= 2:
            # Check interval between consecutive peaks
            intervals = np.diff(peaks)
            if np.any(intervals <= self.max_blink_interval_samples):
                is_double_blink_veto = True

        details = {
            "is_veto_active": is_double_blink_veto,
            "blink_count": blink_count,
            "peak_indices": peaks.tolist(),
            "peak_heights_uv": properties.get("peak_heights", np.array([])).tolist()
        }

        return is_double_blink_veto, blink_count, details
