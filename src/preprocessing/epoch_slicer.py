"""
Epoch Slicer Module for 2.0-Second Sliding Windows (100ms Step Size).
"""

import numpy as np
from typing import List, Tuple


class EpochSlicer:
    def __init__(self, window_sec: float = 2.0, step_sec: float = 0.1, sample_rate: int = 250):
        """
        :param window_sec: Sliding epoch window in seconds (2.0s = 500 samples)
        :param step_sec: Sliding step size in seconds (0.1s = 25 samples)
        :param sample_rate: EEG sampling frequency in Hz (250 Hz)
        """
        self.window_size = int(window_sec * sample_rate)
        self.step_size = int(step_sec * sample_rate)
        self.sample_rate = sample_rate

    def slice_signal(self, eeg_signal: np.ndarray) -> np.ndarray:
        """
        Slice 2D continuous array (n_channels, n_samples) into 3D epochs array (n_epochs, n_channels, window_size).
        """
        if eeg_signal.ndim != 2:
            raise ValueError(f"Expected 2D array (n_channels, n_samples), got {eeg_signal.ndim}D")

        n_channels, n_samples = eeg_signal.shape

        if n_samples < self.window_size:
            return np.empty((0, n_channels, self.window_size))

        n_epochs = 1 + (n_samples - self.window_size) // self.step_size
        epochs = np.zeros((n_epochs, n_channels, self.window_size), dtype=np.float32)

        for i in range(n_epochs):
            start = i * self.step_size
            epochs[i] = eeg_signal[:, start : start + self.window_size]

        return epochs
