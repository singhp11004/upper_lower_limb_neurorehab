"""
Periauricular EOG Peak & Double-Blink Detector for Safety Interlock Veto (<100ms latency).
Method adapted from King et al. (Nature Scientific Reports 2025).
"""

import numpy as np
from scipy.signal import find_peaks
from typing import Tuple, Dict, Any, Optional


class EOGBlinkDetector:
    def __init__(self, sample_rate: int = 250, peak_threshold_uv: float = 80.0, max_blink_interval_sec: float = 0.5, ch_pos: int = 0, ch_neg: Optional[int] = -1):
        """
        :param sample_rate: Sampling frequency in Hz (250 Hz)
        :param peak_threshold_uv: Differential EOG peak amplitude threshold (default 80 uV)
        :param max_blink_interval_sec: Maximum time delta between two consecutive blinks for double-blink veto (0.5s)
        :param ch_pos: Positive channel index for differential EOG (default 0)
        :param ch_neg: Negative channel index for differential EOG (default -1)
        """
        self.sample_rate = sample_rate
        self.peak_threshold_uv = peak_threshold_uv
        self.max_blink_interval_samples = int(max_blink_interval_sec * sample_rate)
        self.ch_pos = ch_pos
        self.ch_neg = ch_neg

    def detect_blinks(self, eeg_signal: np.ndarray) -> Tuple[bool, int, Dict[str, Any]]:
        """
        Detect double-blink emergency veto flag on differential temporal/periauricular channels.

        :param eeg_signal: 2D array (n_channels, n_samples)
        :return: Tuple (is_veto_active, blink_count, details_dict)
        """
        if eeg_signal.ndim == 1:
            eeg_signal = eeg_signal[np.newaxis, :]

        # Derive differential EOG channel signal (or single channel if only 1 channel provided)
        if eeg_signal.shape[0] > 1 and self.ch_neg is not None:
            pos_idx = self.ch_pos % eeg_signal.shape[0]
            neg_idx = self.ch_neg % eeg_signal.shape[0]
            diff_eog = eeg_signal[pos_idx, :] - eeg_signal[neg_idx, :]
        else:
            diff_eog = eeg_signal[0, :]

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
