# Chapter 5: Conclusion & Future Scope

## 5.1 Project Summary
This work implemented and benchmarked an unobtrusive, hybrid brain-computer interface system for upper- and lower-limb neurorehabilitation. By leveraging periauricular cEEGrid electrodes, the pipeline eliminates the need for messy conductive hair gels and lengthy montage setups while successfully capturing ERPs, ocular dipoles, and temporalis electromyography.

Key accomplishments include:
1. **End-to-End Real-Time Pipeline**: A unified MVP runner (`src/demo_mvp.py`) orchestrating 10 Hz windowed acquisition, artifact cleaning, parallel biosignal detection, priority arbitration, and 7-byte binary UART packet transmission.
2. **Robust Multi-Modal Detection**: High classification accuracies achieved across P300 ERP (86.0% accuracy, AUC 0.884), jaw-clench EMG (96.5% accuracy), alpha cognitive workload (86.2%), and double-blink veto (>98% sensitivity).
3. **Embedded Optimization & Model Decoupling**: Separation of the extensive research/metric pipeline from the lightweight edge inference runtime (`<60 µs` linear dot-product on Jetson Orin Nano).
4. **Deterministic Cyber-Physical Latency**: Total software latency of under $10\text{ ms}$, comfortably fitting within the $100\text{ ms}$ real-time control budget.

## 5.2 Future Scope
1. **Direct Validation with Native cEEGrid Patients**: Conduct real-time clinical rehabilitation trials with stroke survivors using custom 3D-printed orthotic hand and lower-limb braces.
2. **Closed-Loop Auditory P300 Oddball**: Integrate spatial auditory stimuli to provide BCI control without requiring visual gaze fixation.
3. **Adaptive Thresholding**: Implement continuous background EMG baseline tracking to adjust jaw-clench thresholds across sessions.
