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
        assert win is not None  # pyright type narrowing
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
    def test_qneuro_telemetry_parsing(self):
        from src.acquisition import parse_int24_be, process_packet

        # Test 24-bit integer parsing
        b_zero = bytes([0x00, 0x00, 0x00])
        self.assertEqual(parse_int24_be(b_zero, 0), 0)

        b_pos = bytes([0x00, 0x01, 0x00])  # 256
        self.assertEqual(parse_int24_be(b_pos, 0), 256)

        b_neg = bytes([0xFF, 0xFF, 0xFF])  # -1
        self.assertEqual(parse_int24_be(b_neg, 0), -1)

        b_min = bytes([0x80, 0x00, 0x00])  # -8388608
        self.assertEqual(parse_int24_be(b_min, 0), -8388608)

        # Build synthetic 46-byte Qneuro telemetry packet
        # [0:2] = 0xAA 0x55
        # [2] = packet counter
        # [3:27] = 8 channels x 3 bytes = 24 bytes
        # [27:29] = PPG Red (uint16)
        # [29:31] = PPG IR (uint16)
        # [31:45] = IMU bytes (14 bytes)
        # [45] = checksum (sum(packet[2:45]) & 0xFF)
        packet = bytearray(46)
        packet[0] = 0xAA
        packet[1] = 0x55
        packet[2] = 42  # counter
        # Set EEG ch1 to 1000
        packet[4] = 0x03
        packet[5] = 0xE8
        # Set PPG Red to 50000
        packet[27] = 0xC3
        packet[28] = 0x50
        # Checksum
        packet[45] = sum(packet[2:45]) & 0xFF

        result = process_packet(bytes(packet))
        self.assertIsNotNone(result)
        assert result is not None  # pyright type narrowing
        self.assertEqual(len(result), 10)  # 8 EEG + 2 PPG
        # EEG ch1 raw ADC = 1000, scaled by ADC_TO_UV ≈ 0.02235 µV/LSB
        from src.acquisition.qneuro_pipeline import ADC_TO_UV
        self.assertAlmostEqual(result[0], 1000.0 * ADC_TO_UV, places=2)
        self.assertEqual(result[8], 50000.0)  # PPG Red (no scaling)

        # Invalid checksum should return None
        bad_packet = bytearray(packet)
        bad_packet[45] = (bad_packet[45] + 1) & 0xFF
        self.assertIsNone(process_packet(bytes(bad_packet)))

        # Invalid sync header should return None
        bad_header = bytearray(packet)
        bad_header[0] = 0x00
        self.assertIsNone(process_packet(bytes(bad_header)))

    def test_ring_buffer_wraparound_and_1d(self):
        buf = CircularRingBuffer(n_channels=8, window_sec=1.0, step_sec=0.1, sample_rate=100)
        # 1D single sample append
        sample_1d = np.ones(8, dtype=np.float32) * 5.0
        buf.append(sample_1d)
        self.assertEqual(buf.total_samples_written, 1)

        # Append multi-chunk to trigger wrap-around (capacity is 400 samples)
        large_chunk = np.full((8, 399), 10.0, dtype=np.float32)
        buf.append(large_chunk)
        self.assertEqual(buf.total_samples_written, 400)
        self.assertTrue(buf.is_ready())

        win = buf.get_latest_window()
        self.assertIsNotNone(win)
        assert win is not None  # pyright type narrowing
        self.assertEqual(win.shape, (8, 100))
        np.testing.assert_allclose(win, 10.0)

    def test_signal_quality_monitor_statuses(self):
        sqm = SignalQualityMonitor(n_channels=4, sat_threshold_uv=100.0, flatline_std_uv=0.5)
        # Create test signals:
        # Ch 0: Clean (std ~ 10 uV)
        # Ch 1: Disconnected (flatline std = 0.0 uV)
        # Ch 2: Poor (weak std = 0.3 uV, between 0.1 and 0.5)
        # Ch 3: Saturated (amplitude > 100 uV)
        sig = np.zeros((4, 250))
        sig[0, :] = np.random.randn(250) * 10.0
        sig[1, :] = 0.0
        sig[2, :] = np.random.randn(250) * 0.3
        sig[3, :] = 200.0

        metrics = sqm.evaluate_window(sig)
        self.assertEqual(metrics["channel_status"][0], "GOOD")
        self.assertEqual(metrics["channel_status"][1], "DISCONNECTED")
        self.assertEqual(metrics["channel_status"][2], "POOR")
        self.assertEqual(metrics["channel_status"][3], "SATURATED")


if __name__ == "__main__":
    unittest.main()
