# 🔧 Instrucciones para Aplicar Fix de Exportaciones

**Fecha**: 31 de Marzo de 2026  
**Fix**: Content-Disposition Header Bloqueado por CORS

## ¿Qué se Arregló?

Los archivos exportados ahora se descargarán con el formato correcto:
- **Antes**: `comparacion_ricoh_253_307.xlsx`
- **Después**: `E174MA11130 31.03.2026.xlsx`

## 🚀 Pasos para Aplicar el Fix

### Opción 1: Reconstruir Solo Backend (Más Rápido)

```bash
# 1. Detener todos los contenedores
docker-compose down

# 2. Reconstruir solo el backend sin caché
docker-compose build --no-cache backend

# 3. Iniciar todos los contenedores
docker-compose up -d
```

### Opción 2: Reconstruir Todo (Más Seguro)

```bash
# 1. Detener todos los contenedores
docker-compose down

# 2. Reconstruir todo sin caché
docker-compose build --no-cache

# 3. Iniciar todos los contenedores
docker-compose up -d
```

## ✅ Verificar que Funciona

1. Abre la aplicación: http://localhost:5173
2. Inicia sesión
3. Ve a **Cierres Mensuales**
4. Selecciona una impresora (debe tener serial number)
5. Exporta un cierre o comparación
6. **Verifica el nombre del archivo descargado**

### Nombre Esperado

```
E174MA11130 31.03.2026.xlsx
```

Donde:
- `E174MA11130` = Serial de la impresora
- `31.03.2026` = Fecha actual (día de la exportación)
- `.xlsx` = Extensión del archivo

## 🔍 Debugging (Si No Funciona)

### 1. Verificar Logs en Consola del Navegador

Presiona `F12` y ve a la pestaña **Console**. Deberías ver:

```
Content-Disposition header: attachment; filename="E174MA11130 31.03.2026.xlsx"
Filename extraído del backend: E174MA11130 31.03.2026.xlsx
Filename final a usar: E174MA11130 31.03.2026.xlsx
```

### 2. Si Sigue Mostrando `null`

```
Content-Disposition header: null
```

Significa que el backend no se reconstruyó correctamente. Intenta:

```bash
# Limpiar todo
docker-compose down -v
docker system prune -f

# Reconstruir desde cero
docker-compose build --no-cache
docker-compose up -d
```

### 3. Verificar que el Backend Está Corriendo

```bash
docker-compose ps
```

Deberías ver:
```
NAME                IMAGE               STATUS
ricoh-backend       ricoh-backend       Up
ricoh-frontend      ricoh-frontend      Up
ricoh-postgres      postgres:16         Up
ricoh-adminer       adminer             Up
```

### 4. Ver Logs del Backend

```bash
docker-compose logs -f backend
```

Busca errores al iniciar.

## 📝 Cambio Técnico Realizado

**Archivo**: `backend/main.py`

Se agregó `Content-Disposition` a los headers expuestos en CORS:

```python
expose_headers=[
    "X-RateLimit-Limit",
    "X-RateLimit-Remaining",
    "Content-Disposition"  # ← NUEVO
]
```

## 📚 Documentación Completa

- **Fix Detallado**: `docs/fixes/FIX_EXPORT_FILENAME_CORS.md`
- **Resumen Sesión**: `docs/resumen/RESUMEN_FIX_EXPORTACIONES_31_MARZO.md`

## ❓ Preguntas Frecuentes

### ¿Por qué necesito reconstruir Docker?

El cambio está en el código del backend (`backend/main.py`). Docker necesita reconstruir la imagen para incluir el código actualizado.

### ¿Se perderán mis datos?

No. La base de datos está en un volumen persistente. Solo se reconstruye el código de la aplicación.

### ¿Cuánto tarda?

- Reconstruir solo backend: ~1-2 minutos
- Reconstruir todo: ~3-5 minutos

### ¿Funciona para todas las exportaciones?

Sí. Aplica para:
- ✅ CSV cierre individual
- ✅ Excel cierre individual
- ✅ CSV comparación
- ✅ Excel comparación
- ✅ Excel Ricoh (3 hojas)

### ¿Qué pasa si la impresora no tiene serial?

Se usará el hostname como fallback:
```
192.168.1.100 31.03.2026.xlsx
```

## 🎯 Resultado Final

Después de aplicar el fix, todos los archivos exportados tendrán nombres descriptivos con el serial de la impresora y la fecha actual, facilitando su organización y búsqueda.

---

**¿Necesitas ayuda?** Revisa los logs o consulta la documentación completa en `docs/fixes/FIX_EXPORT_FILENAME_CORS.md`
