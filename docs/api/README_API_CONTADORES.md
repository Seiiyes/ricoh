# API de Contadores - Guía Rápida

## 🚀 Inicio Rápido

### 1. Iniciar el Servidor

```bash
# Opción 1: Script batch (Windows)
start-api-server.bat

# Opción 2: Comando directo
cd backend
venv\Scripts\python.exe main.py
```

El servidor estará disponible en: http://localhost:8000

### 2. Verificar que Funciona

Abre en tu navegador:
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

### 3. Probar los Endpoints

```bash
# Opción 1: Script de prueba automático
test-api-endpoints.bat

# Opción 2: Pruebas manuales con curl
curl http://localhost:8000/api/counters/printer/4
curl http://localhost:8000/api/counters/users/4
curl -X POST http://localhost:8000/api/counters/read/4
```

---

## 📋 Endpoints Disponibles

### Contadores Totales

```bash
# Obtener último contador
GET /api/counters/printer/{printer_id}

# Obtener histórico
GET /api/counters/printer/{printer_id}/history?limit=50
```

### Contadores por Usuario

```bash
# Obtener últimos contadores
GET /api/counters/users/{printer_id}

# Obtener histórico de un usuario
GET /api/counters/users/{printer_id}/history?codigo_usuario=9967
```

### Lectura Manual

```bash
# Leer una impresora
POST /api/counters/read/{printer_id}

# Leer todas las impresoras
POST /api/counters/read-all
```

### Cierres Mensuales

```bash
# Realizar cierre mensual
POST /api/counters/close-month
Body: {"printer_id": 4, "anio": 2026, "mes": 3}

# Obtener cierres
GET /api/counters/monthly/{printer_id}
GET /api/counters/monthly/{printer_id}/2026/3
```

---

## 📖 Documentación Completa

Ver: `docs/API_CONTADORES.md`

---

## 🧪 Scripts de Prueba

| Script | Descripción |
|--------|-------------|
| `start-api-server.bat` | Inicia el servidor API |
| `test-api-endpoints.bat` | Prueba todos los endpoints |
| `test_api_endpoints.py` | Script Python de pruebas |

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Obtener Último Contador

```bash
curl http://localhost:8000/api/counters/printer/4
```

Respuesta:
```json
{
  "id": 7,
  "printer_id": 4,
  "total": 372573,
  "copiadora_bn": 59142,
  "impresora_bn": 313065,
  "fecha_lectura": "2026-03-02T10:41:15.537568Z"
}
```

### Ejemplo 2: Obtener Top Usuarios

```bash
curl http://localhost:8000/api/counters/users/4
```

Respuesta:
```json
[
  {
    "codigo_usuario": "9967",
    "nombre_usuario": "SANDRA GARCIA",
    "total_paginas": 16647,
    "tipo_contador": "usuario"
  }
]
```

### Ejemplo 3: Ejecutar Lectura Manual

```bash
curl -X POST http://localhost:8000/api/counters/read/4
```

Respuesta:
```json
{
  "success": true,
  "printer_id": 4,
  "contador_total": { ... },
  "usuarios_count": 265,
  "error": null
}
```

---

## 🔧 Configuración

### Variables de Entorno

Archivo: `backend/.env`

```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/ricoh

# API
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

---

## 📊 Estado del Proyecto

✅ **Fase 1**: Parsers implementados  
✅ **Fase 2**: Modelos de base de datos  
✅ **Fase 3**: Servicio de lectura  
✅ **Fase 4**: API REST (9 endpoints)  
⏳ **Fase 5**: Frontend (pendiente)  
⏳ **Fase 6**: Automatización (pendiente)

---

## 🐛 Troubleshooting

### El servidor no inicia

```bash
# Verificar que el entorno virtual esté activado
cd backend
call venv\Scripts\activate.bat

# Verificar dependencias
pip install -r requirements.txt

# Verificar base de datos
python -c "from db.database import engine; print('DB OK')"
```

### Error de conexión a la base de datos

1. Verificar que PostgreSQL esté corriendo
2. Verificar credenciales en `.env`
3. Verificar que la base de datos `ricoh` exista

### Los endpoints retornan 404

1. Verificar que el servidor esté corriendo
2. Verificar la URL: http://localhost:8000
3. Verificar que la impresora exista en la base de datos

---

## 📞 Soporte

Para más información:
- **Documentación completa**: `docs/API_CONTADORES.md`
- **Fase 4 completada**: `docs/FASE_4_COMPLETADA.md`
- **Índice de documentación**: `docs/INDICE_DOCUMENTACION.md`
