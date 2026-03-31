"""
AuditOrchestrator: Componente principal que coordina el pipeline de auditoría.

Responsable de:
- Inicializar todos los componentes del sistema
- Coordinar las 3 etapas del pipeline (Mapeo, Análisis, Priorización)
- Generar el reporte final de optimización
"""

import os
from typing import List, Tuple
from datetime import datetime
from pathlib import Path

from audit_system.models import AnalysisResult, Finding, ProjectStructure
from audit_system.config import get_config
from audit_system.logger import get_logger

# Scanners (Etapa 1: Mapeo y Recolección)
from audit_system.scanners.file_scanner import FileScanner
from audit_system.scanners.dependency_extractor import DependencyExtractor
from audit_system.scanners.metrics_collector import MetricsCollector

# Analyzers (Etapa 2: Análisis Multi-Dimensional)
from audit_system.analyzers.performance_analyzer import PerformanceAnalyzer
from audit_system.analyzers.quality_analyzer import QualityAnalyzer
from audit_system.analyzers.security_analyzer import SecurityAnalyzer
from audit_system.analyzers.architecture_analyzer import ArchitectureAnalyzer
from audit_system.analyzers.ux_analyzer import UXAnalyzer
from audit_system.analyzers.error_handling_analyzer import ErrorHandlingAnalyzer
from audit_system.analyzers.testing_analyzer import TestingAnalyzer
from audit_system.analyzers.config_analyzer import ConfigAnalyzer

# Classifiers (Etapa 3: Clasificación)
from audit_system.classifiers.severity_classifier import SeverityClassifier
from audit_system.classifiers.impact_calculator import ImpactCalculator

# Planners (Etapa 3: Planificación)
from audit_system.planners.refactor_planner import RefactorPlanner

# Generators (Etapa 4: Generación)
from audit_system.generators.report_generator import ReportGenerator

logger = get_logger(__name__)


class AuditOrchestrator:
    """Orquestador principal del sistema de auditoría."""
    
    def __init__(self):
        """Inicializa todos los componentes del sistema."""
        logger.info("Inicializando AuditOrchestrator")
        
        self.config = get_config()
        
        # Etapa 1: Scanners
        self.file_scanner = FileScanner()
        self.dependency_extractor = DependencyExtractor()
        self.metrics_collector = MetricsCollector()
        
        # Etapa 2: Analyzers
        self.performance_analyzer = PerformanceAnalyzer()
        self.quality_analyzer = QualityAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.architecture_analyzer = ArchitectureAnalyzer()
        self.ux_analyzer = UXAnalyzer()
        self.error_handling_analyzer = ErrorHandlingAnalyzer()
        self.testing_analyzer = TestingAnalyzer()
        self.config_analyzer = ConfigAnalyzer()
        
        # Etapa 3: Classifiers y Planners
        self.severity_classifier = SeverityClassifier()
        self.impact_calculator = ImpactCalculator()
        self.refactor_planner = RefactorPlanner()
        
        # Etapa 4: Generators
        self.report_generator = ReportGenerator()
        
        logger.info("AuditOrchestrator inicializado correctamente")
    
    def save_report(self, report: str, output_path: str) -> None:
        """
        Guarda el reporte en un archivo.
        
        Args:
            report: Contenido del reporte en formato markdown
            output_path: Ruta donde guardar el reporte
        """
        try:
            # Crear directorio si no existe
            output_dir = os.path.dirname(output_path)
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                logger.info(f"Directorio creado/verificado: {output_dir}")
            
            # Guardar reporte
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"Reporte guardado exitosamente en: {output_path}")
        except Exception as e:
            logger.error(f"Error al guardar reporte en {output_path}: {e}")
            raise
    
    def run_audit(self, project_path: str, output_path: str = None) -> Tuple[str, str]:
        """
        Ejecuta auditoría completa del proyecto y genera reporte.
        
        Coordina las 4 etapas del pipeline:
        1. Mapeo: Escanea estructura, dependencias y métricas
        2. Análisis: Ejecuta todos los analizadores
        3. Clasificación: Asigna severidades y calcula priorización
        4. Generación: Crea el reporte markdown
        
        Args:
            project_path: Ruta raíz del proyecto a auditar
            output_path: Ruta donde guardar el reporte (opcional, por defecto docs/OPTIMIZACION_HALLAZGOS.md)
            
        Returns:
            Tupla (reporte_markdown, ruta_archivo)
        """
        logger.info(f"Iniciando auditoría del proyecto: {project_path}")
        
        # Configurar ruta de salida
        if output_path is None:
            output_path = os.path.join(
                self.config.REPORT_OUTPUT_DIR,
                self.config.REPORT_FILENAME
            )
        
        # Variables para reporte parcial en caso de errores
        structure = None
        findings: List[Finding] = []
        python_deps = []
        npm_deps = []
        metrics = None
        priority_matrix = None
        top_10 = []
        refactor_plan = None
        
        # ========== ETAPA 1: MAPEO Y RECOLECCIÓN ==========
        logger.info("=== ETAPA 1: Mapeo y Recolección ===")
        
        try:
            # Escanear estructura del proyecto
            logger.info("Escaneando estructura del proyecto...")
            structure = self.file_scanner.scan_project(project_path)
            logger.info(f"Estructura escaneada: {len(structure.backend_files)} archivos Python, "
                       f"{len(structure.frontend_files)} archivos TypeScript")
        except Exception as e:
            logger.error(f"Error al escanear estructura del proyecto: {e}")
            logger.warning("Continuando con estructura vacía...")
            structure = ProjectStructure(root_path=project_path)
        
        try:
            # Extraer dependencias
            logger.info("Extrayendo dependencias...")
            python_deps, npm_deps = self.dependency_extractor.extract_all_dependencies(project_path)
            structure.backend_dependencies = python_deps
            structure.frontend_dependencies = npm_deps
            logger.info(f"Dependencias extraídas: {len(python_deps)} Python, {len(npm_deps)} npm")
        except Exception as e:
            logger.error(f"Error al extraer dependencias: {e}")
            logger.warning("Continuando sin dependencias...")
        
        try:
            # Recolectar métricas
            logger.info("Recolectando métricas del código...")
            metrics = self.metrics_collector.collect_metrics(structure)
            structure.metrics = metrics
            logger.info("Métricas recolectadas exitosamente")
        except Exception as e:
            logger.error(f"Error al recolectar métricas: {e}")
            logger.warning("Continuando sin métricas...")
        
        logger.info(f"Etapa 1 completada")
        
        # ========== ETAPA 2: ANÁLISIS MULTI-DIMENSIONAL ==========
        logger.info("=== ETAPA 2: Análisis Multi-Dimensional ===")
        
        all_files = structure.get_all_files() if structure else []
        
        # Análisis de Performance
        try:
            logger.info("Ejecutando análisis de performance...")
            perf_findings = self.performance_analyzer.analyze(all_files)
            findings.extend(perf_findings)
            logger.info(f"Performance: {len(perf_findings)} hallazgos")
        except Exception as e:
            logger.error(f"Error en análisis de performance: {e}")
            logger.warning("Continuando sin análisis de performance...")
        
        # Análisis de Calidad
        try:
            logger.info("Ejecutando análisis de calidad...")
            quality_findings = self.quality_analyzer.analyze(all_files)
            findings.extend(quality_findings)
            logger.info(f"Calidad: {len(quality_findings)} hallazgos")
        except Exception as e:
            logger.error(f"Error en análisis de calidad: {e}")
            logger.warning("Continuando sin análisis de calidad...")
        
        # Análisis de Seguridad
        try:
            logger.info("Ejecutando análisis de seguridad...")
            security_findings = self.security_analyzer.analyze(all_files)
            findings.extend(security_findings)
            logger.info(f"Seguridad: {len(security_findings)} hallazgos")
        except Exception as e:
            logger.error(f"Error en análisis de seguridad: {e}")
            logger.warning("Continuando sin análisis de seguridad...")
        
        # Análisis de Arquitectura
        try:
            logger.info("Ejecutando análisis de arquitectura...")
            arch_findings = self.architecture_analyzer.analyze(all_files)
            findings.extend(arch_findings)
            logger.info(f"Arquitectura: {len(arch_findings)} hallazgos")
        except Exception as e:
            logger.error(f"Error en análisis de arquitectura: {e}")
            logger.warning("Continuando sin análisis de arquitectura...")
        
        # Análisis de UX
        try:
            logger.info("Ejecutando análisis de UX...")
            ux_findings = self.ux_analyzer.analyze(all_files)
            findings.extend(ux_findings)
            logger.info(f"UX: {len(ux_findings)} hallazgos")
        except Exception as e:
            logger.error(f"Error en análisis de UX: {e}")
            logger.warning("Continuando sin análisis de UX...")
        
        # Análisis de Error Handling
        try:
            logger.info("Ejecutando análisis de error handling...")
            error_findings = self.error_handling_analyzer.analyze(all_files)
            findings.extend(error_findings)
            logger.info(f"Error Handling: {len(error_findings)} hallazgos")
        except Exception as e:
            logger.error(f"Error en análisis de error handling: {e}")
            logger.warning("Continuando sin análisis de error handling...")
        
        # Análisis de Testing
        try:
            logger.info("Ejecutando análisis de testing...")
            testing_findings = self.testing_analyzer.analyze(all_files)
            findings.extend(testing_findings)
            logger.info(f"Testing: {len(testing_findings)} hallazgos")
        except Exception as e:
            logger.error(f"Error en análisis de testing: {e}")
            logger.warning("Continuando sin análisis de testing...")
        
        # Análisis de Configuración
        try:
            logger.info("Ejecutando análisis de configuración...")
            config_findings = self.config_analyzer.analyze(all_files)
            findings.extend(config_findings)
            logger.info(f"Configuración: {len(config_findings)} hallazgos")
        except Exception as e:
            logger.error(f"Error en análisis de configuración: {e}")
            logger.warning("Continuando sin análisis de configuración...")
        
        logger.info(f"Etapa 2 completada: {len(findings)} hallazgos totales")
        
        # ========== ETAPA 3: CLASIFICACIÓN Y PRIORIZACIÓN ==========
        logger.info("=== ETAPA 3: Clasificación y Priorización ===")
        
        try:
            # Clasificar severidades
            logger.info("Clasificando severidades...")
            for finding in findings:
                try:
                    finding.severity = self.severity_classifier.classify(finding)
                except Exception as e:
                    logger.error(f"Error al clasificar hallazgo {finding.id}: {e}")
                    # Mantener severidad por defecto si ya existe
            logger.info("Severidades clasificadas")
        except Exception as e:
            logger.error(f"Error en clasificación de severidades: {e}")
            logger.warning("Continuando con severidades por defecto...")
        
        try:
            # Calcular matriz de priorización
            logger.info("Calculando matriz de priorización...")
            priority_matrix = self.impact_calculator.calculate_priority_matrix(findings)
            logger.info("Matriz de priorización calculada")
        except Exception as e:
            logger.error(f"Error al calcular matriz de priorización: {e}")
            logger.warning("Continuando sin matriz de priorización...")
        
        try:
            # Seleccionar Top 10
            logger.info("Seleccionando Top 10 mejoras prioritarias...")
            top_10 = self.impact_calculator.select_top_10(findings)
            logger.info(f"Top 10 seleccionado: {len(top_10)} hallazgos")
        except Exception as e:
            logger.error(f"Error al seleccionar Top 10: {e}")
            logger.warning("Continuando sin Top 10...")
        
        try:
            # Crear plan de refactor de 4 semanas
            logger.info("Creando plan de refactor de 4 semanas...")
            refactor_plan = self.refactor_planner.create_4_week_plan(findings)
            logger.info("Plan de refactor creado")
        except Exception as e:
            logger.error(f"Error al crear plan de refactor: {e}")
            logger.warning("Continuando sin plan de refactor...")
        
        logger.info("Etapa 3 completada")
        
        # ========== ETAPA 4: GENERACIÓN DE REPORTE ==========
        logger.info("=== ETAPA 4: Generación de Reporte ===")
        
        try:
            # Crear resultado de análisis
            analysis_result = AnalysisResult(
                structure=structure,
                findings=findings,
                top_10=top_10,
                priority_matrix=priority_matrix,
                dependencies=python_deps + npm_deps,
                metrics=metrics,
                refactor_plan=refactor_plan,
                generated_at=datetime.now()
            )
            
            # Generar reporte markdown
            logger.info("Generando reporte markdown...")
            report = self.report_generator.generate_report(analysis_result)
            logger.info("Reporte generado exitosamente")
        except Exception as e:
            logger.error(f"Error al generar reporte: {e}")
            # Generar reporte mínimo de error
            report = f"""# Reporte de Auditoría - Error

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Error

Ocurrió un error durante la generación del reporte completo:

```
{str(e)}
```

## Hallazgos Parciales

Se encontraron {len(findings)} hallazgos antes del error.

Revise los logs para más detalles.
"""
        
        # Guardar reporte
        try:
            self.save_report(report, output_path)
        except Exception as e:
            logger.error(f"Error crítico al guardar reporte: {e}")
            logger.warning("El reporte se retornará pero no se guardó en archivo")
        
        logger.info(f"Auditoría completada: {len(findings)} hallazgos, "
                   f"Top 10: {len(top_10)}, Reporte guardado en: {output_path}")
        
        return report, output_path
