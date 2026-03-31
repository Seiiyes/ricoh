"""
Configuración del sistema de auditoría.

Define umbrales, límites y parámetros configurables para el análisis de código.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AuditConfig:
    """Configuración principal del sistema de auditoría."""
    
    # Umbrales de tamaño de archivo
    LARGE_FILE_THRESHOLD: int = 300  # líneas
    
    # Umbrales de complejidad de funciones
    LONG_FUNCTION_THRESHOLD: int = 50  # líneas
    CRITICAL_FUNCTION_THRESHOLD: int = 100  # líneas (severidad crítica)
    
    # Umbrales de indentación
    DEEP_NESTING_THRESHOLD: int = 3  # niveles
    
    # Umbrales de duplicación de código
    CODE_DUPLICATION_THRESHOLD: float = 0.8  # 80% similitud
    
    # Umbrales de paginación
    PAGINATION_RECORD_THRESHOLD: int = 100  # registros
    
    # Umbrales de componentes React
    LARGE_COMPONENT_THRESHOLD: int = 200  # líneas
    
    # Umbrales de props drilling
    PROPS_DRILLING_DEPTH_THRESHOLD: int = 2  # niveles
    
    # Umbrales de vulnerabilidades
    CRITICAL_CVSS_THRESHOLD: float = 9.0  # CVSS score
    HIGH_CVSS_THRESHOLD: float = 7.0  # CVSS score
    
    # Umbrales de esfuerzo semanal
    MAX_WEEKLY_EFFORT_HOURS: float = 40.0  # horas
    
    # Directorios a analizar
    BACKEND_DIRS: List[str] = None
    FRONTEND_DIRS: List[str] = None
    
    # Directorios a excluir
    EXCLUDE_DIRS: List[str] = None
    
    # Extensiones de archivo
    PYTHON_EXTENSIONS: List[str] = None
    TYPESCRIPT_EXTENSIONS: List[str] = None
    
    # Patrones de secrets a detectar
    SECRET_PATTERNS: List[str] = None
    
    # Configuración de reportes
    REPORT_OUTPUT_DIR: str = "docs"
    REPORT_FILENAME: str = "OPTIMIZACION_HALLAZGOS.md"
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "audit_system/logs/audit.log"
    
    def __post_init__(self):
        """Inicializa valores por defecto para listas."""
        if self.BACKEND_DIRS is None:
            self.BACKEND_DIRS = [
                "backend/api",
                "backend/db",
                "backend/middleware",
                "backend/jobs",
                "backend/services"
            ]
        
        if self.FRONTEND_DIRS is None:
            self.FRONTEND_DIRS = [
                "src/components",
                "src/pages",
                "src/hooks",
                "src/services",
                "src/utils"
            ]
        
        if self.EXCLUDE_DIRS is None:
            self.EXCLUDE_DIRS = [
                "__pycache__",
                "node_modules",
                ".git",
                ".venv",
                "venv",
                "dist",
                "build",
                ".pytest_cache",
                ".hypothesis",
                "migrations"
            ]
        
        if self.PYTHON_EXTENSIONS is None:
            self.PYTHON_EXTENSIONS = [".py"]
        
        if self.TYPESCRIPT_EXTENSIONS is None:
            self.TYPESCRIPT_EXTENSIONS = [".ts", ".tsx"]
        
        if self.SECRET_PATTERNS is None:
            self.SECRET_PATTERNS = [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]",
                r"token\s*=\s*['\"][^'\"]+['\"]",
                r"aws[_-]?access[_-]?key\s*=\s*['\"][^'\"]+['\"]",
                r"private[_-]?key\s*=\s*['\"][^'\"]+['\"]"
            ]
    
    def get_severity_weights(self) -> Dict[str, int]:
        """Retorna pesos de severidad para cálculos de impacto."""
        return {
            "CRITICO": 4,
            "ALTO": 3,
            "MEDIO": 2,
            "BAJO": 1
        }
    
    def get_complexity_factors(self) -> Dict[str, int]:
        """Retorna factores de complejidad para cálculos de esfuerzo."""
        return {
            "simple": 1,      # Cambio localizado
            "moderado": 3,    # Múltiples archivos
            "complejo": 5     # Refactor arquitectónico
        }


# Instancia global de configuración
config = AuditConfig()


def get_config() -> AuditConfig:
    """
    Obtiene la configuración global del sistema.
    
    Returns:
        Instancia de AuditConfig
    """
    return config


def update_config(**kwargs) -> None:
    """
    Actualiza la configuración global con nuevos valores.
    
    Args:
        **kwargs: Parámetros de configuración a actualizar
    """
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
