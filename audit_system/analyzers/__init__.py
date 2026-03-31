"""
Analizadores de código para el sistema de auditoría.

Este módulo contiene los analizadores especializados para diferentes aspectos
del código: performance, calidad, seguridad, arquitectura, UX, manejo de errores,
testing y configuración.
"""

from audit_system.analyzers.performance_analyzer import PerformanceAnalyzer
from audit_system.analyzers.quality_analyzer import QualityAnalyzer
from audit_system.analyzers.security_analyzer import SecurityAnalyzer
from audit_system.analyzers.architecture_analyzer import ArchitectureAnalyzer
from audit_system.analyzers.ux_analyzer import UXAnalyzer
from audit_system.analyzers.error_handling_analyzer import ErrorHandlingAnalyzer
from audit_system.analyzers.testing_analyzer import TestingAnalyzer
from audit_system.analyzers.config_analyzer import ConfigAnalyzer

__all__ = [
    "PerformanceAnalyzer",
    "QualityAnalyzer",
    "SecurityAnalyzer",
    "ArchitectureAnalyzer",
    "UXAnalyzer",
    "ErrorHandlingAnalyzer",
    "TestingAnalyzer",
    "ConfigAnalyzer",
]
