# RefactorPlanner

Planificador de refactor temporal que distribuye hallazgos de auditoría en un plan de 4 semanas.

## Características

### 1. Distribución por Severidad

El planner distribuye automáticamente los hallazgos según su severidad:

- **Semana 1**: Hallazgos Críticos
- **Semanas 1-2**: Hallazgos Altos
- **Semanas 2-3**: Hallazgos Medios
- **Semanas 3-4**: Hallazgos Bajos

### 2. Cálculo de Esfuerzo Semanal

Calcula el esfuerzo total estimado para cada semana sumando los `effort_score` de todos los hallazgos asignados.

### 3. Redistribución Automática

Cuando el esfuerzo de una semana excede 40 horas, el planner redistribuye automáticamente hallazgos a semanas posteriores para mantener una carga de trabajo razonable.

### 4. Balanceo Backend/Frontend

Intenta mantener un balance entre trabajo de Backend y Frontend en cada semana:

- Si una semana tiene >70% de trabajo en Backend, mueve algunos hallazgos a la siguiente semana
- Si una semana tiene >70% de trabajo en Frontend, mueve algunos hallazgos a la siguiente semana
- Objetivo: mantener un ratio cercano al 60/40

## Uso

```python
from audit_system.planners.refactor_planner import RefactorPlanner
from audit_system.models import Finding

# Crear planner
planner = RefactorPlanner()

# Generar plan de 4 semanas
plan = planner.create_4_week_plan(findings)

# Calcular esfuerzo de una semana
effort = planner.calculate_weekly_effort(plan, week=1)

# Obtener resumen completo
summary = planner.get_weekly_summary(plan)
```

## Ejemplo de Salida

```
SEMANA 1
========
📊 Resumen:
  • Total hallazgos: 2
  • Esfuerzo total: 14.0 horas
  • Backend: 2 hallazgos (14.0h)
  • Frontend: 0 hallazgos (0.0h)

📈 Por severidad:
  • Crítico: 1
  • Alto: 1
```

## Métodos Principales

### `create_4_week_plan(findings: List[Finding]) -> RefactorPlan`

Crea un plan de refactor de 4 semanas distribuyendo los hallazgos según severidad, balanceando carga de trabajo y redistribuyendo cuando sea necesario.

**Parámetros:**
- `findings`: Lista de hallazgos a distribuir

**Retorna:**
- `RefactorPlan` con hallazgos distribuidos en 4 semanas

### `calculate_weekly_effort(plan: RefactorPlan, week: int) -> float`

Calcula el esfuerzo total estimado para una semana específica.

**Parámetros:**
- `plan`: Plan de refactor
- `week`: Número de semana (1-4)

**Retorna:**
- Total de horas estimadas

### `balance_workload(plan: RefactorPlan) -> None`

Balancea la carga de trabajo entre Backend y Frontend por semana. Modifica el plan in-place.

**Parámetros:**
- `plan`: Plan de refactor a balancear

### `get_weekly_summary(plan: RefactorPlan) -> Dict[int, Dict[str, any]]`

Genera un resumen detallado de cada semana del plan.

**Parámetros:**
- `plan`: Plan de refactor

**Retorna:**
- Diccionario con resumen por semana incluyendo:
  - `total_findings`: Número total de hallazgos
  - `total_effort`: Esfuerzo total en horas
  - `backend_findings`: Número de hallazgos de Backend
  - `frontend_findings`: Número de hallazgos de Frontend
  - `backend_effort`: Esfuerzo de Backend en horas
  - `frontend_effort`: Esfuerzo de Frontend en horas
  - `severity_counts`: Conteo por severidad

## Configuración

El planner utiliza la configuración global del sistema:

```python
from audit_system.config import get_config

config = get_config()
config.MAX_WEEKLY_EFFORT_HOURS  # Límite de horas por semana (default: 40.0)
```

## Tests

Ejecutar tests unitarios:

```bash
pytest audit_system/planners/test_refactor_planner.py -v
```

Ejecutar demo:

```bash
python audit_system/planners/demo_refactor_planner.py
```

## Validaciones de Requirements

Este componente implementa los siguientes requisitos:

- **16.1**: Plan de refactor de 4 semanas
- **16.2**: Distribución de hallazgos Crítico en Semana 1
- **16.3**: Distribución de hallazgos Alto en Semanas 1-2
- **16.4**: Distribución de hallazgos Medio en Semanas 2-3
- **16.5**: Distribución de hallazgos Bajo en Semanas 3-4
- **16.6**: Estimación de horas de esfuerzo por semana
- **16.7**: Balanceo de carga Backend/Frontend por semana
- **16.8**: Redistribución cuando esfuerzo semanal >40 horas
