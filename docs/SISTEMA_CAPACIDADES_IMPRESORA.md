# Sistema de Capacidades de Impresora

## Descripción General

El Sistema de Capacidades de Impresora es una funcionalidad que detecta automáticamente las características técnicas de cada impresora Ricoh y adapta la interfaz de usuario para mostrar solo la información relevante según el modelo.

## Problema que Resuelve

Anteriormente, el sistema mostraba todas las columnas de contadores sin importar las capacidades reales de cada impresora. Esto generaba confusión porque:

- Se mostraban columnas de "Color" con valores en 0 para impresoras blanco y negro
- Se mostraban campos especiales (hojas a 2 caras, páginas combinadas) que no todas las impresoras soportan
- La interfaz era confusa y mostraba información innecesaria

## Capacidades Detectadas

El sistema detecta automáticamente:

### 1. Formato de Contadores

- **Estándar** (18+ columnas): Impresoras con todas las funciones
- **Simplificado** (13 columnas): Impresoras con funciones básicas
- **Ecológico**: Impresoras con métricas de uso ecológico

### 2. Soporte de Color

- Detecta si la impresora soporta impresión a color
- Oculta columnas de color en impresoras blanco y negro

### 3. Campos Especiales

- **Hojas a 2 caras**: Impresión dúplex
- **Páginas combinadas**: Múltiples páginas en una hoja
- **Mono color**: Impresión en un solo color
- **Dos colores**: Impresión en dos colores

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │UserCounter   │  │CierreDetalle │  │Comparacion   │      │
│  │Table         │  │Modal         │  │Modal         │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │ColumnVisibility │                        │
│                   │ Logic           │                        │
│                   └─────────────────┘                        │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP/JSON
┌─────────────────────────────▼───────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │/printers     │  │/counters     │  │/closes       │      │
│  │endpoints     │  │endpoints     │  │endpoints     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    Service Layer (Python)                    │
│  ┌──────────────────────────────────────────────────┐       │
│  │           Counter Parser Service                 │       │
│  │  ┌──────────────┐  ┌──────────────┐             │       │
│  │  │Format        │  │Capabilities  │             │       │
│  │  │Detector      │  │Detector      │             │       │
│  │  └──────────────┘  └──────────────┘             │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                   Data Layer (PostgreSQL)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Printer       │  │ContadorUsuario│ │CierreMensual │      │
│  │(capabilities)│  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

## Flujo de Detección

1. **Lectura de Contadores**: El sistema lee el HTML de contadores de la impresora
2. **Análisis de Estructura**: El parser analiza el número de columnas y estructura
3. **Detección de Capacidades**: Se detecta formato, color y campos especiales
4. **Almacenamiento**: Las capacidades se guardan en la base de datos
5. **Exposición en API**: La API incluye las capacidades en sus respuestas
6. **Adaptación de UI**: El frontend oculta columnas no relevantes

## Configuración de Impresoras

### Impresoras Actuales

| IP | Formato | Color | Hojas 2 Caras | Págs. Combinadas |
|----|---------|-------|---------------|------------------|
| 192.168.91.250 | Estándar | No | No | No |
| 192.168.91.251 | Estándar | Sí | Sí | Sí |
| 192.168.91.252 | Simplificado | No | Sí | Sí |
| 192.168.91.253 | Ecológico | No | No | No |
| 192.168.110.250 | Estándar | No | No | No |

## API Endpoints

### Obtener Capacidades de una Impresora

```http
GET /api/printers/{printer_id}/capabilities
```

**Respuesta:**
```json
{
  "formato_contadores": "estandar",
  "has_color": true,
  "has_hojas_2_caras": true,
  "has_paginas_combinadas": true,
  "has_mono_color": true,
  "has_dos_colores": true,
  "detected_at": "2024-03-15T10:30:00Z",
  "manual_override": false
}
```

### Actualizar Capacidades Manualmente

```http
PUT /api/printers/{printer_id}/capabilities
```

**Body:**
```json
{
  "formato_contadores": "simplificado",
  "has_color": false,
  "has_hojas_2_caras": true,
  "has_paginas_combinadas": true,
  "has_mono_color": false,
  "has_dos_colores": false
}
```

**Nota**: La actualización manual establece `manual_override=true`, lo que previene sobrescritura automática.

### Endpoints Extendidos

Los siguientes endpoints ahora incluyen información de capacidades:

- `GET /api/counters/latest/{printer_id}` - Incluye `printer.capabilities`
- `GET /api/counters/user-counters/{printer_id}` - Incluye `printer.capabilities`
- `GET /api/closes/{cierre_id}` - Incluye `printer.capabilities`

## Base de Datos

### Campo capabilities_json

Las capacidades se almacenan en un campo JSONB en la tabla `printers`:

```sql
ALTER TABLE printers 
ADD COLUMN capabilities_json JSONB DEFAULT NULL;

CREATE INDEX idx_printers_capabilities 
ON printers USING GIN (capabilities_json);
```

**Estructura del JSON:**
```json
{
  "formato_contadores": "estandar",
  "has_color": true,
  "has_hojas_2_caras": true,
  "has_paginas_combinadas": true,
  "has_mono_color": true,
  "has_dos_colores": true,
  "detected_at": "2024-03-15T10:30:00Z",
  "manual_override": false
}
```

## Frontend - Uso de Capacidades

### Hook useColumnVisibility

```typescript
import { useColumnVisibility } from '@/hooks/useColumnVisibility';

function UserCounterTable({ printerId }) {
  const { data } = useQuery(['user-counters', printerId]);
  const visibility = useColumnVisibility(data?.printer?.capabilities);
  
  // visibility contiene:
  // {
  //   showColorColumns: boolean,
  //   showHojas2Caras: boolean,
  //   showPaginasCombinadas: boolean,
  //   showMonoColor: boolean,
  //   showDosColores: boolean
  // }
}
```

### Filtrado de Columnas

```typescript
const visibleColumns = ALL_COLUMNS.filter(col => {
  if (!col.group) return true; // Columnas sin grupo siempre visibles
  
  switch (col.group) {
    case 'color':
      return visibility.showColorColumns;
    case 'hojas_2_caras':
      return visibility.showHojas2Caras;
    case 'paginas_combinadas':
      return visibility.showPaginasCombinadas;
    default:
      return true;
  }
});
```

## Validación y Consistencia

### Detección de Inconsistencias

El sistema valida automáticamente:

1. **Valores de color > 0 pero has_color=False**
   - Registra advertencia en logs
   - Incrementa contador de inconsistencias

2. **Formato detectado diferente al almacenado**
   - Actualiza formato automáticamente (si no hay override manual)
   - Registra cambio en logs

3. **Múltiples inconsistencias consecutivas**
   - Después de 3 inconsistencias, envía notificación al administrador

### Logs de Validación

```python
logger.warning(
    f"Inconsistencia en printer {printer_id}: "
    f"valores color > 0 pero has_color=False. "
    f"Contador inconsistencias: {count}"
)
```

## Retrocompatibilidad

El sistema mantiene compatibilidad total con código existente:

1. **API**: Siempre retorna todos los campos de contadores (incluso en 0)
2. **Frontend**: Muestra todas las columnas si no hay información de capacidades
3. **Base de Datos**: Campo `capabilities_json` es nullable
4. **Parser**: Funciona con impresoras sin capacidades configuradas

## Troubleshooting

### Columnas no se ocultan correctamente

1. Verificar que la impresora tiene capacidades detectadas:
   ```http
   GET /api/printers/{printer_id}/capabilities
   ```

2. Verificar que el frontend recibe las capacidades:
   - Abrir DevTools → Network → Buscar request de contadores
   - Verificar que la respuesta incluye `printer.capabilities`

3. Verificar que el hook `useColumnVisibility` se está usando correctamente

### Capacidades detectadas incorrectamente

1. Verificar el HTML de contadores de la impresora:
   - El sistema guarda HTML en archivos de debug durante lectura

2. Actualizar capacidades manualmente:
   ```http
   PUT /api/printers/{printer_id}/capabilities
   ```

3. Revisar logs del sistema para advertencias de inconsistencias

### Impresora nueva no detecta capacidades

1. Ejecutar lectura manual de contadores:
   ```http
   POST /api/counters/read/{printer_id}
   ```

2. Verificar que la impresora tiene `tiene_contador_usuario=True` en la base de datos

3. Si la detección automática falla, configurar manualmente usando el endpoint PUT

## Monitoreo

### Métricas Recomendadas

1. **Número de inconsistencias detectadas por día**
2. **Distribución de formatos detectados**
3. **Tiempo de detección de capacidades**
4. **Errores en parsing de HTML**
5. **Actualizaciones manuales de capacidades**

### Alertas

- **Crítico**: 3+ inconsistencias consecutivas en una impresora
- **Advertencia**: Formato detectado diferente al almacenado
- **Info**: Capacidades actualizadas manualmente

## Referencias

- **Spec Completo**: `.kiro/specs/sistema-capacidades-impresora/`
- **Requirements**: `.kiro/specs/sistema-capacidades-impresora/requirements.md`
- **Design**: `.kiro/specs/sistema-capacidades-impresora/design.md`
- **Tasks**: `.kiro/specs/sistema-capacidades-impresora/tasks.md`
- **Lecciones Aprendidas**: `.kiro/lessons-learned/sistema-capacidades-impresora.md`

## Próximos Pasos

Para implementar este sistema, seguir el plan de tareas en 4 fases:

1. **Fase 1**: Backend - Detección de Capacidades
2. **Fase 2**: Base de Datos y Persistencia
3. **Fase 3**: API - Exposición de Capacidades
4. **Fase 4**: Frontend - Adaptación de UI

Ver `.kiro/specs/sistema-capacidades-impresora/tasks.md` para detalles de implementación.
