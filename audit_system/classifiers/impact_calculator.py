"""
Calculador de impacto y esfuerzo para priorización de hallazgos.

Calcula scores de impacto y esfuerzo, genera matriz de priorización,
y selecciona los hallazgos más importantes según ratio impacto/esfuerzo.
"""

from typing import List
from audit_system.models import Finding, PriorityMatrix
from audit_system.config import get_config


class ImpactCalculator:
    """Calcula impacto y esfuerzo para priorización de hallazgos."""
    
    def __init__(self):
        """Inicializa el calculador con configuración."""
        self.config = get_config()
    
    def calculate_impact_score(self, finding: Finding) -> float:
        """
        Calcula score de impacto basado en severidad y alcance.
        
        Fórmula: (severity_weight * 10) + (affected_files * 2) + (frequency * 5)
        
        Args:
            finding: Hallazgo a evaluar
            
        Returns:
            Score de impacto calculado
        """
        # Obtener peso de severidad
        severity_weight = finding.severity.get_weight()
        
        # Extraer metadata
        metadata = getattr(finding, "metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        
        affected_files = metadata.get("affected_files", 1)
        frequency = metadata.get("frequency", 1)
        
        # Aplicar fórmula
        impact_score = (severity_weight * 10) + (affected_files * 2) + (frequency * 5)
        
        return float(impact_score)
    
    def calculate_effort_score(self, finding: Finding) -> float:
        """
        Calcula score de esfuerzo basado en complejidad.
        
        Fórmula: complexity_factor + (files_to_modify * 2) + (dependencies * 3)
        
        complexity_factor:
          - simple: 1 (cambio localizado)
          - moderado: 3 (múltiples archivos)
          - complejo: 5 (refactor arquitectónico)
        
        Args:
            finding: Hallazgo a evaluar
            
        Returns:
            Score de esfuerzo calculado
        """
        # Extraer metadata
        metadata = getattr(finding, "metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        
        # Obtener complejidad
        complexity = metadata.get("complexity", "simple")
        complexity_factors = self.config.get_complexity_factors()
        complexity_factor = complexity_factors.get(complexity, 1)
        
        files_to_modify = metadata.get("files_to_modify", 1)
        dependencies_count = metadata.get("dependencies", 0)
        
        # Aplicar fórmula
        effort_score = complexity_factor + (files_to_modify * 2) + (dependencies_count * 3)
        
        return float(effort_score)
    
    def calculate_priority_matrix(self, findings: List[Finding]) -> PriorityMatrix:
        """
        Genera matriz impacto/esfuerzo para todos los hallazgos.
        
        Clasifica hallazgos en cuatro cuadrantes:
        - Alto impacto, bajo esfuerzo: Quick wins
        - Alto impacto, alto esfuerzo: Major projects
        - Bajo impacto, bajo esfuerzo: Fill-ins
        - Bajo impacto, alto esfuerzo: Avoid
        
        Args:
            findings: Lista de hallazgos a clasificar
            
        Returns:
            Matriz de priorización con hallazgos clasificados
        """
        # Calcular scores para todos los hallazgos
        for finding in findings:
            finding.impact_score = self.calculate_impact_score(finding)
            finding.effort_score = self.calculate_effort_score(finding)
            if finding.effort_score > 0:
                finding.priority_ratio = finding.impact_score / finding.effort_score
            else:
                finding.priority_ratio = finding.impact_score
        
        # Calcular medianas para dividir cuadrantes
        if not findings:
            return PriorityMatrix()
        
        impact_scores = [f.impact_score for f in findings]
        effort_scores = [f.effort_score for f in findings]
        
        impact_median = self._calculate_median(impact_scores)
        effort_median = self._calculate_median(effort_scores)
        
        # Clasificar en cuadrantes
        matrix = PriorityMatrix()
        
        for finding in findings:
            high_impact = finding.impact_score >= impact_median
            high_effort = finding.effort_score >= effort_median
            
            if high_impact and not high_effort:
                matrix.high_impact_low_effort.append(finding)
            elif high_impact and high_effort:
                matrix.high_impact_high_effort.append(finding)
            elif not high_impact and not high_effort:
                matrix.low_impact_low_effort.append(finding)
            else:  # low impact, high effort
                matrix.low_impact_high_effort.append(finding)
        
        return matrix
    
    def select_top_10(self, findings: List[Finding]) -> List[Finding]:
        """
        Selecciona los 10 hallazgos con mayor ratio impacto/esfuerzo.
        
        Args:
            findings: Lista de hallazgos a evaluar
            
        Returns:
            Lista de los 10 hallazgos con mayor prioridad
        """
        # Calcular scores si no están calculados
        for finding in findings:
            if finding.impact_score == 0.0:
                finding.impact_score = self.calculate_impact_score(finding)
            if finding.effort_score == 0.0:
                finding.effort_score = self.calculate_effort_score(finding)
            if finding.priority_ratio == 0.0:
                if finding.effort_score > 0:
                    finding.priority_ratio = finding.impact_score / finding.effort_score
                else:
                    finding.priority_ratio = finding.impact_score
        
        # Ordenar por priority_ratio descendente
        sorted_findings = sorted(findings, key=lambda f: f.priority_ratio, reverse=True)
        
        # Retornar top 10
        return sorted_findings[:10]
    
    def _calculate_median(self, values: List[float]) -> float:
        """
        Calcula la mediana de una lista de valores.
        
        Args:
            values: Lista de valores numéricos
            
        Returns:
            Mediana de los valores
        """
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            # Par: promedio de los dos valores centrales
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            # Impar: valor central
            return sorted_values[n // 2]
