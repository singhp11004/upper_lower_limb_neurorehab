"""
P300 ERP Template Matching & Feature Vector Extractor (250–500ms Post-Stimulus Window).
"""

import numpy as np
from typing import Tuple, Optional


class P300Extractor:
    def __init__(self, sample_rate: int = 250, erp_window_sec: Tuple[float, float] = (0.25, 0.50)):
        """
        :param sample_rate: Sampling frequency in Hz (250 Hz)
        :param erp_window_sec: Time-locked window relative to stimulus onset (default 250-500ms)
        """
        self.sample_rate = sample_rate
        self.start_sample = int(erp_window_sec[0] * sample_rate)  # 62 samples
        self.end_sample = int(erp_window_sec[1] * sample_rate)    # 125 samples
        self.window_length = self.end_sample - self.start_sample

    def extract_features(self, epoch: np.ndarray) -> np.ndarray:
        """
        Extract P300 feature vector from a single 2D epoch (n_channels, n_samples).

        :return: 1D feature vector concatenating downsampled amplitude values in ERP window.
        """
        if epoch.ndim != 2:
            raise ValueError(f"Expected 2D array (n_channels, n_samples), got {epoch.shape}")

        n_channels, n_samples = epoch.shape

        # Extract 250-500ms time window
        if n_samples >= self.end_sample:
            erp_region = epoch[:, self.start_sample : self.end_sample]
        else:
            erp_region = epoch[:, -self.window_length :]

        # Downsample window by factor of 4 for LDA dimensionality reduction
        downsampled = erp_region[:, ::4]

        # Flatten into 1D feature vector for SWLDA classifier
        feature_vector = downsampled.flatten()
        return feature_vector

    def extract_batch_features(self, epochs: np.ndarray) -> np.ndarray:
        """
        Extract feature vectors for 3D epochs array (n_epochs, n_channels, n_samples).
        """
        if epochs.size == 0:
            return np.empty((0, 0))

        features = [self.extract_features(epochs[i]) for i in range(len(epochs))]
        return np.vstack(features)
