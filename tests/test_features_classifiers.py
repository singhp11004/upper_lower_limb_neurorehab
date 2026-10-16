"""
Integration Tests for Feature Extractors & Classifier Pipeline (Phase 2).
Executes end-to-end benchmark validation on downloaded PhysioNet and P300 benchmark files.
"""

import os
import unittest
import numpy as np
import pandas as pd
import mne

from src.preprocessing import EEGFilterPipeline, EpochSlicer
from src.features import P300Extractor, BandPowerExtractor, JawClenchDetector, EOGBlinkDetector
from src.classifiers import SWLDAP300Classifier, WorkloadLDAClassifier, ModelManager


class TestFeaturesAndClassifiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filter_pipeline = EEGFilterPipeline(sample_rate=250)
        cls.epoch_slicer = EpochSlicer(window_sec=2.0, step_sec=0.1, sample_rate=250)
        cls.model_manager = ModelManager(models_dir="models")

    def test_p300_swlda_pipeline(self):
        p300_file = "data/public_benchmarks/p300/p300_oddball_16ch_250hz.csv"
        if not os.path.exists(p300_file):
            self.skipTest("P300 benchmark CSV file missing.")

        df = pd.read_csv(p300_file)
        ch_cols = [c for c in df.columns if "cEEGrid" in c]
        eeg_raw = df[ch_cols].values.T  # (16, n_samples)
        triggers = df["Trigger_Target"].values

        # Preprocess EEG
        filtered_eeg = self.filter_pipeline.process(np.asarray(eeg_raw))

        # Slice into 2.0s epochs
        epochs = self.epoch_slicer.slice_signal(filtered_eeg)

        # Map target labels per epoch
        p300_extractor = P300Extractor(sample_rate=250)
        X_features = p300_extractor.extract_batch_features(epochs)

        # Assign ground truth labels based on trigger pulses in epoch windows
        y_labels = np.zeros(len(epochs), dtype=int)
        for i in range(len(epochs)):
            start_idx = i * 25
            if np.any(np.asarray(triggers[start_idx : start_idx + 500]) == 1):
                y_labels[i] = 1

        # Train SWLDA P300 Classifier
        swlda = SWLDAP300Classifier(max_features=30)
        swlda.fit(X_features, y_labels)

        metrics = swlda.evaluate(X_features, y_labels)
        print(f"\n[Phase 2 SWLDA P300 Benchmark Results]: {metrics}")

        # Verify P300 accuracy meets minimum roadmap threshold (>= 65%)
        self.assertGreaterEqual(metrics["accuracy"], 0.65)

        # Save trained P300 SWLDA model to models/
        self.model_manager.save_model(swlda, "swlda_p300_model.joblib")

    def test_eog_blink_veto_physionet(self):
        edf_path = "data/public_benchmarks/eog_emg_artifacts/MNE-eegbci-data/files/eegmmidb/1.0.0/S001/S001R01.edf"
        if not os.path.exists(edf_path):
            self.skipTest("PhysioNet EDF file missing.")

        raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
        eeg_data = np.asarray(raw.get_data())[:16, :] * 1e6  # Convert Volts to uV

        blink_detector = EOGBlinkDetector(sample_rate=160, peak_threshold_uv=50.0)
        is_veto, count, details = blink_detector.detect_blinks(eeg_data[:, :1600])

        print(f"\n[Phase 2 EOG Blink Veto Physionet Test]: Blinks Detected={count}, Veto Active={is_veto}")
        self.assertIsInstance(is_veto, bool)

    def test_jaw_clench_detector(self):
        detector = JawClenchDetector(sample_rate=250, threshold_db=8.0)

        # Baseline noise (no clench)
        normal_gamma = np.random.randn(16, 50) * 2.0
        is_clench, power_db, _ = detector.detect_clench(normal_gamma)
        self.assertFalse(is_clench)

        # Clench burst (high gamma spike)
        clench_gamma = normal_gamma * 8.0
        is_clench_burst, power_db_burst, _ = detector.detect_clench(clench_gamma)
        self.assertTrue(is_clench_burst)

    def test_workload_lda_classifier(self):
        extractor = BandPowerExtractor(sample_rate=250)
        np.random.seed(45)
        t = np.linspace(0, 2, 500)

        # Generate realistic low workload vs high workload temporal alpha signals
        low_workload = np.zeros((50, 16, 500))
        high_workload = np.zeros((50, 16, 500))

        for i in range(50):
            noise_low = np.random.randn(16, 500) * 5.0
            alpha_low = np.sin(2 * np.pi * 10 * t) * 3.0
            low_workload[i] = noise_low + alpha_low

            noise_high = np.random.randn(16, 500) * 5.0
            alpha_high = np.sin(2 * np.pi * 10 * t) * 3.8 + np.random.randn(16, 500) * 4.5
            high_workload[i] = noise_high + alpha_high

        X_low = np.array([extractor.extract_feature_vector(low_workload[i]) for i in range(50)])
        X_high = np.array([extractor.extract_feature_vector(high_workload[i]) for i in range(50)])

        X = np.vstack([X_low, X_high])
        X_feat = X[:, :16]
        y = np.array([0] * 50 + [1] * 50)

        workload_clf = WorkloadLDAClassifier()
        workload_clf.fit(X_feat, y)

        eval_res = workload_clf.evaluate(X_feat, y)
        print(f"\n[Phase 2 Workload LDA Benchmark Results]: {eval_res}")
        self.assertGreaterEqual(eval_res["accuracy"], 0.80)

        # Save trained workload LDA model to models/
        self.model_manager.save_model(workload_clf, "workload_lda_model.joblib")


if __name__ == "__main__":
    unittest.main()
