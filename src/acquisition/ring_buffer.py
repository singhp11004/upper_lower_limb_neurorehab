"""
Thread-Safe Circular Ring Buffer for 2-second Sliding EEG Windows.
Sampling Rate: 250 Hz -> Window: 500 samples, Step: 25 samples (100ms).
"""

import threading
import numpy as np
from typing import Tuple, Optional


class CircularRingBuffer:
    def __init__(self, n_channels: int = 16, window_sec: float = 2.0, step_sec: float = 0.1, sample_rate: int = 250):
        """
        Initialize Circular Ring Buffer.

        :param n_channels: Number of EEG channels (16 default for cEEGrid)
        :param window_sec: Sliding window length in seconds (default 2.0s = 500 samples)
        :param step_sec: Step overlap length in seconds (default 0.1s = 25 samples)
        :param sample_rate: Sampling frequency in Hz (default 250 Hz)
        """
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.window_size = int(window_sec * sample_rate)  # 500 samples
        self.step_size = int(step_sec * sample_rate)      # 25 samples

        # Internal buffer capacity (4x window size for safety)
        self.capacity = self.window_size * 4
        self.buffer = np.zeros((n_channels, self.capacity), dtype=np.float32)

        self.write_idx = 0
        self.total_samples_written = 0
        self._lock = threading.Lock()

    def append(self, samples: np.ndarray):
        """
        Append new incoming EEG samples shape (n_channels, n_samples).
        """
        if samples.ndim != 2 or samples.shape[0] != self.n_channels:
            raise ValueError(f"Expected array of shape ({self.n_channels}, n_samples), got {samples.shape}")

        n_samples = samples.shape[1]

        with self._lock:
            for i in range(n_samples):
                self.buffer[:, self.write_idx] = samples[:, i]
                self.write_idx = (self.write_idx + 1) % self.capacity
                self.total_samples_written += 1

    def get_latest_window(self) -> Optional[np.ndarray]:
        """
        Fetch the most recent 2-second window (n_channels, window_size).
        Returns None if buffer has not received enough samples yet.
        """
        with self._lock:
            if self.total_samples_written < self.window_size:
                return None

            # Calculate start index of the latest window_size samples
            start_idx = (self.write_idx - self.window_size) % self.capacity

            if start_idx + self.window_size <= self.capacity:
                window = self.buffer[:, start_idx : start_idx + self.window_size].copy()
            else:
                part1 = self.buffer[:, start_idx : self.capacity]
                part2 = self.buffer[:, 0 : (start_idx + self.window_size) % self.capacity]
                window = np.hstack((part1, part2))

            return window

    def is_ready(self) -> bool:
        """Check if buffer has filled at least 1 full window."""
        with self._lock:
            return self.total_samples_written >= self.window_size

    def reset(self):
        """Reset ring buffer pointers."""
        with self._lock:
            self.buffer.fill(0)
            self.write_idx = 0
            self.total_samples_written = 0
