#!/usr/bin/env python3
"""
Prompted EEG Dataset Recorder for Qneuro H100
Acquires real-time multi-channel EEG over Lab Streaming Layer (LSL), displays timed visual/terminal
prompts for Motor Execution and Veto artifacts, and logs synchronized raw data and event labels.

Supported Conditions:
  0: REST (Baseline)
  1: DOUBLE_BLINK (EOG Veto Signal)
  2: JAW_CLENCH (EMG Veto Signal)
  3: HAND_CLENCH (Upper-Limb Real Execution)
  4: LEG_EXTENSION (Lower-Limb Real Execution)
"""

import os
import sys
import time
import random
import argparse
import json
from datetime import datetime
import numpy as np
from pylsl import StreamInlet, resolve_byprop, resolve_streams

# Standard Event Mapping (with laterality for motor conditions)
CONDITIONS = {
    0: {"name": "REST", "text": "RELAX & LOOK AT CROSSHAIR (+)", "cue": "[ + ]"},
    1: {"name": "DOUBLE_BLINK", "text": "BLINK - BLINK (Quick Double Blink)", "cue": "[ ** BLINK ** ]"},
    2: {"name": "JAW_CLENCH", "text": "CLENCH JAW (Bite Down Firmly)", "cue": "[ ## CLENCH JAW ## ]"},
    3: {"name": "LEFT_HAND_CLENCH", "text": "SQUEEZE LEFT HAND & RELAX (Fist)", "cue": "[ >> LEFT HAND << ]"},
    4: {"name": "LEFT_LEG_EXTENSION", "text": "EXTEND LEFT LEG & RELAX (Kick)", "cue": "[ ^^ LEFT LEG ^^ ]"},
    5: {"name": "RIGHT_HAND_CLENCH", "text": "SQUEEZE RIGHT HAND & RELAX (Fist)", "cue": "[ >> RIGHT HAND << ]"},
    6: {"name": "RIGHT_LEG_EXTENSION", "text": "EXTEND RIGHT LEG & RELAX (Kick)", "cue": "[ ^^ RIGHT LEG ^^ ]"},
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def clear_screen():
    print("\033[H\033[J", end="")


def print_prompt(banner: str, cue: str, event_name: str, trial_idx: int, total_trials: int, rem_sec: float, total_sec: float, phase: str):
    """Displays a clean in-terminal progress prompt with countdown."""
    clear_screen()
    print("=" * 65)
    print(f"  QNEURO H100 DATA ACQUISITION | Trial {trial_idx}/{total_trials} [{phase}]")
    print("=" * 65)
    print(f"\n  TASK:    {event_name}\n")
    print(f"  >>>      {banner}      <<<\n")
    print(f"           {cue}\n")
    bar_len = 30
    filled = int(max(0.0, min(1.0, 1.0 - (rem_sec / max(total_sec, 0.01)))) * bar_len)
    bar = "#" * filled + "-" * (bar_len - filled)
    print(f"  [{bar}] {rem_sec:4.1f}s remaining\n")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Prompted EEG Dataset Recorder")
    parser.add_argument("--stream", type=str, default="aq1", help="LSL Stream Name (default: aq1, fallback: EEG, Qneuro_H100_EEG_PPG)")
    parser.add_argument("--paradigm", type=str, choices=["motor_execution", "motor_imagery"], default="motor_execution",
                        help="Data category: motor_execution (real movement) or motor_imagery")
    parser.add_argument("--laterality", type=str, choices=["bilateral", "left", "right"], default="bilateral",
                        help="Which side to record: bilateral (both), left, or right (default: bilateral)")
    parser.add_argument("--trials-per-class", type=int, default=10,
                        help="Number of trials per action class (default: 10, ~6 min total)")
    parser.add_argument("--prep-time", type=float, default=2.0, help="Preparation countdown duration in seconds")
    parser.add_argument("--action-time", type=float, default=2.5, help="Action execution duration in seconds")
    parser.add_argument("--rest-time", type=float, default=3.0, help="Rest duration after action in seconds")
    parser.add_argument("--subject", type=str, default="sub-01", help="Subject identifier (e.g. sub-01)")
    args = parser.parse_args()

    # Destination directory setup
    out_dir = os.path.join(BASE_DIR, "data", "raw", args.paradigm)
    os.makedirs(out_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = os.path.join(out_dir, f"qneuro_{args.subject}_{args.paradigm}_{timestamp_str}.csv")
    out_meta = os.path.join(out_dir, f"qneuro_{args.subject}_{args.paradigm}_{timestamp_str}_metadata.json")

    print(f"[*] Discovering LSL stream '{args.stream}'...")
    streams = resolve_byprop('name', args.stream, timeout=4.0)
    if not streams:
        for fallback in ["aq1", "EEG", "Qneuro_H100_EEG_PPG", "admin_EEG"]:
            streams = resolve_byprop('name', fallback, timeout=1.5)
            if streams:
                print(f"[+] Connected to fallback stream: {fallback}")
                break

    if not streams:
        print(f"[-] Stream '{args.stream}' not found directly. Searching all available LSL streams...")
        all_s = resolve_streams(wait_time=2.0)
        eeg_candidates = [s for s in all_s if "aq1" in s.name().lower() or "eeg" in s.name().lower() or "qneuro" in s.name().lower()]
        if eeg_candidates:
            streams = [eeg_candidates[0]]
            print(f"[+] Found candidate stream: {streams[0].name()}")
        else:
            print("[-] No suitable LSL stream found.")
            print("[!] Please ensure either `qneuro_pipeline.py --stream aq1` or the Qneuro host application is streaming.")
            sys.exit(1)

    inlet = StreamInlet(streams[0], max_buflen=360)
    info = inlet.info()
    n_ch = info.channel_count()
    srate = info.nominal_srate() if info.nominal_srate() > 0 else 250.0
    print(f"[+] Connected: {info.name()} ({n_ch} channels @ ~{srate:.0f} Hz)")
    print(f"[+] Target Output CSV: {out_csv}")

    # Build randomized trial sequence based on laterality
    # Veto classes (always included): 1 (Blink), 2 (Jaw)
    # Motor classes depend on laterality setting
    if args.laterality == "left":
        motor_classes = [3, 4]           # Left hand, Left leg
    elif args.laterality == "right":
        motor_classes = [5, 6]           # Right hand, Right leg
    else:  # bilateral
        motor_classes = [3, 4, 5, 6]     # Both sides

    action_classes = [1, 2] + motor_classes
    trial_sequence = action_classes * args.trials_per_class
    random.shuffle(trial_sequence)
    total_trials = len(trial_sequence)

    total_est_seconds = (args.prep_time + args.action_time + args.rest_time) * total_trials + 20.0
    print(f"\n[i] Session Plan: {total_trials} total trials ({args.trials_per_class} trials × {len(action_classes)} action classes)")
    print(f"[i] Estimated Duration: ~{total_est_seconds / 60.0:.1f} minutes")
    paradigm_desc = "Overt Real Physical Movements" if args.paradigm == "motor_execution" else "Kinesthetic Motor Imagery (No Overt Movement)"
    print(f"[i] Paradigm: {args.paradigm.upper()} ({paradigm_desc})")
    input("\n[>>>] Press [ENTER] when the subject is seated, relaxed, and ready to start...")

    # Open CSV writer
    csv_file = open(out_csv, "w")
    headers = ["timestamp_ms", "lsl_timestamp"]
    if n_ch == 10:
        headers += [f"EEG_{i+1}" for i in range(8)] + ["PPG_Red", "PPG_IR"]
    else:
        headers += [f"EEG_{i+1}" for i in range(n_ch)]
    headers += ["event_id", "event_label"]
    csv_file.write(",".join(headers) + "\n")

    recorded_samples = 0
    samples_since_flush = 0
    trial_events_log = []

    def record_chunk(event_id: int, event_label: str, duration: float):
        nonlocal recorded_samples, samples_since_flush
        t_end = time.time() + duration
        while time.time() < t_end:
            chunk, timestamps = inlet.pull_chunk(timeout=0.04, max_samples=64)
            if chunk:
                for s, ts in zip(chunk, timestamps):
                    sample_ms = ts * 1000.0  # Use LSL timestamp for per-sample accuracy
                    row = [f"{sample_ms:.3f}", f"{ts:.6f}"]
                    row += [f"{val:.3f}" for val in s]
                    row += [str(event_id), event_label]
                    csv_file.write(",".join(row) + "\n")
                    recorded_samples += 1
                    samples_since_flush += 1
                # Flush to disk every ~1 second of data to prevent loss on crash
                if samples_since_flush >= 250:
                    csv_file.flush()
                    samples_since_flush = 0

    session_interrupted = False
    try:
        # 1. Baseline Rest Run (15 seconds initial quiet rest)
        t_start_base = time.time()
        while time.time() - t_start_base < 15.0:
            rem = 15.0 - (time.time() - t_start_base)
            print_prompt("RELAX & LOOK AT CROSSHAIR (+)", "[ + ]", "BASELINE REST", 0, total_trials, rem, 15.0, "BASELINE")
            record_chunk(0, "REST", 0.1)

        # 2. Main Prompted Trial Loop
        for idx, act_id in enumerate(trial_sequence, start=1):
            act_info = CONDITIONS[act_id]

            # Phase 1: Preparation (Crosshair)
            t_target = time.time() + args.prep_time
            while time.time() < t_target:
                rem = t_target - time.time()
                print_prompt(f"GET READY FOR {act_info['name']}", "[ + ]", act_info['name'], idx, total_trials, rem, args.prep_time, "PREPARE")
                record_chunk(0, "REST", 0.1)

            # Phase 2: Action Execution
            t_action_start = time.time()
            trial_events_log.append({
                "trial": idx,
                "event_id": act_id,
                "event_label": act_info["name"],
                "start_time_iso": datetime.now().isoformat(),
                "start_epoch": t_action_start
            })
            t_target = time.time() + args.action_time
            while time.time() < t_target:
                rem = t_target - time.time()
                print_prompt(act_info['text'], act_info['cue'], act_info['name'], idx, total_trials, rem, args.action_time, "ACTION")
                record_chunk(act_id, act_info["name"], 0.1)

            # Phase 3: Post-Action Rest & Reset
            t_target = time.time() + args.rest_time
            while time.time() < t_target:
                rem = t_target - time.time()
                print_prompt("RELEASE MUSCLES & RELAX", "[ ... ]", act_info['name'], idx, total_trials, rem, args.rest_time, "RECOVER")
                record_chunk(0, "REST", 0.1)

    except KeyboardInterrupt:
        session_interrupted = True
        print("\n[!] Recording interrupted by user. Finalizing and saving captured telemetry...")
    finally:
        csv_file.flush()
        csv_file.close()

        # Save Session Metadata
        paradigm_meta_desc = (
            "Overt physical movements for rehabilitation & safety veto tuning"
            if args.paradigm == "motor_execution"
            else "Kinesthetic motor imagery without overt muscle contraction (stroke/rehab target)"
        )
        # Convert int keys to strings for JSON compatibility
        event_mapping_json = {str(k): v for k, v in CONDITIONS.items()}
        meta = {
            "subject": args.subject,
            "paradigm": args.paradigm,
            "paradigm_description": paradigm_meta_desc,
            "timestamp": timestamp_str,
            "sample_rate_hz": srate,
            "channel_count": n_ch,
            "total_trials_planned": total_trials,
            "completed_trials": len(trial_events_log),
            "interrupted": session_interrupted,
            "total_recorded_samples": recorded_samples,
            "duration_seconds": recorded_samples / srate if srate > 0 else 0,
            "event_mapping": event_mapping_json,
            "trials_log": trial_events_log
        }
        with open(out_meta, "w") as f:
            json.dump(meta, f, indent=2)

    clear_screen()
    status_header = "⚠ RECORDING HALTED (PARTIAL DATASET SAVED)" if session_interrupted else "✓ RECORDING SESSION COMPLETE"
    print("=" * 65)
    print(f"  {status_header}")
    print("=" * 65)
    print(f"  Trials Completed:        {len(trial_events_log)} / {total_trials}")
    print(f"  Total Samples Recorded:  {recorded_samples}")
    print(f"  Total Duration:          {recorded_samples / srate / 60.0:.2f} minutes")
    print(f"  Saved CSV:               {out_csv}")
    print(f"  Saved Metadata:          {out_meta}")
    print("=" * 65)


if __name__ == "__main__":
    main()
