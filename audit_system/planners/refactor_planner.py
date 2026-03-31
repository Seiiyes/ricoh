"""
Planificador de refactor temporal.

Distribuye hallazgos de auditoría en un plan de 4 semanas, balanceando
carga de trabajo entre Backend y Frontend según severidad y esfuerzo estimado.
"""

from typing import List, Dict
from audit_system.models import Finding, RefactorPlan, Severity
from audit_system.config import get_config


class RefactorPlanner:
    """Crea planes de refactor distribuidos en 4 semanas."""
    
    def __init__(self):
        """Inicializa el planificador con configuración."""
        self.config = get_config()
    
    def create_4_week_plan(self, findings: List[Finding]) -> RefactorPlan:
        """
        Distribuye hallazgos en un plan de 4 semanas según severidad.
        
        Distribución:
        - Semana 1: Crítico
        - Semanas 1-2: Alto
        - Semanas 2-3: Medio
        - Semanas 3-4: Bajo
        
        Args:
            findings: Lista de hallazgos a distribuir
            
        Returns:
            Plan de refactor con hallazgos distribuidos por semana
        """
        # Separar hallazgos por severidad
        critical = [f for f in findings if f.severity == Severity.CRITICO]
        high = [f for f in findings if f.severity == Severity.ALTO]
        medium = [f for f in findings if f.severity == Severity.MEDIO]
        low = [f for f in findings if f.severity == Severity.BAJO]
        
        # Crear plan inicial
        plan = RefactorPlan()
        
        # Semana 1: Todos los críticos
        plan.week_1.extend(critical)
        
        # Distribuir hallazgos Alto entre semanas 1-2
        high_split = len(high) // 2
        plan.week_1.extend(high[:high_split])
        plan.week_2.extend(high[high_split:])
        
        # Distribuir hallazgos Medio entre semanas 2-3
        medium_split = len(medium) // 2
        plan.week_2.extend(medium[:medium_split])
        plan.week_3.extend(medium[medium_split:])
        
        # Distribuir hallazgos Bajo entre semanas 3-4
        low_split = len(low) // 2
        plan.week_3.extend(low[:low_split])
        plan.week_4.extend(low[low_split:])
        
        # Balancear carga de trabajo
        self._redistribute_by_effort(plan)
        
        # Balancear Backend/Frontend
        self.balance_workload(plan)
        
        return plan
    
    def calculate_weekly_effort(self, plan: RefactorPlan, week: int) -> float:
        """
        Calcula horas de esfuerzo estimadas para una semana.
        
        Args:
            plan: Plan de refactor
            week: Número de semana (1-4)
            
        Returns:
            Total de horas estimadas para la semana
        """
        if week < 1 or week > 4:
            raise ValueError(f"Week must be between 1 and 4, got {week}")
        
        week_findings = getattr(plan, f"week_{week}")
        return sum(f.effort_score for f in week_findings)
    
    def balance_workload(self, plan: RefactorPlan) -> None:
        """
        Balancea carga entre Backend y Frontend por semana.
        
        Intenta distribuir hallazgos de manera que cada semana tenga
        una mezcla equilibrada de trabajo de Backend y Frontend.
        
        Args:
            plan: Plan de refactor a balancear (modificado in-place)
        """
        for week in range(1, 5):
            week_findings = getattr(plan, f"week_{week}")
            
            # Separar por tipo de archivo
            backend_findings = []
            frontend_findings = []
            
            for finding in week_findings:
                if self._is_backend_file(finding.file_path):
                    backend_findings.append(finding)
                else:
                    frontend_findings.append(finding)
            
            # Calcular esfuerzo por tipo
            backend_effort = sum(f.effort_score for f in backend_findings)
            frontend_effort = sum(f.effort_score for f in frontend_findings)
            
            # Si hay desbalance significativo (>70% en un lado), intentar balancear
            total_effort = backend_effort + frontend_effort
            if total_effort > 0:
                backend_ratio = backend_effort / total_effort
                
                # Si Backend > 70%, mover algunos hallazgos a siguiente semana
                if backend_ratio > 0.7 and week < 4:
                    self._move_findings_to_next_week(
                        plan, week, backend_findings, target_ratio=0.6
                    )
                # Si Frontend > 70%, mover algunos hallazgos a siguiente semana
                elif backend_ratio < 0.3 and week < 4:
                    self._move_findings_to_next_week(
                        plan, week, frontend_findings, target_ratio=0.6
                    )
    
    def _redistribute_by_effort(self, plan: RefactorPlan) -> None:
        """
        Redistribuye tareas cuando el esfuerzo semanal excede 40 horas.
        
        Args:
            plan: Plan de refactor a redistribuir (modificado in-place)
        """
        max_effort = self.config.MAX_WEEKLY_EFFORT_HOURS
        
        for week in range(1, 5):
            week_effort = self.calculate_weekly_effort(plan, week)
            
            # Si excede el límite, mover hallazgos a semanas posteriores
            while week_effort > max_effort and week < 4:
                week_findings = getattr(plan, f"week_{week}")
                
                if not week_findings:
                    break
                
                # Ordenar por esfuerzo (menor primero para mover gradualmente)
                week_findings.sort(key=lambda f: f.effort_score)
                
                # Mover el hallazgo de menor esfuerzo a la siguiente semana
                finding_to_move = week_findings.pop()
                next_week_findings = getattr(plan, f"week_{week + 1}")
                next_week_findings.append(finding_to_move)
                
                # Recalcular esfuerzo
                week_effort = self.calculate_weekly_effort(plan, week)
    
    def _is_backend_file(self, file_path: str) -> bool:
        """
        Determina si un archivo pertenece al Backend.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            True si es archivo de Backend, False si es Frontend
        """
        backend_indicators = [
            "backend/",
            ".py",
            "/api/",
            "/db/",
            "/middleware/",
            "/jobs/",
            "/services/"
        ]
        
        return any(indicator in file_path for indicator in backend_indicators)
    
    def _move_findings_to_next_week(
        self,
        plan: RefactorPlan,
        current_week: int,
        findings_to_consider: List[Finding],
        target_ratio: float
    ) -> None:
        """
        Mueve hallazgos a la siguiente semana para balancear carga.
        
        Args:
            plan: Plan de refactor
            current_week: Semana actual (1-4)
            findings_to_consider: Hallazgos candidatos a mover
            target_ratio: Ratio objetivo de balance (0.6 = 60%)
        """
        if current_week >= 4 or not findings_to_consider:
            return
        
        current_week_findings = getattr(plan, f"week_{current_week}")
        next_week_findings = getattr(plan, f"week_{current_week + 1}")
        
        # Ordenar por esfuerzo (menor primero)
        findings_to_consider.sort(key=lambda f: f.effort_score)
        
        # Mover hallazgos hasta alcanzar el ratio objetivo
        moved_count = 0
        max_to_move = len(findings_to_consider) // 3  # Máximo 1/3 de los hallazgos
        
        for finding in findings_to_consider:
            if moved_count >= max_to_move:
                break
            
            if finding in current_week_findings:
                current_week_findings.remove(finding)
                next_week_findings.append(finding)
                moved_count += 1
    
    def get_weekly_summary(self, plan: RefactorPlan) -> Dict[int, Dict[str, any]]:
        """
        Genera resumen de cada semana del plan.
        
        Args:
            plan: Plan de refactor
            
        Returns:
            Diccionario con resumen por semana
        """
        summary = {}
        
        for week in range(1, 5):
            week_findings = getattr(plan, f"week_{week}")
            
            # Separar por tipo
            backend = [f for f in week_findings if self._is_backend_file(f.file_path)]
            frontend = [f for f in week_findings if not self._is_backend_file(f.file_path)]
            
            # Calcular esfuerzos
            backend_effort = sum(f.effort_score for f in backend)
            frontend_effort = sum(f.effort_score for f in frontend)
            total_effort = backend_effort + frontend_effort
            
            # Contar por severidad
            severity_counts = {
                "Crítico": len([f for f in week_findings if f.severity == Severity.CRITICO]),
                "Alto": len([f for f in week_findings if f.severity == Severity.ALTO]),
                "Medio": len([f for f in week_findings if f.severity == Severity.MEDIO]),
                "Bajo": len([f for f in week_findings if f.severity == Severity.BAJO])
            }
            
            summary[week] = {
                "total_findings": len(week_findings),
                "total_effort": total_effort,
                "backend_findings": len(backend),
                "frontend_findings": len(frontend),
                "backend_effort": backend_effort,
                "frontend_effort": frontend_effort,
                "severity_counts": severity_counts
            }
        
        return summary
