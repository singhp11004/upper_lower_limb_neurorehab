"""Binary UART Packet Encoder for Jetson-to-ESP32 communication.

Follows the 7-byte protocol:
  Byte 0: 0xAA (Sync byte)
  Byte 1: Module ID (0x01 = Hand, 0x02 = Leg)
  Byte 2: Command ID (0x10 = Open, 0x20 = Close, 0x30 = Step Fwd, 0x40 = Step Back, 0x99 = E-Stop)
  Byte 3: Param High (Upper 8 bits of 16-bit parameter, e.g. servo angle or duty cycle)
  Byte 4: Param Low (Lower 8 bits of 16-bit parameter)
  Byte 5: Confidence (0 - 100 integer)
  Byte 6: CRC-8/MAXIM checksum over bytes 0..5 (poly 0x31 / reflected 0x8C, init 0x00, xorout 0x00)
"""

import struct
from typing import Tuple


def compute_crc8_maxim(data: bytes) -> int:
    """Computes CRC-8/MAXIM (Dallas/Maxim 1-Wire: poly 0x31 reversed to 0x8C).
    
    Polynomial: x^8 + x^5 + x^4 + 1 (0x31)
    Initial value: 0x00
    Reflected input/output
    """
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x01:
                crc = (crc >> 1) ^ 0x8C
            else:
                crc >>= 1
    return crc & 0xFF


class PacketEncoder:
    """Encodes and decodes binary UART packets between Jetson and ESP32."""

    SYNC_HEADER = 0xAA

    MODULE_HAND = 0x01
    MODULE_LEG = 0x02

    CMD_OPEN = 0x10
    CMD_CLOSE = 0x20
    CMD_STEP_FWD = 0x30
    CMD_STEP_BACK = 0x40
    CMD_ESTOP = 0x99

    @classmethod
    def encode(cls, module_id: int, cmd_id: int, param: int = 0, confidence: float = 1.0) -> bytes:
        """Encodes command into a 7-byte binary packet with CRC-8 checksum.
        
        Args:
            module_id: 0x01 (Hand) or 0x02 (Leg).
            cmd_id: 0x10, 0x20, 0x30, 0x40, 0x99.
            param: 16-bit unsigned integer (0 - 65535), e.g. servo angle in degrees.
            confidence: Float between 0.0 and 1.0 (or 0-100), mapped to 0..100.
        
        Returns:
            bytes: Exactly 7 bytes.
        """
        conf_int = int(round(confidence * 100)) if confidence <= 1.0 else int(round(min(100, confidence)))
        conf_int = max(0, min(100, conf_int))
        param_uint16 = max(0, min(65535, int(param)))

        param_hi = (param_uint16 >> 8) & 0xFF
        param_lo = param_uint16 & 0xFF

        payload = struct.pack('>BBBBBB', cls.SYNC_HEADER, module_id, cmd_id, param_hi, param_lo, conf_int)
        crc = compute_crc8_maxim(payload)
        return payload + bytes([crc])

    @classmethod
    def decode(cls, packet: bytes) -> Tuple[bool, dict]:
        """Decodes a 7-byte packet and verifies its CRC checksum.
        
        Returns:
            Tuple of (is_valid, parsed_dict).
        """
        if len(packet) != 7:
            return False, {"error": f"Expected 7 bytes, got {len(packet)}"}

        if packet[0] != cls.SYNC_HEADER:
            return False, {"error": f"Invalid sync header: 0x{packet[0]:02X}"}

        calc_crc = compute_crc8_maxim(packet[:6])
        if calc_crc != packet[6]:
            return False, {
                "error": f"CRC mismatch: expected 0x{calc_crc:02X}, received 0x{packet[6]:02X}"
            }

        module_id = packet[1]
        cmd_id = packet[2]
        param = (packet[3] << 8) | packet[4]
        confidence = packet[5]

        return True, {
            "module_id": module_id,
            "cmd_id": cmd_id,
            "param": param,
            "confidence": confidence,
            "crc8": packet[6]
        }
