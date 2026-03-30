# Error 500 en Sincronización de Usuarios - CORREGIDO

**Fecha**: 30 de Marzo de 2026  
**Tipo**: Error de Configuración  
**Severidad**: Alta  
**Estado**: ✅ CORREGIDO

---

## Descripción del Problema

Al intentar sincronizar usuarios desde las impresoras, se producía un error 500 (Internal Server Error) con el siguiente mensaje en los logs:

```
ERROR - ❌ ERROR EN SINCRONIZACIÓN
ERROR -    Tipo: ValueError
ERROR -    Mensaje: RICOH_ADMIN_PASSWORD must be set. Configure it in environment variables or pass it explicitly.
```

## Causa Raíz

El código de `RicohWebClient` estaba validando que `RICOH_ADMIN_PASSWORD` no estuviera vacío, pero algunas impresoras Ricoh no tienen contraseña configurada para el usuario administrador (es común en entornos de red interna).

## Solución Implementada

Se modificó el constructor de `RicohWebClient` en `backend/services/ricoh_web_client.py` para permitir contraseñas vacías:

**Antes**:
```python
# Validate that password is provided and not empty
if not admin_password:
    raise ValueError(
        "RICOH_ADMIN_PASSWORD must be set. "
        "Configure it in environment variables or pass it explicitly."
    )

self.admin_password = admin_password
```

**Después**:
```python
# Allow empty password (some Ricoh printers don't have password set)
# Store as empty string if None
self.admin_password = admin_password if admin_password is not None else ""
```

## Configuración

El archivo `backend/.env` puede tener la contraseña vacía:

```env
# Ricoh Printer Admin Credentials
RICOH_ADMIN_USER=admin
RICOH_ADMIN_PASSWORD=
```

Esto es válido para impresoras sin contraseña configurada.

## Verificación

Después de aplicar el fix:

1. Reiniciar el backend
2. Intentar sincronizar usuarios desde la interfaz web
3. El error 500 debería desaparecer y la sincronización debería funcionar correctamente

## Archivos Modificados

- `backend/services/ricoh_web_client.py` - Eliminada validación estricta de contraseña

---

**Estado**: ✅ CORREGIDO  
**Fecha de corrección**: 30 de Marzo de 2026
