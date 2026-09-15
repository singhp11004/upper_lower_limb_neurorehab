"""
BrainFlow Streamer Wrapper for OpenBCI 16-Channel cEEGrid Acquisition.
Supports live hardware (Cyton+Daisy), synthetic streams, and playback files.
"""

import time
import numpy as np
from typing import Optional, Tuple


class BrainFlowStreamer:
    def __init__(self, mode: str = "playback", playback_file: Optional[str] = None, serial_port: Optional[str] = None):
        """
        Initialize BrainFlow Streamer.

        :param mode: 'live' (OpenBCI Cyton+Daisy), 'synthetic', or 'playback'
        :param playback_file: Path to CSV playback dataset file for 'playback' mode
        :param serial_port: Serial COM/tty port for live hardware
        """
        self.mode = mode.lower()
        self.playback_file = playback_file
        self.serial_port = serial_port
        self.board = None
        self.board_id = None
        self.sampling_rate = 250  # Hz
        self.eeg_channels = list(range(1, 17))  # 16 channels default

        self._init_board()

    def _init_board(self):
        try:
            from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

            params = BrainFlowInputParams()

            if self.mode == "live":
                self.board_id = BoardIds.CYTON_DAISY_BOARD.value
                if self.serial_port:
                    params.serial_port = self.serial_port
            elif self.mode == "playback" and self.playback_file:
                self.board_id = BoardIds.PLAYBACK_FILE_BOARD.value
                params.file = self.playback_file
            else:
                self.board_id = BoardIds.SYNTHETIC_BOARD.value

            BoardShim.enable_dev_board_logger()
            self.board = BoardShim(self.board_id, params)
            self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
            self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)[:16]
        except ImportError:
            # Fallback mock mode if BrainFlow is not installed in runtime environment
            print("[BrainFlowStreamer] Warning: brainflow library not detected, running in standalone mock mode.")
            self.board = None

    def start_stream(self, buffer_size: int = 450000):
        """Start acquisition stream."""
        if self.board:
            self.board.prepare_session()
            self.board.start_stream(buffer_size)
            print(f"[BrainFlowStreamer] Stream started in '{self.mode}' mode at {self.sampling_rate} Hz.")
        else:
            print(f"[BrainFlowStreamer] Mock stream started at {self.sampling_rate} Hz.")

    def get_data(self, num_samples: Optional[int] = None) -> np.ndarray:
        """
        Fetch latest EEG channel data (16, N_samples).

        :param num_samples: Number of latest samples to fetch (fetch all available if None)
        :return: 2D numpy array of shape (16, num_samples) in microvolts
        """
        if self.board:
            if num_samples:
                data = self.board.get_current_board_data(num_samples)
            else:
                data = self.board.get_board_data()
            eeg_data = data[self.eeg_channels, :]
            return eeg_data
        else:
            # Mock data generator (16, num_samples or 500)
            n_pts = num_samples if num_samples else 500
            t = time.time() + np.linspace(0, n_pts / self.sampling_rate, n_pts)
            mock_signal = np.sin(2 * np.pi * 10 * t) * 10.0 + np.random.randn(16, n_pts) * 2.0
            return mock_signal

    def stop_stream(self):
        """Stop acquisition stream and release session."""
        if self.board:
            self.board.stop_stream()
            self.board.release_session()
            print("[BrainFlowStreamer] Stream stopped and session released.")
