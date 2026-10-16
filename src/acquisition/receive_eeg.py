#!/usr/bin/env python3
"""
Qneuro H100 Real-Time LSL Receiver and Pipeline Bridge
Receives live 8-channel EEG at 250 Hz, 2-channel PPG, and 7-axis IMU from Qneuro app on host.
Features real-time bandpass filtering (0.5 - 45 Hz), notch filtering (50 Hz), and CSV logging.
"""

import sys
import time
import argparse
import numpy as np
from pylsl import StreamInlet, resolve_byprop, resolve_streams
from scipy.signal import butter, filtfilt, iirnotch

def build_filters(srate=250.0):
    # Bandpass 0.5 - 45 Hz (4th order Butterworth)
    nyq = 0.5 * srate
    low = 0.5 / nyq
    high = 45.0 / nyq
    b_band, a_band = butter(4, [low, high], btype='band')  # type: ignore[misc]
    
    # 50 Hz Notch filter (Q=30)
    w0 = 50.0 / nyq
    b_notch, a_notch = iirnotch(w0, 30.0)
    return (b_band, a_band), (b_notch, a_notch)

def main():
    parser = argparse.ArgumentParser(description="Qneuro H100 LSL Stream Consumer")
    parser.add_argument("--stream", type=str, default="aq1", help="LSL Stream Name (default: aq1, fallback: EEG, admin_EEG)")
    parser.add_argument("--filter", action="store_true", help="Apply real-time 0.5-45 Hz bandpass + 50 Hz notch filter")
    parser.add_argument("--save", type=str, default=None, help="Save raw and filtered stream to CSV filename")
    args = parser.parse_args()

    print(f"[*] Discovering Qneuro stream '{args.stream}' on local network...")
    streams = []
    attempt = 0
    while not streams:
        attempt += 1
        streams = resolve_byprop('name', args.stream, timeout=2.0)
        if streams:
            break
        for fallback in ["aq1", "EEG", "ulnr_EEG", "Qneuro_H100_EEG_PPG", "admin_EEG"]:
            streams = resolve_byprop('name', fallback, timeout=1.0)
            if streams:
                print(f"[+] Connected to fallback stream: {fallback}")
                break
        if not streams and attempt % 5 == 0:
            all_s = resolve_streams(wait_time=1.0)
            avail = [f"{s.name()} ({s.type()})" for s in all_s]
            print(f"[*] Still waiting for '{args.stream}'... Visible streams: {avail if avail else 'None'}")
        time.sleep(0.5)

    inlet = StreamInlet(streams[0], max_buflen=360)
    info = inlet.info()
    n_channels = info.channel_count()
    srate = info.nominal_srate() if info.nominal_srate() > 0 else 250.0
    print(f"[+] Connected to: {info.name()} ({info.type()}) from {info.hostname()}")
    print(f"[+] Channels: {n_channels} | Sampling Rate: {srate:.1f} Hz | Format: {info.channel_format()}")

    # Setup file logging if requested
    csv_file = None
    if args.save:
        csv_file = open(args.save, 'w')
        headers = ["timestamp"] + [f"ch_{i+1}" for i in range(n_channels)]
        csv_file.write(",".join(headers) + "\n")
        print(f"[+] Logging telemetry into {args.save}")

    (b_band, a_band), (b_notch, a_notch) = build_filters(srate)
    buffer_len = int(srate * 2) # 2-second circular buffer for filtering
    data_buffer = np.zeros((buffer_len, n_channels))
    write_idx = 0
    buffer_filled = 0

    print("\n[*] Receiving live stream (Ctrl+C to stop)...\n")
    sample_count = 0
    t_start = time.time()
    last_print = time.time()

    try:
        while True:
            sample, timestamp = inlet.pull_sample(timeout=1.0)
            if sample is None:
                continue

            sample_count += 1
            sample_arr = np.array(sample)

            if csv_file:
                csv_file.write(f"{timestamp}," + ",".join([f"{v:.4f}" for v in sample_arr]) + "\n")

            # O(1) write-pointer circular buffer (no array copy)
            data_buffer[write_idx, :] = sample_arr
            write_idx = (write_idx + 1) % buffer_len
            buffer_filled = min(buffer_filled + 1, buffer_len)

            # Display snapshot at ~5 Hz
            now = time.time()
            if now - last_print >= 0.2:
                if args.filter and buffer_filled >= buffer_len:
                    # Reconstruct temporally-ordered buffer from circular write-pointer
                    linear_buf = np.vstack((data_buffer[write_idx:], data_buffer[:write_idx]))
                    # Apply notch + bandpass across buffer
                    notched = filtfilt(b_notch, a_notch, linear_buf, axis=0)
                    filtered = filtfilt(b_band, a_band, notched, axis=0)
                    disp = [round(x, 2) for x in filtered[-1, :]]
                    tag = "FILTERED [0.5-45Hz]"
                else:
                    disp = [round(x, 2) for x in sample_arr]
                    tag = "RAW µV"

                rate_est = sample_count / (now - t_start)
                print(f"[{timestamp:.3f}] ({rate_est:.1f} Hz) {tag}: {disp}")
                last_print = now

    except KeyboardInterrupt:
        print(f"\n[+] Acquisition halted by user. Total samples collected: {sample_count}")
    finally:
        if csv_file:
            csv_file.close()
            print(f"[+] Saved dataset to {args.save}")

if __name__ == "__main__":
    main()
