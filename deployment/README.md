# Deployment - Ricoh Equipment Management

Archivos de configuración para despliegue en producción en Ubuntu Server.

## Archivos Incluidos

### Configuración de Docker

- **docker-compose.prod.yml**: Configuración de Docker Compose para producción
  - Incluye PostgreSQL, Redis, Backend, Frontend, y Nginx
  - Configurado con healthchecks y restart policies
  - Redis para CSRF y rate limiting distribuidos

- **.env.production.example**: Plantilla de variables de entorno para producción
  - Incluye todas las variables de seguridad requeridas
  - Instrucciones para generar claves

### Configuración de Nginx

- **nginx/nginx.conf**: Configuración principal de Nginx
  - Rate limiting configurado
  - Security headers
  - Gzip compression

- **nginx/conf.d/ricoh.conf**: Configuración del sitio
  - HTTP a HTTPS redirect
  - Reverse proxy para backend y frontend
  - SSL/TLS configurado
  - Rate limiting por endpoint

### Scripts de Deployment

- **setup-ubuntu-server.sh**: Script de configuración inicial del servidor
  - Instala Docker, Docker Compose, Nginx
  - Configura firewall (UFW)
  - Crea usuario de deployment
  - Configura systemd service
  - Optimizaciones del kernel

- **deploy-production.sh**: Script de deployment
  - Pre-flight checks de seguridad
  - Backup automático de base de datos
  - Build y deploy de contenedores
  - Verificación de health checks

### Documentación

- **DEPLOYMENT_GUIDE.md**: Guía completa de despliegue paso a paso
  - Requisitos del servidor
  - Configuración de SSL
  - Verificación de seguridad
  - Troubleshooting
  - Comandos útiles

---

## Quick Start

### Para servidor nuevo (Ubuntu Server):

```bash
# 1. Ejecutar setup inicial (como root)
sudo bash deployment/setup-ubuntu-server.sh

# 2. Clonar repositorio
cd /opt/ricoh
git clone <your-repo-url> .

# 3. Configurar variables de entorno
cp deployment/.env.production.example .env.production
nano .env.production  # Editar con valores reales

# 4. Obtener certificados SSL
sudo certbot certonly --standalone -d tu-dominio.com -d api.tu-dominio.com
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem deployment/ssl/
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem deployment/ssl/

# 5. Actualizar configuración de Nginx con tu dominio
nano deployment/nginx/conf.d/ricoh.conf

# 6. Desplegar
bash deployment/deploy-production.sh

# 7. Inicializar base de datos (primera vez)
docker exec ricoh-backend python scripts/init_db.py
docker exec ricoh-backend python scripts/init_superadmin.py

# 8. Verificar
docker exec ricoh-backend python scripts/verify_deployment.py
```

---

## Correcciones de Seguridad Incluidas

Este deployment incluye las 11 correcciones de vulnerabilidades del spec `correccion-vulnerabilidades-seguridad-auditoria`:

### Gestión de Secretos (4)
1. ✅ ENCRYPTION_KEY obligatoria
2. ✅ SECRET_KEY con validación de entropía
3. ✅ RICOH_ADMIN_PASSWORD obligatoria
4. ✅ DATABASE_URL sin credenciales hardcodeadas

### Exposición de Información (3)
5. ✅ JWT tokens enmascarados (XXXX...YYYY)
6. ✅ Contraseñas no expuestas
7. ✅ wimTokens enmascarados

### Configuración Restrictiva (4)
8. ✅ CORS con listas explícitas
9. ✅ CSRF habilitada en producción
10. ✅ CSRF con Redis
11. ✅ Rate limiting con Redis

---

## Arquitectura de Producción

```
Internet
    ↓
[Firewall: UFW - Puertos 22, 80, 443]
    ↓
[Nginx Reverse Proxy + SSL]
    ↓
    ├─→ Frontend (React SPA)
    └─→ Backend API (FastAPI)
            ↓
            ├─→ PostgreSQL (Database)
            └─→ Redis (CSRF + Rate Limiting)
```

---

## Soporte

Para más información, consulta:
- **DEPLOYMENT_GUIDE.md**: Guía completa de despliegue
- **.kiro/specs/correccion-vulnerabilidades-seguridad-auditoria/**: Documentación de correcciones de seguridad
- **backend/tests/CHECKPOINT_FINAL_SUMMARY.md**: Resultados de tests de seguridad
