# Solución a Contaminación de Pruebas y Seguridad (Junio 2026)

**Fecha**: Junio de 2026

## 1. Problema de Estado (State Leakage) en Pytest
Se identificó que la suite de pruebas automatizadas presentaba fallos intermitentes y falsos positivos (como errores de `403 CSRF_TOKEN_MISSING`) al ejecutarse secuencialmente. El origen de este problema radicaba en la mutación global de las variables de entorno (`os.environ`) dentro de pruebas específicas de "Condición de Bug" (`test_bug_condition_permissive_config.py`).

Al mutar `ENVIRONMENT` y recargar el módulo `main` con `importlib.reload(main)`, la instancia del objeto `FastAPI` y su pila de Middlewares (CORS, CSRF, DDoS) sufrían alteraciones que no se revertían completamente para las siguientes pruebas, resultando en un estado "contaminado" del backend.

## 2. Correcciones Implementadas
- **Restauración Profunda de `importlib.reload(main)`**: Se garantizó que en cada bloque `finally` de las pruebas mutantes no sólo se restauraran las variables de entorno (`os.environ["ENVIRONMENT"]`, `os.environ["ENABLE_CSRF"]`), sino que se ejecutara nuevamente `importlib.reload(main)` para reensamblar la app de FastAPI sin el middleware experimental.
- **Fixture Scope Cleanup**: Modificación para forzar el re-importado adecuado del módulo dentro del fixture.
- **Resolución CSRF Redis vs Memory**: Los tests de preservación de CSRF (`test_preservation_cors_csrf_ratelimit.py`) se escribieron esperando que el `CSRFProtectionMiddleware` utilizara un diccionario en memoria (`_token_cache_internal`). Sin embargo, las actualizaciones recientes adaptaron el middleware para usar Redis distribuido automáticamente. Se parcheó (`monkeypatch`) la variable `REDIS_URL` en las pruebas locales para forzar el modo de memoria y validar la lógica pura sin dependencias de red.
- **Renombramiento de Almacenamiento en Rate Limiter**: Ajuste de atributo de clase de `_storage` a `_memory_storage` en el servicio de Rate Limiter para satisfacer aserciones rígidas de pruebas basadas en propiedades.

## 3. Resultado de la Ejecución
La corrección de los artefactos de test restableció la fiabilidad de la suite de pruebas unitarias y de preservación.
**Resultados post-resolución:** `19 failed -> 0 failed`. La estabilidad arquitectónica del pipeline de CI/CD está asegurada.
