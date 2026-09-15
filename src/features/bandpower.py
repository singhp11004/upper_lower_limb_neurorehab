"""
Band Power & Relative Log-Energy Extractor (Alpha 8-13 Hz, High-Gamma 30-45 Hz).
"""

import numpy as np
from scipy.signal import welch
from typing import Dict, List


class BandPowerExtractor:
    def __init__(self, sample_rate: int = 250):
        self.sample_rate = sample_rate
        self.freq_bands = {
            "theta": (4.0, 8.0),
            "alpha": (8.0, 13.0),
            "beta": (13.0, 30.0),
            "high_gamma": (30.0, 45.0)
        }

    def compute_bandpower(self, epoch: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Compute Welch Power Spectral Density and relative log bandpower per channel.

        :param epoch: 2D array (n_channels, n_samples)
        :return: Dict mapping band_name -> 1D array of channel log-powers
        """
        if epoch.ndim != 2:
            raise ValueError(f"Expected 2D array (n_channels, n_samples), got {epoch.shape}")

        freqs, psd = welch(epoch, fs=self.sample_rate, nperseg=min(128, epoch.shape[1]), axis=-1)

        total_power = np.sum(psd, axis=-1) + 1e-9
        bandpowers = {}

        for band, (f_min, f_max) in self.freq_bands.items():
            idx_band = np.logical_and(freqs >= f_min, freqs <= f_max)
            band_power = np.sum(psd[:, idx_band], axis=-1)
            rel_power = band_power / total_power
            bandpowers[band] = np.log(np.maximum(rel_power, 1e-6))

        return bandpowers

    def extract_feature_vector(self, epoch: np.ndarray) -> np.ndarray:
        """
        Extract concatenated log-energy vector across alpha, beta, and high-gamma bands for all channels.
        """
        bp = self.compute_bandpower(epoch)
        feat_vec = np.hstack([bp["alpha"], bp["beta"], bp["high_gamma"]])
        return feat_vec
