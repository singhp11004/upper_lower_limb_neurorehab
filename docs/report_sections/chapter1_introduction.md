# Chapter 1: Introduction

## 1.1 Background & Motivation
Motor impairment resulting from cerebrovascular accidents (stroke), traumatic brain injury (TBI), and spinal cord injury represents one of the foremost causes of long-term adult disability globally. Post-stroke hemiparesis compromises independent activities of daily living (ADLs), impacting both upper-limb manual dexterity and lower-limb ambulatory function. Conventional neurorehabilitation paradigms rely heavily on continuous physical therapist intervention, which is resource-intensive and often lacks objective, continuous biofeedback regarding active cortical engagement.

Brain-Computer Interfaces (BCIs) offer a direct neural bridge translating real-time neuroelectric activity into actuation commands for external robotic exoskeletons and orthoses. By coupling motor intention or discrete cognitive responses with immediate robotic limb mobilization, BCIs foster hebbian plasticity—reinforcing neural pathway reorganization ("cells that fire together, wire together").

## 1.2 Limitations of Existing Approaches
Traditional EEG-based BCIs encounter several critical bottlenecks that prevent practical clinical and domestic translation:
1. **Bulky Whole-Scalp Caps**: Standard 64-channel 10–20 caps require conductive electrolytic gel application, causing hair contamination, long setup times (>30–45 minutes), and impedance degradation within 1–2 hours.
2. **Motor Imagery (MI) Inefficiency**: Classical Sensorimotor Rhythm (SMR) / Motor Imagery BCIs require extensive user training (often dozens of sessions), and suffer from "BCI illiteracy" in 15–30% of stroke survivors whose motor cortices are severely infarcted.
3. **Rigid Edge Processing Constraints**: Clinical rehabilitation exoskeletons require sub-100 ms real-time responsiveness and rigorous fail-safe emergency veto mechanisms. Desktop-tethered pipelines cannot operate in ambulatory, mobile rehabilitation environments.

## 1.3 Proposed System & Objectives
This project presents an unobtrusive, wearable hybrid BCI framework utilizing **periauricular cEEGrid electrodes** coupled with an embedded **NVIDIA Jetson Orin Nano** edge compute module and a dedicated **ESP32-P4 FreeRTOS** motor controller.

### Primary Engineering Objectives:
- **Zero-Gel Periauricular Sensing**: Acquisition of 16-channel EEG via c-shaped flex-printed arrays positioned around the ear.
- **Hybrid Multi-Modal Biosignal Paradigms**:
  1. *P300 Oddball ERP*: Evoked visual/auditory potential for voluntary target intent selection (e.g., Hand Open).
  2. *High-Gamma Temporalis EMG (Jaw-Clench)*: Fast, high-SNR intentional burst (30–45 Hz) for rapid activation (e.g., Hand Close).
  3. *Periauricular EOG Double-Blink Veto*: Hardware/software overriding safety gate achieving instantaneous Emergency Stop (<15 ms).
  4. *Alpha-Band Workload Monitor*: Spectral power assessment gating commands to prevent exhaustion-induced errors.
- **Embedded Edge Decoupling**: Export of lightweight linear discriminant models executing in <100 µs on Jetson edge cores.
