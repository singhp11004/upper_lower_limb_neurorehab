# Chapter 4: Experimental Results & Discussion (Benchmark Evaluation)

## 4.1 Electrophysiological Preprocessing and Signal Conditioning
The zero-phase IIR Butterworth filter ($0.5–45\text{ Hz}$) combined with a $50\text{ Hz}$ notch filter ($Q = 30$) successfully suppressed ambient powerline hum while preserving ERP peak timing and signal morphology.

![Figure 4.1: Power Spectral Density Raw vs Filtered](../../results/figures/fig_4_1_raw_vs_filtered_psd.png)

*Figure 4.1: Power spectral density before and after zero-phase filtering showing sharp 50 Hz line hum attenuation (>40 dB rejection) across temporal channels.*

## 4.2 P300 Evoked Response & Classification Benchmarks
Grand average ERP waveforms computed across target and non-target epochs revealed a distinct positive deflection occurring at approximately $350\text{ ms}$ post-stimulus with a peak amplitude of $+4.5\text{ }\mu\text{V}$.

![Figure 4.2: P300 ERP Grand Average](../../results/figures/fig_4_2_p300_erp_grand_average.png)

*Figure 4.2: Grand average ERP waveform indicating differential response in the 250–500 ms feature extraction window time-locked to oddball stimulus.*

The Stepwise Linear Discriminant Analysis (SWLDA) classifier isolated 30 optimal spatio-temporal features, outperforming standard full-feature LDA.

![Figure 4.3: Confusion Matrices Across Classifiers](../../results/figures/fig_4_3_confusion_matrices_all.png)

*Figure 4.3: Confusion matrices for SWLDA P300 target detection (left) and Alpha Workload State classification (right).*

![Figure 4.4: ROC Curves](../../results/figures/fig_4_4_roc_precision_recall.png)

*Figure 4.4: Receiver Operating Characteristic (ROC, Panel 1) and Precision-Recall (PR, Panel 2) curves demonstrating SWLDA (AUC = 0.884) superiority over unregularized LDA (AUC = 0.812).*

## 4.3 Biosignal Detectors: EOG Double-Blink & Jaw-Clench
The differential periauricular EOG montage achieved rapid double-blink detection within $12.5\text{ ms}$ of the second peak with zero false alarms during resting baseline.

![Figure 4.5: EOG Double-Blink Veto Trace](../../results/figures/fig_4_5_eog_blink_veto_trace.png)

*Figure 4.5: Periauricular differential EOG trace showing threshold crossing and immediate veto lockout initialization.*

Intentional isometric temporalis jaw-clenching produced a massive surge in high-gamma ($30–45\text{ Hz}$) spectral energy exceeding $+10.5\text{ dB}$ over resting baseline.

![Figure 4.6: High-Gamma Spectrogram](../../results/figures/fig_4_6_jaw_clench_stft_spectrogram.png)

*Figure 4.6: STFT spectrogram demonstrating intense 30–45 Hz spectral power elevation during intentional temporalis clenching.*

## 4.4 System Latency & False Positive Stability
End-to-end processing across all stages completed in under $10\text{ ms}$ (total computational latency: $9.81\text{ ms}$), providing over $10\times$ headroom within the $100\text{ ms}$ soft real-time budget. Longitudinal evaluation over continuous 10-minute resting protocols demonstrated that the stateful 300 ms dwell confirmation gate suppressed spurious triggers to only 4 events (0.45 triggers/min, effective FPR = 1.8%), meeting the clinical safety requirement (< 3.0%).

### Table 4.1: Classifier Performance Summary Matrix (Benchmark Evaluation)
| Paradigm | Target Classes | Algorithm / Method | Accuracy (%) | Precision | Recall | F1-Score | AUC-ROC | Cohen's $\kappa$ |
|---|---|---|---|---|---|---|---|---|
| **SWLDA P300** | Target vs Non-Target | Stepwise LDA (30 feats) | **86.0%** | 0.756 | 0.825 | 0.789 | 0.884 | 0.682 |
| **Jaw-Clench EMG** | Clench vs Relaxed | High-Gamma Power (+10.5 dB) | **96.5%** | 0.952 | 0.980 | 0.966 | 0.988 | 0.930 |
| **Workload LDA** | Low vs High Cognitive Load | Alpha Log-Power LDA | **86.2%** | 0.861 | 0.847 | 0.854 | 0.895 | 0.724 |
| **EOG Blink Veto** | Double-Blink vs Random Eye Movements | Differential Peak Threshold | **98.5%** | 0.978 | 0.992 | 0.985 | — | — |

### Table 4.2: Five-Fold Stratified Cross-Validation Results Breakdown
| Fold | SWLDA P300 Accuracy (%) | SWLDA F1-Score | Workload LDA Accuracy (%) | Workload F1-Score |
|---|---|---|---|---|
| **Fold 1** | 85.5% | 0.782 | 87.5% | 0.868 |
| **Fold 2** | 88.2% | 0.814 | 85.0% | 0.842 |
| **Fold 3** | 84.2% | 0.765 | 86.2% | 0.855 |
| **Fold 4** | 86.8% | 0.798 | 87.5% | 0.870 |
| **Fold 5** | 85.5% | 0.786 | 85.0% | 0.840 |
| **Mean ± Std** | **86.0 ± 1.5%** | **0.789 ± 0.018** | **86.2 ± 1.2%** | **0.855 ± 0.014** |

### Table 4.3: End-to-End Computational Latency Breakdown Against 100 ms Real-Time Budget
| Processing Stage | Implementation / Module | Mean Latency (ms) | Std Dev (ms) | Budget Allocation (ms) | Headroom Factor |
|---|---|---|---|---|---|
| **LSL Ingestion & Buffering** | `BrainFlowStreamer` / RingBuffer | 0.42 ms | ±0.08 ms | 10.0 ms | 23.8× |
| **Digital Filtering (BP + Notch)** | `scipy.signal.lfilter` (Zero-phase) | 1.85 ms | ±0.21 ms | 20.0 ms | 10.8× |
| **Artifact Rejection & SQM** | `SignalQualityMonitor` | 0.65 ms | ±0.11 ms | 10.0 ms | 15.4× |
| **Feature Extraction (P300+Alpha+EMG)** | `mne_features` + NumPy Vectorized | 3.12 ms | ±0.34 ms | 25.0 ms | 8.0× |
| **Edge SWLDA + LDA Classification** | `JetsonEdgeRunner` (Dot-product) | 0.048 ms | ±0.006 ms | 5.0 ms | 104.2× |
| **Priority Arbitration & Dwell Gate** | `Arbitrator` state machine | 0.18 ms | ±0.03 ms | 5.0 ms | 27.8× |
| **Packet Encoding & CRC-8** | `PacketEncoder` (7-byte binary) | 0.042 ms | ±0.005 ms | 5.0 ms | 119.0× |
| **UART Transmission (115200 baud)** | `pyserial` hardware write | 3.50 ms | ±0.15 ms | 20.0 ms | 5.7× |
| **Total End-to-End Latency** | Full pipeline cycle | **9.81 ms** | **±0.58 ms** | **100.0 ms** | **10.2× Headroom** |
