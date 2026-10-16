#!/usr/bin/env python3
"""
Qneuro H100 Acquisition and LSL Streamer
Connects to Qneuro H100 over Bluetooth RFCOMM SPP, triggers live binary telemetry,
unpacks 24-bit EEG + 16-bit PPG, and broadcasts via Lab Streaming Layer (LSL).
"""

import sys
import time
import socket
import struct
from pylsl import StreamInfo, StreamOutlet

BD_ADDR = "2C:FE:8B:FC:80:C1"
RFCOMM_CHANNELS = [6, 8]
PACKET_SIZE = 46
DEFAULT_STREAM_NAME = "aq1"

# ADS1299 ADC-to-Microvolt conversion factor
# Formula: VREF / (Gain * 2^23) * 1e6
# Qneuro H100 defaults: VREF = 4.5V, Gain = 24
ADC_TO_UV = (4.5 / (24 * (2**23))) * 1e6  # ≈ 0.02235 µV/LSB


def parse_int24_be(b: bytes, offset: int) -> int:
    """Unpacks a signed 24-bit Big-Endian integer from a byte array."""
    val = (b[offset] << 16) | (b[offset + 1] << 8) | b[offset + 2]
    if val & 0x800000:
        val -= 0x1000000
    return val


def process_packet(packet: bytes):
    """Validates the 46-byte frame structure and decodes multi-signal arrays."""
    # Verify strict frame boundary alignments
    if packet[0] != 0xAA or packet[1] != 0x55:
        return None

    # Checksum validation loop (Modulo 256 sum of bytes 2 to 44)
    expected_checksum = packet[45]
    calculated_checksum = sum(packet[2:45]) & 0xFF
    if expected_checksum != calculated_checksum:
        return None

    packet_counter = packet[2]

    # Unpack 8 Channels of 24-Bit EEG Data and convert ADC counts to microvolts
    eeg_data = []
    for i in range(8):
        idx = 3 + (i * 3)
        eeg_data.append(float(parse_int24_be(packet, idx)) * ADC_TO_UV)

    # Unpack 2 Channels of 16-Bit PPG Data (Big-Endian unsigned)
    ppg_red = float(struct.unpack('>H', packet[27:29])[0])
    ppg_ir = float(struct.unpack('>H', packet[29:31])[0])

    return eeg_data + [ppg_red, ppg_ir]


def create_lsl_outlet(stream_name: str = DEFAULT_STREAM_NAME):
    """Instantiate the Lab Streaming Layer (LSL) Blueprint."""
    lsl_info = StreamInfo(stream_name, 'EEG_PPG', 10, 250, 'float32', 'qneuro_80c1')
    channels = lsl_info.desc().append_child("channels")
    labels = [f"EEG_{i+1}" for i in range(8)] + ["PPG_Red", "PPG_IR"]
    for label in labels:
        channels.append_child("channel").append_child_value("label", label)
    return StreamOutlet(lsl_info)


def connect_socket(bd_addr: str = BD_ADDR, channels=None):
    if channels is None:
        channels = RFCOMM_CHANNELS
    for ch in channels:
        try:
            print(f"[*] Trying Bluetooth Serial SPP Socket ({bd_addr}: Channel {ch})...")
            s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            s.settimeout(4.0)
            s.connect((bd_addr, ch))
            print(f"[+] Successfully connected to RFCOMM Channel {ch}!")
            return s
        except Exception as e:
            print(f"[-] Channel {ch} failed: {e}")
            try:
                s.close()
            except Exception:
                pass
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Qneuro H100 Acquisition and LSL Streamer")
    parser.add_argument("--stream", type=str, default=DEFAULT_STREAM_NAME, help="LSL Stream Name (default: aq1)")
    parser.add_argument("--addr", type=str, default=BD_ADDR, help=f"Bluetooth device address (default: {BD_ADDR})")
    parser.add_argument("--channel", type=int, default=None, help="Specific RFCOMM channel (e.g. 6 or 8)")
    args = parser.parse_args()

    lsl_outlet = create_lsl_outlet(args.stream)
    print(f"[+] Initialized LSL Outlet with stream name: '{args.stream}'")

    rfcomm_chs = [args.channel] if args.channel else RFCOMM_CHANNELS
    s = connect_socket(bd_addr=args.addr, channels=rfcomm_chs)
    if not s:
        print("[-] Could not establish Bluetooth RFCOMM connection to headset.")
        sys.exit(1)

    try:
        print("[+] Initializing Qneuro hardware stream...")
        # Send activation opcode sequence (STRM + 0x01)
        s.sendall(b'\x53\x54\x52\x4D\x01')
        time.sleep(0.2)

        print(f"[+] Streaming active. Broadcasting brainwaves to LSL stream '{args.stream}'. Press Ctrl+C to close.")

        raw_buffer = b""
        packet_count = 0
        dropped_count = 0
        seq_gap_count = 0
        last_counter = -1
        last_stat_time = time.time()

        while True:
            chunk = s.recv(1024)
            if not chunk:
                print("[-] Device disconnected prematurely.")
                break
            raw_buffer += chunk

            # Extract and parse whole packets out of the active socket array
            while len(raw_buffer) >= PACKET_SIZE:
                sync_idx = raw_buffer.find(b'\xAA\x55')

                if sync_idx == -1:
                    raw_buffer = raw_buffer[-(PACKET_SIZE - 1):]
                    break
                elif sync_idx > 0:
                    raw_buffer = raw_buffer[sync_idx:]
                    continue

                packet = raw_buffer[:PACKET_SIZE]
                sample = process_packet(packet)

                if sample:
                    # Detect packet counter sequence gaps (Bluetooth dropout detection)
                    current_counter = packet[2]
                    if last_counter >= 0:
                        expected = (last_counter + 1) % 256
                        if current_counter != expected:
                            gap = (current_counter - last_counter) % 256 - 1
                            seq_gap_count += gap
                    last_counter = current_counter

                    lsl_outlet.push_sample(sample)
                    packet_count += 1
                    raw_buffer = raw_buffer[PACKET_SIZE:]
                else:
                    # Checksum mismatch or invalid payload: advance by 2 bytes to find the next valid sync header
                    dropped_count += 1
                    raw_buffer = raw_buffer[2:]

            now = time.time()
            if now - last_stat_time >= 3.0:
                elapsed = now - last_stat_time
                gap_str = f" | Seq Gaps: {seq_gap_count}" if seq_gap_count > 0 else ""
                print(f"[STATUS] Stream '{args.stream}' - Streamed: {packet_count} (~{packet_count / elapsed:.1f} Hz) | CRC Drops: {dropped_count}{gap_str}")
                packet_count = 0
                dropped_count = 0
                seq_gap_count = 0
                last_stat_time = now

    except KeyboardInterrupt:
        print("\n[*] Halting data pipeline safely. Sending stop code...")
        try:
            s.sendall(b'\x53\x54\x52\x4D\x00')
            time.sleep(0.1)
        except Exception:
            pass
    except Exception as e:
        print(f"[-] Pipeline error: {e}")
    finally:
        s.close()
        print("[+] Serial radio detached successfully.")


if __name__ == "__main__":
    main()
