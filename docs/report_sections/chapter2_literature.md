# Chapter 2: Literature Review

## 2.1 Survey of Brain-Computer Interfaces in Neurorehabilitation
Over the past decade, non-invasive robotic rehabilitation has transitioned from passive continuous passive motion (CPM) machines to active, intention-driven closed-loop robotic orthoses.

| Author & Year | Focus & Paradigm | Strengths | Bottlenecks / Gaps |
|---|---|---|---|
| **Debener et al. (2015)** | Unobtrusive around-the-ear EEG with cEEGrid | Ear-EEG captures clean P300 and alpha rhythms without hair gel | Limited channel density; requires dedicated spatial calibration |
| **Bleichner & Debener (2017)** | Concealed around-the-ear EEG | Validates mobile recording and long-term electrode stability | Susceptible to temporalis myogenic crosstalk during mastication |
| **Pfurtscheller et al. (2006)** | Hybrid BCI combining EEG and EMG | Enhanced throughput, reduced false positive rate | Bulky multi-lead wiring across scalp and extremities |
| **Krusienski et al. (2006)** | Stepwise LDA for P300 Speller | Optimal feature reduction (F-test entry/removal), robust against overfitting | Evaluated solely on standard 64-channel wet montages |
| **Ang et al. (2015)** | Clinical stroke trial with EEG robotic arm | Demonstrates significant Fugl-Meyer motor score improvements | Relied on motor imagery; 20% non-responder rate |

## 2.2 Electrode Topography: Standard 10–20 vs. Periauricular cEEGrid
Periauricular arrays position electrodes around the pinna (auricle), capturing:
- **Temporal & parietal cortical activity**: Adequate projection of P300 ERPs and alpha-band oscillations.
- **Periauricular Differential EOG**: Dipolar ocular potentials during vertical and horizontal saccades / blinks.
- **Temporalis EMG bursts**: High-frequency electromyographic signatures (>30 Hz) during intentional mandible clenches.

## 2.3 Edge Deployment in Robotic Prosthetics & Exoskeletons
Modern rehabilitation robotics mandates real-time safety compliance (IEC 60601-1 / ISO 13482). Classical cloud or PC-tethered pipelines exhibit high jitter (30–120 ms) and communication drops. Distributed architectures segregating heavy neural feature pipelines on embedded edge processors (NVIDIA Jetson) and deterministic real-time PWM motion profiling on dual-core microcontrollers (ESP32 FreeRTOS) represent the state of the art in medical cyber-physical systems.
