# Chapter 3: Methodology & System Architecture

## 3.1 Hardware Architecture & Signal Ingestion
The system integrates a hierarchical cyber-physical loop:
1. **Sensing Subsystem**: OpenBCI Cyton (8-ch) + Daisy (8-ch) digitizing 16 periauricular cEEGrid channels at $f_s = 250\text{ Hz}$ (24-bit ADS1299 ADC).
2. **Edge Computing Unit**: NVIDIA Jetson Orin Nano receiving BLE / USB serial streams via `BrainFlowStreamer` into a thread-safe `CircularRingBuffer` (500 samples window, 25 samples step at 10 Hz).
3. **Actuation Controller**: ESP32-P4 receiving 7-byte binary UART packets at 115200 baud, controlling 5× MG996R metal-gear servos via PCA9685 I2C PWM driver and dual high-torque planetary DC motors.

## 3.2 Signal Preprocessing Pipeline
To condition weak periauricular electrophysiological potentials ($\pm 5\text{ to } 50\text{ }\mu\text{V}$):
- **Zero-Phase Butterworth Filtering**: 4th-order zero-phase IIR bandpass filter ($0.5\text{ to } 45.0\text{ Hz}$) mitigating phase distortion across transient ERP peaks.
- **50 Hz Powerline Notch**: 2nd-order IIR notch filter ($Q = 30$) rejecting grid interference.
- **Artifact Rejection Engine**: Dual-stage thresholding (amplitude clamping at $\pm 150\text{ }\mu\text{V}$ and low standard deviation flatline detection).

## 3.3 Feature Extraction & Classification Framework

### 3.3.1 Priority 1: EOG Double-Blink Veto
- Differential temporal montage: $V_{\text{EOG}} = V_{L1} - V_{R1}$.
- Peak detection: `scipy.signal.find_peaks` with height threshold $80\text{ }\mu\text{V}$ and temporal coincidence window $\Delta t \le 500\text{ ms}$.
- Output: Emergency Veto (Command `0x99`).

### 3.3.2 Priority 2: High-Gamma Temporalis Clench
- Sub-band filtering: $30\text{ to }45\text{ Hz}$ high-gamma extraction over lateral temporal electrodes.
- Log-variance computation:
  $$\text{Energy}_{\text{dB}} = 10 \log_{10} \left( \frac{1}{N} \sum_{i=1}^N x[i]^2 + \epsilon \right)$$
- Threshold: $+8.0\text{ dB}$ above resting baseline. Output: Hand Close (`0x20`).

### 3.3.3 Priority 3: P300 Oddball ERP via SWLDA
- Temporal extraction: $250\text{ to }500\text{ ms}$ post-stimulus interval downsampled by $4\times$.
- Stepwise Feature Selection: Forward stepwise linear discriminant selection ($p_{\text{enter}} = 0.10$).
- Inference: $P(y=1|x) = \sigma(w^T x + b) \ge 0.65$. Output: Hand Open (`0x10`).

### 3.3.4 Priority 4: Alpha-Band Workload Gating
- Relative alpha power ratio ($8\text{ to }13\text{ Hz}$) gating state machine into Active vs. Rest to prevent accidental triggers during cognitive fatigue.

## 3.4 Command Arbitration & Binary UART Communication Protocol
Commands are packaged into 7-byte packets with CRC-8/MAXIM checksum:
`[0xAA | Module_ID | Cmd_ID | Param_High | Param_Low | Confidence | CRC8]`
Arbitration enforces priority override: EOG Veto overrides all states instantly with a 500 ms safety lockout cooldown.
