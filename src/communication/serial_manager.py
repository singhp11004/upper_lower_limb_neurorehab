"""Serial Manager for sending binary UART packets to ESP32 with ACK/retry and console fallback.
"""

import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import serial
except ImportError:
    serial = None


class SerialManager:
    """Manages serial communication with ESP32-P4 over UART."""

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, timeout: float = 0.1):
        self.port_name = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.is_connected = False

        if port and serial is not None:
            self._connect()
        else:
            if port and serial is None:
                logger.warning("pyserial is not installed. Running in console fallback mode.")
            self.is_connected = False

    def _connect(self) -> bool:
        try:
            self.serial_conn = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.is_connected = True
            logger.info(f"Connected to ESP32 on {self.port_name} at {self.baudrate} baud.")
            return True
        except Exception as e:
            logger.warning(f"Could not open serial port {self.port_name}: {e}. Fallback to console.")
            self.serial_conn = None
            self.is_connected = False
            return False

    def send_packet(self, packet: bytes, max_retries: int = 3) -> bool:
        """Sends a 7-byte binary packet. In console mode, logs hex representation."""
        hex_str = " ".join(f"{b:02X}" for b in packet)

        if not self.is_connected or self.serial_conn is None:
            # Console simulation mode
            logger.info(f"[SIMULATED UART TX] -> {hex_str}")
            return True

        for attempt in range(max_retries):
            try:
                self.serial_conn.write(packet)
                self.serial_conn.flush()
                # Wait briefly for ACK (0x06) if protocol supports it
                ack = self.serial_conn.read(1)
                if ack == b"\x06":
                    return True
                elif len(ack) == 0:
                    # No ACK returned within timeout, retry
                    time.sleep(0.01)
                    continue
                else:
                    logger.warning(f"Unexpected response from ESP32: {ack.hex()}")
            except Exception as e:
                logger.error(f"Serial write error: {e}")
                time.sleep(0.01)

        logger.warning(f"Failed to receive ACK for packet {hex_str} after {max_retries} attempts.")
        return False

    def close(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.is_connected = False
