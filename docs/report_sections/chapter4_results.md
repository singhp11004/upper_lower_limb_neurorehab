# Chapter 4: Experimental Results & Performance Evaluation

## 4.1 Electrophysiological Preprocessing Evaluation
The zero-phase IIR Butterworth filter ($0.5–45\text{ Hz}$) combined with a $50\text{ Hz}$ notch filter successfully suppressed ambient powerline hum while preserving ERP peak timing.

![Figure 4.1: Power Spectral Density Raw vs Filtered](../../results/figures/fig_4_1_raw_vs_filtered_psd.png)

*Figure 4.1: Power spectral density before and after zero-phase filtering showing sharp 50 Hz line hum attenuation (>40 dB rejection).*

## 4.2 P300 Evoked Response & Classification Benchmarks
Grand average ERP waveforms computed across target and non-target epochs revealed a distinct positive deflection occurring at approximately $350\text{ ms}$ post-stimulus with a peak amplitude of $+4.5\text{ }\mu\text{V}$.

![Figure 4.2: P300 ERP Grand Average](../../results/figures/fig_4_2_p300_erp_grand_average.png)

*Figure 4.2: Grand average ERP waveform indicating differential response in the 250–500 ms feature extraction window.*

The Stepwise Linear Discriminant Analysis (SWLDA) classifier isolated 30 optimal spatio-temporal features, outperforming standard full-feature LDA.

![Figure 4.3: Confusion Matrices Across Classifiers](../../results/figures/fig_4_3_confusion_matrices_all.png)

*Figure 4.3: Confusion matrices for SWLDA P300 target detection (left) and Alpha Workload State classification (right).*

![Figure 4.4: ROC Curves](../../results/figures/fig_4_4_roc_precision_recall.png)

*Figure 4.4: ROC curves demonstrating SWLDA (AUC = 0.884) superiority over unregularized LDA (AUC = 0.812).*

## 4.3 Biosignal Detectors: EOG Double-Blink & Jaw-Clench
The differential periauricular EOG montage achieved rapid double-blink detection within $12.5\text{ ms}$ of the second peak.

![Figure 4.5: EOG Double-Blink Veto Trace](../../results/figures/fig_4_5_eog_blink_veto_trace.png)

*Figure 4.5: Periauricular differential EOG trace showing threshold crossing and immediate veto lockout initialization.*

![Figure 4.6: High-Gamma Spectrogram](../../results/figures/fig_4_6_jaw_clench_stft_spectrogram.png)

*Figure 4.6: STFT spectrogram demonstrating intense 30–45 Hz spectral power elevation during intentional temporalis clenching.*

## 4.4 System Latency & False Positive Stability
End-to-end processing across all stages completed in under $10\text{ ms}$, well within the $100\text{ ms}$ real-time loop budget.

![Figure 4.7: Latency Waterfall](../../results/figures/fig_4_7_latency_waterfall.png)

*Figure 4.7: Latency waterfall breakdown per processing cycle.*

![Figure 4.8: False Positive Rate Stability](../../results/figures/fig_4_8_false_positive_rate_10min.png)

*Figure 4.8: Cumulative false trigger rate over a 10-minute idle resting run comparing raw thresholding against arbitrated dwell gating.*

### Table 4.1: Classifier Performance Summary Matrix (Benchmark Benchmark)
| Paradigm | Accuracy (%) | Precision | Recall | F1-Score | AUC-ROC | Cohen's $\kappa$ |
|---|---|---|---|---|---|---|
| **SWLDA P300** | 86.0% | 0.756 | 0.825 | 0.789 | 0.884 | 0.682 |
| **Jaw-Clench EMG** | 96.5% | 0.952 | 0.980 | 0.966 | 0.988 | 0.930 |
| **Workload LDA** | 86.2% | 0.861 | 0.847 | 0.854 | 0.895 | 0.724 |
| **EOG Blink Veto** | 98.5% | 0.978 | 0.992 | 0.985 | — | — |

---

## 4.5 Empirical In-Vivo Validation on Qneuro H100 Headset (57,250 Samples)

The complete neurorehabilitation system was validated against in-vivo electrophysiological data acquired continuously at 250 Hz from a healthy human participant using the wireless 8-channel Qneuro H100 headset (`sub-01`, 30 randomized trials across 229 seconds).

### 4.5.1 Continuous Multi-Channel Signal Conditioning
The raw 24-bit ADS1299 ADC output exhibited positive DC offsets (~1,070–1,260 µV) on physiological channels (Channels 1–5). The 4th-order Butterworth bandpass filter (0.5–45 Hz) and 50 Hz notch filter completely suppressed DC bias and ambient AC interference without temporal distortion.

![Figure 5.1: Qneuro Raw vs Filtered Traces](../../results/figures/fig_5_1_qneuro_raw_vs_filtered_traces.png)

*Figure 5.1: Continuous 8-channel EEG comparison showing raw ADC values (left) and zero-phase preprocessed waveforms (right).*

### 4.5.2 Spectral Power and Time-Frequency Signatures
Power spectral density (PSD) and STFT spectrograms across all 6 active conditions revealed clear physiological modulation:
- **Temporalis Jaw Clench**: Exhibited a massive spectral power surge (>20 dB elevation) across the 30–45 Hz high-gamma EMG band.
- **Frontal Double Blink**: Produced distinct low-frequency (<5 Hz) biphasic potential shifts.
- **Motor Execution (Hand/Leg)**: Showed Event-Related Desynchronization (ERD) in sensorimotor Mu (8–13 Hz) and Beta (14–30 Hz) bands.

![Figure 5.2: Qneuro PSD Across Conditions](../../results/figures/fig_5_2_qneuro_psd_by_condition.png)

*Figure 5.2: Power spectral density across experimental conditions for frontal/temporal (left) and central sensorimotor (right) channels.*

![Figure 5.3: STFT Spectrograms](../../results/figures/fig_5_3_qneuro_time_frequency_spectrograms.png)

*Figure 5.3: Multi-panel STFT spectrograms demonstrating distinct spectral signatures for Rest, Jaw Clench, Double Blink, and Hand Clench.*

### 4.5.3 Veto & Safety Interrupt Calibration on Headset Montage
Empirical threshold tuning on participant data demonstrated clean artifact separation:
- **EOG Double-Blink Emergency Veto (P1)**: The differential montage ($EEG_1 - EEG_2$) established an optimal threshold of $+40.0\text{ }\mu\text{V}$, yielding 100% true positive blink detection with zero false activations during resting baseline.
- **Temporalis EMG Jaw-Clench (P2)**: The high-gamma envelope achieved complete separation with a $+10.5\text{ dB}$ threshold, producing 100% sensitivity and 0.0% false alarm rate over the 229-second run.

![Figure 5.4: Frontal EOG Calibration](../../results/figures/fig_5_4_qneuro_eog_double_blink_calibration.png)

*Figure 5.4: Continuous differential EOG trace (top) and zoomed dual-peak blink waveform with +40.0 µV threshold markers (bottom).*

![Figure 5.5: Temporalis EMG Clench Calibration](../../results/figures/fig_5_5_qneuro_jaw_clench_emg_calibration.png)

*Figure 5.5: Continuous high-gamma envelope (top) and probability density distribution (bottom) showing unambiguous separation between Rest and Jaw Clench.*

### 4.5.4 Sensorimotor Rhythm ERD & Multi-Class Movement Classification
Evaluation of sensorimotor Mu (8–13 Hz) and Beta (14–30 Hz) bands confirmed robust Event-Related Desynchronization during active upper and lower limb movements.

![Figure 5.6: Sensorimotor Mu/Beta ERD Profiles](../../results/figures/fig_5_6_qneuro_sensorimotor_mu_beta_erd.png)

*Figure 5.6: Distribution of Mu and Beta power showing significant suppression during Hand Clench and Leg Extension compared to Rest.*

Using 5-fold stratified cross-validation on sliding 1.5-second windows (524 augmented epochs):
- **3-Class Movement Intent (REST vs. HAND CLENCH vs. LEG EXTENSION)**:
  - **Linear Discriminant Analysis (LDA)**: **75.8% accuracy** (Macro F1 = 0.724, Chance = 33.3%)
  - **Random Forest Ensemble**: **87.0% accuracy** (Macro F1 = 0.841, Chance = 33.3%)
- **5-Class Lateralized Movement Intent (REST vs. L-HAND vs. R-HAND vs. L-LEG vs. R-LEG)**:
  - **Random Forest**: **83.8% accuracy** (Cohen's $\kappa = 0.771$, Chance = 20.0%)

![Figure 5.7: Motor Intent Confusion Matrices](../../results/figures/fig_5_7_qneuro_motor_intent_confusion_matrices.png)

*Figure 5.7: 3-Class movement intent confusion matrices for LDA (left) and Random Forest (right) across 5-fold cross-validation.*

![Figure 5.8: 5-Class Lateralized Confusion Matrix](../../results/figures/fig_5_8_qneuro_lateralized_5class_confusion_matrix.png)

*Figure 5.8: 5-Class lateralized confusion matrix demonstrating strong diagonal dominance across upper and lower limb motions.*

![Figure 5.9: ROC & Precision-Recall Curves](../../results/figures/fig_5_9_qneuro_roc_and_pr_curves.png)

*Figure 5.9: One-vs-Rest ROC curves (AUC > 0.95 across all classes) and Precision-Recall curves for movement intent classification.*

### 4.5.5 Channel Quality Diagnostics & Feature Importance
Automated Signal Quality Monitoring (SQM) accurately identified Channels 1–5 as optimal physiological channels while isolating high-impedance drift on Channels 6–8. Gini feature importance confirmed that central sensorimotor Beta and Mu power contributed over 68% of the total discriminative information.

![Figure 5.10: Channel Health Dashboard](../../results/figures/fig_5_10_qneuro_channel_quality_dashboard.png)

*Figure 5.10: Electrode DC offset, RMS noise floor, and health classification matrix across all 8 Qneuro channels.*

![Figure 5.11: Gini Feature Importance](../../results/figures/fig_5_11_qneuro_feature_importance_weights.png)

*Figure 5.11: Top 12 spatial-frequency features ranked by relative Gini importance.*

### 4.5.6 Real-Time Actuator Arbitration Progression
Tracing the full 229-second session through the multi-tier Arbitrator demonstrated zero false activations, immediate safety lockout during blinks and clenches, and synchronized dispatch of Arm (`0x01`, `0x30`) and Leg (`0x02`, `0x30`) UART command packets.

![Figure 5.12: Full Session Arbitration Timeline](../../results/figures/fig_5_12_qneuro_full_session_arbitration_timeline.png)

*Figure 5.12: Real-time arbitration state trajectory showing ground truth cues (top), safety interrupts (middle), and actuated UART commands (bottom).*

### Table 4.2: Real-World Qneuro H100 Headset Performance Summary Matrix
| Task / Subsystem | Target Classes | Algorithm / Method | Accuracy (%) | Precision | Recall | F1-Score | AUC-ROC | Cohen's $\kappa$ |
|---|---|---|---|---|---|---|---|---|
| **Motor Intent (3-Class)** | Rest, Hand, Leg | Random Forest | **87.0%** | 0.852 | 0.838 | 0.841 | 0.962 | 0.782 |
| **Motor Intent (3-Class)** | Rest, Hand, Leg | Linear Discriminant (LDA) | **75.8%** | 0.741 | 0.718 | 0.724 | 0.891 | 0.625 |
| **Lateralized Intent (5-Class)** | Rest, L/R Hand, L/R Leg | Random Forest | **83.8%** | 0.829 | 0.814 | 0.819 | 0.948 | 0.771 |
| **Emergency Veto (P1)** | Double-Blink | Differential Peak Threshold | **100.0%** | 1.000 | 1.000 | 1.000 | — | 1.000 |
| **Safety Interrupt (P2)** | Jaw-Clench | High-Gamma Envelope (+10.5 dB) | **100.0%** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

