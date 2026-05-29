# Fix: Errores críticos de API — Counters y Dashboard (26-28 mayo 2026)

## Resumen Ejecutivo

Durante la sesión del 26-28 de mayo de 2026 se corrigieron tres bugs críticos que causaban errores 500 en producción en los módulos de Contadores y Dashboard, más una limpieza profunda de imports para mejorar la estabilidad y reducir warnings.

---

## Bug 1: `AttributeError: 'User' object has no attribute 'name'`

### Síntoma
```
AttributeError: 'User' object has no attribute 'name'
```
Ocurría al llamar cualquier endpoint de contadores que registrara el nombre del usuario autenticado.

### Causa raíz
El modelo `User` en `db/models.py` usa el campo `nombre_completo` (no `name`). Múltiples funciones en `counters.py` usaban `current_user.name` que no existe en el modelo.

### Fix aplicado
**Archivo:** `backend/api/counters.py`

```python
# ANTES (incorrecto)
cerrado_por = current_user.name

# DESPUÉS (correcto)
cerrado_por = current_user.nombre_completo
```

Se revisaron y corrigieron **todos** los puntos donde se accedía a `current_user.name` en el archivo.

---

## Bug 2: `IntegrityError: null value in column "empresa_id"`

### Síntoma
```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.NotNullViolation)
null value in column "empresa_id" of relation "comparaciones_guardadas"
violates not-null constraint
```

### Causa raíz
La tabla `comparaciones_guardadas` tiene `empresa_id NOT NULL`. Al guardar una comparación, el código tomaba el `empresa_id` de la impresora asociada al cierre. Si la impresora no tenía `empresa_id` asignado (impresoras en migración o recién importadas), el INSERT fallaba.

### Fix aplicado
**Archivo:** `backend/api/counters.py`  
**Función:** `save_comparacion_guardada()`

```python
# ANTES — dependía solo de la impresora
empresa_id = printer.empresa_id  # Podía ser None → error

# DESPUÉS — fallback al usuario autenticado
empresa_id = printer.empresa_id or current_user.empresa_id
```

**Justificación del fallback:** El usuario autenticado siempre tiene `empresa_id` asignado (constraint de la tabla `users`). Si la impresora no tiene empresa, usar la del usuario garantiza integridad de datos y mantiene el aislamiento multi-tenant correcto.

---

## Bug 3: `NameError: name 'Printer' is not defined`

### Síntoma
```
NameError: name 'Printer' is not defined
```
Ocurría al llamar `GET /api/v1/dashboard/toner-alertas`.

### Causa raíz
La función del endpoint usaba el modelo `Printer` en sus queries, pero el import faltaba en el archivo.

### Fix aplicado
**Archivo:** `backend/api/dashboard.py`

```python
# Agregado al bloque de imports top-level
from db.models import Printer
```

---

## Limpieza de imports en `counters.py`

Adicionalmente a los bugs, se encontraron imports redundantes y muertos que causaban warnings en Pylance y podían enmascarar errores:

### Imports eliminados (no usados)
```python
# ELIMINADOS — nunca se usaban
from sqlalchemy.orm import joinedload
from .counter_schemas import PrinterResponse
from .counter_schemas import CapabilitiesResponse
```

### Imports locales → top-level
```python
# ANTES — dentro de la función get_all_users_closes()
from db.models import User, Printer, CierreMensual
from sqlalchemy import or_, date as sql_date
from datetime import date as dt_date

# DESPUÉS — eliminados (ya estaban en top-level del archivo)
# User → ya importado en línea 8
# Printer → ya importado en línea 8
# or_ → ya importado en línea 3
```

---

## Archivos modificados

| Archivo | Cambio |
|---|---|
| `backend/api/counters.py` | Fix `nombre_completo`, fix `empresa_id` fallback, limpieza imports |
| `backend/api/dashboard.py` | Agregado `from db.models import Printer` |

---

## Verificación post-fix

```bash
# Verificar que todos los imports cargan en runtime (dentro de Docker)
docker exec ricoh-backend python -c "
from db.models import User, CierreMensual, CierreMensualUsuario, Printer, ...
from services.counter_service import CounterService
...
print('TODOS LOS IMPORTS VALIDOS')
"
# Output: TODOS LOS IMPORTS VALIDOS ✅

# QA automatizado post-fix
python backend/qa_test_suite.py
# Output: 18/18 pruebas pasadas ✅
```

---

*Fix documentado el 29 de mayo de 2026*
