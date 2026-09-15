"""
EEG Preprocessing Engine Package (Phase 1).
Includes IIR bandpass/notch filtering, sub-band extraction, artifact rejection, and epoch slicing.
"""

from .filters import EEGFilterPipeline
from .artifact_rejection import ArtifactRejectionEngine
from .epoch_slicer import EpochSlicer

__all__ = ["EEGFilterPipeline", "ArtifactRejectionEngine", "EpochSlicer"]
