# 🧠 EEG-Based Exoskeleton Control for Upper- and Lower-Limb Neurorehabilitation

[![Tests](https://img.shields.io/badge/pytest-17%20passed-brightgreen.svg)]()
[![Hardware](https://img.shields.io/badge/Hardware-Qneuro%20H100%20%7C%20OpenBCI%20cEEGrid-blue.svg)]()
[![Target](https://img.shields.io/badge/Target-Jetson%20Orin%20Nano%20%2B%20ESP32--P4-orange.svg)]()

> **Degree Project**: BCSE497J Project-I, B.Tech CSE (AI & Robotics), School of Computer Science and Engineering, VIT Chennai  
> **Team**: Pardeep Singh (23BRS1123) · Aastha Kumari (23BRS1040)  
> **Repository**: [singhp11004/upper_lower_limb_neurorehab](https://github.com/singhp11004/upper_lower_limb_neurorehab)

---

## 📌 Executive Summary

This project implements an end-to-end, edge-deployable Brain-Computer Interface (BCI) system designed for stroke neurorehabilitation. By acquiring biosignals via wearable periauricular / multi-channel headsets (**Qneuro H100 NeuroState** and **OpenBCI Cyton+Daisy with cEEGrid**), the pipeline detects user intent, safeguards the patient with prioritized veto locks, and dispatches real-time actuation packets to upper- and lower-limb robotic exoskeletons.

The complete software stack features:
- **Telemetry Streaming & Ingestion**: Bluetooth RFCOMM SPP direct socket parsing and Lab Streaming Layer (LSL) integration.
- **Signal Preprocessing & Conditioning**: Real-time zero-phase 4th-order Butterworth bandpass (0.5–45 Hz) and 50 Hz IIR notch filter.
- **Multimodal Feature Extraction**: Differential EOG blink detection, high-gamma temporalis EMG jaw-clench burst detection, Welch PSD bandpower, and P300 ERP feature extraction.
- **Hybrid Intent Classification**: Bidirectional Stepwise Linear Discriminant Analysis (SWLDA) with forward selection and backward elimination, plus alpha-band cognitive workload evaluation.
- **5-Level Safety Arbitration**: Hardware emergency stops, priority arbitration with dwell confirmation, and dual upper/lower-limb module command routing.
- **Edge Deployment**: Zero-dependency pure NumPy model execution (<50 µs latency) on NVIDIA Jetson Orin Nano with binary UART packet serialization (CRC-8/MAXIM) to an ESP32-P4 microcontroller.

---

## 🏛️ System Architecture

```
                                [Biosignal Acquisition]
                  Qneuro H100 (8-Ch EEG + PPG)  /  OpenBCI cEEGrid (16-Ch)
                                         │
                         (Bluetooth SPP / LSL / BrainFlow)
                                         ▼
                             [Circular Ring Buffer]
                          2.0s Window @ 100ms Step (250 Hz)
                                         │
                             [Filtering & Conditioning]
                        0.5-45 Hz Bandpass + 50 Hz IIR Notch
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
         [Safety & Intent Features]                     [ERP & Cognitive State]
      • EOG Differential Double Blink                • P300 Downsampled Waveform
      • Temporalis High-Gamma Clench (30-45 Hz)      • Alpha Relative Power (8-13 Hz)
                 │                                               │
                 ▼                                               ▼
     [Veto & Burst Detectors]                        [SWLDA & LDA Classifiers]
   (Threshold & Peak Coincidence)                   (F-test Stepwise Selection)
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                         [5-Level Priority Arbitrator]
              Level 1 (Highest): EOG Double Blink ────→ E-Stop (0x99)
              Level 2: Jaw Clench Burst ──────────────→ Hand Close (0x20)
              Level 2.5: Leg Motor Intent ────────────→ Leg Step Fwd (0x30)
              Level 3: P300 Oddball ERP ──────────────→ Hand Open (0x10)
              Level 4: Cognitive Workload State ──────→ Rest / Active Gate
                                         │
                       [UART Packet Encoder (CRC-8/MAXIM)]
                                         │
                         (UART 115200 Baud / PySerial)
                                         ▼
                            [ESP32-P4 Real-Time MCU]
                            PCA9685 PWM + L298N Drivers
                                         │
                        ┌────────────────┴────────────────┐
                        ▼                                 ▼
              [Upper-Limb Hand]                 [Lower-Limb Leg]
             5x MG996R Tendons                 2x DC Gear Motors
```

---

## 📁 Repository File Inventory

```
.
├── develop_demo.md                 # Complete development roadmap & audit record
├── Software_Development_Roadmap.md # Architectural specification & hardware roadmap
├── build_full_report_docx.py       # Master university thesis DOCX report builder
├── pytest.ini                      # Pytest suite configuration
├── models/
│   ├── swlda_p300_model.joblib     # Pre-trained SWLDA P300 classifier weights
│   └── edge_swlda_weights.json     # Zero-dependency sparse weights for Jetson Orin
├── data/
│   ├── DATASETS_MANIFEST.md        # Public benchmark & data directory documentation
│   └── raw/
│       ├── README.md               # Dataset taxonomy (execution vs. imagery) & event codes
│       ├── motor_execution/        # Physical movement calibration runs (Blink, Clench, Hand, Leg)
│       └── motor_imagery/          # Mental kinesthetic imagery runs for neurorehab
├── src/
│   ├── demo_mvp.py                 # Real-time CLI runner with live ANSI terminal dashboard
│   ├── acquisition/
│   │   ├── qneuro_pipeline.py      # Qneuro H100 Bluetooth SPP parser & LSL outlet (stream 'aq1')
│   │   ├── receive_eeg.py          # LSL receiver with online filtering & CSV recording
│   │   ├── record_prompted_dataset.py # Guided calibration protocol with bilateral laterality
│   │   ├── view_stream.py          # Real-time scrolling Matplotlib 8-channel EEG oscilloscope
│   │   ├── ring_buffer.py          # Thread-safe circular buffer (2s window / 100ms step)
│   │   ├── signal_quality_monitor.py # Impedance proxy & lead detachment detector
│   │   └── brainflow_streamer.py   # Multi-mode acquisition (synthetic, playback, Cyton, LSL)
│   ├── preprocessing/
│   │   ├── filters.py              # Butterworth bandpass, notch, alpha, & gamma sub-bands
│   │   ├── artifact_rejection.py   # Amplitude clipping (±150 µV) & flatline variance rejection
│   │   └── epoch_slicer.py         # Slices continuous stream into 3D epoch tensors
│   ├── features/
│   │   ├── eog_blink_detector.py   # Differential peak detector for emergency stop veto
│   │   ├── jaw_clench_detector.py  # High-gamma variance burst detector
│   │   ├── p300_extractor.py       # Time-locked post-stimulus downsampled ERP extractor
│   │   └── bandpower.py            # Welch PSD relative bandpower (theta/alpha/beta/gamma)
│   ├── classifiers/
│   │   ├── swlda_p300.py           # Bidirectional Stepwise LDA (forward add + backward remove)
│   │   ├── workload_lda.py         # LDA classifier for cognitive fatigue / active workload
│   │   ├── model_manager.py        # Model serialization & Stratified K-Fold validation
│   │   └── export_edge_model.py    # Exporter from scikit-learn models to edge JSON
│   ├── communication/
│   │   ├── packet_encoder.py       # 7-byte binary UART packet serializer with CRC-8/MAXIM
│   │   ├── arbitrator.py           # 5-tier priority state machine with dwell-time confirmation
│   │   └── serial_manager.py       # PySerial driver with ACK timeouts, retries, and console mock
│   ├── edge/
│   │   └── jetson_edge_runner.py   # Ultra-low latency pure NumPy edge inference engine
│   └── analysis/
│       └── generate_report_figures.py # Generates publication figures & validation tables
└── tests/
    ├── test_acquisition.py         # Acquisition, ring buffer, telemetry, and impedance tests
    ├── test_preprocessing.py       # Bandpass, notch, artifact rejection, and slicing tests
    ├── test_features_classifiers.py# EOG, EMG, P300, SWLDA, and Workload tests
    └── test_communication_edge.py  # UART packet CRC, priority veto, and edge inference tests
```

---

## 🚦 Current Stage of the Project

| Milestone | Phase | Status | Details |
|---|---|---|---|
| **Phase 0** | Architecture, BOM & Literature Survey | ✅ **Completed** | Full hardware BOM, feasibility analysis, and cEEGrid suitability report compiled. |
| **Phase 1** | Signal Conditioning Engine | ✅ **Completed** | Production zero-phase IIR filters, dynamic artifact rejection, and circular ring buffer. |
| **Phase 2** | Real-Time MVP & Embedded Edge | ✅ **Completed** | 5-tier Arbitrator, SWLDA with bidirectional pruning, Jetson edge runner, 17/17 tests passing. |
| **Phase 3** | Live Acquisition & Calibration | 🟡 **In Progress (Current)** | Qneuro H100 Bluetooth/LSL pipeline operational; guided calibration protocol ready for subject ingestion. |
| **Phase 4** | Physical Exoskeleton Integration | ⏳ **Upcoming** | ESP32-P4 firmware flashed to drive PCA9685 PWM servos and DC gear motors on the 3D-printed testbed. |
| **Phase 5** | Academic Viva & Thesis Defense | 📝 **Ready** | Full automated DOCX thesis builder (`build_full_report_docx.py`) and high-resolution figures. |

---

## ⚡ Quick Start Guide

### 1. Prerequisites & Environment Setup

```bash
# Clone the repository
git clone git@github.com:singhp11004/upper_lower_limb_neurorehab.git
cd upper_lower_limb_neurorehab

# Install required dependencies
pip install numpy scipy scikit-learn matplotlib pylsl pyserial joblib pytest
```

### 2. Verify Test Suite (100% Pass Rate)

```bash
python3 -m pytest tests/ -v
```

### 3. Run Real-Time BCI Demo (MVP)

You can launch the live MVP immediately using pre-recorded playback, synthetic simulation, or a live wireless stream:

```bash
# Mode A: Synthetic EEG generator (runs standalone without hardware)
python3 src/demo_mvp.py --mode synthetic

# Mode B: Pre-recorded cEEGrid playback stream
python3 src/demo_mvp.py --mode playback

# Mode C: Live Qneuro H100 LSL stream (stream name 'aq1')
python3 src/demo_mvp.py --mode lsl --stream aq1
```

### 4. Live Hardware Ingestion & Calibration Workflow

#### Step 4.1: Stream Live Telemetry from Qneuro H100
Connect to the headset via Bluetooth RFCOMM SPP and publish 250 Hz EEG + PPG to LSL:
```bash
python3 src/acquisition/qneuro_pipeline.py --stream aq1
```

#### Step 4.2: Inspect Live EEG Oscilloscope
In another terminal, display the multi-channel real-time scrolling waveform monitor:
```bash
python3 src/acquisition/view_stream.py --stream aq1
```

#### Step 4.3: Record Guided Calibration Dataset
Execute the automated visual prompt protocol to acquire labeled calibration trials:
```bash
# Bilateral 6-class protocol (Double Blink, Jaw Clench, Left/Right Hand, Left/Right Leg)
python3 src/acquisition/record_prompted_dataset.py --stream aq1 --laterality bilateral --trials-per-class 10

# Hemiparetic single-side protocol (e.g. for left-hemiparesis rehab)
python3 src/acquisition/record_prompted_dataset.py --stream aq1 --laterality left --trials-per-class 10
```

Raw session CSVs and session metadata are saved automatically under `data/raw/motor_execution/`.

---

## 🛡️ Safety & Priority Arbitration Engine

Exoskeletons interacting with impaired limbs must prioritize safety above all actuation commands. The `Arbitrator` enforces this through a 5-tier priority cascade:

| Priority | Signal Source | Neural / Physiological Mechanism | Dispatched Command | Safety Lockout / Constraints |
|:---:|---|---|:---:|---|
| **Level 1** *(Highest)* | **EOG Double-Blink** | Rapid dual ocular dipole deflection ($>80\,\mu\text{V}$, 500 ms window) | `0x99` **Emergency Stop** | Overrides all commands; freezes motors immediately; imposes 500 ms lockout. |
| **Level 2** | **Temporalis Jaw Clench** | High-gamma ($30\text{--}45\,\text{Hz}$) EMG burst power | `0x20` **Hand Close** | Requires 300 ms dwell confirmation to prevent accidental spasm actuation. |
| **Level 2.5** | **Leg Motor Intent** | Sensorimotor beta desynchronization / leg intention cue | `0x30` **Leg Step Forward** | Requires 300 ms dwell confirmation; routes to Leg Module (`0x02`). |
| **Level 3** | **P300 Oddball ERP** | Centroparietal P300 positive deflection ($250\text{--}500\,\text{ms}$) | `0x10` **Hand Open** | Activated when SWLDA confidence $\ge 0.65$ across repeated epochs. |
| **Level 4** *(Lowest)* | **Cognitive Workload** | Temporal alpha ($8\text{--}13\,\text{Hz}$) bandpower | State Gate | Inhibits high-effort triggers when subject experiences cognitive fatigue. |

---

## 📡 Serial Actuation Protocol (Jetson → ESP32-P4)

Commands are serialized into a fixed **7-byte binary UART frame** at 115200 baud:

```
[0xAA] [MODULE] [CMD] [PARAM_HI] [PARAM_LO] [CONFIDENCE] [CRC8_MAXIM]
 Byte 0   Byte 1  Byte 2   Byte 3     Byte 4       Byte 5       Byte 6
```

- **Header (`0xAA`)**: Frame synchronization delimiter.
- **Module ID**: `0x01` (Hand Module), `0x02` (Leg Module).
- **Command ID**: `0x10` (Open), `0x20` (Close), `0x30` (Step Fwd), `0x40` (Step Back), `0x99` (Emergency Stop).
- **Parameter (16-bit)**: Actuation angle or speed (big-endian).
- **Confidence (8-bit)**: Scaled classifier probability ($0\text{--}100\%$).
- **CRC-8/MAXIM**: Hardware polynomial $x^8 + x^5 + x^4 + 1$ ensuring noise rejection across the physical serial link.

---

## 👥 Authors & Academic Affiliation

- **Pardeep Singh** — Reg. No. `23BRS1123`  
  School of Computer Science and Engineering, VIT Chennai  
  Email: `pardeep.singh2023@vitstudent.ac.in`
- **Aastha Kumari** — Reg. No. `23BRS1040`  
  School of Computer Science and Engineering, VIT Chennai  
  Email: `aastha.kumari2023@vitstudent.ac.in`

**Faculty Guide**: Advanced Brain-Computer Interface & Rehabilitation Robotics Group, VIT Chennai.
