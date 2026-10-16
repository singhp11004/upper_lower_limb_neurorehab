"""
Artifact Rejection Pipeline (Amplitude Thresholding & Quality Flagging).
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional, List


class ArtifactRejectionEngine:
    def __init__(self, amplitude_threshold_uv: float = 150.0, flatline_threshold_std: float = 0.5,
                 active_channels: Optional[List[int]] = None):
        """
        :param amplitude_threshold_uv: Microvolt spike limit (default 150 uV)
        :param flatline_threshold_std: Flatline detection std limit
        :param active_channels: List of channel indices to evaluate (default: all channels).
                                Use this to exclude zero-padded channels (e.g. Qneuro 8ch padded to 16).
        """
        self.amplitude_threshold_uv = amplitude_threshold_uv
        self.flatline_threshold_std = flatline_threshold_std
        self.active_channels = active_channels

    def clean_epoch(self, epoch: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Evaluate and clean a single EEG epoch array (n_channels, n_samples).

        :return: Tuple (cleaned_epoch, metadata_dict)
        """
        is_rejected = False
        reasons = []

        # Determine which channels to evaluate for artifact criteria
        if self.active_channels is not None:
            eval_epoch = epoch[self.active_channels, :]
        else:
            eval_epoch = epoch

        max_val = np.max(np.abs(eval_epoch))
        if max_val > self.amplitude_threshold_uv:
            is_rejected = True
            reasons.append(f"Peak amplitude ({max_val:.1f} uV) exceeded {self.amplitude_threshold_uv} uV")

        stds = np.std(eval_epoch, axis=1)
        if np.any(stds < self.flatline_threshold_std):
            is_rejected = True
            reasons.append("Electrode contact loss/flatline detected")

        cleaned = epoch.copy()
        if is_rejected:
            # Soft clip extreme microvolt artifacts
            cleaned = np.clip(cleaned, -self.amplitude_threshold_uv, self.amplitude_threshold_uv)

        meta = {
            "is_rejected": is_rejected,
            "reasons": reasons,
            "max_amplitude_uv": float(max_val),
            "channel_stds": stds.tolist()
        }

        return cleaned, meta

