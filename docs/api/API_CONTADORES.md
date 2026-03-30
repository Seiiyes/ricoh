# API de Contadores - Documentación

## Descripción General

La API de contadores proporciona endpoints REST para leer, consultar y gestionar contadores de impresoras Ricoh. Incluye funcionalidad para:

- Consultar contadores totales de impresoras
- Consultar contadores por usuario
- Ejecutar lecturas manuales
- Realizar cierres mensuales
- Consultar históricos

## Base URL

```
http://localhost:8000/api/counters
```

## Endpoints

### 1. Obtener Último Contador Total

Obtiene el último contador total registrado de una impresora.

**Endpoint:** `GET /api/counters/printer/{printer_id}`

**Parámetros:**
- `printer_id` (path, requerido): ID de la impresora

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "printer_id": 4,
  "total": 372573,
  "copiadora_bn": 59142,
  "copiadora_color": 0,
  "copiadora_color_personalizado": 0,
  "copiadora_dos_colores": 0,
  "impresora_bn": 313065,
  "impresora_color": 0,
  "impresora_color_personalizado": 0,
  "impresora_dos_colores": 0,
  "fax_bn": 0,
  "enviar_total_bn": 170292,
  "enviar_total_color": 0,
  "transmision_fax_total": 0,
  "envio_escaner_bn": 170292,
  "envio_escaner_color": 0,
  "otras_a3_dlt": 0,
  "otras_duplex": 0,
  "fecha_lectura": "2026-03-02T10:41:15.537568Z",
  "created_at": "2026-03-02T10:41:15.537568Z"
}
```

**Errores:**
- `404`: Impresora no encontrada o sin contadores registrados

**Ejemplo curl:**
```bash
curl http://localhost:8000/api/counters/printer/4
```

---

### 2. Obtener Histórico de Contadores Totales

Obtiene el histórico de contadores totales de una impresora con filtros opcionales.

**Endpoint:** `GET /api/counters/printer/{printer_id}/history`

**Parámetros:**
- `printer_id` (path, requerido): ID de la impresora
- `start_date` (query, opcional): Fecha inicial (ISO 8601)
- `end_date` (query, opcional): Fecha final (ISO 8601)
- `limit` (query, opcional): Límite de registros (default: 100, max: 1000)

**Respuesta exitosa (200):**
```json
[
  {
    "id": 7,
    "printer_id": 4,
    "total": 372573,
    "copiadora_bn": 59142,
    ...
    "fecha_lectura": "2026-03-02T10:41:15.537568Z",
    "created_at": "2026-03-02T10:41:15.537568Z"
  },
  {
    "id": 6,
    "printer_id": 4,
    "total": 372525,
    ...
  }
]
```

**Ejemplo curl:**
```bash
# Últimos 50 registros
curl "http://localhost:8000/api/counters/printer/4/history?limit=50"

# Filtrar por rango de fechas
curl "http://localhost:8000/api/counters/printer/4/history?start_date=2026-03-01T00:00:00Z&end_date=2026-03-02T23:59:59Z"
```

---

### 3. Obtener Últimos Contadores por Usuario

Obtiene los últimos contadores por usuario de una impresora.

**Endpoint:** `GET /api/counters/users/{printer_id}`

**Parámetros:**
- `printer_id` (path, requerido): ID de la impresora

**Respuesta exitosa (200):**
```json
[
  {
    "id": 1,
    "printer_id": 4,
    "codigo_usuario": "9967",
    "nombre_usuario": "SANDRA GARCIA",
    "total_paginas": 16647,
    "total_bn": 16647,
    "total_color": 0,
    "copiadora_bn": 0,
    "copiadora_mono_color": 0,
    "copiadora_dos_colores": 0,
    "copiadora_todo_color": 0,
    "impresora_bn": 16647,
    "impresora_mono_color": 0,
    "impresora_dos_colores": 0,
    "impresora_color": 0,
    "escaner_bn": 0,
    "escaner_todo_color": 0,
    "fax_bn": 0,
    "fax_paginas_transmitidas": 0,
    "revelado_negro": 0,
    "revelado_color_ymc": 0,
    "eco_uso_2_caras": null,
    "eco_uso_combinar": null,
    "eco_reduccion_papel": null,
    "tipo_contador": "usuario",
    "fecha_lectura": "2026-03-02T10:41:15.537568Z",
    "created_at": "2026-03-02T10:41:15.537568Z"
  }
]
```

**Ejemplo curl:**
```bash
curl http://localhost:8000/api/counters/users/4
```

---

### 4. Obtener Histórico de Contadores por Usuario

Obtiene el histórico de contadores por usuario con filtros opcionales.

**Endpoint:** `GET /api/counters/users/{printer_id}/history`

**Parámetros:**
- `printer_id` (path, requerido): ID de la impresora
- `codigo_usuario` (query, opcional): Código de usuario específico
- `start_date` (query, opcional): Fecha inicial (ISO 8601)
- `end_date` (query, opcional): Fecha final (ISO 8601)
- `limit` (query, opcional): Límite de registros (default: 100, max: 1000)

**Ejemplo curl:**
```bash
# Histórico de un usuario específico
curl "http://localhost:8000/api/counters/users/4/history?codigo_usuario=9967&limit=10"

# Todos los usuarios en un rango de fechas
curl "http://localhost:8000/api/counters/users/4/history?start_date=2026-03-01T00:00:00Z&limit=500"
```

---

### 5. Ejecutar Lectura Manual de Contadores

Ejecuta una lectura manual de contadores de una impresora (total + usuarios).

**Endpoint:** `POST /api/counters/read/{printer_id}`

**Parámetros:**
- `printer_id` (path, requerido): ID de la impresora

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "printer_id": 4,
  "contador_total": {
    "id": 8,
    "printer_id": 4,
    "total": 372600,
    ...
  },
  "usuarios_count": 265,
  "error": null
}
```

**Errores:**
- `404`: Impresora no encontrada
- `500`: Error al leer contadores (impresora no accesible, timeout, etc.)

**Ejemplo curl:**
```bash
curl -X POST http://localhost:8000/api/counters/read/4
```

---

### 6. Ejecutar Lectura de Todas las Impresoras

Ejecuta lectura de contadores de TODAS las impresoras registradas.

**Endpoint:** `POST /api/counters/read-all`

**Nota:** Esta operación puede tomar varios minutos dependiendo del número de impresoras.

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "total_printers": 5,
  "successful": 5,
  "failed": 0,
  "results": [
    {
      "success": true,
      "printer_id": 3,
      "contador_total": { ... },
      "usuarios_count": 232,
      "error": null
    },
    {
      "success": true,
      "printer_id": 4,
      "contador_total": { ... },
      "usuarios_count": 265,
      "error": null
    }
  ]
}
```

**Ejemplo curl:**
```bash
curl -X POST http://localhost:8000/api/counters/read-all
```

---

### 7. Realizar Cierre Mensual

Realiza un cierre mensual de contadores para una impresora.

**Endpoint:** `POST /api/counters/close-month`

**Body (JSON):**
```json
{
  "printer_id": 4,
  "anio": 2026,
  "mes": 3,
  "cerrado_por": "admin",
  "notas": "Cierre mensual de marzo 2026"
}
```

**Parámetros:**
- `printer_id` (requerido): ID de la impresora
- `anio` (requerido): Año del cierre (2020-2100)
- `mes` (requerido): Mes del cierre (1-12)
- `cerrado_por` (opcional): Usuario que realiza el cierre
- `notas` (opcional): Notas adicionales

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "printer_id": 4,
  "anio": 2026,
  "mes": 3,
  "total_paginas": 372600,
  "total_copiadora": 59200,
  "total_impresora": 313100,
  "total_escaner": 170300,
  "total_fax": 0,
  "diferencia_total": 5000,
  "diferencia_copiadora": 500,
  "diferencia_impresora": 4200,
  "diferencia_escaner": 300,
  "diferencia_fax": 0,
  "fecha_cierre": "2026-03-02T15:30:00Z",
  "cerrado_por": "admin",
  "notas": "Cierre mensual de marzo 2026",
  "created_at": "2026-03-02T15:30:00Z"
}
```

**Errores:**
- `400`: Ya existe un cierre para ese mes o no hay contadores registrados
- `404`: Impresora no encontrada

**Ejemplo curl:**
```bash
curl -X POST http://localhost:8000/api/counters/close-month \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": 4,
    "anio": 2026,
    "mes": 3,
    "cerrado_por": "admin",
    "notas": "Cierre mensual de marzo 2026"
  }'
```

---

### 8. Obtener Cierres Mensuales

Obtiene los cierres mensuales de una impresora, opcionalmente filtrados por año.

**Endpoint:** `GET /api/counters/monthly/{printer_id}`

**Parámetros:**
- `printer_id` (path, requerido): ID de la impresora
- `year` (query, opcional): Año (2020-2100)

**Respuesta exitosa (200):**
```json
[
  {
    "id": 1,
    "printer_id": 4,
    "anio": 2026,
    "mes": 2,
    "total_paginas": 367600,
    "total_copiadora": 58700,
    "total_impresora": 308900,
    "total_escaner": 170000,
    "total_fax": 0,
    "diferencia_total": 4800,
    "diferencia_copiadora": 450,
    "diferencia_impresora": 4100,
    "diferencia_escaner": 250,
    "diferencia_fax": 0,
    "fecha_cierre": "2026-02-28T23:59:00Z",
    "cerrado_por": "admin",
    "notas": null,
    "created_at": "2026-02-28T23:59:00Z"
  }
]
```

**Ejemplo curl:**
```bash
# Todos los cierres
curl http://localhost:8000/api/counters/monthly/4

# Solo cierres de 2026
curl "http://localhost:8000/api/counters/monthly/4?year=2026"
```

---

### 9. Obtener Cierre Mensual Específico

Obtiene un cierre mensual específico por año y mes.

**Endpoint:** `GET /api/counters/monthly/{printer_id}/{year}/{month}`

**Parámetros:**
- `printer_id` (path, requerido): ID de la impresora
- `year` (path, requerido): Año
- `month` (path, requerido): Mes (1-12)

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "printer_id": 4,
  "anio": 2026,
  "mes": 3,
  "total_paginas": 372600,
  ...
}
```

**Errores:**
- `404`: Impresora no encontrada o cierre no existe

**Ejemplo curl:**
```bash
curl http://localhost:8000/api/counters/monthly/4/2026/3
```

---

## Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `400 Bad Request`: Datos de entrada inválidos
- `404 Not Found`: Recurso no encontrado
- `422 Unprocessable Entity`: Error de validación
- `500 Internal Server Error`: Error del servidor

## Notas Importantes

### Tipos de Contadores

El sistema soporta dos tipos de contadores por usuario:

1. **Contador Usuario** (`tipo_contador: "usuario"`): Contador estándar con desglose completo por función
2. **Contador Ecológico** (`tipo_contador: "ecologico"`): Contador alternativo para impresoras B/N, incluye métricas ecológicas

### Validaciones de Integridad

El servicio incluye validaciones exhaustivas:
- Verificación de tipos de datos
- Validación de campos requeridos
- Consistencia de totales vs suma de parciales
- Transacciones con rollback automático en caso de error

### Rendimiento

- La lectura de una impresora individual toma ~5-10 segundos
- La lectura de todas las impresoras puede tomar varios minutos
- Se recomienda usar endpoints individuales para operaciones en tiempo real
- Usar `read-all` solo para sincronizaciones programadas

## Documentación Interactiva

FastAPI genera documentación interactiva automáticamente:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Estas interfaces permiten probar los endpoints directamente desde el navegador.
