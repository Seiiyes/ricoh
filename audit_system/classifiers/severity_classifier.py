"""
Clasificador de severidad para hallazgos de auditoría.

Clasifica hallazgos en niveles de severidad (Crítico, Alto, Medio, Bajo)
según reglas definidas basadas en tipo de hallazgo y métricas asociadas.
"""

from audit_system.models import Finding, Severity
from audit_system.config import get_config


class SeverityClassifier:
    """Clasifica hallazgos por severidad según reglas definidas."""
    
    def __init__(self):
        """Inicializa el clasificador con configuración."""
        self.config = get_config()
    
    def classify(self, finding: Finding) -> Severity:
        """
        Clasifica un hallazgo en Crítico, Alto, Medio o Bajo.
        
        Reglas de clasificación:
        - Crítico: Secrets hardcodeados, funciones >100 líneas, CVSS ≥9.0
        - Alto: N+1 >100 registros, archivos sin tests, CVSS 7.0-8.9
        - Medio: Type any, sin type hints, componentes >200 líneas
        - Bajo: TODOs, console.log, comentarios faltantes
        
        Args:
            finding: Hallazgo a clasificar
            
        Returns:
            Nivel de severidad asignado
        """
        # Reglas de severidad CRÍTICO
        if self._is_critical(finding):
            return Severity.CRITICO
        
        # Reglas de severidad ALTO
        if self._is_high(finding):
            return Severity.ALTO
        
        # Reglas de severidad MEDIO
        if self._is_medium(finding):
            return Severity.MEDIO
        
        # Reglas de severidad BAJO
        if self._is_low(finding):
            return Severity.BAJO
        
        # Por defecto: BAJO
        return Severity.BAJO
    
    def _is_critical(self, finding: Finding) -> bool:
        """Verifica si el hallazgo es de severidad crítica."""
        # Secrets hardcodeados
        if finding.subcategory == "hardcoded_secret":
            return True
        
        # Funciones que exceden 100 líneas
        if finding.subcategory == "long_function":
            metadata = getattr(finding, "metadata", {})
            if isinstance(metadata, dict):
                lines = metadata.get("lines", 0)
                if lines > self.config.CRITICAL_FUNCTION_THRESHOLD:
                    return True
        
        # Vulnerabilidades con CVSS >= 9.0
        if finding.category == "security" and finding.subcategory == "vulnerability":
            metadata = getattr(finding, "metadata", {})
            if isinstance(metadata, dict):
                cvss_score = metadata.get("cvss_score", 0.0)
                if cvss_score >= self.config.CRITICAL_CVSS_THRESHOLD:
                    return True
        
        return False
    
    def _is_high(self, finding: Finding) -> bool:
        """Verifica si el hallazgo es de severidad alta."""
        # Queries N+1 con más de 100 registros sin paginación
        if finding.subcategory == "n_plus_one":
            metadata = getattr(finding, "metadata", {})
            if isinstance(metadata, dict):
                records = metadata.get("records", 0)
                if records > self.config.PAGINATION_RECORD_THRESHOLD:
                    return True
        
        # Archivos sin tests (críticos)
        if finding.subcategory == "missing_tests":
            metadata = getattr(finding, "metadata", {})
            if isinstance(metadata, dict):
                is_critical = metadata.get("is_critical_file", False)
                if is_critical:
                    return True
        
        # Endpoints sin manejo de excepciones de base de datos
        if finding.subcategory == "no_db_exception_handling":
            return True
        
        # Vulnerabilidades con CVSS 7.0-8.9
        if finding.category == "security" and finding.subcategory == "vulnerability":
            metadata = getattr(finding, "metadata", {})
            if isinstance(metadata, dict):
                cvss_score = metadata.get("cvss_score", 0.0)
                if self.config.HIGH_CVSS_THRESHOLD <= cvss_score < self.config.CRITICAL_CVSS_THRESHOLD:
                    return True
        
        # Variables de entorno sensibles sin valor por defecto seguro
        if finding.subcategory == "insecure_env_default":
            return True
        
        return False
    
    def _is_medium(self, finding: Finding) -> bool:
        """Verifica si el hallazgo es de severidad media."""
        # Type 'any' en TypeScript
        if finding.subcategory == "type_any":
            return True
        
        # Funciones sin type hints en Python
        if finding.subcategory == "missing_type_hints":
            return True
        
        # Componentes que exceden 200 líneas
        if finding.subcategory == "large_component":
            metadata = getattr(finding, "metadata", {})
            if isinstance(metadata, dict):
                lines = metadata.get("lines", 0)
                if lines > self.config.LARGE_COMPONENT_THRESHOLD:
                    return True
        
        return False
    
    def _is_low(self, finding: Finding) -> bool:
        """Verifica si el hallazgo es de severidad baja."""
        # TODOs, FIXMEs, HACKs
        if finding.subcategory in ["todo_comment", "fixme_comment", "hack_comment"]:
            return True
        
        # console.log en producción
        if finding.subcategory == "console_log":
            return True
        
        # Comentarios faltantes o docstrings faltantes
        if finding.subcategory in ["missing_comments", "missing_docstring"]:
            return True
        
        return False
