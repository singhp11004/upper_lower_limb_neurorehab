"""
Unit Tests for Biosignal Acquisition Engine (Phase 0).
Tests BrainFlowStreamer, CircularRingBuffer, and SignalQualityMonitor.
"""

import os
import unittest
import numpy as np
from src.acquisition import BrainFlowStreamer, CircularRingBuffer, SignalQualityMonitor


class TestAcquisitionModule(unittest.TestCase):
    def test_ring_buffer(self):
        buf = CircularRingBuffer(n_channels=16, window_sec=2.0, step_sec=0.1, sample_rate=250)
        self.assertFalse(buf.is_ready())

        # Append 500 samples (2.0s)
        samples = np.random.randn(16, 500).astype(np.float32)
        buf.append(samples)

        self.assertTrue(buf.is_ready())
        win = buf.get_latest_window()
        self.assertIsNotNone(win)
        self.assertEqual(win.shape, (16, 500))

    def test_signal_quality_monitor(self):
        sqm = SignalQualityMonitor(n_channels=16)

        # Normal clean signal
        clean_signal = np.random.randn(16, 500) * 10.0
        metrics = sqm.evaluate_window(clean_signal)
        self.assertEqual(metrics["good_channels_count"], 16)

        # Flatline signal on channel 0
        noisy_signal = clean_signal.copy()
        noisy_signal[0, :] = 0.0
        metrics_noisy = sqm.evaluate_window(noisy_signal)
        self.assertEqual(metrics_noisy["channel_status"][0], "DISCONNECTED")

    def test_brainflow_streamer_playback(self):
        playback_file = "data/public_benchmarks/ceegrid_eeg/openbci_ceegrid_16ch_250hz_playback.csv"
        if os.path.exists(playback_file):
            streamer = BrainFlowStreamer(mode="playback", playback_file=playback_file)
            streamer.start_stream()
            data = streamer.get_data(num_samples=250)
            streamer.stop_stream()
            self.assertEqual(data.shape[0], 16)


if __name__ == "__main__":
    unittest.main()
