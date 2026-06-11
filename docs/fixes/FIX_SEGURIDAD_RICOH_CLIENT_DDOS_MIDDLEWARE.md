# Mejoras de Seguridad – Validación de Credenciales y Control de Middleware

**Fecha**: 4 de Junio de 2026  
**Módulo**: `services/ricoh_web_client.py`, `middleware/ddos_protection.py`  
**Tipo**: Mejora de seguridad + soporte de testing

---

## 1. Validación de Contraseña Vacía en RicohWebClient

### Problema Detectado
El constructor de `RicohWebClient` aceptaba silenciosamente `admin_password` vacío o `None`,  
almacenándolo como cadena vacía. Esto permitía instanciar un cliente sin credenciales válidas,  
lo que podría resultar en intentos de autenticación con contraseña en blanco contra impresoras reales.

```python
# ANTES (comportamiento inseguro)
self.admin_password = admin_password if admin_password is not None else ""
```

### Corrección Aplicada

```python
# DESPUÉS (validación estricta)
if admin_password is None:
    admin_password = os.getenv("RICOH_ADMIN_PASSWORD", None)

if not admin_password:
    raise ValueError(
        "RICOH_ADMIN_PASSWORD must be set. "
        "Provide admin_password parameter or set RICOH_ADMIN_PASSWORD environment variable."
    )

self.admin_password = admin_password
```

### Comportamiento Resultante

| Escenario | Antes | Después |
|---|---|---|
| `RicohWebClient(admin_user="admin", admin_password="SecurePass1!")` | ✅ OK | ✅ OK |
| `RicohWebClient(admin_user="admin", admin_password="")` | ✅ Silencioso | ❌ `ValueError` |
| `RicohWebClient(admin_user="admin", admin_password=None)` | ✅ Silencioso | ❌ `ValueError` (si `RICOH_ADMIN_PASSWORD` no está en env) |
| `RICOH_ADMIN_PASSWORD=SecurePass1!` en `.env` | ✅ OK | ✅ OK |
| `RICOH_ADMIN_PASSWORD=` (vacío en `.env`) | ✅ Silencioso | ❌ `ValueError` |

### Impacto en el Código Existente

Todos los usos de `RicohWebClient` en producción (`api/provisioning.py`, `api/discovery.py`)  
leen la contraseña desde la variable de entorno `RICOH_ADMIN_PASSWORD`, que siempre debe  
estar configurada. No hay cambio funcional para un entorno correctamente configurado.

---

## 2. Control de DDoS Middleware via Variable de Entorno

### Problema Detectado
`DDoSProtectionMiddleware` no tenía mecanismo para deshabilitarse en entornos de test.  
Los tests que necesitaban probar CORS o endpoints genéricos recibían 403/429 del middleware  
DDoS antes de llegar al handler real, ya que el IP del test no pasaba los filtros.

### Corrección Aplicada

Se añadió un check al inicio del método `dispatch()`:

```python
async def dispatch(self, request: Request, call_next):
    import os
    # Allow disabling DDoS protection via environment variable (for testing)
    if os.getenv("ENABLE_DDOS_PROTECTION", "true").lower() == "false":
        return await call_next(request)
    
    # ... resto de la lógica DDoS
```

### Uso en Tests

```python
# En test unitario
def test_cors_allows_configured_origins(self):
    os.environ["ENABLE_DDOS_PROTECTION"] = "false"
    from main import app
    client = TestClient(app)
    response = client.options("/", headers={"Origin": CORS_ORIGINS[0]})
    assert response.status_code == 200
```

### Uso en Docker Compose

```yaml
# docker-compose.yml (producción)
backend:
  environment:
    ENABLE_DDOS_PROTECTION: "true"  # Por defecto

# docker-compose.test.yml (pruebas)
backend:
  environment:
    ENABLE_DDOS_PROTECTION: "false"
```

### Seguridad

> ⚠️ **IMPORTANTE**: Esta variable NUNCA debe configurarse como `false` en producción.  
> El valor por defecto es `"true"` si la variable no está definida, por lo que omitirla  
> en producción es equivalente a mantener la protección activa.

---

## 3. Archivos Modificados

| Archivo | Tipo de Cambio | Líneas Afectadas |
|---|---|---|
| `services/ricoh_web_client.py` | Validación de seguridad | `__init__()` L.34-55 |
| `middleware/ddos_protection.py` | Soporte de testing | `dispatch()` L.181-187 |
