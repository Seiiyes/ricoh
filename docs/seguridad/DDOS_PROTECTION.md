# Protección contra Ataques DDoS

## Descripción General

El sistema implementa protección multicapa contra ataques de denegación de servicio distribuido (DDoS) para garantizar la disponibilidad y estabilidad de la API.

## Capas de Protección

### 1. Rate Limiting Global por IP

**Límite**: 100 requests por minuto por IP

Cada dirección IP tiene un límite global de requests que puede realizar en una ventana de tiempo. Esto previene que un solo cliente abuse del sistema.

```
Límite: 100 requests / 60 segundos
```

### 2. Rate Limiting por Endpoint

Endpoints críticos tienen límites específicos más restrictivos:

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| `/auth/login` | 5 requests | 60 segundos |
| `/auth/refresh` | 10 requests | 60 segundos |
| `/discovery/scan` | 2 requests | 300 segundos (5 min) |
| `/discovery/sync-users-from-printers` | 3 requests | 300 segundos (5 min) |

### 3. Detección de Burst Attacks

**Threshold**: 30 requests en 10 segundos

El sistema detecta ráfagas anormales de requests (burst attacks) y bloquea automáticamente la IP origen.

```python
BURST_THRESHOLD = 30  # requests
BURST_WINDOW = 10     # segundos
```

### 4. Bloqueo Temporal de IPs

Cuando se detecta actividad sospechosa, la IP se bloquea temporalmente:

- **Duración del bloqueo**: 15 minutos (900 segundos)
- **Causas de bloqueo**:
  - Burst attack detectado
  - Múltiples violaciones de rate limit
  - Bloqueo manual por administrador

### 5. Validación de Tamaño de Payload

**Límite**: 10 MB por request

Previene ataques de agotamiento de recursos mediante payloads excesivamente grandes.

```python
MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
```

### 6. Whitelist de IPs

IPs en whitelist no están sujetas a rate limiting:

- `127.0.0.1` (localhost)
- `::1` (localhost IPv6)
- Redes privadas: `192.168.x.x`, `10.x.x.x`, `172.x.x.x`

## Headers de Rate Limit

Todas las respuestas incluyen headers informativos:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

Cuando se excede el límite:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890

{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Try again in 45 seconds.",
  "reset_at": "2026-03-20T16:30:00Z"
}
```

## API de Administración

### Obtener Estadísticas

```bash
GET /admin/ddos/stats
Authorization: Bearer <superadmin_token>
```

**Respuesta**:
```json
{
  "blocked_ips": {
    "192.168.1.100": "2026-03-20T16:45:00Z"
  },
  "blocked_count": 1,
  "config": {
    "global_rate_limit": 100,
    "global_rate_window": 60,
    "burst_threshold": 30,
    "burst_window": 10,
    "block_duration": 900,
    "max_payload_size": 10485760
  }
}
```

### Desbloquear IP

```bash
POST /admin/ddos/unblock-ip
Authorization: Bearer <superadmin_token>
Content-Type: application/json

{
  "ip": "192.168.1.100"
}
```

### Bloquear IP Manualmente

```bash
POST /admin/ddos/block-ip
Authorization: Bearer <superadmin_token>
Content-Type: application/json

{
  "ip": "192.168.1.100",
  "duration_seconds": 1800
}
```

### Obtener IPs Bloqueadas

```bash
GET /admin/ddos/blocked-ips
Authorization: Bearer <superadmin_token>
```

### Limpiar Datos Antiguos

```bash
POST /admin/ddos/cleanup
Authorization: Bearer <superadmin_token>
```

### Obtener Configuración

```bash
GET /admin/ddos/config
Authorization: Bearer <token>
```

## Respuestas de Error

### 429 Too Many Requests

```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Try again in 45 seconds.",
  "reset_at": "2026-03-20T16:30:00Z"
}
```

### 403 Forbidden (IP Bloqueada)

```json
{
  "error": "IP_BLOCKED",
  "message": "Your IP has been temporarily blocked due to suspicious activity",
  "blocked_ips": {
    "192.168.1.100": "2026-03-20T16:45:00Z"
  }
}
```

### 413 Payload Too Large

```json
{
  "error": "PAYLOAD_TOO_LARGE",
  "message": "Request payload exceeds maximum size of 10485760 bytes"
}
```

## Configuración

### Variables de Entorno

Puedes ajustar los límites mediante variables de entorno (opcional):

```bash
# Rate limiting global
DDOS_GLOBAL_RATE_LIMIT=100
DDOS_GLOBAL_RATE_WINDOW=60

# Detección de burst
DDOS_BURST_THRESHOLD=30
DDOS_BURST_WINDOW=10

# Bloqueo temporal
DDOS_BLOCK_DURATION=900

# Tamaño máximo de payload
DDOS_MAX_PAYLOAD_SIZE=10485760
```

### Personalizar Límites por Endpoint

Edita `backend/middleware/ddos_protection.py`:

```python
ENDPOINT_LIMITS = {
    "/auth/login": (5, 60),
    "/auth/refresh": (10, 60),
    "/tu-endpoint": (limite, ventana_segundos),
}
```

### Agregar IPs a Whitelist

```python
WHITELIST_IPS = [
    "127.0.0.1",
    "::1",
    "tu.ip.especial",
]
```

## Monitoreo y Logs

El sistema registra eventos de seguridad:

```
⚠️ Burst attack detectado: 192.168.1.100 - 35 requests en 10s
🚫 IP bloqueada: 192.168.1.100 hasta 2026-03-20T16:45:00Z
✅ IP desbloqueada: 192.168.1.100
⚠️ Rate limit global excedido: 192.168.1.100
⚠️ Rate limit de endpoint excedido: 192.168.1.100 - /auth/login
⚠️ Payload demasiado grande de 192.168.1.100: 15000000 bytes
```

## Mejores Prácticas

### Para Clientes de la API

1. **Respetar los límites**: Verifica los headers `X-RateLimit-*`
2. **Implementar backoff exponencial**: Espera más tiempo entre reintentos
3. **Cachear respuestas**: Reduce requests innecesarios
4. **Usar tokens de autenticación**: Evita múltiples logins

### Para Administradores

1. **Monitorear logs**: Revisa regularmente los eventos de seguridad
2. **Ajustar límites**: Según el tráfico real de tu aplicación
3. **Whitelist IPs confiables**: Oficinas, servidores internos
4. **Ejecutar cleanup periódicamente**: Libera memoria de datos antiguos

## Limitaciones

### Almacenamiento en Memoria

El sistema actual usa almacenamiento en memoria (RAM). Esto significa:

- ✅ Muy rápido y eficiente
- ❌ Los datos se pierden al reiniciar el servidor
- ❌ No funciona en clusters multi-servidor

### Soluciones para Producción

Para entornos de producción con múltiples servidores, considera:

1. **Redis**: Almacenamiento compartido entre servidores
2. **Nginx/HAProxy**: Rate limiting a nivel de proxy reverso
3. **Cloudflare**: Protección DDoS en la capa de CDN
4. **AWS WAF**: Web Application Firewall con reglas DDoS

## Testing

### Probar Rate Limiting

```bash
# Hacer múltiples requests rápidos
for i in {1..10}; do
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}'
done
```

### Probar Burst Detection

```bash
# Script para generar burst
for i in {1..35}; do
  curl http://localhost:8000/ &
done
wait
```

### Verificar Bloqueo

```bash
# Después de burst, debería retornar 403
curl http://localhost:8000/
```

## Seguridad Adicional

La protección DDoS se complementa con:

1. **HTTPS/TLS**: Encriptación de tráfico
2. **JWT Authentication**: Tokens seguros
3. **CORS**: Control de orígenes permitidos
4. **Security Headers**: HSTS, X-Frame-Options, etc.
5. **Input Validation**: Validación de datos de entrada
6. **SQL Injection Protection**: ORM con queries parametrizadas

## Soporte

Para reportar problemas o sugerencias sobre la protección DDoS:

1. Revisa los logs del servidor
2. Verifica las estadísticas en `/admin/ddos/stats`
3. Contacta al equipo de desarrollo con detalles del incidente
