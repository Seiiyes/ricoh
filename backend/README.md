# Ricoh Multi-Fleet Governance Suite - Backend

Backend API en Python con FastAPI para descubrimiento y gestión de impresoras Ricoh en red.

## Características

- **Escaneo de Red**: Detecta impresoras Ricoh en rangos de IP especificados
- **Registro de Dispositivos**: Permite asignar nombres personalizados a las impresoras
- **Modo Demo**: Incluye 3 impresoras ficticias para pruebas sin hardware físico
- **API Asíncrona**: Escaneo concurrente de múltiples IPs sin bloqueo
- **Persistencia**: Almacena el registro de flota en `fleet.json`
- **CORS Configurado**: Listo para integrarse con el frontend React

## Requisitos

- Python 3.8+
- pip

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Configuración

Copia el archivo de ejemplo y ajusta según necesites:

```bash
cp .env.example .env
```

Variables disponibles:
- `DEMO_MODE`: `true` para usar dispositivos demo, `false` para escaneo real
- `API_HOST`: Host del servidor (default: 0.0.0.0)
- `API_PORT`: Puerto del servidor (default: 8000)

## Ejecución

### Modo Desarrollo

```bash
cd backend
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Modo Producción

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

El servidor estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

## Endpoints

### GET /
Health check del servicio

### GET /scan
Escanea la red en busca de impresoras Ricoh

**Query Parameters:**
- `ip_range` (string): Rango de IPs en notación CIDR (ej: `192.168.1.0/24`)

**Response:**
```json
{
  "devices": [
    {
      "ip": "192.168.1.100",
      "hostname": "RICOH-MP-C3004",
      "status": "online",
      "detected_model": "RICOH MP C3004",
      "capabilities": {"color": true, "scanner": true},
      "toner_levels": {"cyan": 75, "magenta": 60, "yellow": 85, "black": 90}
    }
  ],
  "total_scanned": 254,
  "total_found": 3,
  "scan_duration_seconds": 2.45
}
```

### POST /register
Registra una impresora con un nombre asignado

**Request Body:**
```json
{
  "ip": "192.168.1.100",
  "assigned_name": "Impresora Oficina Principal"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Printer 'Impresora Oficina Principal' registered successfully",
  "device": { /* device info */ }
}
```

### GET /fleet
Obtiene todas las impresoras registradas

**Response:**
```json
[
  {
    "ip": "192.168.1.100",
    "hostname": "Impresora Oficina Principal",
    "status": "online",
    "detected_model": "RICOH MP C3004",
    "capabilities": {"color": true, "scanner": true},
    "toner_levels": {"cyan": 75, "magenta": 60, "yellow": 85, "black": 90}
  }
]
```

### DELETE /fleet/{ip}
Elimina una impresora del registro

**Response:**
```json
{
  "success": true,
  "message": "Printer 'Impresora Oficina Principal' removed from fleet"
}
```

## Modo Demo

Por defecto, el backend funciona en modo DEMO con 3 impresoras ficticias:

1. **RICOH-MP-C3004** (192.168.1.100) - Color, Scanner
2. **RICOH-SP-4510DN** (192.168.1.101) - Monocromática
3. **RICOH-IM-C2500** (192.168.1.102) - Color, Scanner

Para desactivar el modo demo y usar escaneo real:
```bash
export DEMO_MODE=false
```

## Arquitectura

```
backend/
├── main.py           # FastAPI app y endpoints
├── models.py         # Pydantic schemas
├── scanner.py        # Lógica de escaneo de red
├── requirements.txt  # Dependencias
├── fleet.json        # Registro persistente (generado)
└── README.md
```

## Integración con Frontend

El backend está configurado para aceptar peticiones desde:
- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:5173`

Actualiza el frontend para apuntar a `http://localhost:8000`

## Notas Técnicas

- **Escaneo Asíncrono**: Usa `asyncio` para escanear múltiples IPs concurrentemente
- **Timeout**: Cada conexión tiene timeout de 0.5-1 segundo
- **Puertos Verificados**: 80 (HTTP), 443 (HTTPS), 161 (SNMP)
- **Límite de Subnet**: Máximo 256 direcciones (/24) para evitar escaneos largos
- **Validación**: Pydantic valida todos los inputs automáticamente

## Próximos Pasos

- [ ] Implementar consultas SNMP reales para obtener modelo exacto
- [ ] Agregar autenticación JWT
- [ ] Conectar a base de datos (PostgreSQL/MongoDB)
- [ ] Implementar WebSockets para escaneos en tiempo real
- [ ] Agregar caché de dispositivos descubiertos
- [ ] Implementar health checks periódicos de dispositivos registrados
