# 003 - Conflicto de Rutas en FastAPI

**Fecha:** 4 de marzo de 2026  
**Severidad:** Media  
**Módulo:** Backend  
**Tags:** #api #fastapi #routing #endpoints

---

## 🐛 Descripción del Error

El endpoint `/api/counters/closes/{cierre_id}` no devolvía el detalle de un cierre específico. En su lugar, devolvía una lista de cierres (como si fuera el endpoint `/api/counters/closes/{printer_id}`).

## 🔍 Síntomas

- Request a `/api/counters/closes/7` devuelve una lista en lugar de un objeto
- El endpoint de detalle nunca se ejecuta
- FastAPI siempre usa el primer endpoint que coincide con el patrón
- Error al intentar acceder a propiedades del objeto (porque es una lista)

### Ejemplo del Problema
```bash
# Request
curl http://localhost:8000/api/counters/closes/7

# Respuesta esperada (objeto)
{
  "id": 7,
  "printer_id": 4,
  "usuarios": [...]
}

# Respuesta real (lista)
[
  {"id": 7, ...},
  {"id": 8, ...}
]
```

## 🎯 Causa Raíz

En FastAPI, cuando hay dos rutas con el mismo patrón, la primera definida tiene prioridad. En `backend/api/counters.py` había:

```python
# Ruta 1 (línea 362)
@router.get("/closes/{printer_id}", response_model=List[CierreMensualResponse])
def get_closes(printer_id: int, ...):
    # Lista de cierres por impresora
    pass

# Ruta 2 (línea 445)
@router.get("/closes/{cierre_id}", response_model=CierreMensualResponse)
def get_close_by_id(cierre_id: int, ...):
    # Detalle de un cierre específico
    pass
```

FastAPI interpreta ambas rutas como `/closes/{variable}` y siempre usa la primera (get_closes).

### Por qué ocurrió
- No se consideró el orden de definición de rutas en FastAPI
- Ambas rutas usan el mismo patrón con un parámetro entero
- FastAPI no puede distinguir entre "printer_id" y "cierre_id" en la URL
- No se probó el endpoint de detalle después de agregarlo

## ✅ Solución Implementada

Usar una ruta diferente para el detalle que no entre en conflicto. La solución fue usar el endpoint existente `/monthly/{cierre_id}/detail` que ya estaba implementado.

### Rutas Antes (Conflicto)
```python
# backend/api/counters.py

# Ruta 1 - Lista de cierres
@router.get("/closes/{printer_id}")
def get_closes(printer_id: int, ...):
    pass

# Ruta 2 - Detalle de cierre (NUNCA SE EJECUTA)
@router.get("/closes/{cierre_id}")
def get_close_by_id(cierre_id: int, ...):
    pass
```

### Rutas Después (Sin Conflicto)
```python
# backend/api/counters.py

# Ruta 1 - Lista de cierres
@router.get("/closes/{printer_id}")
def get_closes(printer_id: int, ...):
    pass

# Ruta 2 - Detalle de cierre (ruta diferente)
@router.get("/monthly/{cierre_id}/detail")
def get_monthly_close_detail(cierre_id: int, ...):
    pass
```

### Actualización en Frontend
```typescript
// Antes
const response = await fetch(`${API_BASE}/api/counters/closes/${cierre.id}`);

// Después
const response = await fetch(`${API_BASE}/api/counters/monthly/${cierre.id}/detail`);
```

## 🛡️ Prevención Futura

- [x] Usar rutas específicas que no entren en conflicto
- [x] Documentar el orden de rutas en FastAPI
- [ ] Agregar test que verifique cada endpoint individualmente
- [ ] Usar prefijos diferentes para recursos diferentes
- [ ] Revisar rutas antes de agregar nuevas

### Mejores Prácticas para Rutas en FastAPI

#### ❌ Evitar (Rutas Ambiguas)
```python
@router.get("/items/{item_id}")  # Puede ser cualquier entero
@router.get("/items/{category}")  # Conflicto!
```

#### ✅ Preferir (Rutas Específicas)
```python
@router.get("/items/{item_id}")
@router.get("/items/by-category/{category}")  # Sin conflicto
```

#### ✅ Usar Prefijos Claros
```python
@router.get("/printers/{printer_id}/closes")  # Lista de cierres
@router.get("/closes/{close_id}")  # Detalle de cierre
```

#### ✅ Orden de Rutas Específicas Primero
```python
# Rutas específicas primero
@router.get("/closes/latest")  # Más específica
@router.get("/closes/{close_id}")  # Más general
```

## 📚 Referencias

- [FastAPI Routing](https://fastapi.tiangolo.com/tutorial/path-params/)
- [Path Operation Order](https://fastapi.tiangolo.com/tutorial/path-params/#order-matters)
- [Archivo corregido](../../backend/api/counters.py)
- [Frontend actualizado](../../src/components/contadores/cierres/CierreDetalleModal.tsx)

## 💡 Lecciones Clave

1. **Orden importa en FastAPI**: La primera ruta que coincide se ejecuta
2. **Rutas específicas primero**: Definir rutas más específicas antes que las generales
3. **Evitar ambigüedad**: Usar prefijos o sufijos para diferenciar rutas
4. **Probar cada endpoint**: Verificar que cada endpoint se ejecuta correctamente
5. **Documentar rutas**: Mantener un mapa de todas las rutas del API

## 🔧 Herramientas de Validación

### Listar Todas las Rutas
```python
# Script para listar rutas
from fastapi import FastAPI
from backend.api import counters

app = FastAPI()
app.include_router(counters.router)

for route in app.routes:
    print(f"{route.methods} {route.path}")
```

### Test de Endpoints
```python
def test_endpoint_detalle_cierre():
    """Verifica que el endpoint de detalle funciona"""
    response = client.get("/api/counters/monthly/7/detail")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "usuarios" in data
    assert isinstance(data["usuarios"], list)

def test_endpoint_lista_cierres():
    """Verifica que el endpoint de lista funciona"""
    response = client.get("/api/counters/closes/4")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

---

## 📊 Impacto

- **Tiempo de detección:** 30 minutos
- **Tiempo de corrección:** 15 minutos
- **Endpoints afectados:** 1
- **Usuarios afectados:** 0 (detectado en desarrollo)
- **Severidad real:** Media (funcionalidad no disponible)

---

## 🔄 Alternativas Consideradas

### Opción 1: Cambiar Orden de Rutas
```python
# Definir ruta específica primero
@router.get("/closes/{close_id}")  # Primero
@router.get("/closes/{printer_id}")  # Después
```
**Problema:** Ambas rutas siguen siendo ambiguas

### Opción 2: Usar Query Parameters
```python
@router.get("/closes")
def get_closes(printer_id: Optional[int] = None, close_id: Optional[int] = None):
    if close_id:
        return get_by_id(close_id)
    return get_by_printer(printer_id)
```
**Problema:** Menos RESTful, más complejo

### Opción 3: Usar Rutas Diferentes (ELEGIDA)
```python
@router.get("/closes/{printer_id}")  # Lista
@router.get("/monthly/{close_id}/detail")  # Detalle
```
**Ventaja:** Sin ambigüedad, RESTful, claro

---

**Documentado por:** Sistema Kiro  
**Revisado por:** Equipo de desarrollo  
**Estado:** ✅ Resuelto

**Última actualización:** 4 de marzo de 2026
