# Fix: Error 404 en Endpoint /read-all - Conflicto de Orden de Rutas

**Fecha:** 24 de marzo de 2026  
**Tipo:** Bug - Conflicto de rutas en FastAPI  
**Severidad:** Alta  
**Estado:** ✅ Resuelto

---

## Problema

El endpoint `POST /api/counters/read-all` retornaba error 404 aunque estaba correctamente implementado en el backend.

### Síntomas

```
POST http://localhost:8000/api/counters/read-all 404 (Not Found)
```

- El endpoint estaba definido en `backend/api/counters.py`
- La autenticación pasaba correctamente
- No había errores en los logs del backend
- El router estaba correctamente incluido en `main.py`

---

## Causa Raíz

**Conflicto de orden de rutas en FastAPI**

En FastAPI, el orden en que se definen las rutas es crítico. Cuando tienes rutas con parámetros dinámicos, FastAPI intenta hacer match en el orden en que fueron definidas.

### Orden Incorrecto (ANTES)

```python
@router.post("/read/{printer_id}")  # ← Esta ruta se evalúa primero
async def read_counter(printer_id: int, ...):
    ...

@router.post("/read-all")  # ← Esta ruta NUNCA se alcanza
async def read_all_counters(...):
    ...
```

**¿Qué pasaba?**

1. Cliente hace petición a `/read-all`
2. FastAPI evalúa `/read/{printer_id}` primero
3. FastAPI intenta hacer match: `/read/all` → `printer_id = "all"`
4. FastAPI intenta convertir "all" a `int` → FALLA
5. FastAPI retorna 404 (no encuentra ruta válida)
6. La ruta `/read-all` nunca se evalúa

---

## Solución

**Reordenar las rutas: rutas específicas ANTES de rutas con parámetros**

### Orden Correcto (DESPUÉS)

```python
# IMPORTANTE: /read-all debe estar ANTES de /read/{printer_id}
@router.post("/read-all")  # ← Ruta específica primero
async def read_all_counters(...):
    ...

@router.post("/read/{printer_id}")  # ← Ruta con parámetro después
async def read_counter(printer_id: int, ...):
    ...
```

**¿Por qué funciona ahora?**

1. Cliente hace petición a `/read-all`
2. FastAPI evalúa `/read-all` primero → MATCH EXACTO ✅
3. Ejecuta `read_all_counters()`
4. Retorna respuesta exitosa

---

## Archivos Modificados

### `backend/api/counters.py`

- Movido `@router.post("/read-all")` ANTES de `@router.post("/read/{printer_id}")`
- Agregado comentario explicativo sobre el orden

---

## Regla General: Orden de Rutas en FastAPI

**Siempre definir rutas en este orden:**

1. **Rutas estáticas/específicas** (sin parámetros)
   ```python
   @router.get("/users/me")
   @router.get("/users/active")
   ```

2. **Rutas con parámetros**
   ```python
   @router.get("/users/{user_id}")
   ```

### Ejemplos de Conflictos Comunes

❌ **INCORRECTO:**
```python
@router.get("/items/{item_id}")  # Captura TODO, incluso "latest"
@router.get("/items/latest")     # Nunca se alcanza
```

✅ **CORRECTO:**
```python
@router.get("/items/latest")     # Específica primero
@router.get("/items/{item_id}")  # Parámetro después
```

---

## Verificación

### Antes del Fix
```bash
curl -X POST http://localhost:8000/api/counters/read-all
# 404 Not Found
```

### Después del Fix
```bash
curl -X POST http://localhost:8000/api/counters/read-all
# 200 OK
# {
#   "success": true,
#   "message": "Lectura completada: 7 exitosas, 0 fallidas",
#   "successful": 7,
#   "failed": 0,
#   "total": 7,
#   "results": [...]
# }
```

---

## Lecciones Aprendidas

1. **El orden de las rutas importa en FastAPI** - No es como en otros frameworks donde el orden no afecta
2. **Rutas específicas siempre antes de rutas con parámetros** - Regla de oro
3. **FastAPI no da error de configuración** - Simplemente retorna 404 si no encuentra match
4. **Debugging:** Si un endpoint retorna 404 pero está definido, revisar el orden de las rutas

---

## Prevención

Para evitar este tipo de errores en el futuro:

1. **Revisar el orden al agregar nuevas rutas** - Especialmente si tienen prefijos similares
2. **Documentar rutas con parámetros** - Agregar comentarios sobre el orden
3. **Pruebas de integración** - Verificar que todos los endpoints respondan correctamente
4. **Code review** - Revisar el orden de rutas en PRs

---

## Referencias

- [FastAPI Path Parameters - Order Matters](https://fastapi.tiangolo.com/tutorial/path-params/#order-matters)
- Documentación interna: `docs/VERIFICACION_ENDPOINTS_COUNTERS.md`
- Documentación interna: `docs/FIX_ENDPOINT_READ_ALL.md` (implementación inicial)

---

## Relacionado

- **Task 10:** Verificación de Endpoints y Fix read-all (implementación inicial)
- **Task 11:** Fix orden de rutas (este documento)
