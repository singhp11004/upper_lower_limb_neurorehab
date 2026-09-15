"""
Signal Quality Monitor for 16-Channel cEEGrid Electrodes.
Computes SNR, impedance proxy, rail-to-rail saturation, and flatline flags.
"""

import numpy as np
from typing import Dict, List, Any


class SignalQualityMonitor:
    def __init__(self, n_channels: int = 16, sat_threshold_uv: float = 150.0, flatline_std_uv: float = 0.5):
        """
        :param n_channels: 16 channels for cEEGrid
        :param sat_threshold_uv: Microvolt threshold for saturation/rail (default 150 uV)
        :param flatline_std_uv: Microvolt standard deviation threshold for electrode contact loss
        """
        self.n_channels = n_channels
        self.sat_threshold_uv = sat_threshold_uv
        self.flatline_std_uv = flatline_std_uv

    def evaluate_window(self, eeg_window: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate quality metrics on a 2D EEG window (n_channels, n_samples).

        :return: Dict containing channel_status, snr_db, saturation_flags, flatline_flags
        """
        if eeg_window.ndim != 2 or eeg_window.shape[0] != self.n_channels:
            raise ValueError(f"Expected shape ({self.n_channels}, n_samples), got {eeg_window.shape}")

        stds = np.std(eeg_window, axis=1)
        max_amps = np.max(np.abs(eeg_window), axis=1)

        flatline_flags = stds < self.flatline_std_uv
        saturation_flags = max_amps > self.sat_threshold_uv

        # Calculate SNR proxy (ratio of bandpower signal variance to high-frequency noise estimate)
        signal_var = np.var(eeg_window, axis=1)
        diff_var = np.var(np.diff(eeg_window, axis=1), axis=1) + 1e-6
        # Signal variance relative to noise
        snr_db = 10 * np.log10(np.maximum(signal_var / (diff_var / 2.0), 1e-6))

        channel_status = []
        for ch in range(self.n_channels):
            if flatline_flags[ch]:
                status = "DISCONNECTED"
            elif saturation_flags[ch]:
                status = "SATURATED"
            elif stds[ch] < 0.1:
                status = "POOR"
            else:
                status = "GOOD"
            channel_status.append(status)

        return {
            "channel_status": channel_status,
            "snr_db": np.round(snr_db, 2).tolist(),
            "saturation_flags": saturation_flags.tolist(),
            "flatline_flags": flatline_flags.tolist(),
            "mean_snr_db": float(np.round(np.mean(snr_db), 2)),
            "good_channels_count": int(sum(s == "GOOD" for s in channel_status))
        }
