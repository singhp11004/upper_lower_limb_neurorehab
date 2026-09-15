"""
Unit Tests for Preprocessing Engine (Phase 1).
Tests EEGFilterPipeline, ArtifactRejectionEngine, and EpochSlicer.
"""

import unittest
import numpy as np
from src.preprocessing import EEGFilterPipeline, ArtifactRejectionEngine, EpochSlicer


class TestPreprocessingModule(unittest.TestCase):
    def test_filter_pipeline(self):
        pipeline = EEGFilterPipeline(sample_rate=250, lowcut=0.5, highcut=45.0, notch_freq=50.0)

        # 16 channels, 1000 samples (4s)
        t = np.linspace(0, 4, 1000)
        signal = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 50 * t)  # 10Hz + 50Hz notch
        signal_16ch = np.tile(signal, (16, 1))

        filtered = pipeline.process(signal_16ch)
        self.assertEqual(filtered.shape, (16, 1000))

        # Check alpha extraction
        alpha = pipeline.extract_alpha_band(signal_16ch)
        self.assertEqual(alpha.shape, (16, 1000))

        # Check high-gamma extraction
        gamma = pipeline.extract_high_gamma_band(signal_16ch)
        self.assertEqual(gamma.shape, (16, 1000))

    def test_artifact_rejection(self):
        engine = ArtifactRejectionEngine(amplitude_threshold_uv=150.0)

        # Clean epoch
        epoch_clean = np.random.randn(16, 500) * 10.0
        cleaned, meta = engine.clean_epoch(epoch_clean)
        self.assertFalse(meta["is_rejected"])

        # Spiked epoch (> 150 uV)
        epoch_spike = epoch_clean.copy()
        epoch_spike[2, 100] = 250.0
        cleaned_spike, meta_spike = engine.clean_epoch(epoch_spike)
        self.assertTrue(meta_spike["is_rejected"])

    def test_epoch_slicer(self):
        slicer = EpochSlicer(window_sec=2.0, step_sec=0.1, sample_rate=250)
        signal_10s = np.random.randn(16, 2500)  # 10s = 2500 samples

        epochs = slicer.slice_signal(signal_10s)
        # (2500 - 500) / 25 + 1 = 81 epochs
        self.assertEqual(epochs.shape[0], 81)
        self.assertEqual(epochs.shape[1], 16)
        self.assertEqual(epochs.shape[2], 500)


if __name__ == "__main__":
    unittest.main()
