"""Lightweight real-time runner for Jetson Orin Nano edge execution.

Loads only numpy, struct, json, and pyserial.
Performs linear discriminant evaluation via dot product: logit = w.dot(x) + b
Decoupled entirely from scikit-learn, mne, matplotlib, and seaborn.
"""

import os
import sys
import json
import time
import struct
import numpy as np
from typing import Tuple, Optional

# Re-use packet encoder & arbitrator from lightweight communication module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.communication.packet_encoder import PacketEncoder
from src.communication.arbitrator import Arbitrator
from src.communication.serial_manager import SerialManager


class JetsonEdgeRunner:
    """Minimal latency edge inference engine."""

    def __init__(self, config_path: str = "models/edge_swlda_weights.json", serial_port: Optional[str] = None):
        if not os.path.isabs(config_path):
            config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", config_path))

        with open(config_path, "r") as f:
            self.cfg = json.load(f)

        self.weights = np.array(self.cfg["weights"], dtype=np.float32)
        self.intercept = np.float32(self.cfg["intercept"])
        self.selected_indices = np.array(self.cfg["selected_feature_indices"], dtype=np.int32)
        self.p300_thresh = float(self.cfg.get("p300_confidence_threshold", 0.65))

        self.arbitrator = Arbitrator(p300_confidence_thresh=self.p300_thresh)
        self.serial_mgr = SerialManager(port=serial_port)

    def classify_p300(self, feature_vector: np.ndarray) -> Tuple[float, bool]:
        """Classifies a single 1D feature vector using exported weights.
        
        Args:
            feature_vector: 1D numpy array from P300 feature extractor.
            
        Returns:
            Tuple of (probability, is_target_bool).
        """
        x_sub = feature_vector[self.selected_indices]
        logit = float(np.dot(self.weights, x_sub) + self.intercept)
        # Standard sigmoid mapping
        prob = 1.0 / (1.0 + np.exp(-logit))
        return prob, (prob >= self.p300_thresh)

    def process_cycle(
        self,
        is_veto: bool,
        is_clench: bool,
        feature_vector: np.ndarray,
        workload_state: str = "ACTIVE"
    ) -> dict:
        """Runs one inference + arbitration step."""
        t0 = time.perf_counter()
        prob, is_target = self.classify_p300(feature_vector)
        decision = self.arbitrator.process(
            is_veto=is_veto,
            is_clench=is_clench,
            p300_prob=prob,
            workload_state=workload_state
        )

        packet = None
        if decision.cmd_id is not None:
            packet = PacketEncoder.encode(
                module_id=decision.module_id,
                cmd_id=decision.cmd_id,
                param=decision.param,
                confidence=decision.confidence
            )
            self.serial_mgr.send_packet(packet)

        t1 = time.perf_counter()
        return {
            "p300_prob": prob,
            "decision": decision.reason,
            "packet": packet.hex() if packet else None,
            "latency_us": (t1 - t0) * 1e6
        }
