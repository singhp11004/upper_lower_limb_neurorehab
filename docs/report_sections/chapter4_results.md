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

### Table 4.1: Classifier Performance Summary Matrix
| Paradigm | Accuracy (%) | Precision | Recall | F1-Score | AUC-ROC | Cohen's $\kappa$ |
|---|---|---|---|---|---|---|
| **SWLDA P300** | 86.0% | 0.756 | 0.825 | 0.789 | 0.884 | 0.682 |
| **Jaw-Clench EMG** | 96.5% | 0.952 | 0.980 | 0.966 | 0.988 | 0.930 |
| **Workload LDA** | 86.2% | 0.861 | 0.847 | 0.854 | 0.895 | 0.724 |
| **EOG Blink Veto** | 98.5% | 0.978 | 0.992 | 0.985 | — | — |
