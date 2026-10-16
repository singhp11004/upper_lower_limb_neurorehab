"""
BrainFlow Streamer Wrapper for OpenBCI 16-Channel cEEGrid Acquisition.
Supports live hardware (Cyton+Daisy), synthetic streams, and playback files.
"""

import time
import numpy as np
from typing import Optional, Tuple


class BrainFlowStreamer:
    def __init__(self, mode: str = "playback", playback_file: Optional[str] = None, serial_port: Optional[str] = None, lsl_stream_name: str = "aq1"):
        """
        Initialize BrainFlow Streamer.

        :param mode: 'live' (OpenBCI Cyton+Daisy), 'synthetic', 'playback', or 'lsl' (Qneuro H100)
        :param playback_file: Path to CSV playback dataset file for 'playback' mode
        :param serial_port: Serial COM/tty port for live hardware
        :param lsl_stream_name: Name of LSL stream if in 'lsl' mode (default: 'aq1')
        """
        self.mode = mode.lower()
        self.playback_file = playback_file
        self.serial_port = serial_port
        self.lsl_stream_name = lsl_stream_name
        self.lsl_inlet = None
        self.board = None
        self.board_id = None
        self.sampling_rate = 250  # Hz
        self.eeg_channels = list(range(1, 17))  # 16 channels default

        if self.mode == "lsl":
            self._init_lsl()
        else:
            self._init_board()

    def _init_lsl(self):
        try:
            from pylsl import StreamInlet, resolve_byprop, resolve_streams
            streams = resolve_byprop('name', self.lsl_stream_name, timeout=2.0)
            if not streams:
                for fallback in ["aq1", "EEG", "Qneuro_H100_EEG_PPG", "admin_EEG"]:
                    streams = resolve_byprop('name', fallback, timeout=1.0)
                    if streams:
                        print(f"[BrainFlowStreamer] Connected to LSL fallback stream: {fallback}")
                        break
            if not streams:
                all_s = resolve_streams(wait_time=1.5)
                eeg_c = [s for s in all_s if "aq1" in s.name().lower() or "eeg" in s.name().lower()]
                if eeg_c:
                    streams = [eeg_c[0]]

            if streams:
                self.lsl_inlet = StreamInlet(streams[0], max_buflen=360)
                info = self.lsl_inlet.info()
                self.sampling_rate = int(info.nominal_srate()) if info.nominal_srate() > 0 else 250
                print(f"[BrainFlowStreamer] Connected to LSL Stream '{info.name()}' ({info.channel_count()} ch @ {self.sampling_rate} Hz)")
            else:
                print(f"[BrainFlowStreamer] Notice: No active LSL stream found for '{self.lsl_stream_name}'. Running in mock mode.")
        except Exception as e:
            print(f"[BrainFlowStreamer] LSL Init failed ({e}), falling back to mock.")
            self.lsl_inlet = None

    def _init_board(self):
        try:
            from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds  # type: ignore

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
        if self.mode == "lsl":
            print(f"[BrainFlowStreamer] LSL stream active for '{self.lsl_stream_name}'.")
            return

        if self.board:
            try:
                if hasattr(self.board, "is_prepared") and not self.board.is_prepared():
                    self.board.prepare_session()
                elif not hasattr(self.board, "is_prepared"):
                    self.board.prepare_session()
            except Exception as e:
                # Board may already be prepared
                pass
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
        if self.mode == "lsl" and self.lsl_inlet:
            max_s = num_samples if num_samples else 25
            chunk, _ = self.lsl_inlet.pull_chunk(timeout=0.04, max_samples=max_s)
            if chunk:
                arr = np.array(chunk).T  # (n_ch, n_samples)
                # Pad to 16 channels if incoming stream has fewer (e.g. 8-channel Qneuro)
                if arr.shape[0] < 16:
                    padded = np.zeros((16, arr.shape[1]), dtype=arr.dtype)
                    padded[:arr.shape[0], :] = arr
                    return padded
                return arr[:16, :]
            else:
                return np.empty((16, 0))

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
        if self.mode == "lsl":
            self.lsl_inlet = None
            print("[BrainFlowStreamer] LSL stream detached.")
            return

        if self.board:
            try:
                self.board.stop_stream()
            except Exception:
                pass
            try:
                self.board.release_session()
            except Exception:
                pass
            print("[BrainFlowStreamer] Stream stopped and session released.")
