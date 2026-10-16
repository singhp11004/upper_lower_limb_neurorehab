"""
Biosignal Acquisition Module for Qneuro H100 (Bluetooth RFCOMM + LSL) & OpenBCI cEEGrid (BrainFlow API).
Supports live hardware streaming, synthetic/playback modes, and Lab Streaming Layer (LSL) integration.
"""

from .brainflow_streamer import BrainFlowStreamer
from .ring_buffer import CircularRingBuffer
from .signal_quality_monitor import SignalQualityMonitor
from .qneuro_pipeline import parse_int24_be, process_packet, create_lsl_outlet

__all__ = [
    "BrainFlowStreamer",
    "CircularRingBuffer",
    "SignalQualityMonitor",
    "parse_int24_be",
    "process_packet",
    "create_lsl_outlet"
]
