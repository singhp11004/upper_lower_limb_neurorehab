#!/usr/bin/env python3
"""demo_mvp.py - Minimal Viable Product Real-Time Neurorehabilitation BCI Runner.

Wires the complete end-to-end pipeline:
1. BrainFlowStreamer (Synthetic / Playback / Live)
2. CircularRingBuffer (16 channels, 2.0s window, 100ms step)
3. EEGFilterPipeline + ArtifactRejectionEngine
4. 4 Parallel Biosignal Detectors:
   - Priority 1: EOGBlinkDetector (double-blink veto -> E-Stop 0x99)
   - Priority 2: JawClenchDetector (temporalis EMG high-gamma -> Hand Close 0x20)
   - Priority 3: P300Extractor + SWLDAP300Classifier (ERP -> Hand Open 0x10)
   - Priority 4: BandPowerExtractor + WorkloadLDAClassifier (Alpha state gate)
5. Priority Arbitrator & Safety Dwell State Machine
6. Binary UART PacketEncoder (7 bytes, CRC-8/MAXIM) + SerialManager
7. Live Terminal Dashboard
"""

import os
import sys
import time
import argparse
import numpy as np

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.acquisition.brainflow_streamer import BrainFlowStreamer
from src.acquisition.ring_buffer import CircularRingBuffer
from src.preprocessing.filters import EEGFilterPipeline
from src.preprocessing.artifact_rejection import ArtifactRejectionEngine
from src.features.eog_blink_detector import EOGBlinkDetector
from src.features.jaw_clench_detector import JawClenchDetector
from src.features.p300_extractor import P300Extractor
from src.features.bandpower import BandPowerExtractor
from src.classifiers.model_manager import ModelManager
from src.communication.packet_encoder import PacketEncoder
from src.communication.arbitrator import Arbitrator
from src.communication.serial_manager import SerialManager


def parse_args():
    parser = argparse.ArgumentParser(description="Neurorehab BCI MVP Demo Runner")
    parser.add_argument(
        "--mode",
        choices=["synthetic", "playback", "live", "lsl"],
        default="playback",
        help="Acquisition mode: synthetic, playback, live (OpenBCI), or lsl (Qneuro H100)"
    )
    parser.add_argument(
        "--stream",
        type=str,
        default="aq1",
        help="LSL Stream Name if in 'lsl' mode (default: aq1, fallback: EEG)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="data/public_benchmarks/ceegrid_eeg/openbci_ceegrid_16ch_250hz_playback.csv",
        help="Path to playback CSV file if in playback mode"
    )
    parser.add_argument(
        "--serial-port",
        type=str,
        default=None,
        help="ESP32 serial port (e.g. /dev/ttyTHS1 or COM3). Omit for console simulation."
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Total runtime in seconds (default: 30.0)"
    )
    parser.add_argument(
        "--inject-veto-at",
        type=float,
        default=-1.0,
        help="Inject synthetic double-blink at timestamp (sec) for testing"
    )
    parser.add_argument(
        "--inject-clench-at",
        type=float,
        default=-1.0,
        help="Inject synthetic jaw clench burst at timestamp (sec) for testing"
    )
    return parser.parse_args()


def render_dashboard(
    epoch_idx: int,
    elapsed_sec: float,
    blink_count: int,
    is_veto: bool,
    gamma_db: float,
    is_clench: bool,
    p300_prob: float,
    workload_state: str,
    alpha_power_db: float,
    decision_reason: str,
    last_packet_hex: str,
    latencies: dict,
):
    """Renders formatted ANSI console dashboard."""
    # Move cursor to top of screen or print block
    veto_status = "■ ACTIVE (E-STOP)" if is_veto else "□ INACTIVE"
    clench_status = "■ TRIGGERED" if is_clench else "□ BELOW THRESHOLD"
    p300_status = "■ TARGET DETECTED" if p300_prob >= 0.65 else "□ NON-TARGET"

    sys.stdout.write("\033[2J\033[H")  # clear screen and move to (0,0)
    print("┌─────────────────────────────────────── BCI MVP LIVE DASHBOARD ────────────────────────────────────────┐")
    print(f"│ Epoch: #{epoch_idx:05d} | Elapsed: {elapsed_sec:5.1f}s | Fs: 250 Hz | Window: 2.0s (500 pts) | Step: 100ms               │")
    print("├────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    print(f"│ EOG BLINK-VETO (P1) : Blinks: {blink_count:1d}  | Status: {veto_status:<20}                                    │")
    print(f"│ JAW-CLENCH     (P2) : Gamma: {gamma_db:+5.1f} dB (Thresh: +8.0 dB) | Status: {clench_status:<18}             │")
    print(f"│ P300 SWLDA     (P3) : Prob:  {p300_prob:5.3f} (Thresh:  0.65) | Status: {p300_status:<18}             │")
    print(f"│ ALPHA WORKLOAD (P4) : State: {workload_state:<6} | Alpha Power: {alpha_power_db:+5.2f} dB                                     │")
    print("├────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    print(f"│ ARBITRATOR DECISION : {decision_reason:<72} │")
    print(f"│ LATEST UART PACKET  : {last_packet_hex:<72} │")
    total_lat = sum(latencies.values())
    print(f"│ LATENCY BREAKDOWN   : Filt: {latencies.get('filter', 0):.2f}ms | Feat: {latencies.get('feature', 0):.2f}ms | Clf: {latencies.get('clf', 0):.2f}ms | Total: {total_lat:.2f}ms │")
    print("└────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    sys.stdout.flush()


def main():
    args = parse_args()

    # 1. Initialize Acquisition
    print("Initializing acquisition streamer...")
    playback_path = args.file if os.path.exists(args.file) else None
    streamer = BrainFlowStreamer(mode=args.mode, playback_file=playback_path, lsl_stream_name=args.stream)
    ring_buf = CircularRingBuffer(n_channels=16, window_sec=2.0, step_sec=0.1, sample_rate=250)

    # 2. Initialize Preprocessing
    filter_pipe = EEGFilterPipeline(sample_rate=250)
    artifact_engine = ArtifactRejectionEngine(amplitude_threshold_uv=150.0)

    # 3. Initialize Feature Detectors
    blink_detector = EOGBlinkDetector(sample_rate=250, peak_threshold_uv=80.0)
    clench_detector = JawClenchDetector(sample_rate=250, threshold_db=8.0)
    p300_extractor = P300Extractor(sample_rate=250)
    bandpower_extractor = BandPowerExtractor(sample_rate=250)

    # 4. Load Models
    model_mgr = ModelManager(models_dir="models")
    swlda_clf = None
    workload_clf = None
    try:
        swlda_clf = model_mgr.load_model("swlda_p300_model")
        print("✓ Loaded SWLDA P300 classifier.")
    except Exception as e:
        print(f"Notice: SWLDA model load failed ({e}), using baseline fallback.")

    try:
        workload_clf = model_mgr.load_model("workload_lda_model")
        print("✓ Loaded Workload LDA classifier.")
    except Exception as e:
        print(f"Notice: Workload model load failed ({e}), using baseline fallback.")

    # 5. Initialize Arbitration & Communication
    arbitrator = Arbitrator(p300_confidence_thresh=0.65, dwell_time_sec=0.3, veto_lockout_sec=0.5)
    serial_mgr = SerialManager(port=args.serial_port)

    # Start Stream
    streamer.start_stream()
    time.sleep(0.5)  # Let buffer accumulate initial samples

    start_time = time.monotonic()
    epoch_idx = 0
    last_packet_hex = "None"
    latencies = {"filter": 0.0, "feature": 0.0, "clf": 0.0}

    print("Starting real-time loop...")

    try:
        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= args.duration:
                break

            # Fetch step samples (25 samples = 100 ms at 250 Hz)
            new_samples = streamer.get_data(num_samples=25)
            if new_samples.shape[1] > 0:
                ring_buf.append(new_samples)

            if not ring_buf.is_ready():
                time.sleep(0.02)
                continue

            epoch_idx += 1
            window = ring_buf.get_latest_window()  # (16, 500)

            # Injections for automated verification
            if 0 <= args.inject_veto_at <= elapsed <= args.inject_veto_at + 0.4:
                # Inject 2 positive EOG peaks on channel 0 and 1
                window[0, 100:130] += 120.0
                window[0, 200:230] += 120.0

            if 0 <= args.inject_clench_at <= elapsed <= args.inject_clench_at + 0.5:
                # Inject 35 Hz high-gamma burst on temporalis channels
                t_arr = np.linspace(0, 2.0, 500)
                burst = 50.0 * np.sin(2 * np.pi * 38 * t_arr)
                window[0:4, 250:500] += burst[250:500]

            # --- Preprocessing ---
            t0 = time.perf_counter()
            filtered = filter_pipe.process(window)
            cleaned, artifact_meta = artifact_engine.clean_epoch(filtered)
            t1 = time.perf_counter()
            latencies["filter"] = (t1 - t0) * 1000

            # --- Detectors ---
            t2 = time.perf_counter()
            # 1. Blink veto
            is_veto, blink_count, _ = blink_detector.detect_blinks(cleaned)

            # 2. Jaw clench
            gamma_band = filter_pipe.extract_high_gamma_band(cleaned)
            is_clench, gamma_db, _ = clench_detector.detect_clench(gamma_band)

            # 3. P300 ERP
            p300_feat = p300_extractor.extract_features(cleaned)
            p300_prob = 0.0
            if swlda_clf is not None:
                try:
                    probs = swlda_clf.predict_proba(p300_feat.reshape(1, -1))
                    p300_prob = float(probs[0, 1])
                except Exception:
                    p300_prob = 0.0

            # 4. Alpha Workload
            bp = bandpower_extractor.compute_bandpower(cleaned)
            alpha_power_db = float(np.mean(bp["alpha"]))  # mean alpha power across channels
            bp_features = bandpower_extractor.extract_feature_vector(cleaned)
            workload_state = "ACTIVE"
            if workload_clf is not None:
                try:
                    workload_state = str(workload_clf.predict(bp_features.reshape(1, -1))[0])
                except Exception:
                    workload_state = "ACTIVE"

            t3 = time.perf_counter()
            latencies["feature"] = (t3 - t2) * 1000

            # --- Arbitration & Command Dispatch ---
            t4 = time.perf_counter()
            decision = arbitrator.process(
                is_veto=is_veto,
                is_clench=is_clench,
                p300_prob=p300_prob,
                workload_state=workload_state,
                current_time=time.monotonic()
            )
            t5 = time.perf_counter()
            latencies["clf"] = (t5 - t4) * 1000

            if decision.cmd_id is not None:
                packet = PacketEncoder.encode(
                    module_id=decision.module_id,
                    cmd_id=decision.cmd_id,
                    param=decision.param,
                    confidence=decision.confidence
                )
                serial_mgr.send_packet(packet)
                last_packet_hex = " ".join(f"{b:02X}" for b in packet)

            render_dashboard(
                epoch_idx=epoch_idx,
                elapsed_sec=elapsed,
                blink_count=blink_count,
                is_veto=is_veto,
                gamma_db=gamma_db,
                is_clench=is_clench,
                p300_prob=p300_prob,
                workload_state=workload_state,
                alpha_power_db=alpha_power_db,
                decision_reason=decision.reason,
                last_packet_hex=last_packet_hex,
                latencies=latencies
            )

            # 10 Hz target loop pacing
            time.sleep(0.08)

    except KeyboardInterrupt:
        print("\nStopping demo...")
    finally:
        streamer.stop_stream()
        serial_mgr.close()
        print(f"\nMVP Demo finished cleanly after {epoch_idx} epochs.")


if __name__ == "__main__":
    main()
