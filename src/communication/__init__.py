"""Communication module for Jetson-to-ESP32 binary UART protocol and command arbitration.
"""

from .packet_encoder import PacketEncoder
from .arbitrator import Arbitrator, ArbitratorDecision
from .serial_manager import SerialManager

__all__ = ["PacketEncoder", "Arbitrator", "ArbitratorDecision", "SerialManager"]
