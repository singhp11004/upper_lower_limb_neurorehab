# Chapter 5: In-Vivo Validation on Qneuro H100 Headset

This chapter presents the comprehensive empirical validation of the complete neurorehabilitation pipeline against in-vivo electrophysiological data acquired continuously at 250 Hz from a healthy human participant using the wireless 8-channel Qneuro H100 NeuroState headset. This validation represents a critical advancement beyond the benchmark dataset evaluations presented in Chapter 4, demonstrating real-world performance under actual wireless acquisition conditions with electrode impedance variability, participant movement artifacts, and live Bluetooth telemetry latency.

## 5.1 Live Data Acquisition Protocol and Experimental Setup
The Qneuro H100 NeuroState headset was connected to the host system via Bluetooth RFCOMM Serial Port Profile (SPP). The custom `qneuro_pipeline.py` parser ingested raw 24-bit ADC telemetry frames, reconstructed 8-channel EEG samples and 2-channel PPG samples, and published them via Lab Streaming Layer (LSL) under stream name `aq1`. A guided calibration protocol (`record_prompted_dataset.py`) was executed to acquire labeled trials across 6 motor conditions.

### Table 5.1: Qneuro H100 Live Acquisition Session Parameters and Dataset Statistics
| Parameter | Value |
|---|---|
| **Participant Identifier** | `sub-01` (healthy adult, right-hand dominant) |
| **Headset Hardware** | Qneuro H100 NeuroState (8-ch EEG + 2-ch PPG) |
| **ADC Resolution** | 24-bit Texas Instruments ADS1299 |
| **Sampling Rate** | 250 Hz |
| **Transport Protocol** | Bluetooth RFCOMM SPP (wireless) |
| **Total Acquired Samples** | 57,250 samples |
| **Session Duration** | 229 seconds (3 min 49 sec) |
| **Number of Randomized Trials** | 30 complete trials |
| **Motor Conditions (6-class)** | REST, L-HAND, R-HAND, L-LEG, R-LEG, DOUBLE-BLINK, JAW-CLENCH |
| **Active Physiological Channels** | Channels 1–5 (frontal, temporal, central) |
| **Rejected Noisy Channels** | Channels 6–8 (high impedance / drift) |
| **Calibrated EOG Blink Threshold** | +40.0 µV (differential) |
| **Calibrated Jaw Clench Threshold** | +10.5 dB (high-gamma envelope) |

Figures 5.1–5.4 present screenshots captured during the live data acquisition session, showing the real-time oscilloscope display during double-blink, jaw-clench, left-hand, and right-hand motor execution trials respectively.

![Figure 5.1: Double-Blink Acquisition](../../screenshots/data_acq/double_blink.png)

*Figure 5.1: Data Acquisition Screenshot — Double-Blink EOG Recording Session (real-time 8-channel oscilloscope view showing characteristic biphasic frontal dipole deflections during voluntary rapid double-blink execution).*

![Figure 5.2: Jaw-Clench Acquisition](../../screenshots/data_acq/jaw_clench.png)

*Figure 5.2: Data Acquisition Screenshot — Jaw-Clench EMG Recording Session (real-time oscilloscope view showing high-amplitude temporalis EMG bursts during sustained isometric mandible clenching).*

![Figure 5.3: Left-Hand Motor Execution Acquisition](../../screenshots/data_acq/left_hand.png)

*Figure 5.3: Data Acquisition Screenshot — Left-Hand Motor Execution Recording Session (real-time oscilloscope view during voluntary left-hand clenching showing sensorimotor rhythm modulation).*

![Figure 5.4: Right-Hand Motor Execution Acquisition](../../screenshots/data_acq/right_hand.png)

*Figure 5.4: Data Acquisition Screenshot — Right-Hand Motor Execution Recording Session (real-time oscilloscope view during voluntary right-hand clenching with contralateral sensorimotor desynchronization).*

## 5.2 Continuous Multi-Channel Signal Conditioning
The raw 24-bit ADS1299 ADC output exhibited positive DC offsets (~1,070–1,260 µV) on physiological channels (Channels 1–5). The 4th-order Butterworth bandpass filter (0.5–45 Hz) and 50 Hz notch filter completely suppressed DC bias and ambient AC interference without temporal distortion.

![Figure 5.5: Qneuro Raw vs Filtered Traces](../../results/figures/fig_5_1_qneuro_raw_vs_filtered_traces.png)

*Figure 5.5: Continuous 8-channel EEG comparison showing raw ADC values (left) and zero-phase preprocessed waveforms (right).*

## 5.3 Spectral Power and Time-Frequency Signatures
Power spectral density (PSD) and STFT spectrograms across all 6 active conditions revealed clear physiological modulation unique to each motor paradigm:
- **Temporalis Jaw Clench**: Exhibited a massive spectral power surge (>20 dB elevation) across the 30–45 Hz high-gamma EMG band, with peak energy concentrated on temporal electrodes (Channels 1–2).
- **Frontal Double Blink**: Produced distinct low-frequency (<5 Hz) biphasic potential shifts characteristic of corneal-retinal dipole rotation, cleanly separable from EEG background activity.
- **Motor Execution (Hand/Leg)**: Showed Event-Related Desynchronization (ERD) in sensorimotor Mu (8–13 Hz) and Beta (14–30 Hz) bands over central channels (Channels 3–4), consistent with Penfield’s motor homunculus somatotopic organization.

![Figure 5.6: Qneuro PSD Across Conditions](../../results/figures/fig_5_2_qneuro_psd_by_condition.png)

*Figure 5.6: Power spectral density across experimental conditions for frontal/temporal (left) and central sensorimotor (right) channels.*

![Figure 5.7: STFT Spectrograms](../../results/figures/fig_5_3_qneuro_time_frequency_spectrograms.png)

*Figure 5.7: Multi-panel STFT spectrograms demonstrating distinct spectral signatures for Rest, Jaw Clench, Double Blink, and Hand Clench conditions.*

## 5.4 Veto and Safety Interrupt Calibration on Headset Montage
Empirical threshold tuning on participant data demonstrated clean artifact separation for both safety-critical biosignal channels:

### 5.4.1 EOG Double-Blink Emergency Veto (Priority 1)
The differential montage ($EEG_1 - EEG_2$) established an optimal threshold of $+40.0\text{ }\mu\text{V}$, yielding 100% true positive blink detection with zero false activations during resting baseline.

![Figure 5.8: Frontal EOG Calibration](../../results/figures/fig_5_4_qneuro_eog_double_blink_calibration.png)

*Figure 5.8: Continuous differential EOG trace (top) and zoomed dual-peak blink waveform with +40.0 µV threshold markers (bottom).*

### 5.4.2 Temporalis EMG Jaw-Clench Safety Interrupt (Priority 2)
The high-gamma envelope achieved complete separation with a $+10.5\text{ dB}$ threshold, producing 100% sensitivity and 0.0% false alarm rate over the entire 229-second recording session.

![Figure 5.9: Temporalis EMG Clench Calibration](../../results/figures/fig_5_5_qneuro_jaw_clench_emg_calibration.png)

*Figure 5.9: Continuous high-gamma envelope (top) and probability density distribution (bottom) showing unambiguous separation between Rest and Jaw Clench states.*

## 5.5 Sensorimotor Rhythm ERD and Multi-Class Movement Classification
Evaluation of sensorimotor Mu (8–13 Hz) and Beta (14–30 Hz) bands confirmed robust Event-Related Desynchronization during active upper and lower limb movements.

![Figure 5.10: Sensorimotor Mu/Beta ERD Profiles](../../results/figures/fig_5_6_qneuro_sensorimotor_mu_beta_erd.png)

*Figure 5.10: Distribution of sensorimotor Mu (8–13 Hz) and Beta (14–30 Hz) power showing significant suppression (ERD) during Hand Clench and Leg Extension vs. Rest.*

Using 5-fold stratified cross-validation on sliding 1.5-second windows (524 augmented epochs):
- **3-Class Movement Intent (REST vs. HAND CLENCH vs. LEG EXTENSION)**:
  - **Linear Discriminant Analysis (LDA)**: **75.8% accuracy** (Macro F1 = 0.724, Chance = 33.3%)
  - **Random Forest Ensemble**: **87.0% accuracy** (Macro F1 = 0.841, Chance = 33.3%)
- **5-Class Lateralized Movement Intent (REST vs. L-HAND vs. R-HAND vs. L-LEG vs. R-LEG)**:
  - **Random Forest**: **83.8% accuracy** (Cohen's $\kappa = 0.771$, Chance = 20.0%)

![Figure 5.11: Motor Intent Confusion Matrices](../../results/figures/fig_5_7_qneuro_motor_intent_confusion_matrices.png)

*Figure 5.11: 3-Class movement intent confusion matrices for LDA (left, 75.8%) and Random Forest (right, 87.0%) across 5-fold cross-validation.*

![Figure 5.12: 5-Class Lateralized Confusion Matrix](../../results/figures/fig_5_8_qneuro_lateralized_5class_confusion_matrix.png)

*Figure 5.12: 5-Class lateralized confusion matrix demonstrating strong diagonal dominance across upper and lower limb motions (Random Forest, 83.8% accuracy).*

![Figure 5.13: ROC & PR Curves](../../results/figures/fig_5_9_qneuro_roc_and_pr_curves.png)

*Figure 5.13: One-vs-Rest ROC curves (AUC > 0.95 across all classes) and Precision-Recall curves for movement intent classification.*

## 5.6 Channel Quality Diagnostics and Feature Importance
Automated Signal Quality Monitoring (SQM) accurately identified Channels 1–5 as optimal physiological channels while isolating high-impedance drift on Channels 6–8.

![Figure 5.14: Channel Health Dashboard](../../results/figures/fig_5_10_qneuro_channel_quality_dashboard.png)

*Figure 5.14: Electrode DC offset, RMS noise floor, and health classification matrix across all 8 Qneuro channels.*

Gini feature importance analysis confirmed that central sensorimotor Beta and Mu power contributed over 68% of the total discriminative information.

![Figure 5.15: Gini Feature Importance](../../results/figures/fig_5_11_qneuro_feature_importance_weights.png)

*Figure 5.15: Top 12 spatial-frequency features ranked by relative Gini importance (sensorimotor Beta and Mu power contributing >68% total weight).*

## 5.7 Real-Time Actuator Arbitration Progression
Tracing the full 229-second session through the multi-tier Arbitrator demonstrated zero false activations, immediate safety lockout during blinks and clenches, and synchronized dispatch of Arm (`0x01`, `0x30`) and Leg (`0x02`, `0x30`) UART command packets.

![Figure 5.16: Full Session Arbitration Timeline](../../results/figures/fig_5_12_qneuro_full_session_arbitration_timeline.png)

*Figure 5.16: Full 229-second real-time arbitration timeline showing ground truth cues (top), safety interrupts (middle), and dispatched UART actuator commands (bottom).*

## 5.8 In-Vivo Performance Summary Matrix

### Table 5.2: Real-World Qneuro H100 Headset Performance Summary Matrix (57,250 In-Vivo Samples)
| Task / Subsystem | Target Classes | Algorithm / Method | Accuracy (%) | Precision | Recall | F1-Score | AUC-ROC | Cohen's $\kappa$ |
|---|---|---|---|---|---|---|---|---|
| **Motor Intent (3-Class)** | Rest, Hand, Leg | Random Forest | **87.0%** | 0.852 | 0.838 | 0.841 | 0.962 | 0.782 |
| **Motor Intent (3-Class)** | Rest, Hand, Leg | Linear Discriminant (LDA) | **75.8%** | 0.741 | 0.718 | 0.724 | 0.891 | 0.625 |
| **Lateralized Intent (5-Class)** | Rest, L/R Hand, L/R Leg | Random Forest | **83.8%** | 0.829 | 0.814 | 0.819 | 0.948 | 0.771 |
| **Emergency Veto (P1)** | Double-Blink | Differential Peak (+40 µV) | **100.0%** | 1.000 | 1.000 | 1.000 | — | 1.000 |
| **Safety Interrupt (P2)** | Jaw-Clench | High-Gamma Envelope (+10.5 dB) | **100.0%** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
