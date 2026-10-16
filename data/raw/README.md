# Raw EEG Datasets Classification & Directory Architecture

This directory stores raw recordings captured directly from the **Qneuro H100** headset (or OpenBCI devices).

To ensure experimental and clinical validity, recordings are strictly divided into **Real Movement (Motor Execution)** and **Imagined Movement (Motor Imagery)**.

---

## 1. Directory Structure

```
data/raw/
├── README.md                          # This architecture definition
├── motor_execution/                   # REAL PHYSICAL MOVEMENTS (Current Dataset)
│   ├── metadata_manifest.json         # Trial log, subject details, timestamp catalog
│   └── qneuro_exec_YYYYMMDD_HHMMSS.csv # Raw stream with synchronized event codes
│
└── motor_imagery/                     # KINESTHETIC MOTOR IMAGERY (Stroke / Rehab Target)
    ├── metadata_manifest.json         # Patient/subject imagery protocol catalog
    └── qneuro_imag_YYYYMMDD_HHMMSS.csv # Imagined movements without overt muscle contraction
```

---

## 2. Why This Distinction Matters

| Dimension | `data/raw/motor_execution/` | `data/raw/motor_imagery/` |
|---|---|---|
| **Movement Type** | **Overt Physical Movement** (Real hand squeeze, leg extension, jaw clench, eye blinks) | **Mental Kinesthetic Imagery** (Imagining movement sensation with zero overt muscle contraction) |
| **Primary Purpose** | System validation, sensorimotor ERD/ERS baseline benchmarking, and hardware calibration | Neurorehabilitation target for hemiparetic stroke / spinal cord injury patients |
| **Neural vs. Muscle Signature** | Robust sensorimotor rhythm desynchronization (mu/beta ERD) + peripheral muscle dynamics | Subtle cortical mu/beta ERD without peripheral EMG activity |
| **Veto Signals** | Ground-truth ocular EOG (double blink) & temporalis EMG (jaw clench) | Calibrated veto thresholds transferred from execution runs |

---

## 3. Event Codes Reference

| Event ID | Event Label | Class Type | Description |
|---|---|---|---|
| `0` | `REST` | Baseline | Eyes open, relaxed fixation crosshair |
| `1` | `DOUBLE_BLINK` | Safety Veto (EOG) | Two deliberate, crisp blinks within 1.0s |
| `2` | `JAW_CLENCH` | Safety Veto (EMG) | Firm molar bite down for 1.5s (Emergency Halt) |
| `3` | `LEFT_HAND_CLENCH` | Upper Limb (Left) | Physical left hand/fist squeeze and relax |
| `4` | `LEFT_LEG_EXTENSION` | Lower Limb (Left) | Physical left leg extension/kick forward and relax |
| `5` | `RIGHT_HAND_CLENCH` | Upper Limb (Right) | Physical right hand/fist squeeze and relax |
| `6` | `RIGHT_LEG_EXTENSION` | Lower Limb (Right) | Physical right leg extension/kick forward and relax |

### Laterality Recording Modes

| `--laterality` Flag | Motor Event IDs Recorded | Use Case |
|---|---|---|
| `bilateral` (default) | 3, 4, 5, 6 | Full bilateral ERD/ERS mapping |
| `left` | 3, 4 | Left hemiparesis rehabilitation (right hemisphere stroke) |
| `right` | 5, 6 | Right hemiparesis rehabilitation (left hemisphere stroke) |

---

## 4. In-Vivo Recorded Datasets Catalog

| Filename | Subject | Paradigm | Duration | Samples | Channels | Sampling Rate | Trials Completed | Status |
|---|---|---|---|---|---|---|---|---|
| `qneuro_sub-01_motor_execution_20261016_162654.csv` | `sub-01` | `motor_execution` (bilateral) | 229.0s (~3.8 min) | 57,250 | 8 EEG | 250.06 Hz | 30 trials (5/class) | **Primary Benchmark Dataset** (Analyzed in Report Chapter 4) |
| `qneuro_sub-01_motor_execution_20261016_160122.csv` | `sub-01` | `motor_execution` (bilateral) | 229.0s (~3.8 min) | 57,250 | 8 EEG | 250.06 Hz | 30 trials (5/class) | Verification Run 1 |
| `qneuro_sub-01_motor_execution_20261016_162551.csv` | `sub-01` | `motor_execution` (bilateral) | 28.7s | 7,175 | 8 EEG | 250.06 Hz | Pilot / Handshake | Initial Stream Sanity Check |

