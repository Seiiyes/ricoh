# Sistema de Auditoría y Optimización de Código

Sistema automatizado de análisis estático para identificar oportunidades de mejora en rendimiento, calidad, seguridad y arquitectura del código.

## Descripción General

El sistema de auditoría analiza proyectos Backend (Python/FastAPI) y Frontend (TypeScript/React) para generar un reporte priorizado de hallazgos sin modificar el código fuente. Utiliza una arquitectura de pipeline con tres etapas principales:

1. **Mapeo y Recolección**: Escanea estructura, dependencias y métricas
2. **Análisis Multi-Dimensional**: Ejecuta 8 analizadores especializados
3. **Priorización y Reporte**: Clasifica hallazgos y genera plan de acción

## Arquitectura

```
audit_system/
├── scanners/           # Etapa 1: Mapeo
│   ├── file_scanner.py
│   ├── dependency_extractor.py
│   └── metrics_collector.py
├── analyzers/          # Etapa 2: Análisis
│   ├── performance_analyzer.py
│   ├── quality_analyzer.py
│   ├── security_analyzer.py
│   ├── architecture_analyzer.py
│   ├── ux_analyzer.py
│   ├── error_handling_analyzer.py
│   ├── testing_analyzer.py
│   └── config_analyzer.py
├── classifiers/        # Etapa 3: Clasificación
│   ├── severity_classifier.py
│   └── impact_calculator.py
├── planners/           # Etapa 3: Planificación
│   └── refactor_planner.py
├── generators/         # Etapa 4: Generación
│   └── report_generator.py
├── orchestrator.py     # Coordinador principal
├── models.py           # Modelos de datos
├── config.py           # Configuración
└── logger.py           # Sistema de logging
```

## Instalación

### Requisitos

- Python 3.8+
- pip

### Instalar Dependencias

```bash
pip install -r audit_system/requirements.txt
```

## Uso

### Ejecución Simple

Para auditar el proyecto actual:

```bash
python run_audit.py
```

Esto generará el reporte en `docs/OPTIMIZACION_HALLAZGOS.md`.

### CLI con Opciones

Para mayor control, use el CLI:

```bash
python -m audit_system.cli -p /ruta/proyecto -o reporte.md
```

**Opciones disponibles:**

- `-p, --project-path`: Ruta del proyecto a auditar (requerido)
- `-o, --output`: Ruta del archivo de reporte (default: docs/OPTIMIZACION_HALLAZGOS.md)
- `-v, --verbose`: Habilitar logging detallado
- `-c, --categories`: Filtrar categorías (performance,security,quality,architecture)

**Ejemplos:**

```bash
# Auditar proyecto específico
python -m audit_system.cli -p /path/to/project

# Especificar ruta de salida
python -m audit_system.cli -p . -o custom_report.md

# Modo verbose para debugging
python -m audit_system.cli -p . -v

# Filtrar categorías (funcionalidad futura)
python -m audit_system.cli -p . -c performance,security
```

## Interpretar el Reporte

El reporte generado (`OPTIMIZACION_HALLAZGOS.md`) contiene las siguientes secciones:

### 1. Resumen Ejecutivo

Tabla con conteo de hallazgos por severidad:

- 🔴 **Crítico**: Requiere atención inmediata (secrets, vulnerabilidades críticas)
- 🟠 **Alto**: Impacto significativo (N+1 queries, archivos sin tests)
- 🟡 **Medio**: Mejoras importantes (type any, componentes grandes)
- 🟢 **Bajo**: Mejoras menores (TODOs, console.log)

### 2. Top 10 Mejoras Prioritarias

Lista de los 10 hallazgos con mayor ratio impacto/esfuerzo. Estos son los "quick wins" que generan mayor valor con menor inversión.

**Campos por hallazgo:**
- **Título**: Descripción breve del problema
- **Severidad**: Nivel de criticidad
- **Impacto**: Score calculado (0-100)
- **Esfuerzo**: Score estimado (1-10)
- **Ratio**: Impacto/Esfuerzo (mayor es mejor)
- **Ubicación**: Archivo y línea exacta
- **Recomendación**: Solución sugerida

### 3. Hallazgos por Severidad

Todos los hallazgos organizados por nivel de severidad, con detalles completos:

- Descripción del problema
- Ubicación exacta (archivo:línea)
- Snippet de código problemático
- Recomendación de solución
- Estimación de esfuerzo

### 4. Métricas del Código

Métricas cuantitativas del estado actual:

- Líneas de código (Backend/Frontend)
- Número de archivos
- Archivos grandes (>300 líneas)
- Funciones largas (>50 líneas)
- Dependencias totales
- Dependencias desactualizadas

### 5. Matriz de Priorización

Matriz impacto vs esfuerzo que clasifica hallazgos en cuadrantes:

- **Alto Impacto / Bajo Esfuerzo**: Quick wins (prioridad máxima)
- **Alto Impacto / Alto Esfuerzo**: Proyectos mayores (planificar)
- **Bajo Impacto / Bajo Esfuerzo**: Fill-ins (tiempo libre)
- **Bajo Impacto / Alto Esfuerzo**: Evitar (no vale la pena)

### 6. Plan de Refactor de 4 Semanas

Plan temporal distribuido por severidad:

- **Semana 1**: Hallazgos críticos
- **Semana 2**: Hallazgos altos + algunos medios
- **Semana 3**: Hallazgos medios + algunos bajos
- **Semana 4**: Hallazgos bajos restantes

Cada semana incluye:
- Lista de tareas específicas
- Estimación de horas totales
- Balance Backend/Frontend

## Extender el Sistema

### Agregar un Nuevo Analizador

Para agregar un nuevo tipo de análisis:

1. **Crear el analizador** en `audit_system/analyzers/`:

```python
# audit_system/analyzers/my_analyzer.py
from typing import List
from audit_system.models import Finding, SourceFile

class MyAnalyzer:
    """Descripción del analizador."""
    
    def analyze(self, files: List[SourceFile]) -> List[Finding]:
        """
        Analiza archivos y retorna hallazgos.
        
        Args:
            files: Lista de archivos a analizar
            
        Returns:
            Lista de hallazgos detectados
        """
        findings = []
        
        for file in files:
            # Implementar lógica de detección
            if self._detect_pattern(file):
                finding = Finding(
                    id=f"MY-{len(findings)+1}",
                    category="my_category",
                    subcategory="my_pattern",
                    severity="MEDIO",  # Será reclasificado
                    title="Título del hallazgo",
                    description="Descripción detallada",
                    file_path=file.path,
                    line_number=None,
                    code_snippet=None,
                    recommendation="Solución recomendada",
                    impact_score=0.0,
                    effort_score=0.0,
                    priority_ratio=0.0
                )
                findings.append(finding)
        
        return findings
    
    def _detect_pattern(self, file: SourceFile) -> bool:
        """Detecta patrón específico en archivo."""
        # Implementar detección
        return False
```

2. **Registrar en el orquestador** (`audit_system/orchestrator.py`):

```python
from audit_system.analyzers.my_analyzer import MyAnalyzer

class AuditOrchestrator:
    def __init__(self):
        # ... otros analizadores ...
        self.my_analyzer = MyAnalyzer()
    
    def run_audit(self, project_path: str, output_path: str = None):
        # ... en la sección de análisis ...
        try:
            logger.info("Ejecutando mi análisis...")
            my_findings = self.my_analyzer.analyze(all_files)
            findings.extend(my_findings)
            logger.info(f"Mi Análisis: {len(my_findings)} hallazgos")
        except Exception as e:
            logger.error(f"Error en mi análisis: {e}")
```

3. **Agregar tests** en `audit_system/analyzers/test_my_analyzer.py`:

```python
import pytest
from audit_system.analyzers.my_analyzer import MyAnalyzer
from audit_system.models import SourceFile

def test_my_analyzer_detects_pattern():
    """Test que el analizador detecta el patrón."""
    analyzer = MyAnalyzer()
    
    # Crear archivo de prueba con patrón
    file = SourceFile(
        path="test.py",
        language="python",
        lines_of_code=10,
        is_large=False,
        content="código con patrón",
        ast_tree=None
    )
    
    findings = analyzer.analyze([file])
    
    assert len(findings) > 0
    assert findings[0].category == "my_category"
```

### Agregar Reglas de Severidad

Para agregar nuevas reglas de clasificación, editar `audit_system/classifiers/severity_classifier.py`:

```python
def classify(self, finding: Finding) -> str:
    """Clasifica hallazgo por severidad."""
    
    # Agregar nueva regla
    if finding.subcategory == "my_pattern":
        if self._is_critical_case(finding):
            return "CRITICO"
        return "ALTO"
    
    # ... reglas existentes ...
```

### Personalizar Umbrales

Los umbrales de detección se configuran en `audit_system/config.py`:

```python
@dataclass
class AuditConfig:
    # Modificar umbrales existentes
    LARGE_FILE_THRESHOLD: int = 300  # líneas
    LONG_FUNCTION_THRESHOLD: int = 50  # líneas
    DEEP_NESTING_THRESHOLD: int = 3  # niveles
    
    # Agregar nuevos umbrales
    MY_CUSTOM_THRESHOLD: int = 100
```

## Categorías de Análisis

El sistema incluye 8 categorías de análisis:

### 1. Performance
- Queries N+1
- Falta de paginación
- Operaciones bloqueantes en async
- Re-renders innecesarios
- useEffect con dependencias incorrectas

### 2. Quality
- Funciones largas (>50 líneas)
- Indentación profunda (>3 niveles)
- Código duplicado (>80% similitud)
- Falta de type hints
- Type 'any' en TypeScript
- Props drilling

### 3. Security
- Secrets hardcodeados
- SQL injection
- Falta de validación de inputs
- Falta de autenticación
- Configuración HTTPS/CORS
- Dependencias con vulnerabilidades

### 4. Architecture
- Separación de capas
- Lógica de negocio en endpoints
- Llamadas API dispersas
- Acoplamiento fuerte
- Consistencia de códigos HTTP

### 5. UX
- Estados de loading
- Estados de error
- Estados vacíos
- Validación de formularios
- Feedback visual

### 6. Error Handling
- Try-except sin logging
- Excepciones genéricas
- Errores silenciados
- Códigos HTTP incorrectos

### 7. Testing
- Archivos sin tests
- Componentes sin tests
- Funciones complejas sin tests
- Falta de tests de integración

### 8. Configuration
- Variables de entorno no documentadas
- Valores por defecto inseguros
- Configuraciones hardcodeadas
- Falta de validación de env vars

## Logs

Los logs se guardan en `audit_system/logs/audit.log` con niveles:

- **INFO**: Progreso normal de la auditoría
- **WARNING**: Problemas no críticos (continúa la ejecución)
- **ERROR**: Errores en componentes específicos (continúa con otros)
- **DEBUG**: Información detallada (activar con `--verbose`)

## Limitaciones

- **Análisis estático**: No ejecuta código, puede tener falsos positivos/negativos
- **Patrones heurísticos**: Detecta patrones comunes, no todos los casos
- **Dependencias**: Verificación de vulnerabilidades requiere conexión a internet
- **TypeScript**: Parsing limitado, algunos patrones complejos pueden no detectarse
- **Contexto**: No entiende lógica de negocio, solo patrones de código

## Troubleshooting

### Error: "No se encontraron archivos Python/TypeScript"

**Causa**: Ruta del proyecto incorrecta o estructura no estándar.

**Solución**: Verificar que la ruta contenga directorios `backend/` y `frontend/src/`.

### Error: "Error al parsear archivo X"

**Causa**: Sintaxis inválida o encoding no UTF-8.

**Solución**: El sistema continúa con otros archivos. Revisar el archivo problemático manualmente.

### Warning: "Continuando sin análisis de X"

**Causa**: Error en un analizador específico.

**Solución**: Revisar logs detallados con `--verbose` para identificar la causa.

### Reporte vacío o incompleto

**Causa**: Errores durante la generación o proyecto sin hallazgos.

**Solución**: 
1. Ejecutar con `--verbose` para ver logs detallados
2. Verificar que el proyecto tenga código en `backend/` y `frontend/src/`
3. Revisar `audit_system/logs/audit.log`

## Contribuir

Para contribuir al sistema:

1. Agregar tests para nuevas funcionalidades
2. Seguir convenciones de código existentes
3. Documentar nuevos analizadores y reglas
4. Actualizar este README con cambios relevantes

## Licencia

Sistema interno para auditoría del proyecto Ricoh Suite.
