"""Arbitration Engine and Safety State Machine.

Implements the 4-level signal priority cascade:
  Level 1 (Highest): EOG Double-Blink Veto -> Emergency Stop (0x99), 500 ms lockout
  Level 2: Jaw-Clench High-Gamma Burst -> Hand Close (0x20) / Leg Step (0x30), dwell confirmation
  Level 3: P300 Oddball ERP -> Hand Open (0x10), confidence >= threshold + dwell confirmation
  Level 4: Alpha Workload -> Rest/Active state gate
"""

import time
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ArbitratorDecision:
    module_id: Optional[int]
    cmd_id: Optional[int]
    param: int
    confidence: float
    reason: str
    is_vetoed: bool = False


class Arbitrator:
    """Stateful priority arbitrator and safety manager."""

    def __init__(
        self,
        p300_confidence_thresh: float = 0.65,
        dwell_time_sec: float = 0.3,
        veto_lockout_sec: float = 0.5,
    ):
        self.p300_thresh = p300_confidence_thresh
        self.dwell_time_sec = dwell_time_sec
        self.veto_lockout_sec = veto_lockout_sec

        self.veto_until_time = 0.0
        self.pending_intent: Optional[Tuple[int, int]] = None  # (module, cmd)
        self.pending_intent_start_time = 0.0
        self.pending_confidence = 0.0

        self.last_dispatched_cmd_time = 0.0

    def process(
        self,
        is_veto: bool,
        is_clench: bool,
        p300_prob: float,
        workload_state: str = "ACTIVE",
        current_time: Optional[float] = None,
    ) -> ArbitratorDecision:
        """Processes current detector outputs and resolves arbitration.
        
        Args:
            is_veto: True if double-blink veto detected.
            is_clench: True if high-gamma jaw-clench burst detected.
            p300_prob: Classifier probability for P300 target (0.0 to 1.0).
            workload_state: 'ACTIVE' or 'REST' (alpha state gate).
            current_time: Optional epoch timestamp (defaults to time.monotonic()).
            
        Returns:
            ArbitratorDecision with command details or None if idle/dwell pending.
        """
        now = time.monotonic() if current_time is None else current_time

        # PRIORITY 1: Blink-Veto (Immediate Emergency Stop + Lockout)
        if is_veto:
            self.veto_until_time = now + self.veto_lockout_sec
            self.pending_intent = None
            return ArbitratorDecision(
                module_id=0x01,  # Broadcast / Hand E-Stop
                cmd_id=0x99,     # Emergency Stop
                param=0,
                confidence=1.0,
                reason="Double-Blink Veto Triggered (Emergency Stop)",
                is_vetoed=True
            )

        # Check if in veto lockout cooldown
        if now < self.veto_until_time:
            self.pending_intent = None
            remaining_ms = int((self.veto_until_time - now) * 1000)
            return ArbitratorDecision(
                module_id=None,
                cmd_id=None,
                param=0,
                confidence=0.0,
                reason=f"Suppressed by Veto Lockout ({remaining_ms}ms remaining)",
                is_vetoed=True
            )

        # Check Alpha Workload gate: If in deep REST / Fatigue, suppress normal motor triggers
        if workload_state.upper() == "REST":
            self.pending_intent = None
            return ArbitratorDecision(
                module_id=None,
                cmd_id=None,
                param=0,
                confidence=0.0,
                reason="Idle / Gated by Alpha Workload (REST state)"
            )

        # PRIORITY 2: Jaw-Clench Intent (Close Hand 0x20)
        candidate_intent = None
        candidate_conf = 0.0

        if is_clench:
            candidate_intent = (0x01, 0x20)  # Hand Close
            candidate_conf = 0.95
        # PRIORITY 3: P300 ERP Intent (Open Hand 0x10)
        elif p300_prob >= self.p300_thresh:
            candidate_intent = (0x01, 0x10)  # Hand Open
            candidate_conf = float(p300_prob)

        # Dwell-time confirmation state machine
        if candidate_intent is not None:
            if self.pending_intent == candidate_intent:
                elapsed = now - self.pending_intent_start_time
                if elapsed >= self.dwell_time_sec:
                    # Confirmed! Reset pending to avoid re-triggering constantly without re-dwell
                    self.pending_intent = None
                    self.last_dispatched_cmd_time = now
                    cmd_name = "Hand Close" if candidate_intent[1] == 0x20 else "Hand Open"
                    return ArbitratorDecision(
                        module_id=candidate_intent[0],
                        cmd_id=candidate_intent[1],
                        param=90,  # 90 degrees target position
                        confidence=candidate_conf,
                        reason=f"Confirmed {cmd_name} after {int(elapsed*1000)}ms dwell"
                    )
                else:
                    return ArbitratorDecision(
                        module_id=None,
                        cmd_id=None,
                        param=0,
                        confidence=candidate_conf,
                        reason=f"Dwelling on intent ({int(elapsed*1000)}/{int(self.dwell_time_sec*1000)}ms)"
                    )
            else:
                # Start dwelling on new intent
                self.pending_intent = candidate_intent
                self.pending_intent_start_time = now
                self.pending_confidence = candidate_conf
                return ArbitratorDecision(
                    module_id=None,
                    cmd_id=None,
                    param=0,
                    confidence=candidate_conf,
                    reason="Started dwelling on candidate intent"
                )
        else:
            # No intent detected in this frame
            self.pending_intent = None
            return ArbitratorDecision(
                module_id=None,
                cmd_id=None,
                param=0,
                confidence=0.0,
                reason="Idle (No candidate intent)"
            )
