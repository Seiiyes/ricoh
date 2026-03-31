"""
Demo del ReportGenerator.

Genera un reporte de ejemplo mostrando todas las capacidades del generador.
"""

from datetime import datetime
from audit_system.generators.report_generator import ReportGenerator
from audit_system.models import (
    Finding, 
    Severity, 
    AnalysisResult, 
    PriorityMatrix, 
    RefactorPlan,
    CodeMetrics,
    ProjectStructure
)


def create_demo_findings():
    """Crea hallazgos de demostración."""
    findings = [
        Finding(
            id="F001",
            category="security",
            subcategory="hardcoded_secret",
            severity=Severity.CRITICO,
            title="Credencial de base de datos hardcodeada",
            description="Se encontró una contraseña de base de datos hardcodeada en el código fuente",
            file_path="backend/db/database.py",
            line_number=15,
            code_snippet='DB_PASSWORD = "postgres123"',
            recommendation="Mover la contraseña a variables de entorno usando .env",
            impact_score=50.0,
            effort_score=2.0,
            priority_ratio=25.0
        ),
        Finding(
            id="F002",
            category="performance",
            subcategory="n_plus_one",
            severity=Severity.ALTO,
            title="Query N+1 en endpoint de usuarios",
            description="Patrón N+1 detectado: se ejecuta una query por cada usuario para obtener sus contadores",
            file_path="backend/api/users.py",
            line_number=78,
            code_snippet="""users = session.query(User).all()
for user in users:
    counters = session.query(Counter).filter(Counter.user_id == user.id).all()""",
            recommendation="Usar eager loading con joinedload() o selectinload()",
            impact_score=45.0,
            effort_score=5.0,
            priority_ratio=9.0
        ),
        Finding(
            id="F003",
            category="performance",
            subcategory="missing_pagination",
            severity=Severity.ALTO,
            title="Endpoint sin paginación retorna 500+ registros",
            description="El endpoint /api/printers retorna todos los registros sin paginación",
            file_path="backend/api/printers.py",
            line_number=45,
            recommendation="Implementar paginación con limit y offset",
            impact_score=40.0,
            effort_score=4.0,
            priority_ratio=10.0
        ),
        Finding(
            id="F004",
            category="quality",
            subcategory="long_function",
            severity=Severity.CRITICO,
            title="Función excede 150 líneas",
            description="La función process_discovery() tiene 152 líneas, dificultando mantenimiento",
            file_path="backend/api/discovery.py",
            line_number=120,
            recommendation="Dividir en funciones más pequeñas: validate_input(), scan_network(), save_results()",
            impact_score=35.0,
            effort_score=8.0,
            priority_ratio=4.375
        ),
        Finding(
            id="F005",
            category="quality",
            subcategory="type_any",
            severity=Severity.MEDIO,
            title="Uso de 'any' en componente UserList",
            description="El tipo 'any' elimina la verificación de tipos en TypeScript",
            file_path="src/components/UserList.tsx",
            line_number=15,
            code_snippet="const handleClick = (data: any) => {",
            recommendation="Definir interface User apropiada",
            impact_score=20.0,
            effort_score=3.0,
            priority_ratio=6.67
        ),
        Finding(
            id="F006",
            category="quality",
            subcategory="missing_type_hints",
            severity=Severity.MEDIO,
            title="Función sin type hints",
            description="La función calculate_metrics() carece de type hints",
            file_path="backend/services/metrics.py",
            line_number=34,
            recommendation="Agregar type hints: def calculate_metrics(data: List[Dict]) -> MetricsResult:",
            impact_score=18.0,
            effort_score=2.0,
            priority_ratio=9.0
        ),
        Finding(
            id="F007",
            category="architecture",
            subcategory="business_logic_in_api",
            severity=Severity.ALTO,
            title="Lógica de negocio en endpoint",
            description="El endpoint contiene lógica de cálculo de métricas directamente",
            file_path="backend/api/counters.py",
            line_number=89,
            recommendation="Mover lógica a CounterService",
            impact_score=30.0,
            effort_score=6.0,
            priority_ratio=5.0
        ),
        Finding(
            id="F008",
            category="quality",
            subcategory="console_log",
            severity=Severity.BAJO,
            title="Console.log en producción",
            description="Console.log sin remover en código de producción",
            file_path="src/utils/helpers.ts",
            line_number=23,
            code_snippet="console.log('Debug:', data);",
            recommendation="Remover console.log o usar logger apropiado",
            impact_score=5.0,
            effort_score=1.0,
            priority_ratio=5.0
        ),
        Finding(
            id="F009",
            category="testing",
            subcategory="missing_tests",
            severity=Severity.ALTO,
            title="Archivo crítico sin tests",
            description="El módulo de autenticación no tiene tests unitarios",
            file_path="backend/api/auth.py",
            recommendation="Crear test_auth.py con cobertura de casos críticos",
            impact_score=38.0,
            effort_score=10.0,
            priority_ratio=3.8
        ),
        Finding(
            id="F010",
            category="security",
            subcategory="vulnerability",
            severity=Severity.ALTO,
            title="Dependencia con vulnerabilidad CVE-2023-1234",
            description="La librería requests tiene vulnerabilidad conocida CVSS 7.5",
            file_path="backend/requirements.txt",
            line_number=12,
            recommendation="Actualizar requests de 2.28.0 a 2.31.0",
            impact_score=42.0,
            effort_score=2.0,
            priority_ratio=21.0
        )
    ]
    return findings


def create_demo_metrics():
    """Crea métricas de demostración."""
    return CodeMetrics(
        backend_total_lines=18543,
        backend_total_files=52,
        backend_large_files=12,
        backend_long_functions=18,
        backend_dependencies_count=38,
        frontend_total_lines=15234,
        frontend_total_files=45,
        frontend_large_components=8,
        frontend_dependencies_count=47,
        total_outdated_dependencies=9,
        total_vulnerabilities=4
    )


def create_demo_priority_matrix(findings):
    """Crea matriz de priorización de demostración."""
    matrix = PriorityMatrix()
    
    # Quick wins: Alto impacto, bajo esfuerzo
    matrix.high_impact_low_effort = [findings[0], findings[9], findings[2]]
    
    # Major projects: Alto impacto, alto esfuerzo
    matrix.high_impact_high_effort = [findings[1], findings[3], findings[8]]
    
    # Fill-ins: Bajo impacto, bajo esfuerzo
    matrix.low_impact_low_effort = [findings[7], findings[5]]
    
    # Avoid: Bajo impacto, alto esfuerzo
    matrix.low_impact_high_effort = [findings[4], findings[6]]
    
    return matrix


def create_demo_refactor_plan(findings):
    """Crea plan de refactor de demostración."""
    plan = RefactorPlan()
    
    # Semana 1: Críticos
    plan.week_1 = [findings[0], findings[3]]
    
    # Semana 2: Altos
    plan.week_2 = [findings[1], findings[2], findings[9]]
    
    # Semana 3: Altos y Medios
    plan.week_3 = [findings[6], findings[8], findings[4], findings[5]]
    
    # Semana 4: Bajos
    plan.week_4 = [findings[7]]
    
    return plan


def main():
    """Genera y muestra reporte de demostración."""
    print("🔍 Generando reporte de demostración...\n")
    
    # Crear datos de ejemplo
    findings = create_demo_findings()
    metrics = create_demo_metrics()
    priority_matrix = create_demo_priority_matrix(findings)
    refactor_plan = create_demo_refactor_plan(findings)
    
    # Crear estructura del proyecto
    structure = ProjectStructure(root_path="/home/user/ricoh-suite")
    
    # Crear resultado de análisis
    analysis_result = AnalysisResult(
        structure=structure,
        findings=findings,
        top_10=sorted(findings, key=lambda f: f.priority_ratio, reverse=True)[:10],
        priority_matrix=priority_matrix,
        metrics=metrics,
        refactor_plan=refactor_plan,
        generated_at=datetime.now()
    )
    
    # Generar reporte
    generator = ReportGenerator()
    report = generator.generate_report(analysis_result)
    
    # Guardar reporte
    output_path = "docs/OPTIMIZACION_HALLAZGOS_DEMO.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ Reporte generado exitosamente en: {output_path}")
    print(f"\n📊 Estadísticas:")
    print(f"   - Total hallazgos: {len(findings)}")
    print(f"   - Críticos: {len([f for f in findings if f.severity == Severity.CRITICO])}")
    print(f"   - Altos: {len([f for f in findings if f.severity == Severity.ALTO])}")
    print(f"   - Medios: {len([f for f in findings if f.severity == Severity.MEDIO])}")
    print(f"   - Bajos: {len([f for f in findings if f.severity == Severity.BAJO])}")
    print(f"\n📄 Vista previa del reporte:\n")
    print("=" * 80)
    print(report[:1500])
    print("...")
    print("=" * 80)


if __name__ == "__main__":
    main()
