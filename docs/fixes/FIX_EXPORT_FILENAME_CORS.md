# Fix: Content-Disposition Header Bloqueado por CORS

**Fecha**: 31 de Marzo de 2026  
**Tipo**: Bug Fix  
**Módulo**: Exportaciones  
**Severidad**: Media  

## Problema

Al exportar cierres o comparaciones (CSV, Excel, Excel Ricoh), el archivo se descargaba con el nombre fallback del frontend en lugar del nombre personalizado enviado por el backend.

### Síntomas
- Los archivos se descargaban con nombres genéricos: `comparacion_ricoh_253_307.xlsx`
- El formato esperado era: `SERIAL DD.MM.YYYY.extensión` (ejemplo: `E174MA11130 31.03.2026.xlsx`)
- En la consola del navegador aparecía: `Content-Disposition header: null`

### Causa Raíz
El header `Content-Disposition` enviado por el backend no estaba siendo expuesto por la configuración de CORS en FastAPI. Aunque el backend enviaba correctamente el header, el navegador lo bloqueaba por seguridad CORS.

## Solución

### Cambio en Backend (`backend/main.py`)

Se agregó `Content-Disposition` a la lista de headers expuestos en la configuración de CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "Content-Disposition"],  # ← Agregado
    max_age=3600,
)
```

### Formato de Nombres de Archivo

Todos los endpoints de exportación ahora generan nombres con el formato:
- **Formato**: `SERIAL DD.MM.YYYY.extensión`
- **Ejemplo**: `E174MA11130 31.03.2026.xlsx`

Donde:
- `SERIAL`: Número de serie de la impresora
- `DD.MM.YYYY`: Fecha actual del momento de la exportación
- `extensión`: `.csv` o `.xlsx` según el tipo de exportación

### Endpoints Afectados

Los siguientes 5 endpoints fueron actualizados:

1. `GET /api/export/cierre/{cierre_id}` - Exportar cierre a CSV
2. `GET /api/export/cierre/{cierre_id}/excel` - Exportar cierre a Excel
3. `GET /api/export/comparacion/{cierre1_id}/{cierre2_id}` - Exportar comparación a CSV
4. `GET /api/export/comparacion/{cierre1_id}/{cierre2_id}/excel` - Exportar comparación a Excel
5. `GET /api/export/comparacion/{cierre1_id}/{cierre2_id}/excel-ricoh` - Exportar comparación a Excel formato Ricoh

## Implementación

### Backend (`backend/api/export.py`)

Cada endpoint genera el nombre del archivo con el formato correcto:

```python
from datetime import datetime

# Obtener fecha actual
fecha_actual = datetime.now().strftime('%d.%m.%Y')

# Obtener serial de la impresora
serial = printer.serial_number if printer and printer.serial_number else printer.hostname

# Generar nombre del archivo
filename = f"{serial} {fecha_actual}.xlsx"

# Enviar con header Content-Disposition
return StreamingResponse(
    output,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": f'attachment; filename="{filename}"'}
)
```

### Frontend (`src/services/exportService.ts`)

El frontend extrae el nombre del archivo desde el header `Content-Disposition`:

```typescript
// Extraer el nombre del archivo del header Content-Disposition
let filename = fallbackFilename;
const contentDisposition = response.headers.get('Content-Disposition');
if (contentDisposition) {
  const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
  if (filenameMatch && filenameMatch[1]) {
    filename = filenameMatch[1].replace(/['"]/g, '');
  }
}
```

## Despliegue

Para aplicar el cambio en Docker:

```bash
# Detener contenedores
docker-compose down

# Reconstruir backend (sin caché)
docker-compose build --no-cache backend

# Iniciar contenedores
docker-compose up -d
```

O reconstruir todo:

```bash
docker-compose down
docker-compose up -d --build
```

## Verificación

1. Iniciar sesión en la aplicación
2. Ir a Cierres Mensuales
3. Seleccionar una impresora con serial number
4. Exportar un cierre o comparación
5. Verificar que el archivo se descarga con el formato: `SERIAL DD.MM.YYYY.extensión`

### Logs de Debugging

El frontend incluye logs en consola para debugging:

```
Content-Disposition header: attachment; filename="E174MA11130 31.03.2026.xlsx"
Filename extraído del backend: E174MA11130 31.03.2026.xlsx
Filename final a usar: E174MA11130 31.03.2026.xlsx
```

## Archivos Modificados

- `backend/main.py` - Configuración de CORS
- `backend/api/export.py` - 5 endpoints de exportación (ya modificados previamente)
- `src/services/exportService.ts` - Extracción del header (ya modificado previamente)

## Notas Técnicas

### ¿Por qué `expose_headers`?

Por seguridad, los navegadores solo permiten que JavaScript acceda a un conjunto limitado de headers de respuesta en peticiones CORS. Para que el frontend pueda leer headers personalizados como `Content-Disposition`, el backend debe declararlos explícitamente en `expose_headers`.

### Headers Expuestos Actuales

```python
expose_headers=[
    "X-RateLimit-Limit",      # Rate limiting
    "X-RateLimit-Remaining",  # Rate limiting
    "Content-Disposition"     # Nombres de archivo
]
```

## Referencias

- [MDN: CORS - Access-Control-Expose-Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)
- [RFC 6266: Content-Disposition Header](https://tools.ietf.org/html/rfc6266)
