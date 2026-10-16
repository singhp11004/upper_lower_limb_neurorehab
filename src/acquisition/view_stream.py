#!/usr/bin/env python3
"""
Qneuro H100 Real-Time 8-Channel EEG Waveform Visualizer
Plots live rolling EEG tracks from LSL stream 'aq1' (or fallback).
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pylsl import StreamInlet, resolve_byprop
from scipy.signal import butter, filtfilt, iirnotch

import argparse


WINDOW_SIZE = 750  # 3 seconds at 250 Hz
NUM_CHANNELS = 8


def main():
    parser = argparse.ArgumentParser(description="Qneuro H100 EEG Waveform Visualizer")
    parser.add_argument("--stream", type=str, default="aq1", help="LSL Stream Name (default: aq1)")
    args = parser.parse_args()

    STREAM_NAME = args.stream

    print(f"[*] Connecting to live LSL stream '{STREAM_NAME}'...")
    streams = resolve_byprop('name', STREAM_NAME, timeout=4.0)
    if not streams:
        for fallback in ["aq1", "EEG", "Qneuro_H100_EEG_PPG", "admin_EEG"]:
            streams = resolve_byprop('name', fallback, timeout=1.5)
            if streams:
                print(f"[+] Connected to fallback stream: {fallback}")
                break

    if not streams:
        print(f"[-] Error: Could not find stream '{STREAM_NAME}' (or fallbacks) on local network.")
        sys.exit(1)

    inlet = StreamInlet(streams[0], max_buflen=360)
    print(f"[+] Connected to: {streams[0].name()} from {streams[0].hostname()}")

    # Filter parameters (0.5 - 45 Hz bandpass + 50 Hz notch)
    srate = streams[0].nominal_srate() or 250.0
    nyq = 0.5 * srate
    b_band, a_band = butter(4, [0.5 / nyq, 45.0 / nyq], btype='band')
    b_notch, a_notch = iirnotch(50.0 / nyq, 30.0)

    data_buffer = np.zeros((WINDOW_SIZE, NUM_CHANNELS))

    fig, axes = plt.subplots(NUM_CHANNELS, 1, figsize=(11, 8), sharex=True)
    fig.suptitle(f"Qneuro H100 - Live 8-Channel EEG ({srate:.0f} Hz)", fontsize=14, fontweight='bold')
    lines = []

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

    for i in range(NUM_CHANNELS):
        ax = axes[i]
        ax.set_xlim(0, WINDOW_SIZE)
        ax.set_ylim(-150, 150)
        ax.set_ylabel(f"Ch {i+1}", rotation=0, labelpad=18, va='center', fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.4)
        line, = ax.plot([], [], lw=1.2, color=colors[i % len(colors)])
        lines.append(line)

    axes[-1].set_xlabel("Samples (Rolling 3-Second Window)")

    def update_plot(frame):
        nonlocal data_buffer

        # Drain all pending samples from inlet up to window capacity to avoid lag accumulation
        chunk, timestamps = inlet.pull_chunk(timeout=0.0, max_samples=WINDOW_SIZE)
        if chunk:
            chunk_arr = np.array(chunk)
            n_new = len(chunk)
            n_ch = min(chunk_arr.shape[1], NUM_CHANNELS)

            if n_new >= WINDOW_SIZE:
                data_buffer[:, :n_ch] = chunk_arr[-WINDOW_SIZE:, :n_ch]
            else:
                data_buffer = np.roll(data_buffer, -n_new, axis=0)
                data_buffer[-n_new:, :n_ch] = chunk_arr[:, :n_ch]

        # Preprocess buffer for display: DC-offset removal and notch + bandpass filtering
        detrended = data_buffer - np.mean(data_buffer, axis=0, keepdims=True)
        try:
            filtered = filtfilt(b_notch, a_notch, detrended, axis=0)
            filtered = filtfilt(b_band, a_band, filtered, axis=0)
        except Exception:
            filtered = detrended

        for i in range(NUM_CHANNELS):
            sig = filtered[:, i]
            lines[i].set_data(np.arange(WINDOW_SIZE), sig)
            ch_min, ch_max = float(np.min(sig)), float(np.max(sig))
            cur_min, cur_max = axes[i].get_ylim()

            # Update axis bounds only when signal escapes current view or contracts significantly
            if ch_max > cur_max - 5 or ch_min < cur_min + 5:
                axes[i].set_ylim(ch_min - 20, ch_max + 20)
            elif (ch_max - ch_min) > 10 and (ch_max - ch_min) < 0.3 * (cur_max - cur_min):
                axes[i].set_ylim(ch_min - 20, ch_max + 20)

        return lines

    ani = FuncAnimation(fig, update_plot, blit=False, interval=30, cache_frame_data=False)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


if __name__ == "__main__":
    main()
