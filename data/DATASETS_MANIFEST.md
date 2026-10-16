# 📊 Project1 Dataset Directory & Public Benchmark Manifest

> **Project**: EEG-Based Exoskeleton Control for Upper- and Lower-Limb Neurorehabilitation
> **Repository Location**: `file:///home/singhp11004/vitChennai/project1/project1/data/`

---

## 1. Data Directory Architecture

Aligning with Section 6 of [`Software_Development_Roadmap.md`](file:///home/singhp11004/vitChennai/project1/project1/Software_Development_Roadmap.md), the dataset storage hierarchy is organized as follows:

```
project1/data/
├── raw/                                      # [Phase 0 / Live Capture] Raw 16-ch OpenBCI Cyton+Daisy binary/CSV recordings
├── processed/                                # [Phase 1 / 2] Filtered, notch-applied, and epoched feature arrays (.npy / .npz)
├── public_benchmarks/                        # [Phase 1 / 2 Benchmarking] Pre-recorded public EEG datasets for offline dev
│   ├── p300/                                 # P300 ERP Oddball benchmark datasets (SWLDA classifier training)
│   │   └── p300_oddball_16ch_250hz.csv       # 16-channel 250 Hz P300 ERP time-locked benchmark stream
│   ├── ceegrid_eeg/                          # 16-channel periauricular cEEGrid stream playback
│   │   └── openbci_ceegrid_16ch_250hz_playback.csv  # BrainFlow PlaybackFileBoard compatible stream
│   └── eog_emg_artifacts/                    # PhysioNet EDF files for EOG double-blink & high-gamma jaw clench
│       └── MNE-eegbci-data/files/eegmmidb/1.0.0/ (12 EDF files: S001R01-R06, S002R01-R06)
└── DATASETS_MANIFEST.md                      # This documentation
```

---

## 2. Public Benchmark Dataset Inventory

| Dataset Name | Subdirectory | Paradigm / Signal Target | File Format & Size | Roadmap Phase Target |
|---|---|---|---|---|
| **PhysioNet EEG Motor & Artifact Database (eegmmidb)** | `public_benchmarks/eog_emg_artifacts/` | Eye-blink EOG veto tuning & motor/jaw-clench artifact rejection | 12 `.edf` files (S001, S002; 19.6 MB total) | **Phase 1 (Artifact Rejection)** & **Phase 2A (Blink-Veto Thresholding)** |
| **P300 Oddball ERP Benchmark** | `public_benchmarks/p300/` | P300 stimulus time-locked ERP template matching | `p300_oddball_16ch_250hz.csv` (16-ch @ 250 Hz) | **Phase 2A (P300 Extractor)** & **Phase 2B (SWLDA Classifier)** |
| **OpenBCI cEEGrid Stream Benchmark** | `public_benchmarks/ceegrid_eeg/` | 16-channel periauricular streaming playback via BrainFlow | `openbci_ceegrid_16ch_250hz_playback.csv` | **Phase 1 (BrainFlow Ring Buffer & Streaming)** |

---

## 2.1 In-Vivo Empirical Calibration Datasets (Qneuro H100)

| Dataset Name | Subdirectory | Paradigm / Signal Target | File Format & Size | Roadmap Phase Target |
|---|---|---|---|---|
| **Qneuro H100 Bilateral Motor Execution Session** | `raw/motor_execution/` | Bilateral Real Movements (Double Blink, Jaw Clench, Hand, Leg, Rest) | `qneuro_sub-01_motor_execution_20261016_162654.csv` (8-ch @ 250 Hz, 57,250 samples, 6.3 MB) | **Phase 3 (Live Acquisition & Calibration)** & **Phase 4 (Actuator Loop)** |
| **Session Metadata & Trial Timestamps** | `raw/motor_execution/` | JSON metadata, channel config, sampling rate, trial-by-trial event timing | `qneuro_sub-01_motor_execution_20261016_162654_metadata.json` (6.9 KB) | **Phase 3 / 4 Analysis & Validation** |

---

## 3. How to Load and Use Datasets in Python Scripts

### 3.1 Loading PhysioNet EOG/EMG Data with MNE-Python (Phase 1/2)

```python
import mne

# Load Subject 1 Run 1 (Resting baseline & Eye Blinks)
edf_path = "data/public_benchmarks/eog_emg_artifacts/MNE-eegbci-data/files/eegmmidb/1.0.0/S001/S001R01.edf"
raw = mne.io.read_raw_edf(edf_path, preload=True)

# Bandpass filter 0.5 - 45 Hz per roadmap spec
raw.filter(l_freq=0.5, h_freq=45.0)
raw.notch_filter(freqs=50.0)

print(f"Loaded EEG duration: {raw.times[-1]}s at {raw.info['sfreq']} Hz")
```

### 3.2 Loading P300 Oddball Stream for SWLDA Training (Phase 2B)

```python
import pandas as pd
import numpy as np

# Load P300 ERP benchmark CSV
df = pd.read_csv("data/public_benchmarks/p300/p300_oddball_16ch_250hz.csv")

# Extract 16 EEG channels and stimulus trigger labels
eeg_channels = [col for col in df.columns if 'cEEGrid' in col]
eeg_data = df[eeg_channels].values
triggers = df['Trigger_Target'].values

print(f"EEG shape: {eeg_data.shape}, Total target stimuli: {np.sum(triggers)}")
```

### 3.3 Streaming cEEGrid Data with BrainFlow `PlaybackFileBoard` (Phase 1)

```python
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

params = BrainFlowInputParams()
params.file = "data/public_benchmarks/ceegrid_eeg/openbci_ceegrid_16ch_250hz_playback.csv"

# Use BrainFlow playback board to simulate 250 Hz live stream without hardware attached
board = BoardShim(BoardIds.PLAYBACK_FILE_BOARD.value, params)
board.prepare_session()
board.start_stream()

# Fetch latest 2-second buffer window (500 samples @ 250 Hz)
data = board.get_current_board_data(500)
board.stop_stream()
board.release_session()
```
