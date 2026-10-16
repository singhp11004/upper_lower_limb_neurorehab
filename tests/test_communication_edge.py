"""Unit tests for communication and edge execution modules.
"""

import numpy as np
from src.communication.packet_encoder import PacketEncoder, compute_crc8_maxim
from src.communication.arbitrator import Arbitrator
from src.edge.jetson_edge_runner import JetsonEdgeRunner


def test_packet_encoder_crc():
    packet = PacketEncoder.encode(0x01, 0x99, param=0, confidence=1.0)
    assert len(packet) == 7
    assert packet[0] == 0xAA
    assert packet[1] == 0x01
    assert packet[2] == 0x99

    valid, decoded = PacketEncoder.decode(packet)
    assert valid is True
    assert decoded["module_id"] == 0x01
    assert decoded["cmd_id"] == 0x99
    assert decoded["confidence"] == 100


def test_arbitrator_priority_veto():
    arb = Arbitrator(dwell_time_sec=0.2, veto_lockout_sec=0.5)

    # Double-blink veto must trigger E-Stop immediately
    dec = arb.process(is_veto=True, is_clench=True, p300_prob=0.99, current_time=1.0)
    assert dec.cmd_id == 0x99
    assert dec.is_vetoed is True

    # During lockout, all commands must be suppressed
    dec2 = arb.process(is_veto=False, is_clench=True, p300_prob=0.99, current_time=1.2)
    assert dec2.cmd_id is None
    assert dec2.is_vetoed is True


def test_arbitrator_dwell_time():
    arb = Arbitrator(dwell_time_sec=0.3)

    # Start dwelling on clench
    d1 = arb.process(is_veto=False, is_clench=True, p300_prob=0.1, current_time=10.0)
    assert d1.cmd_id is None

    # Before dwell time elapsed
    d2 = arb.process(is_veto=False, is_clench=True, p300_prob=0.1, current_time=10.2)
    assert d2.cmd_id is None

    # After dwell time elapsed
    d3 = arb.process(is_veto=False, is_clench=True, p300_prob=0.1, current_time=10.35)
    assert d3.cmd_id == 0x20  # Hand Close


def test_jetson_edge_runner_inference():
    runner = JetsonEdgeRunner(config_path="models/edge_swlda_weights.json")
    feat = np.zeros(200, dtype=np.float32)
    prob, is_target = runner.classify_p300(feat)
    assert 0.0 <= prob <= 1.0

    res = runner.process_cycle(is_veto=False, is_clench=False, feature_vector=feat)
    assert "p300_prob" in res
    assert res["latency_us"] < 5000  # Well under 5 ms


def test_arbitrator_leg_intent():
    arb = Arbitrator(dwell_time_sec=0.2)

    # Leg intent triggers MODULE_LEG (0x02) and CMD_STEP_FWD (0x30)
    d1 = arb.process(is_veto=False, is_clench=False, is_leg_intent=True, p300_prob=0.1, current_time=20.0)
    assert d1.cmd_id is None  # Dwell pending

    d2 = arb.process(is_veto=False, is_clench=False, is_leg_intent=True, p300_prob=0.1, current_time=20.25)
    assert d2.cmd_id == 0x30  # Step forward
    assert d2.module_id == 0x02  # Leg module

