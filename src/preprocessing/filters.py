"""
Signal Conditioning Filters (0.5–45 Hz Bandpass, 50 Hz Notch, Alpha & Gamma Sub-bands).
"""

import numpy as np
from scipy.signal import butter, iirnotch, filtfilt, lfilter
from typing import Tuple, Optional


class EEGFilterPipeline:
    def __init__(self, sample_rate: int = 250, lowcut: float = 0.5, highcut: float = 45.0, notch_freq: float = 50.0, notch_q: float = 30.0):
        """
        :param sample_rate: EEG sampling frequency in Hz (250 Hz default)
        :param lowcut: Bandpass lower cutoff (0.5 Hz)
        :param highcut: Bandpass upper cutoff (45.0 Hz)
        :param notch_freq: Powerline notch frequency (50.0 Hz for India)
        :param notch_q: Quality factor for notch filter
        """
        self.sample_rate = sample_rate
        self.lowcut = lowcut
        self.highcut = highcut
        self.notch_freq = notch_freq

        # 4th-order Butterworth bandpass (0.5 - 45 Hz)
        nyq = 0.5 * sample_rate
        self.b_band, self.a_band = butter(4, [lowcut / nyq, highcut / nyq], btype="bandpass")  # type: ignore[misc]

        # 50 Hz iirnotch filter
        self.b_notch, self.a_notch = iirnotch(notch_freq / nyq, notch_q)  # type: ignore[misc]

        # Alpha bandpass (8 - 13 Hz)
        self.b_alpha, self.a_alpha = butter(3, [8.0 / nyq, 13.0 / nyq], btype="bandpass")  # type: ignore[misc]

        # High-Gamma bandpass (30 - 45 Hz)
        self.b_gamma, self.a_gamma = butter(3, [30.0 / nyq, 45.0 / nyq], btype="bandpass")  # type: ignore[misc]

    def process(self, eeg_data: np.ndarray, zero_phase: bool = True) -> np.ndarray:
        """
        Apply 0.5-45 Hz bandpass and 50 Hz notch filter to EEG data (n_channels, n_samples).
        """
        if eeg_data.ndim == 1:
            data = eeg_data[np.newaxis, :]
        else:
            data = eeg_data

        filter_func = filtfilt if zero_phase and data.shape[-1] > 15 else lfilter

        # Apply notch filter
        notched = filter_func(self.b_notch, self.a_notch, data, axis=-1)

        # Apply bandpass filter
        bandpassed = filter_func(self.b_band, self.a_band, notched, axis=-1)

        return bandpassed if eeg_data.ndim != 1 else bandpassed[0]  # type: ignore[return-value]

    def extract_alpha_band(self, eeg_data: np.ndarray, zero_phase: bool = True) -> np.ndarray:
        """Extract temporal alpha sub-band (8–13 Hz)."""
        filter_func = filtfilt if zero_phase and eeg_data.shape[-1] > 15 else lfilter
        return filter_func(self.b_alpha, self.a_alpha, eeg_data, axis=-1)  # type: ignore[return-value]

    def extract_high_gamma_band(self, eeg_data: np.ndarray, zero_phase: bool = True) -> np.ndarray:
        """Extract high-gamma sub-band (30–45 Hz) for jaw-clench triggers."""
        filter_func = filtfilt if zero_phase and eeg_data.shape[-1] > 15 else lfilter
        return filter_func(self.b_gamma, self.a_gamma, eeg_data, axis=-1)  # type: ignore[return-value]
