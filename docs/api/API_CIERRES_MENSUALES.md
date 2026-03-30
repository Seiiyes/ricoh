# API de Cierres Mensuales

Documentación completa de los endpoints para gestión de cierres mensuales con snapshot de usuarios.

## 📋 Índice

1. [Crear Cierre Mensual](#crear-cierre-mensual)
2. [Listar Cierres](#listar-cierres)
3. [Obtener Cierre Específico](#obtener-cierre-específico)
4. [Obtener Usuarios de un Cierre](#obtener-usuarios-de-un-cierre)
5. [Obtener Cierre con Detalle Completo](#obtener-cierre-con-detalle-completo)
6. [Validaciones y Reglas de Negocio](#validaciones-y-reglas-de-negocio)

---

## Crear Cierre Mensual

Crea un cierre mensual con snapshot inmutable de usuarios.

### Endpoint

```http
POST /api/counters/monthly
```

### Request Body

```json
{
  "printer_id": 1,
  "anio": 2026,
  "mes": 2,
  "cerrado_por": "admin",
  "notas": "Cierre mensual de febrero"
}
```

### Parámetros

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `printer_id` | integer | Sí | ID de la impresora (> 0) |
| `anio` | integer | Sí | Año del cierre (2020-2100) |
| `mes` | integer | Sí | Mes del cierre (1-12) |
| `cerrado_por` | string | No | Usuario que realiza el cierre (max 100 chars) |
| `notas` | string | No | Notas adicionales (max 1000 chars) |

### Response (200 OK)

```json
{
  "id": 15,
  "printer_id": 1,
  "anio": 2026,
  "mes": 2,
  "total_paginas": 125430,
  "total_copiadora": 45230,
  "total_impresora": 78200,
  "total_escaner": 2000,
  "total_fax": 0,
  "diferencia_total": 8450,
  "diferencia_copiadora": 3200,
  "diferencia_impresora": 5100,
  "diferencia_escaner": 150,
  "diferencia_fax": 0,
  "fecha_cierre": "2026-03-01T10:30:00",
  "cerrado_por": "admin",
  "notas": "Cierre mensual de febrero",
  "created_at": "2026-03-01T10:30:00"
}
```

### Errores Comunes

#### 400 Bad Request - Cierre Duplicado

```json
{
  "detail": "Ya existe un cierre para 2026-02. Cerrado por: admin Fecha: 2026-03-01 10:30"
}
```

#### 400 Bad Request - Mes Futuro

```json
{
  "detail": "No se puede cerrar un mes futuro"
}
```

#### 400 Bad Request - Mes Muy Antiguo

```json
{
  "detail": "No se puede cerrar un mes con más de 2 meses de antigüedad. Contacte al administrador si necesita cerrar 2025-11."
}
```

#### 400 Bad Request - Contador Antiguo

```json
{
  "detail": "El último contador tiene 10 días de antigüedad. Ejecute una lectura manual antes de cerrar el mes."
}
```

#### 400 Bad Request - Falta Cierre Anterior

```json
{
  "detail": "Debe cerrar 2026-01 antes de cerrar 2026-02"
}
```

#### 400 Bad Request - Reset de Contador Detectado

```json
{
  "detail": "⚠️  RESET DE CONTADOR DETECTADO\nContador anterior: 125,430\nContador actual: 1,250\nDiferencia: -124,180\n\nACCIÓN REQUERIDA:\n1. Verificar si hubo mantenimiento en la impresora\n2. Contactar al técnico para confirmar reset\n3. Ajustar manualmente el cierre\n4. Documentar el incidente en 'notas'"
}
```

---

## Listar Cierres

Obtiene todos los cierres mensuales de una impresora.

### Endpoint

```http
GET /api/counters/monthly?printer_id={printer_id}&year={year}
```

### Parámetros Query

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `printer_id` | integer | Sí | ID de la impresora |
| `year` | integer | No | Filtrar por año específico |

### Response (200 OK)

```json
[
  {
    "id": 15,
    "printer_id": 1,
    "anio": 2026,
    "mes": 2,
    "total_paginas": 125430,
    "total_copiadora": 45230,
    "total_impresora": 78200,
    "total_escaner": 2000,
    "total_fax": 0,
    "diferencia_total": 8450,
    "diferencia_copiadora": 3200,
    "diferencia_impresora": 5100,
    "diferencia_escaner": 150,
    "diferencia_fax": 0,
    "fecha_cierre": "2026-03-01T10:30:00",
    "cerrado_por": "admin",
    "notas": "Cierre mensual de febrero",
    "created_at": "2026-03-01T10:30:00"
  },
  {
    "id": 14,
    "printer_id": 1,
    "anio": 2026,
    "mes": 1,
    "total_paginas": 116980,
    "total_copiadora": 42030,
    "total_impresora": 73100,
    "total_escaner": 1850,
    "total_fax": 0,
    "diferencia_total": 7200,
    "diferencia_copiadora": 2800,
    "diferencia_impresora": 4300,
    "diferencia_escaner": 100,
    "diferencia_fax": 0,
    "fecha_cierre": "2026-02-01T09:15:00",
    "cerrado_por": "admin",
    "notas": null,
    "created_at": "2026-02-01T09:15:00"
  }
]
```

---

## Obtener Cierre Específico

Obtiene un cierre mensual específico por impresora, año y mes.

### Endpoint

```http
GET /api/counters/monthly/{printer_id}/{year}/{month}
```

### Parámetros Path

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `printer_id` | integer | ID de la impresora |
| `year` | integer | Año del cierre |
| `month` | integer | Mes del cierre (1-12) |

### Response (200 OK)

```json
{
  "id": 15,
  "printer_id": 1,
  "anio": 2026,
  "mes": 2,
  "total_paginas": 125430,
  "total_copiadora": 45230,
  "total_impresora": 78200,
  "total_escaner": 2000,
  "total_fax": 0,
  "diferencia_total": 8450,
  "diferencia_copiadora": 3200,
  "diferencia_impresora": 5100,
  "diferencia_escaner": 150,
  "diferencia_fax": 0,
  "fecha_cierre": "2026-03-01T10:30:00",
  "cerrado_por": "admin",
  "notas": "Cierre mensual de febrero",
  "created_at": "2026-03-01T10:30:00"
}
```

### Errores

#### 404 Not Found

```json
{
  "detail": "No se encontró cierre para 2026-02"
}
```

---

## Obtener Usuarios de un Cierre

Obtiene el snapshot de usuarios de un cierre mensual específico.

### Endpoint

```http
GET /api/counters/monthly/{cierre_id}/users
```

### Parámetros Path

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `cierre_id` | integer | ID del cierre mensual |

### Response (200 OK)

```json
[
  {
    "id": 450,
    "cierre_mensual_id": 15,
    "codigo_usuario": "00000252",
    "nombre_usuario": "Juan Pérez",
    "total_paginas": 5430,
    "total_bn": 4200,
    "total_color": 1230,
    "copiadora_bn": 2100,
    "copiadora_color": 800,
    "impresora_bn": 2100,
    "impresora_color": 430,
    "escaner_bn": 50,
    "escaner_color": 20,
    "fax_bn": 0,
    "consumo_total": 1250,
    "consumo_copiadora": 600,
    "consumo_impresora": 630,
    "consumo_escaner": 20,
    "consumo_fax": 0,
    "created_at": "2026-03-01T10:30:00"
  },
  {
    "id": 451,
    "cierre_mensual_id": 15,
    "codigo_usuario": "00000253",
    "nombre_usuario": "María García",
    "total_paginas": 3200,
    "total_bn": 2800,
    "total_color": 400,
    "copiadora_bn": 1500,
    "copiadora_color": 200,
    "impresora_bn": 1300,
    "impresora_color": 200,
    "escaner_bn": 30,
    "escaner_color": 10,
    "fax_bn": 0,
    "consumo_total": 850,
    "consumo_copiadora": 400,
    "consumo_impresora": 430,
    "consumo_escaner": 20,
    "consumo_fax": 0,
    "created_at": "2026-03-01T10:30:00"
  }
]
```

### Notas

- Los usuarios están ordenados por `consumo_total` descendente
- El snapshot es inmutable y representa el estado exacto al momento del cierre
- Incluye tanto contadores acumulados como consumo del mes

---

## Obtener Cierre con Detalle Completo

Obtiene un cierre mensual con la lista completa de usuarios incluida.

### Endpoint

```http
GET /api/counters/monthly/{cierre_id}/detail
```

### Parámetros Path

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `cierre_id` | integer | ID del cierre mensual |

### Response (200 OK)

```json
{
  "id": 15,
  "printer_id": 1,
  "anio": 2026,
  "mes": 2,
  "total_paginas": 125430,
  "total_copiadora": 45230,
  "total_impresora": 78200,
  "total_escaner": 2000,
  "total_fax": 0,
  "diferencia_total": 8450,
  "diferencia_copiadora": 3200,
  "diferencia_impresora": 5100,
  "diferencia_escaner": 150,
  "diferencia_fax": 0,
  "fecha_cierre": "2026-03-01T10:30:00",
  "cerrado_por": "admin",
  "notas": "Cierre mensual de febrero",
  "hash_verificacion": "a3f5c8d9e2b1f4a6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
  "created_at": "2026-03-01T10:30:00",
  "usuarios": [
    {
      "id": 450,
      "cierre_mensual_id": 15,
      "codigo_usuario": "00000252",
      "nombre_usuario": "Juan Pérez",
      "total_paginas": 5430,
      "total_bn": 4200,
      "total_color": 1230,
      "copiadora_bn": 2100,
      "copiadora_color": 800,
      "impresora_bn": 2100,
      "impresora_color": 430,
      "escaner_bn": 50,
      "escaner_color": 20,
      "fax_bn": 0,
      "consumo_total": 1250,
      "consumo_copiadora": 600,
      "consumo_impresora": 630,
      "consumo_escaner": 20,
      "consumo_fax": 0,
      "created_at": "2026-03-01T10:30:00"
    }
  ]
}
```

### Notas

- Este endpoint es ideal para mostrar el detalle completo de un cierre en una sola petición
- Incluye el hash SHA256 de verificación para auditoría
- Los usuarios están ordenados por consumo total descendente

---

## Validaciones y Reglas de Negocio

### 1. Validación de Impresora

- La impresora debe existir en la base de datos
- Debe tener al menos un contador registrado

### 2. Validación de No Duplicados

- No se puede crear dos cierres para el mismo mes/año de una impresora
- Si existe, se retorna error con información del cierre existente

### 3. Validación de Fecha

- No se puede cerrar un mes futuro
- No se puede cerrar un mes con más de 2 meses de antigüedad
- Esto previene errores y mantiene la integridad temporal

### 4. Validación de Contador Reciente

- El último contador debe tener máximo 7 días de antigüedad
- Si es más antiguo, se debe ejecutar una lectura manual primero
- Esto asegura que el cierre refleje el estado actual

### 5. Validación de Secuencia

- Los cierres deben ser consecutivos (excepto el primero)
- No se puede cerrar febrero si no se cerró enero
- Esto mantiene la integridad de la serie temporal

### 6. Detección de Reset de Contador

- Si el contador actual es menor que el anterior, se detecta un reset
- Se bloquea el cierre y se solicita intervención manual
- Se debe documentar el incidente en las notas

### 7. Snapshot de Usuarios

- Se guarda un snapshot inmutable de todos los usuarios
- Incluye contadores acumulados y consumo del mes
- Permite auditoría histórica sin depender de datos actuales

### 8. Validación de Integridad

- Se valida que la suma de consumos de usuarios no difiera más del 10% del total
- Si hay diferencia mayor, se agrega nota de advertencia pero no se bloquea
- Causas comunes: impresiones sin autenticación, usuarios borrados

### 9. Hash de Verificación

- Se genera un hash SHA256 con datos clave del cierre
- Permite detectar modificaciones no autorizadas
- Formato: `SHA256(printer_id + año + mes + total_paginas + count_usuarios)`

### 10. Transaccionalidad

- Todo el proceso se ejecuta en una transacción
- Si falla cualquier paso, se hace rollback completo
- Garantiza consistencia de datos

---

## Ejemplos de Uso

### Ejemplo 1: Crear Cierre Mensual

```bash
curl -X POST "http://localhost:8000/api/counters/monthly" \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": 1,
    "anio": 2026,
    "mes": 2,
    "cerrado_por": "admin",
    "notas": "Cierre mensual de febrero"
  }'
```

### Ejemplo 2: Listar Cierres de 2026

```bash
curl "http://localhost:8000/api/counters/monthly?printer_id=1&year=2026"
```

### Ejemplo 3: Obtener Usuarios de un Cierre

```bash
curl "http://localhost:8000/api/counters/monthly/15/users"
```

### Ejemplo 4: Obtener Detalle Completo

```bash
curl "http://localhost:8000/api/counters/monthly/15/detail"
```

---

## Notas Importantes

1. **Inmutabilidad**: Los cierres y sus snapshots son inmutables. No se pueden modificar después de creados.

2. **Auditoría**: Cada cierre incluye:
   - Fecha y hora exacta del cierre
   - Usuario que lo realizó
   - Hash de verificación
   - Notas opcionales

3. **Performance**: Los snapshots permiten consultas rápidas sin joins complejos.

4. **Escalabilidad**: El diseño soporta millones de registros sin degradación.

5. **Integridad**: Múltiples validaciones aseguran la consistencia de datos.

6. **Trazabilidad**: El snapshot permite auditar el estado exacto en cualquier momento histórico.
