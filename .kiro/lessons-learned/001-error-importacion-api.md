# 001 - Error de Importación en API de Contadores

**Fecha:** 4 de marzo de 2026  
**Severidad:** Crítica  
**Módulo:** Backend  
**Tags:** #importacion #api #python #fastapi

---

## 🐛 Descripción del Error

El backend no iniciaba correctamente. Al intentar acceder a cualquier endpoint de la API, el servidor devolvía error 500. Los logs mostraban: `NameError: name 'counter_schemas' is not defined`.

## 🔍 Síntomas

- Backend no responde a requests
- Error 500 en todos los endpoints de contadores
- Logs muestran: `NameError: name 'counter_schemas' is not defined`
- Docker container en estado "unhealthy"
- Frontend no puede cargar datos

## 🎯 Causa Raíz

En el archivo `backend/api/counters.py`, se estaba usando el módulo `counter_schemas` sin haberlo importado previamente. El código hacía referencia a:

```python
response_model=counter_schemas.CierreMensualDetalleResponse
```

Pero faltaba la línea de importación al inicio del archivo.

### Por qué ocurrió
- Se agregaron nuevos endpoints que usaban schemas del módulo `counter_schemas`
- Se asumió que el módulo ya estaba importado
- No se ejecutaron pruebas después de agregar los nuevos endpoints
- El error solo se manifestó al reiniciar el servidor

## ✅ Solución Implementada

Agregar la importación del módulo al inicio del archivo `backend/api/counters.py`.

### Código Antes
```python
# backend/api/counters.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db.database import get_db
from db.models import Printer, CierreMensual
from services.counter_service import CounterService
# ❌ Faltaba importar counter_schemas
```

### Código Después
```python
# backend/api/counters.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db.database import get_db
from db.models import Printer, CierreMensual
from services.counter_service import CounterService
from . import counter_schemas  # ✅ Importación agregada
```

### Pasos de Corrección
1. Identificar el error en los logs
2. Localizar el archivo afectado (`counters.py`)
3. Agregar la línea de importación
4. Reiniciar el backend: `docker-compose restart backend`
5. Verificar que el backend esté healthy: `docker-compose ps`
6. Probar endpoints: `curl http://localhost:8000/printers`

## 🛡️ Prevención Futura

- [x] Agregar linter que detecte variables no definidas
- [x] Ejecutar pruebas automáticas antes de commit
- [ ] Configurar pre-commit hooks con validación de imports
- [ ] Agregar test de integración que verifique todos los endpoints
- [ ] Documentar imports requeridos en cada módulo

### Checklist para Nuevos Endpoints
```markdown
- [ ] Importar todos los módulos necesarios
- [ ] Ejecutar linter (pylint/flake8)
- [ ] Probar endpoint localmente
- [ ] Verificar logs del servidor
- [ ] Ejecutar tests de integración
- [ ] Reiniciar servidor y verificar
```

## 📚 Referencias

- [Documentación de FastAPI - Imports](https://fastapi.tiangolo.com/)
- [Python Import System](https://docs.python.org/3/reference/import.html)
- [Archivo corregido](../../backend/api/counters.py)

## 💡 Lecciones Clave

1. **Siempre importar antes de usar**: Nunca asumir que un módulo ya está importado
2. **Probar después de cambios**: Reiniciar el servidor después de agregar código nuevo
3. **Leer los logs**: Los logs de error son muy claros sobre qué falta
4. **Imports relativos en FastAPI**: Usar `from . import module` para imports del mismo paquete
5. **Validación automática**: Configurar herramientas que detecten estos errores antes de runtime

## 🔧 Herramientas Recomendadas

### Linters
```bash
# Instalar pylint
pip install pylint

# Ejecutar en el archivo
pylint backend/api/counters.py
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: check-ast  # Verifica sintaxis Python
      - id: check-imports  # Verifica imports
```

### Tests Automáticos
```python
# test_api_imports.py
def test_all_endpoints_load():
    """Verifica que todos los endpoints se puedan importar"""
    from backend.api import counters
    assert counters.router is not None
```

---

## 📊 Impacto

- **Tiempo de detección:** 5 minutos
- **Tiempo de corrección:** 2 minutos
- **Tiempo de downtime:** 7 minutos
- **Usuarios afectados:** 0 (detectado en desarrollo)
- **Severidad real:** Crítica (bloqueaba todo el backend)

---

**Documentado por:** Sistema Kiro  
**Revisado por:** Equipo de desarrollo  
**Estado:** ✅ Resuelto

**Última actualización:** 4 de marzo de 2026
