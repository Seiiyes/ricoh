"""
Clasificadores para el sistema de auditoría.

Este módulo contiene componentes para clasificar y priorizar hallazgos.
"""

from audit_system.classifiers.severity_classifier import SeverityClassifier
from audit_system.classifiers.impact_calculator import ImpactCalculator

__all__ = ["SeverityClassifier", "ImpactCalculator"]
