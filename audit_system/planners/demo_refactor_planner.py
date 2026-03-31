"""
Demo del RefactorPlanner.

Script de demostración que muestra cómo usar el RefactorPlanner
para crear un plan de refactor de 4 semanas.
"""

from audit_system.planners.refactor_planner import RefactorPlanner
from audit_system.models import Finding, Severity


def create_sample_findings():
    """Crea hallazgos de ejemplo para demostración."""
    findings = []
    
    # Críticos
    findings.append(Finding(
        id="C1",
        category="security",
        subcategory="hardcoded_secret",
        severity=Severity.CRITICO,
        title="Password hardcodeado en auth.py",
        description="Credencial expuesta en código fuente",
        file_path="backend/api/auth.py",
        line_number=42,
        recommendation="Usar variables de entorno",
        effort_score=5.0,
        impact_score=40.0
    ))
    
    findings.append(Finding(
        id="C2",
        category="quality",
        subcategory="long_function",
        severity=Severity.CRITICO,
        title="Función process_data de 150 líneas",
        description="Función extremadamente larga y compleja",
        file_path="backend/db/repository.py",
        line_number=100,
        recommendation="Dividir en funciones más pequeñas",
        effort_score=8.0,
        impact_score=35.0
    ))
    
    # Altos
    findings.append(Finding(
        id="H1",
        category="performance",
        subcategory="n_plus_one",
        severity=Severity.ALTO,
        title="Query N+1 en get_users_with_printers",
        description="Loop con query por cada usuario",
        file_path="backend/api/users.py",
        line_number=78,
        recommendation="Usar JOIN o eager loading",
        effort_score=6.0,
        impact_score=30.0
    ))
    
    findings.append(Finding(
        id="H2",
        category="performance",
        subcategory="unnecessary_rerender",
        severity=Severity.ALTO,
        title="PrinterList sin memoización",
        description="Componente se re-renderiza innecesariamente",
        file_path="src/components/PrinterList.tsx",
        line_number=25,
        recommendation="Usar React.memo y useCallback",
        effort_score=3.0,
        impact_score=25.0
    ))
    
    # Medios
    findings.append(Finding(
        id="M1",
        category="quality",
        subcategory="missing_type_hints",
        severity=Severity.MEDIO,
        title="Función validate_printer sin type hints",
        description="Falta tipado en parámetros y retorno",
        file_path="backend/services/printer_service.py",
        line_number=45,
        recommendation="Agregar type hints",
        effort_score=2.0,
        impact_score=15.0
    ))
    
    findings.append(Finding(
        id="M2",
        category="quality",
        subcategory="type_any",
        severity=Severity.MEDIO,
        title="Props con tipo 'any' en Button",
        description="Pérdida de type safety",
        file_path="src/components/Button.tsx",
        line_number=10,
        recommendation="Definir interface para props",
        effort_score=1.0,
        impact_score=12.0
    ))
    
    # Bajos
    findings.append(Finding(
        id="L1",
        category="quality",
        subcategory="todo_comment",
        severity=Severity.BAJO,
        title="TODO: Implementar paginación",
        description="Comentario TODO pendiente",
        file_path="backend/api/export.py",
        line_number=120,
        recommendation="Implementar o remover comentario",
        effort_score=1.0,
        impact_score=5.0
    ))
    
    findings.append(Finding(
        id="L2",
        category="quality",
        subcategory="console_log",
        severity=Severity.BAJO,
        title="console.log en helpers.ts",
        description="Debug log en código de producción",
        file_path="src/utils/helpers.ts",
        line_number=33,
        recommendation="Remover o usar logger apropiado",
        effort_score=0.5,
        impact_score=3.0
    ))
    
    return findings


def main():
    """Ejecuta demostración del RefactorPlanner."""
    print("=" * 80)
    print("DEMO: RefactorPlanner - Plan de Refactor de 4 Semanas")
    print("=" * 80)
    print()
    
    # Crear hallazgos de ejemplo
    findings = create_sample_findings()
    print(f"📋 Total de hallazgos: {len(findings)}")
    print()
    
    # Crear planner
    planner = RefactorPlanner()
    
    # Generar plan de 4 semanas
    print("🔄 Generando plan de refactor...")
    plan = planner.create_4_week_plan(findings)
    print("✅ Plan generado exitosamente")
    print()
    
    # Obtener resumen
    summary = planner.get_weekly_summary(plan)
    
    # Mostrar plan semana por semana
    for week in range(1, 5):
        print(f"{'=' * 80}")
        print(f"SEMANA {week}")
        print(f"{'=' * 80}")
        
        week_summary = summary[week]
        week_findings = getattr(plan, f"week_{week}")
        
        print(f"📊 Resumen:")
        print(f"  • Total hallazgos: {week_summary['total_findings']}")
        print(f"  • Esfuerzo total: {week_summary['total_effort']:.1f} horas")
        print(f"  • Backend: {week_summary['backend_findings']} hallazgos ({week_summary['backend_effort']:.1f}h)")
        print(f"  • Frontend: {week_summary['frontend_findings']} hallazgos ({week_summary['frontend_effort']:.1f}h)")
        print()
        
        print(f"📈 Por severidad:")
        for severity, count in week_summary['severity_counts'].items():
            if count > 0:
                print(f"  • {severity}: {count}")
        print()
        
        if week_findings:
            print(f"📝 Hallazgos:")
            for finding in week_findings:
                emoji = finding.severity.get_emoji()
                print(f"  {emoji} [{finding.id}] {finding.title}")
                print(f"     Archivo: {finding.file_path}")
                print(f"     Esfuerzo: {finding.effort_score:.1f}h | Impacto: {finding.impact_score:.1f}")
                print()
        else:
            print("  (Sin hallazgos asignados)")
            print()
    
    print(f"{'=' * 80}")
    print("RESUMEN GENERAL")
    print(f"{'=' * 80}")
    
    total_effort = sum(summary[w]['total_effort'] for w in range(1, 5))
    print(f"📊 Esfuerzo total estimado: {total_effort:.1f} horas")
    print(f"📅 Distribución: {total_effort / 4:.1f} horas promedio por semana")
    print()
    
    # Verificar que ninguna semana exceda 40 horas
    max_week_effort = max(summary[w]['total_effort'] for w in range(1, 5))
    if max_week_effort <= 40.0:
        print("✅ Todas las semanas están dentro del límite de 40 horas")
    else:
        print(f"⚠️  Advertencia: Semana con mayor carga tiene {max_week_effort:.1f} horas")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
