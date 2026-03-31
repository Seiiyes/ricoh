# Generadores de Reportes

Este módulo contiene los generadores de reportes markdown para el sistema de auditoría de código.

## ReportGenerator

El `ReportGenerator` es responsable de generar reportes completos en formato markdown con todas las secciones requeridas para la auditoría de código del proyecto Ricoh Suite.

### Características

- **Estructura completa del reporte**: Genera todas las secciones requeridas incluyendo resumen ejecutivo, Top 10, métricas, matriz de priorización, hallazgos por severidad y plan de refactor.
- **Formato markdown profesional**: Utiliza tablas, bloques de código, enlaces y emojis para una presentación clara.
- **Emojis para severidades**: 🔴 Crítico, 🟠 Alto, 🟡 Medio, 🟢 Bajo
- **Enlaces a archivos**: Incluye enlaces directos a archivos con números de línea
- **Tabla de contenidos**: Con enlaces a todas las secciones principales
- **Metadata**: Fecha de generación y ruta del proyecto

### Uso

```python
from audit_system.generators import ReportGenerator
from audit_system.models import AnalysisResult

# Crear resultado de análisis
analysis_result = AnalysisResult(
    structure=project_structure,
    findings=findings,
    top_10=top_10_findings,
    priority_matrix=priority_matrix,
    metrics=code_metrics,
    refactor_plan=refactor_plan
)

# Generar reporte
generator = ReportGenerator()
report = generator.generate_report(analysis_result)

# Guardar reporte
with open("docs/OPTIMIZACION_HALLAZGOS.md", "w", encoding="utf-8") as f:
    f.write(report)
```

### Métodos Públicos

#### `generate_report(analysis_result: AnalysisResult) -> str`

Genera el reporte completo en formato markdown.

**Parámetros:**
- `analysis_result`: Resultado completo de la auditoría

**Retorna:**
- String con el reporte en formato markdown

#### `generate_executive_summary(findings: List[Finding]) -> str`

Genera resumen ejecutivo con tabla de severidades y distribución por categoría.

#### `generate_top_10(top_findings: List[Finding]) -> str`

Genera sección Top 10 con las mejoras de mayor impacto/esfuerzo.

#### `generate_findings_by_severity(findings: List[Finding]) -> str`

Genera hallazgos organizados por severidad (Crítico, Alto, Medio, Bajo).

#### `generate_metrics_section(metrics: CodeMetrics) -> str`

Genera sección de métricas cuantitativas con tablas.

#### `generate_priority_matrix(matrix: PriorityMatrix) -> str`

Genera matriz impacto/esfuerzo con cuatro cuadrantes.

#### `generate_refactor_plan(plan: RefactorPlan) -> str`

Genera plan de refactor distribuido en 4 semanas.

#### `generate_table_of_contents() -> str`

Genera tabla de contenidos con enlaces a todas las secciones.

### Estructura del Reporte Generado

1. **Encabezado**
   - Título del reporte
   - Fecha de generación
   - Ruta del proyecto
   - Total de hallazgos

2. **Tabla de Contenidos**
   - Enlaces a todas las secciones principales
   - Subenlaces a severidades

3. **Resumen Ejecutivo**
   - Tabla de distribución por severidad
   - Tabla de distribución por categoría

4. **Top 10 Mejoras Prioritarias**
   - Hallazgos con mayor ratio impacto/esfuerzo
   - Detalles completos con código y recomendaciones

5. **Métricas del Código**
   - Métricas generales (Backend y Frontend)
   - Métricas de dependencias

6. **Matriz de Priorización**
   - Diagrama visual de impacto vs esfuerzo
   - Quick Wins (Alto impacto, Bajo esfuerzo)
   - Major Projects (Alto impacto, Alto esfuerzo)
   - Fill-ins (Bajo impacto, Bajo esfuerzo)
   - Avoid (Bajo impacto, Alto esfuerzo)

7. **Hallazgos por Severidad**
   - Organizados por severidad (Crítico → Bajo)
   - Agrupados por categoría dentro de cada severidad
   - Enlaces a archivos con números de línea

8. **Plan de Refactor (4 Semanas)**
   - Distribución de hallazgos por semana
   - Estimación de esfuerzo por semana
   - Distribución por severidad

### Ejemplo de Salida

```markdown
# Reporte de Optimización - Ricoh Suite

**Fecha de generación:** 2024-01-15 10:30:00
**Proyecto:** /home/user/ricoh-suite
**Total de hallazgos:** 42

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Top 10 Mejoras Prioritarias](#top-10-mejoras-prioritarias)
...

## Resumen Ejecutivo

### Distribución por Severidad

| Severidad | Cantidad | Emoji |
|-----------|----------|-------|
| Crítico | 5 | 🔴 |
| Alto | 12 | 🟠 |
| Medio | 18 | 🟡 |
| Bajo | 7 | 🟢 |
...
```

### Testing

El módulo incluye tests completos en `test_report_generator.py`:

```bash
# Ejecutar tests
pytest audit_system/generators/test_report_generator.py -v

# Ejecutar con cobertura
pytest audit_system/generators/test_report_generator.py --cov=audit_system.generators
```

### Demo

Para ver el generador en acción:

```bash
python audit_system/generators/demo_report_generator.py
```

Esto generará un reporte de ejemplo en `docs/OPTIMIZACION_HALLAZGOS_DEMO.md`.

## Requisitos Validados

El ReportGenerator valida los siguientes requisitos del sistema:

- **Requirement 11**: Generación del Reporte de Hallazgos
  - 11.1: Genera archivo docs/OPTIMIZACION_HALLAZGOS.md
  - 11.2: Incluye resumen ejecutivo con tabla de severidades
  - 11.3: Incluye sección Top 10
  - 11.4: Organiza hallazgos por severidad
  - 11.5: Incluye métricas del código
  - 11.6: Incluye estimación de esfuerzo
  - 11.7: Incluye plan de refactor de 4 semanas
  - 11.8: Incluye ubicación exacta (archivo y línea)
  - 11.9: Incluye descripción y solución recomendada
  - 11.10: Calcula matriz impacto vs esfuerzo

- **Requirement 19**: Formato del Reporte
  - 19.1: Formato markdown estructurado
  - 19.2: Tabla de contenidos con enlaces
  - 19.3: Tablas para métricas
  - 19.4: Bloques de código para ejemplos
  - 19.5: Emojis para severidades
  - 19.6: Fecha de generación y versión
  - 19.7: Enlaces a archivos específicos

## Extensibilidad

El ReportGenerator puede extenderse para incluir secciones adicionales:

```python
class CustomReportGenerator(ReportGenerator):
    def generate_report(self, analysis_result: AnalysisResult) -> str:
        report = super().generate_report(analysis_result)
        
        # Agregar sección personalizada
        custom_section = self.generate_custom_section(analysis_result)
        report += "\n\n" + custom_section
        
        return report
    
    def generate_custom_section(self, analysis_result: AnalysisResult) -> str:
        return "## Sección Personalizada\n\nContenido..."
```
