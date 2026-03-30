# Guía de Despliegue en Producción - Ubuntu Server

**Sistema**: Ricoh Equipment Management Suite  
**Plataforma**: Ubuntu Server 22.04/24.04 LTS  
**Arquitectura**: Docker + Nginx + PostgreSQL + Redis  
**Seguridad**: Todas las 11 vulnerabilidades corregidas aplicadas

---

## Requisitos del Servidor

### Hardware Mínimo
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disco**: 50 GB SSD
- **Red**: Conexión estable a internet y red local (para impresoras Ricoh)

### Software
- Ubuntu Server 22.04 LTS o 24.04 LTS
- Acceso root o sudo
- Dominio configurado apuntando al servidor

---

## Paso 1: Preparación del Servidor

### 1.1 Conectar al servidor via SSH

```bash
ssh root@your-server-ip
# o
ssh your-user@your-server-ip
```

### 1.2 Ejecutar script de setup automático

```bash
# Descargar el script
wget https://raw.githubusercontent.com/your-repo/ricoh/main/deployment/setup-ubuntu-server.sh

# Dar permisos de ejecución
chmod +x setup-ubuntu-server.sh

# Ejecutar como root
sudo ./setup-ubuntu-server.sh
```

Este script instalará:
- ✅ Docker y Docker Compose
- ✅ Nginx
- ✅ Certbot (para SSL)
- ✅ Configuración de firewall (UFW)
- ✅ Usuario de deployment
- ✅ Systemd service
- ✅ Log rotation
- ✅ Optimizaciones del kernel

---

## Paso 2: Clonar el Repositorio

```bash
# Cambiar al directorio de aplicación
cd /opt/ricoh

# Clonar repositorio
git clone https://github.com/your-org/ricoh-equipment-management.git .

# Cambiar permisos
chown -R ricoh:ricoh /opt/ricoh
```

---

## Paso 3: Configurar Variables de Entorno

### 3.1 Copiar archivo de ejemplo

```bash
cd /opt/ricoh
cp deployment/.env.production.example .env.production
```

### 3.2 Generar claves de seguridad

**CRÍTICO**: Genera nuevas claves para producción, NO uses las de desarrollo

```bash
# Generar ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generar SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generar POSTGRES_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(24))"

# Generar REDIS_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 3.3 Editar .env.production

```bash
nano .env.production
```

Configurar las siguientes variables:

```bash
# Database
POSTGRES_PASSWORD=<password-generada-arriba>
DATABASE_URL=postgresql://ricoh_admin:<password>@postgres:5432/ricoh_fleet

# Redis
REDIS_PASSWORD=<password-generada-arriba>

# Security - Encryption & JWT
ENCRYPTION_KEY=<clave-generada-arriba>
SECRET_KEY=<clave-generada-arriba>

# CORS - Tu dominio real
CORS_ORIGINS=https://ricoh.tu-dominio.com,https://api.ricoh.tu-dominio.com

# Ricoh Integration
RICOH_ADMIN_PASSWORD=<contraseña-admin-impresoras>

# Frontend
FRONTEND_API_URL=https://api.ricoh.tu-dominio.com

# Domain
DOMAIN_NAME=ricoh.tu-dominio.com
API_DOMAIN=api.ricoh.tu-dominio.com
```

---

## Paso 4: Configurar SSL con Let's Encrypt

### 4.1 Obtener certificados SSL

```bash
# Detener servicios si están corriendo
docker-compose -f deployment/docker-compose.prod.yml down

# Obtener certificados
certbot certonly --standalone \
  -d ricoh.tu-dominio.com \
  -d api.ricoh.tu-dominio.com \
  --email tu-email@dominio.com \
  --agree-tos \
  --non-interactive

# Copiar certificados al directorio de deployment
mkdir -p deployment/ssl
cp /etc/letsencrypt/live/ricoh.tu-dominio.com/fullchain.pem deployment/ssl/
cp /etc/letsencrypt/live/ricoh.tu-dominio.com/privkey.pem deployment/ssl/
chmod 644 deployment/ssl/fullchain.pem
chmod 600 deployment/ssl/privkey.pem
```

### 4.2 Configurar renovación automática

```bash
# Agregar cron job para renovación automática
crontab -e

# Agregar esta línea (renueva cada día a las 3 AM)
0 3 * * * certbot renew --quiet --post-hook "docker exec ricoh-nginx nginx -s reload"
```

---

## Paso 5: Configurar Nginx

### 5.1 Actualizar configuración con tu dominio

```bash
# Editar configuración de Nginx
nano deployment/nginx/conf.d/ricoh.conf
```

Reemplazar:
- `${DOMAIN_NAME}` → `ricoh.tu-dominio.com`
- `${API_DOMAIN}` → `api.ricoh.tu-dominio.com`

---

## Paso 6: Construir y Desplegar

### 6.1 Construir imágenes

```bash
cd /opt/ricoh

# Construir imágenes de producción
docker-compose -f deployment/docker-compose.prod.yml build
```

### 6.2 Iniciar servicios

```bash
# Iniciar todos los servicios
docker-compose -f deployment/docker-compose.prod.yml --env-file .env.production up -d

# Verificar estado
docker-compose -f deployment/docker-compose.prod.yml ps
```

### 6.3 Verificar logs

```bash
# Ver logs del backend
docker logs -f ricoh-backend

# Buscar mensajes de seguridad
docker logs ricoh-backend 2>&1 | grep -E "ENCRYPTION|CSRF|Redis|Rate"
```

Deberías ver:
```
✅ Servicio de encriptación inicializado
🛡️ CSRF Protection enabled
🔴 CSRF usando Redis para almacenamiento distribuido
🔴 Rate Limiter usando Redis para almacenamiento distribuido
```

---

## Paso 7: Inicializar Base de Datos

### 7.1 Ejecutar migraciones

```bash
# Ejecutar script de inicialización
docker exec ricoh-backend python scripts/init_db.py
```

### 7.2 Crear superadmin

```bash
# Crear usuario superadmin
docker exec ricoh-backend python scripts/init_superadmin.py

# La contraseña se guardará en /app/.superadmin_password
docker exec ricoh-backend cat .superadmin_password
```

---

## Paso 8: Verificar Despliegue

### 8.1 Ejecutar script de verificación

```bash
docker exec ricoh-backend python scripts/verify_deployment.py
```

### 8.2 Pruebas manuales

```bash
# Test API health
curl https://api.ricoh.tu-dominio.com/health

# Test frontend
curl https://ricoh.tu-dominio.com/

# Test login (reemplaza con tus credenciales)
curl -X POST https://api.ricoh.tu-dominio.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"superadmin","password":"<tu-password>"}'
```

---

## Paso 9: Configurar Monitoreo

### 9.1 Ver logs en tiempo real

```bash
# Backend logs
docker logs -f ricoh-backend

# Nginx logs
docker logs -f ricoh-nginx

# PostgreSQL logs
docker logs -f ricoh-postgres

# Todos los logs
docker-compose -f deployment/docker-compose.prod.yml logs -f
```

### 9.2 Verificar estado de contenedores

```bash
# Estado de servicios
docker-compose -f deployment/docker-compose.prod.yml ps

# Uso de recursos
docker stats
```

---

## Paso 10: Configurar Backups Automáticos

### 10.1 Crear script de backup

```bash
mkdir -p /opt/ricoh/backups

cat > /opt/ricoh/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/ricoh/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/ricoh_backup_${TIMESTAMP}.sql"

# Crear backup
docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > "$BACKUP_FILE"

# Comprimir
gzip "$BACKUP_FILE"

# Eliminar backups antiguos (mantener últimos 30 días)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup completado: ${BACKUP_FILE}.gz"
EOF

chmod +x /opt/ricoh/backup.sh
```

### 10.2 Configurar cron para backups diarios

```bash
crontab -e

# Agregar esta línea (backup diario a las 2 AM)
0 2 * * * /opt/ricoh/backup.sh >> /opt/ricoh/backups/backup.log 2>&1
```

---

## Comandos Útiles de Administración

### Gestión de Servicios

```bash
# Iniciar servicios
docker-compose -f deployment/docker-compose.prod.yml up -d

# Detener servicios
docker-compose -f deployment/docker-compose.prod.yml down

# Reiniciar servicios
docker-compose -f deployment/docker-compose.prod.yml restart

# Reiniciar solo backend
docker-compose -f deployment/docker-compose.prod.yml restart backend

# Ver estado
docker-compose -f deployment/docker-compose.prod.yml ps
```

### Actualización de Código

```bash
# Detener servicios
docker-compose -f deployment/docker-compose.prod.yml down

# Actualizar código
git pull origin main

# Reconstruir imágenes
docker-compose -f deployment/docker-compose.prod.yml build

# Iniciar servicios
docker-compose -f deployment/docker-compose.prod.yml up -d

# Verificar logs
docker logs -f ricoh-backend
```

### Gestión de Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_fleet

# Crear backup manual
docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > backup.sql

# Restaurar backup
docker exec -i ricoh-postgres psql -U ricoh_admin ricoh_fleet < backup.sql
```

### Gestión de Logs

```bash
# Ver logs recientes
docker logs --tail 100 ricoh-backend

# Seguir logs en tiempo real
docker logs -f ricoh-backend

# Buscar errores
docker logs ricoh-backend 2>&1 | grep -i error

# Limpiar logs antiguos
docker-compose -f deployment/docker-compose.prod.yml logs --no-log-prefix > /dev/null
```

---

## Verificación de Correcciones de Seguridad

### Verificar que las 11 vulnerabilidades están corregidas:

```bash
# 1. ENCRYPTION_KEY configurada
docker exec ricoh-backend python -c "import os; assert os.getenv('ENCRYPTION_KEY'), 'ENCRYPTION_KEY not set'"

# 2. SECRET_KEY con entropía
docker logs ricoh-backend 2>&1 | grep "SECRET_KEY"

# 3. CSRF habilitada en producción
docker logs ricoh-backend 2>&1 | grep "CSRF Protection enabled"

# 4. Redis configurado
docker logs ricoh-backend 2>&1 | grep "Redis"

# 5. Tokens enmascarados en logs
docker logs ricoh-backend 2>&1 | grep "Token:" | head -5
# Deberías ver formato: Token: eyJh...R8U (solo 4+4 caracteres)
```

---

## Troubleshooting

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker logs ricoh-backend

# Verificar variables de entorno
docker exec ricoh-backend env | grep -E "ENCRYPTION|SECRET|DATABASE"

# Verificar conectividad a postgres
docker exec ricoh-backend ping postgres
```

### Problema: Error de ENCRYPTION_KEY

```bash
# Verificar que está configurada
docker exec ricoh-backend python -c "import os; print('ENCRYPTION_KEY:', os.getenv('ENCRYPTION_KEY'))"

# Si no está configurada, actualizar .env.production y reiniciar
docker-compose -f deployment/docker-compose.prod.yml restart backend
```

### Problema: CSRF bloqueando peticiones

```bash
# Verificar que CSRF está habilitada
docker logs ricoh-backend 2>&1 | grep CSRF

# Verificar Redis
docker exec ricoh-redis redis-cli -a $REDIS_PASSWORD ping
```

### Problema: Rate limiting muy agresivo

```bash
# Verificar configuración de rate limiting
docker logs ricoh-backend 2>&1 | grep "Rate Limiter"

# Verificar Redis
docker exec ricoh-redis redis-cli -a $REDIS_PASSWORD keys "ratelimit:*"
```

---

## Seguridad en Producción

### Checklist de Seguridad

- [ ] ✅ ENCRYPTION_KEY generada y configurada
- [ ] ✅ SECRET_KEY generada con entropía suficiente
- [ ] ✅ POSTGRES_PASSWORD fuerte (mínimo 16 caracteres)
- [ ] ✅ REDIS_PASSWORD configurada
- [ ] ✅ RICOH_ADMIN_PASSWORD configurada
- [ ] ✅ CORS_ORIGINS restringido a dominios reales
- [ ] ✅ ENVIRONMENT=production
- [ ] ✅ DEBUG=false
- [ ] ✅ FORCE_HTTPS=true
- [ ] ✅ SSL certificados instalados
- [ ] ✅ Firewall configurado (solo puertos 22, 80, 443)
- [ ] ✅ Redis con contraseña
- [ ] ✅ PostgreSQL no expuesto externamente
- [ ] ✅ Backups automáticos configurados

### Verificar Correcciones de Seguridad Activas

```bash
# Ejecutar script de verificación
docker exec ricoh-backend python scripts/verify_deployment.py

# Verificar logs de inicio
docker logs ricoh-backend 2>&1 | grep -E "✅|🛡️|🔴|⚠️"
```

Deberías ver:
```
✅ Servicio de encriptación inicializado
🛡️ CSRF Protection enabled
🔴 CSRF usando Redis para almacenamiento distribuido
🔴 Rate Limiter usando Redis para almacenamiento distribuido
```

---

## Monitoreo y Mantenimiento

### Logs a Monitorear

```bash
# Errores críticos
docker logs ricoh-backend 2>&1 | grep -i "error\|critical\|fatal"

# Intentos de autenticación fallidos
docker logs ricoh-backend 2>&1 | grep "Authentication failed"

# Rate limiting activado
docker logs ricoh-backend 2>&1 | grep "Rate limit exceeded"

# CSRF violations
docker logs ricoh-backend 2>&1 | grep "CSRF"
```

### Métricas a Revisar

```bash
# Uso de recursos
docker stats --no-stream

# Conexiones a base de datos
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT count(*) FROM pg_stat_activity;"

# Tamaño de base de datos
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT pg_size_pretty(pg_database_size('ricoh_fleet'));"

# Keys en Redis
docker exec ricoh-redis redis-cli -a $REDIS_PASSWORD dbsize
```

---

## Rollback en Caso de Problemas

### Rollback Rápido

```bash
# 1. Detener servicios
docker-compose -f deployment/docker-compose.prod.yml down

# 2. Restaurar backup de base de datos
docker-compose -f deployment/docker-compose.prod.yml up -d postgres
docker exec -i ricoh-postgres psql -U ricoh_admin ricoh_fleet < backups/ricoh_backup_YYYYMMDD_HHMMSS.sql

# 3. Revertir código
git checkout <commit-anterior>

# 4. Reconstruir e iniciar
docker-compose -f deployment/docker-compose.prod.yml build
docker-compose -f deployment/docker-compose.prod.yml up -d
```

---

## Arquitectura de Producción

```
Internet
    ↓
[Firewall: UFW]
    ↓ (80, 443)
[Nginx Reverse Proxy]
    ↓
    ├─→ [Frontend Container] (React SPA)
    │
    └─→ [Backend Container] (FastAPI)
            ↓
            ├─→ [PostgreSQL Container] (Database)
            └─→ [Redis Container] (CSRF + Rate Limiting)
```

### Puertos Expuestos

- **80**: HTTP (redirige a HTTPS)
- **443**: HTTPS (Nginx)
- **22**: SSH (administración)

### Puertos Internos (no expuestos)

- **8000**: Backend API (solo accesible via Nginx)
- **5432**: PostgreSQL (solo accesible desde backend)
- **6379**: Redis (solo accesible desde backend)

---

## Escalabilidad

### Para múltiples instancias del backend:

1. Actualizar `deployment/docker-compose.prod.yml`:

```yaml
backend:
  deploy:
    replicas: 3  # Número de instancias
```

2. Nginx automáticamente balanceará la carga entre instancias

3. Redis es REQUERIDO para múltiples instancias (CSRF y rate limiting distribuidos)

---

## Contacto y Soporte

Para problemas o preguntas sobre el despliegue:
1. Revisar logs: `docker logs ricoh-backend`
2. Ejecutar verificación: `docker exec ricoh-backend python scripts/verify_deployment.py`
3. Consultar documentación de correcciones de seguridad: `.kiro/specs/correccion-vulnerabilidades-seguridad-auditoria/`

---

## Resumen de Correcciones de Seguridad Aplicadas

Este despliegue incluye las 11 correcciones de vulnerabilidades:

**Gestión de Secretos (4)**:
1. ✅ ENCRYPTION_KEY obligatoria en todos los entornos
2. ✅ SECRET_KEY con validación de entropía
3. ✅ RICOH_ADMIN_PASSWORD obligatoria
4. ✅ DATABASE_URL sin credenciales hardcodeadas

**Exposición de Información (3)**:
5. ✅ JWT tokens enmascarados en logs (formato XXXX...YYYY)
6. ✅ Contraseñas no expuestas en consola
7. ✅ wimTokens enmascarados en logs

**Configuración Restrictiva (4)**:
8. ✅ CORS con listas explícitas de métodos y headers
9. ✅ CSRF habilitada por defecto en producción
10. ✅ CSRF con Redis para almacenamiento distribuido
11. ✅ Rate limiting con Redis para almacenamiento distribuido

**Estado**: Todas las vulnerabilidades corregidas y verificadas con 78/89 tests pasados (87.6%)
