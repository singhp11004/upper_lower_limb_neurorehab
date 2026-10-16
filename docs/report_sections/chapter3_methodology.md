# Chapter 3: Methodology & System Architecture

## 3.1 Hardware Architecture & Dual-Modality Biosignal Ingestion
The system integrates a hierarchical cyber-physical loop accommodating dual research and wearable hardware platforms:
1. **Sensing Subsystem**:
   - **OpenBCI Cyton (8-ch) + Daisy (8-ch)**: Digitizing 16 periauricular cEEGrid channels at $f_s = 250\text{ Hz}$ via 24-bit Texas Instruments ADS1299 ADC.
   - **Qneuro H100 NeuroState**: Wireless Bluetooth RFCOMM Serial Port Profile (SPP) stream delivering 8 channels of 24-bit EEG ($f_s = 250\text{ Hz}$) and 2 channels of 16-bit optical photoplethysmography (PPG). Unpacked via `src/acquisition/qneuro_pipeline.py` and broadcast via Lab Streaming Layer (LSL) stream `aq1`.
2. **Edge Computing Unit**: NVIDIA Jetson Orin Nano (6-core ARM Cortex-A78AE, 8GB LPDDR5) receiving LSL streams via `BrainFlowStreamer` into a thread-safe `CircularRingBuffer` (500 samples window, 25 samples step at 10 Hz / 100 ms cadence).
3. **Actuation Controller**: ESP32-P4 receiving 7-byte binary UART packets at 115200 baud, driving:
   - **Upper-Limb Hand Orthosis**: 5× MG996R metal-gear tendon servos via PCA9685 I2C 16-channel 12-bit PWM driver.
   - **Lower-Limb Leg Bracing**: Dual high-torque DC planetary gear motors via L298N H-bridge driver.

## 3.2 Signal Preprocessing Pipeline
To condition weak electrophysiological potentials ($\pm 5\text{ to } 50\text{ }\mu\text{V}$) and suppress electrode polarization:
- **Zero-Phase Butterworth Filtering**: 4th-order zero-phase IIR bandpass filter ($0.5\text{ to } 45.0\text{ Hz}$) mitigating phase distortion across transient peaks and baseline drifts.
- **50 Hz Powerline Notch Filter**: 2nd-order IIR notch filter ($Q = 30$) sharply attenuating grid interference (>40 dB attenuation).
- **Dynamic Artifact & Lead Rejection**: Dual-stage thresholding (amplitude clamping at $\pm 150\text{ }\mu\text{V}$) combined with variance-based flatline detection in `SignalQualityMonitor` to identify and isolate loose leads.

## 3.3 Feature Extraction & Classification Framework

### 3.3.1 Priority 1: EOG Double-Blink Emergency Veto
- **Montage**: Frontal-temporal differential derivation ($V_{\text{EOG}} = EEG_1 - EEG_2$).
- **Detection Algorithm**: `scipy.signal.find_peaks` with height threshold $+40.0\text{ }\mu\text{V}$ and temporal coincidence window $\Delta t \in [250, 800]\text{ ms}$.
- **Safety Action**: Immediate emergency halt (`0x99`), 500 ms actuator lockout cooldown, overriding all motor commands.

### 3.3.2 Priority 2: High-Gamma Temporalis Clench Trigger
- **Sub-Band Filtering**: $30\text{ to }45\text{ Hz}$ high-gamma extraction over temporal electrodes.
- **Log-Variance Envelope**:
  $$\text{Energy}_{\text{dB}} = 10 \log_{10} \left( \frac{1}{N} \sum_{i=1}^N x[i]^2 + \epsilon \right)$$
- **Calibrated Threshold**: $+10.5\text{ dB}$ over resting baseline, producing Hand Close command (`0x20`) on Upper-Limb Module (`0x01`).

### 3.3.3 Priority 2.5: Sensorimotor Motor Intent (Hand vs. Leg)
- **Spectral Feature Extraction**: Logarithmic power spectral density across Mu ($8\text{--}13\text{ Hz}$) and Beta ($14\text{--}30\text{ Hz}$) bands over central sensorimotor electrodes (Channels 3–4).
- **Multi-Class Classifier**: Random Forest / Linear Discriminant Analysis decoding user movement intent:
  - **Upper-Limb Hand Clench**: Routes to Hand Module (`MODULE_HAND = 0x01`, `CMD_HAND_CLOSE = 0x20` / `CMD_HAND_OPEN = 0x10`).
  - **Lower-Limb Leg Extension**: Routes to Leg Module (`MODULE_LEG = 0x02`, `CMD_STEP_FWD = 0x30`).
- **Dwell Confirmation**: 300 ms dwell requirement preventing accidental trigger from transient movement artifacts.

### 3.3.4 Priority 3: P300 Oddball ERP via SWLDA
- **Feature Extraction**: $250\text{ to }500\text{ ms}$ post-stimulus window downsampled $4\times$.
- **Stepwise Feature Selection**: Forward stepwise selection ($p_{\text{enter}} = 0.10$) isolating optimal spatial-temporal feature subsets.
- **Classification**: Regularized linear discriminant generating continuous posterior confidence scores.

### 3.3.5 Priority 4: Alpha-Band Workload Gating
- Relative alpha power ratio ($8\text{ to }13\text{ Hz}$) gating state machine into Active vs. Rest to prevent accidental command dispatch during cognitive fatigue.

## 3.4 Command Arbitration & Binary UART Communication Protocol
Commands are serialized into a deterministic 7-byte binary packet at 115200 baud:
```
[0xAA] [MODULE] [CMD] [PARAM_HI] [PARAM_LO] [CONFIDENCE] [CRC8_MAXIM]
 Byte 0   Byte 1  Byte 2   Byte 3     Byte 4       Byte 5       Byte 6
```
- **Frame Sync (`0xAA`)**: Unique start-of-frame delimiter.
- **Module ID**: `0x01` (Hand Module), `0x02` (Leg Module).
- **Command ID**: `0x10` (Open), `0x20` (Close), `0x30` (Step Fwd), `0x40` (Step Back), `0x99` (E-Stop).
- **Parameter (16-bit)**: Target servo position or motor speed.
- **Confidence (8-bit)**: Scaled classifier probability ($0\text{--}100\%$).
- **CRC-8/MAXIM**: Polynomial $x^8 + x^5 + x^4 + 1$ guaranteeing frame error detection over physical UART wiring.

