# API Reference - Sistema de Cierres

Referencia rápida de todos los endpoints del sistema unificado de cierres.

---

## Base URL
```
http://localhost:8000/api/counters
```

---

## 📝 Crear Cierres

### POST `/close`
Crea un cierre de cualquier tipo (diario, semanal, mensual, personalizado).

**Request Body:**
```json
{
  "printer_id": 4,
  "tipo_periodo": "diario",
  "fecha_inicio": "2026-03-03",
  "fecha_fin": "2026-03-03",
  "cerrado_por": "admin",
  "notas": "Cierre diario de prueba"
}
```

**Tipos válidos:** `diario`, `semanal`, `mensual`, `personalizado`

**Response:** `CierreMensualResponse`

**Errores:**
- `400` - Validación fallida (duplicado, fechas inválidas, etc.)
- `404` - Impresora no encontrada
- `500` - Error interno

---

### POST `/close-month`
Crea un cierre mensual (mantiene compatibilidad).

**Request Body:**
```json
{
  "printer_id": 4,
  "anio": 2026,
  "mes": 3,
  "cerrado_por": "admin",
  "notas": "Cierre mensual de marzo"
}
```

**Response:** `CierreMensualResponse`

---

## 📋 Listar Cierres

### GET `/closes/{printer_id}`
Lista cierres con filtros opcionales.

**Query Parameters:**
- `tipo_periodo` (opcional): `diario`, `semanal`, `mensual`, `personalizado`
- `year` (opcional): Año (2020-2100)
- `month` (opcional): Mes (1-12)
- `limit` (opcional): Límite de registros (default: 100, max: 1000)

**Ejemplos:**
```
GET /closes/4                           # Todos los cierres
GET /closes/4?tipo_periodo=diario       # Solo diarios
GET /closes/4?year=2026&month=3         # Marzo 2026
GET /closes/4?tipo_periodo=mensual&year=2026  # Mensuales de 2026
```

**Response:** `CierreMensualResponse[]`

---

### GET `/monthly/{printer_id}`
Lista cierres mensuales (mantiene compatibilidad).

**Query Parameters:**
- `year` (opcional): Año

**Ejemplo:**
```
GET /monthly/4?year=2026
```

**Response:** `CierreMensualResponse[]`

---

## 🔍 Obtener Cierre Específico

### GET `/closes/{cierre_id}`
Obtiene un cierre por ID.

**Ejemplo:**
```
GET /closes/123
```

**Response:** `CierreMensualResponse`

**Errores:**
- `404` - Cierre no encontrado

---

### GET `/monthly/{printer_id}/{year}/{month}`
Obtiene un cierre mensual específico.

**Ejemplo:**
```
GET /monthly/4/2026/3
```

**Response:** `CierreMensualResponse`

**Errores:**
- `404` - Impresora o cierre no encontrado

---

## 👥 Detalle con Usuarios

### GET `/monthly/{cierre_id}/users`
Obtiene el snapshot de usuarios de un cierre.

**Ejemplo:**
```
GET /monthly/123/users
```

**Response:** `CierreMensualUsuarioResponse[]`

**Ordenamiento:** Por consumo descendente

---

### GET `/monthly/{cierre_id}/detail`
Obtiene un cierre con usuarios incluidos.

**Ejemplo:**
```
GET /monthly/123/detail
```

**Response:** `CierreMensualDetalleResponse`

---

## 📊 Comparar Cierres

### GET `/closes/{cierre_id1}/compare/{cierre_id2}`
Compara dos cierres y muestra diferencias.

**Query Parameters:**
- `top_usuarios` (opcional): Cantidad de usuarios en tops (default: 10, max: 100)

**Ejemplo:**
```
GET /closes/123/compare/124?top_usuarios=5
```

**Response:** `ComparacionCierresResponse`

**Incluye:**
- Diferencias de totales (páginas, copiadora, impresora, escáner, fax)
- Días entre cierres
- Top usuarios con mayor aumento
- Top usuarios con mayor disminución
- Estadísticas (usuarios activos, promedio)

**Errores:**
- `400` - Cierres de diferentes impresoras
- `404` - Cierre no encontrado

---

## 🗑️ Eliminar Cierre

### DELETE `/closes/{cierre_id}`
Elimina un cierre y sus usuarios asociados.

**Query Parameters:**
- `force` (opcional): Forzar eliminación sin validaciones (default: false)

**Ejemplo:**
```
DELETE /closes/123
DELETE /closes/123?force=true
```

**Response:**
```json
{
  "success": true,
  "message": "Cierre 123 eliminado exitosamente",
  "cierre": {
    "id": 123,
    "printer_id": 4,
    "tipo_periodo": "diario",
    "fecha_inicio": "2026-03-03",
    "fecha_fin": "2026-03-03",
    "usuarios_eliminados": 266
  }
}
```

**Validaciones (si force=false):**
- No se puede eliminar si hay cierres posteriores del mismo tipo

**Errores:**
- `400` - Validación fallida (hay cierres posteriores)
- `404` - Cierre no encontrado
- `500` - Error al eliminar

---

## 📦 Schemas

### CierreMensualResponse
```typescript
{
  id: number
  printer_id: number
  tipo_periodo: string  // diario, semanal, mensual, personalizado
  fecha_inicio: string  // ISO date
  fecha_fin: string     // ISO date
  anio: number
  mes: number
  total_paginas: number
  total_copiadora: number
  total_impresora: number
  total_escaner: number
  total_fax: number
  diferencia_total: number
  diferencia_copiadora: number
  diferencia_impresora: number
  diferencia_escaner: number
  diferencia_fax: number
  fecha_cierre: string  // ISO datetime
  cerrado_por: string | null
  notas: string | null
  hash_verificacion: string | null
  created_at: string    // ISO datetime
}
```

### CierreMensualUsuarioResponse
```typescript
{
  id: number
  cierre_mensual_id: number
  codigo_usuario: string
  nombre_usuario: string
  total_paginas: number
  total_bn: number
  total_color: number
  copiadora_bn: number
  copiadora_color: number
  impresora_bn: number
  impresora_color: number
  escaner_bn: number
  escaner_color: number
  fax_bn: number
  consumo_total: number
  consumo_copiadora: number
  consumo_impresora: number
  consumo_escaner: number
  consumo_fax: number
  created_at: string    // ISO datetime
}
```

### ComparacionCierresResponse
```typescript
{
  cierre1: CierreMensualResponse
  cierre2: CierreMensualResponse
  diferencia_total: number
  diferencia_copiadora: number
  diferencia_impresora: number
  diferencia_escaner: number
  diferencia_fax: number
  dias_entre_cierres: number
  top_usuarios_aumento: UsuarioComparacion[]
  top_usuarios_disminucion: UsuarioComparacion[]
  total_usuarios_activos: number
  promedio_consumo_por_usuario: number
}
```

### UsuarioComparacion
```typescript
{
  codigo_usuario: string
  nombre_usuario: string
  consumo_cierre1: number
  consumo_cierre2: number
  diferencia: number
  porcentaje_cambio: number
}
```

---

## 🧪 Ejemplos de Uso

### Crear cierre diario
```bash
curl -X POST http://localhost:8000/api/counters/close \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": 4,
    "tipo_periodo": "diario",
    "fecha_inicio": "2026-03-03",
    "fecha_fin": "2026-03-03",
    "cerrado_por": "admin"
  }'
```

### Listar cierres diarios de marzo 2026
```bash
curl "http://localhost:8000/api/counters/closes/4?tipo_periodo=diario&year=2026&month=3"
```

### Comparar dos cierres
```bash
curl "http://localhost:8000/api/counters/closes/123/compare/124?top_usuarios=10"
```

### Eliminar cierre
```bash
curl -X DELETE "http://localhost:8000/api/counters/closes/123"
```

---

## 🔒 Validaciones

### Crear Cierre
- ✅ Tipo de período válido
- ✅ Fechas coherentes (fin >= inicio)
- ✅ Período no mayor a 1 año
- ✅ Impresora existe
- ✅ No duplicados del mismo tipo y período
- ✅ Período no futuro
- ✅ Mes completo para cierres mensuales
- ✅ No cerrar mes actual
- ✅ Contador reciente (máximo 7 días)
- ✅ Secuencia de cierres mensuales sin gaps
- ✅ Detección de reset de contador

### Comparar Cierres
- ✅ Ambos cierres existen
- ✅ Misma impresora

### Eliminar Cierre
- ✅ Cierre existe
- ✅ No hay cierres posteriores del mismo tipo (si force=false)

---

## 📚 Documentación Adicional

- [Backend Completo](./BACKEND_SISTEMA_UNIFICADO_COMPLETO.md)
- [Arquitectura de Cierres](./ARQUITECTURA_CIERRES_ANALISIS_COMPLETO.md)
- [Guía de Uso](./GUIA_DE_USO.md)

---

**Última actualización:** 4 de marzo de 2026
