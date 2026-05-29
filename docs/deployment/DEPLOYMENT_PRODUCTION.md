# 🚀 Guía de Despliegue en Producción

**Proyecto**: Ricoh Fleet Management  
**Versión**: 1.0  
**Fecha**: Mayo 2026

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración de Redis](#configuración-de-redis)
3. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
4. [Despliegue con Docker](#despliegue-con-docker)
5. [Despliegue Manual](#despliegue-manual)
6. [Verificación Post-Despliegue](#verificación-post-despliegue)
7. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos Previos

### Hardware Mínimo
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 20 GB SSD
- **Red**: 100 Mbps

### Hardware Recomendado
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disco**: 50+ GB SSD
- **Red**: 1 Gbps

### Software
- **OS**: Ubuntu 20.04+ / Debian 11+ / RHEL 8+
- **Docker**: 20.10+ y Docker Compose 2.0+
- **Python**: 3.11+ (si despliegue manual)
- **PostgreSQL**: 15+
- **Redis**: 7+
- **Nginx**: 1.20+ (opcional)

---

## 🔴 Configuración de Redis

### Opción A: Redis con Docker (RECOMENDADO)

```bash
# 1. Crear red Docker
docker network create ricoh_network

# 2. Ejecutar Redis
docker run -d \
  --name ricoh_redis \
  --network ricoh_network \
  -p 6379:6379 \
  -v redis_data:/data \
  --restart always \
  redis:7-alpine \
  redis-server \
  --requirepass "TU_PASSWORD_SEGURA" \
  --maxmemory 256mb \
  --maxmemory-policy allkeys-lru

# 3. Verificar
docker exec ricoh_redis redis-cli -a "TU_PASSWORD_SEGURA" ping
# Debe responder: PONG
```

### Opción B: Redis Nativo

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# Configurar Redis
sudo nano /etc/redis/redis.conf

# Agregar/modificar:
# bind 127.0.0.1
# requirepass TU_PASSWORD_SEGURA
# maxmemory 256mb
# maxmemory-policy allkeys-lru

# Reiniciar
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# Verificar
redis-cli -a "TU_PASSWORD_SEGURA" ping
```

### Configuración de Seguridad Redis

```bash
# /etc/redis/redis.conf

# Bind solo a localhost (si backend está en el mismo servidor)
bind 127.0.0.1

# O bind a IP privada (si backend está en otro servidor)
# bind 10.0.0.5

# Contraseña obligatoria
requirepass TU_PASSWORD_SEGURA_AQUI

# Deshabilitar comandos peligrosos
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# Límite de memoria
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistencia
save 900 1
save 300 10
save 60 10000

# Log
loglevel notice
logfile /var/log/redis/redis-server.log
```

---

## ⚙️ Configuración de Variables de Entorno

### 1. Copiar archivo de ejemplo

```bash
cd backend
cp .env.production.example .env
```

### 2. Generar claves de seguridad

```bash
# Generar ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generar SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Editar .env con valores reales

```bash
nano .env
```

**Variables CRÍTICAS a configurar:**

```bash
# Base de datos
DATABASE_URL=postgresql://ricoh_prod:PASSWORD_SEGURA@localhost:5432/ricoh_fleet_prod

# Redis (usar la contraseña configurada anteriormente)
REDIS_URL=redis://:TU_PASSWORD_REDIS@localhost:6379/0

# Seguridad (usar las claves generadas)
ENCRYPTION_KEY=tu-encryption-key-generada-aqui
SECRET_KEY=tu-secret-key-generada-aqui

# Ricoh
RICOH_ADMIN_PASSWORD=password-admin-impresoras

# CORS (dominios reales de producción)
CORS_ORIGINS=https://ricoh.tuempresa.com,https://www.ricoh.tuempresa.com

# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### 4. Proteger archivo .env

```bash
chmod 600 .env
chown ricoh:ricoh .env  # Usuario que ejecuta la aplicación
```

---

## 🐳 Despliegue con Docker

### Opción A: Docker Compose (RECOMENDADO)

#### 1. Crear archivo .env para Docker

```bash
# backend/.env.docker
DB_PASSWORD=password_postgres_segura
REDIS_PASSWORD=password_redis_segura
ENCRYPTION_KEY=tu-encryption-key-aqui
SECRET_KEY=tu-secret-key-aqui
RICOH_ADMIN_PASSWORD=password-ricoh
CORS_ORIGINS=https://ricoh.tuempresa.com
```

#### 2. Iniciar servicios

```bash
cd backend

# Construir imágenes
docker-compose -f docker-compose.production.yml build

# Iniciar servicios
docker-compose -f docker-compose.production.yml up -d

# Ver logs
docker-compose -f docker-compose.production.yml logs -f
```

#### 3. Aplicar migraciones

```bash
# Ejecutar migraciones dentro del contenedor
docker-compose -f docker-compose.production.yml exec backend \
  python -c "from db.database import init_db; init_db()"
```

#### 4. Verificar servicios

```bash
# Ver estado
docker-compose -f docker-compose.production.yml ps

# Verificar Redis
docker-compose -f docker-compose.production.yml exec redis redis-cli ping

# Verificar PostgreSQL
docker-compose -f docker-compose.production.yml exec postgres \
  psql -U ricoh_prod_user -d ricoh_fleet_prod -c "SELECT version();"

# Verificar Backend
curl http://localhost:8000/health
```

---

## 🔧 Despliegue Manual

### 1. Instalar dependencias del sistema

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
  python3.11 \
  python3.11-venv \
  python3-pip \
  postgresql-15 \
  redis-server \
  nginx \
  supervisor
```

### 2. Crear usuario del sistema

```bash
sudo useradd -m -s /bin/bash ricoh
sudo usermod -aG sudo ricoh
```

### 3. Configurar PostgreSQL

```bash
# Crear usuario y base de datos
sudo -u postgres psql << EOF
CREATE USER ricoh_prod WITH PASSWORD 'PASSWORD_SEGURA';
CREATE DATABASE ricoh_fleet_prod OWNER ricoh_prod;
GRANT ALL PRIVILEGES ON DATABASE ricoh_fleet_prod TO ricoh_prod;
\q
EOF
```

### 4. Instalar aplicación

```bash
# Cambiar a usuario ricoh
sudo su - ricoh

# Clonar repositorio
git clone https://github.com/tuempresa/ricoh-fleet.git
cd ricoh-fleet/backend

# Crear entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Configurar .env
cp .env.production.example .env
nano .env  # Editar con valores reales

# Aplicar migraciones
python -c "from db.database import init_db; init_db()"
```

### 5. Configurar Supervisor

```bash
# /etc/supervisor/conf.d/ricoh-backend.conf
sudo nano /etc/supervisor/conf.d/ricoh-backend.conf
```

```ini
[program:ricoh-backend]
command=/home/ricoh/ricoh-fleet/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/home/ricoh/ricoh-fleet/backend
user=ricoh
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ricoh/backend.log
environment=PATH="/home/ricoh/ricoh-fleet/backend/venv/bin"
```

```bash
# Recargar Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ricoh-backend

# Ver estado
sudo supervisorctl status ricoh-backend
```

### 6. Configurar Nginx

```bash
# /etc/nginx/sites-available/ricoh
sudo nano /etc/nginx/sites-available/ricoh
```

```nginx
upstream ricoh_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name ricoh.tuempresa.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ricoh.tuempresa.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/ricoh.crt;
    ssl_certificate_key /etc/ssl/private/ricoh.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # API Backend
    location /api/ {
        proxy_pass http://ricoh_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Frontend
    location / {
        root /var/www/ricoh/frontend;
        try_files $uri $uri/ /index.html;
    }
    
    # Static files
    location /static/ {
        alias /var/www/ricoh/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/ricoh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## ✅ Verificación Post-Despliegue

### 1. Verificar Redis

```bash
# Conexión
redis-cli -a "TU_PASSWORD" ping
# Debe responder: PONG

# Ver estadísticas
redis-cli -a "TU_PASSWORD" INFO stats

# Ver keys de caché
redis-cli -a "TU_PASSWORD" KEYS "dashboard:*"
```

### 2. Verificar Backend

```bash
# Health check
curl http://localhost:8000/health

# Verificar Redis desde backend
curl http://localhost:8000/api/v1/system/cache/stats

# Probar endpoint con caché
curl http://localhost:8000/api/v1/dashboard/kpis

# Ver logs
tail -f /var/log/ricoh/backend.log | grep -i redis
```

### 3. Verificar Caché Funcionando

```bash
# Primera llamada (MISS)
time curl http://localhost:8000/api/v1/dashboard/kpis
# Debe tardar ~500ms

# Segunda llamada (HIT)
time curl http://localhost:8000/api/v1/dashboard/kpis
# Debe tardar ~10ms

# Ver logs de caché
tail -f /var/log/ricoh/backend.log | grep "Cache"
```

### 4. Tests de Carga

```bash
# Instalar Apache Bench
sudo apt install apache2-utils

# Test sin caché (primera vez)
ab -n 100 -c 10 http://localhost:8000/api/v1/dashboard/kpis

# Test con caché (segunda vez)
ab -n 1000 -c 50 http://localhost:8000/api/v1/dashboard/kpis
```

---

## 📊 Monitoreo y Mantenimiento

### Monitoreo de Redis

```bash
# Monitor en tiempo real
redis-cli -a "TU_PASSWORD" MONITOR

# Estadísticas
redis-cli -a "TU_PASSWORD" INFO all

# Memoria usada
redis-cli -a "TU_PASSWORD" INFO memory

# Clientes conectados
redis-cli -a "TU_PASSWORD" CLIENT LIST
```

### Logs

```bash
# Backend
tail -f /var/log/ricoh/backend.log

# Redis
tail -f /var/log/redis/redis-server.log

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Backups

```bash
# Backup de Redis (RDB)
redis-cli -a "TU_PASSWORD" BGSAVE

# Backup de PostgreSQL
pg_dump -U ricoh_prod ricoh_fleet_prod > backup_$(date +%Y%m%d).sql
```

### Limpieza de Caché

```bash
# Limpiar caché específico
redis-cli -a "TU_PASSWORD" DEL "dashboard:kpis"

# Limpiar patrón
redis-cli -a "TU_PASSWORD" --scan --pattern "dashboard:*" | xargs redis-cli -a "TU_PASSWORD" DEL

# Limpiar todo (¡CUIDADO!)
redis-cli -a "TU_PASSWORD" FLUSHDB
```

---

## 🔧 Troubleshooting

### Redis no conecta

```bash
# Verificar que Redis está corriendo
sudo systemctl status redis-server

# Verificar puerto
sudo netstat -tlnp | grep 6379

# Verificar logs
tail -f /var/log/redis/redis-server.log

# Probar conexión
redis-cli -a "TU_PASSWORD" ping
```

### Backend no inicia

```bash
# Ver logs
sudo supervisorctl tail -f ricoh-backend

# Verificar variables de entorno
sudo supervisorctl stop ricoh-backend
cd /home/ricoh/ricoh-fleet/backend
source venv/bin/activate
python -c "from services.redis_service import redis_service; print(redis_service.get_stats())"
```

### Caché no funciona

```bash
# Verificar que Redis está habilitado
curl http://localhost:8000/api/v1/system/cache/stats

# Ver logs de caché
tail -f /var/log/ricoh/backend.log | grep -i "cache\|redis"

# Verificar TTL
redis-cli -a "TU_PASSWORD" TTL "dashboard:kpis"
```

---

## 📝 Checklist Final

- [ ] Redis instalado y corriendo
- [ ] Redis con contraseña configurada
- [ ] PostgreSQL configurado
- [ ] Variables de entorno configuradas
- [ ] ENCRYPTION_KEY y SECRET_KEY únicos
- [ ] Backend iniciado sin errores
- [ ] Logs muestran "Redis conectado"
- [ ] Endpoints responden correctamente
- [ ] Caché funcionando (HIT/MISS en logs)
- [ ] HTTPS configurado
- [ ] Firewall configurado
- [ ] Backups automáticos configurados
- [ ] Monitoreo configurado
- [ ] Documentación actualizada

---

**¡Despliegue completado!** 🎉

Para soporte: contactar al equipo de desarrollo.
