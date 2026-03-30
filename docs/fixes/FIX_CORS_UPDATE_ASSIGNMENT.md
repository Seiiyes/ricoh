# Fix: Error CORS en Update Assignment

**Fecha**: 25 de marzo de 2026  
**Problema**: Error CORS al actualizar permisos de asignación de usuarios

## Error

```
Access to XMLHttpRequest at 'http://localhost:8000/provisioning/update-assignment?...' 
from origin 'http://localhost:5173' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
It does not have HTTP ok status.
```

## Causa Raíz

El endpoint `/provisioning/update-assignment` tenía un parámetro `permissions: dict` sin anotación de tipo que indicara que es del body. FastAPI lo estaba tratando como query parameter, lo que causaba que el preflight OPTIONS fallara con `400 Bad Request`.

**Logs del backend**:
```
INFO: 172.18.0.1:34872 - "OPTIONS /provisioning/update-assignment?user_id=3&printer_id=4&entry_index=00256 HTTP/1.1" 400 Bad Request
```

El preflight OPTIONS debe retornar `200 OK`, pero estaba retornando `400 Bad Request` porque FastAPI intentaba validar los parámetros del body en el OPTIONS.

## Solución

Agregar la anotación `Body(...)` al parámetro `permissions` para indicar explícitamente que es del body:

```python
# ANTES (INCORRECTO)
@router.patch("/update-assignment", response_model=MessageResponse)
async def update_assignment_permissions(
    user_id: int,
    printer_id: int,
    permissions: dict,  # ← Sin anotación, FastAPI lo trata como query param
    entry_index: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ...

# DESPUÉS (CORRECTO)
from fastapi import Body

@router.patch("/update-assignment", response_model=MessageResponse)
async def update_assignment_permissions(
    user_id: int,
    printer_id: int,
    permissions: dict = Body(...),  # ← Explícitamente del body
    entry_index: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ...
```

## Cambios Realizados

1. ✅ Agregado `Body` al import de FastAPI en `backend/api/provisioning.py`
2. ✅ Cambiado `permissions: dict` a `permissions: dict = Body(...)`
3. ✅ Backend reiniciado

## Archivos Modificados

- `backend/api/provisioning.py`

## Testing

1. Ir a Usuarios → Administración de Usuarios
2. Editar un usuario
3. Cambiar permisos de una impresora asignada
4. Hacer clic en "Guardar"
5. Verificar que se guarda sin errores CORS

## Resultado Esperado

- El preflight OPTIONS debe retornar `200 OK`
- La petición PATCH debe ejecutarse correctamente
- Los permisos deben actualizarse en la base de datos y en la impresora

## Notas Técnicas

### FastAPI y Parámetros del Body

En FastAPI, cuando un parámetro no tiene anotación de tipo especial, se infiere su ubicación:
- Tipos simples (int, str, bool) → Query parameters
- Modelos Pydantic → Body
- `dict` o `list` sin anotación → Query parameters (comportamiento por defecto)

Para indicar explícitamente que un parámetro es del body, usar:
- `Body(...)` para parámetros requeridos
- `Body(None)` para parámetros opcionales
- `Body(default_value)` para parámetros con valor por defecto

### CORS y Preflight

El preflight OPTIONS es una petición que el navegador hace antes de la petición real para verificar que el servidor permite la petición. Si el preflight falla (retorna algo diferente de 200 OK), el navegador bloquea la petición real.

En este caso, el preflight fallaba porque FastAPI intentaba validar los parámetros del body en el OPTIONS, lo que causaba un 400 Bad Request.

## Verificación

Después del fix, el preflight debe retornar:
```
INFO: 172.18.0.1:XXXXX - "OPTIONS /provisioning/update-assignment?user_id=3&printer_id=4&entry_index=00256 HTTP/1.1" 200 OK
```

Y la petición PATCH debe ejecutarse correctamente:
```
INFO: 172.18.0.1:XXXXX - "PATCH /provisioning/update-assignment?user_id=3&printer_id=4&entry_index=00256 HTTP/1.1" 200 OK
```
