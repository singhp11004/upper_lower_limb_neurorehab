"""
Classifiers Package (Phase 2B).
Includes Stepwise Linear Discriminant Analysis (SWLDA) for P300, LDA Workload Classifier, and Model Manager.
"""

from .swlda_p300 import SWLDAP300Classifier
from .workload_lda import WorkloadLDAClassifier
from .model_manager import ModelManager

__all__ = ["SWLDAP300Classifier", "WorkloadLDAClassifier", "ModelManager"]
