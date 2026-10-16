#!/usr/bin/env python3
"""
Real-time 8-Channel EEG Stream Visualizer for Qneuro H100
Pulls live streams from LSL and displays scrolling EEG channel waveforms.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pylsl import StreamInlet, resolve_byprop

print("[*] Searching for active Qneuro LSL stream on local network...")
streams = resolve_byprop('type', 'EEG_PPG', timeout=5.0)

if not streams:
    print("[-] Error: No active Qneuro LSL stream found. Ensure qneuro_pipeline.py is running!")
    sys.exit(1)

inlet = StreamInlet(streams[0])
print(f"[+] Connected to stream: {streams[0].name()}")

WINDOW_SIZE = 1000  # 4 seconds at 250Hz
NUM_CHANNELS = 8

data_buffer = np.zeros((WINDOW_SIZE, NUM_CHANNELS))

fig, axes = plt.subplots(NUM_CHANNELS, 1, figsize=(10, 8), sharex=True)
fig.suptitle("Qneuro H100 - Real-time 8-Channel EEG Stream", fontsize=14, fontweight='bold')
lines = []

for i in range(NUM_CHANNELS):
    ax = axes[i]
    ax.set_xlim(0, WINDOW_SIZE)
    ax.set_ylim(-2000, 2000)
    ax.set_ylabel(f"CH {i+1}", rotation=0, labelpad=15, va='center')
    ax.grid(True, linestyle='--', alpha=0.5)
    line, = ax.plot([], [], lw=1.2, color='#1f77b4')
    lines.append(line)

plt.xlabel("Samples (Rolling Time Window)")


def update_plot(frame):
    global data_buffer

    while True:
        sample, timestamp = inlet.pull_sample(timeout=0.0)
        if not sample:
            break

        data_buffer = np.roll(data_buffer, -1, axis=0)
        data_buffer[-1, :] = sample[:NUM_CHANNELS]

    for i in range(NUM_CHANNELS):
        lines[i].set_data(np.arange(WINDOW_SIZE), data_buffer[:, i])
        ch_min, ch_max = np.min(data_buffer[:, i]), np.max(data_buffer[:, i])
        if ch_max - ch_min > 10:
            axes[i].set_ylim(ch_min - (abs(ch_min) * 0.1), ch_max + (abs(ch_max) * 0.1))

    return lines


ani = FuncAnimation(fig, update_plot, blit=False, interval=20, cache_frame_data=False)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
