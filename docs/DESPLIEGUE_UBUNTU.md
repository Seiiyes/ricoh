# Guía de Despliegue en Ubuntu Server

## 📋 Requisitos Previos

- Ubuntu Server 20.04 LTS o superior
- Acceso root o sudo
- Conexión a internet
- Mínimo 2GB RAM, 2 CPU cores
- 20GB de espacio en disco

## 🚀 Opción 1: Despliegue con Docker (RECOMENDADO)

### Ventajas
✅ Fácil de instalar y mantener
✅ Aislamiento de dependencias
✅ Fácil rollback y actualizaciones
✅ Incluye PostgreSQL y Adminer

### Paso 1: Instalar Docker y Docker Compose

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Agregar repositorio de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalación
docker --version
docker compose version

# Agregar usuario al grupo docker (opcional, para no usar sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### Paso 2: Clonar el Proyecto

```bash
# Crear directorio para el proyecto
sudo mkdir -p /opt/ricoh-fleet
cd /opt/ricoh-fleet

# Clonar repositorio (o copiar archivos)
git clone <tu-repositorio> .

# O si copias manualmente:
# scp -r /ruta/local/* usuario@servidor:/opt/ricoh-fleet/
```

### Paso 3: Configurar Variables de Entorno

```bash
# Backend
cd /opt/ricoh-fleet/backend
cp .env.example .env
nano .env
```

Editar `.env`:
```env
# Database (Docker)
DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@postgres:5432/ricoh_fleet

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEMO_MODE=false

# CORS (ajustar según tu dominio)
CORS_ORIGINS=http://tu-servidor.com,http://localhost:5173

# Encryption Key (generar uno nuevo)
ENCRYPTION_KEY=tu-clave-de-encriptacion-aqui

# Ricoh Admin Credentials
RICOH_ADMIN_USER=admin
RICOH_ADMIN_PASSWORD=
```

Generar clave de encriptación:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Paso 4: Iniciar Servicios con Docker Compose

```bash
cd /opt/ricoh-fleet

# Iniciar todos los servicios
docker compose up -d

# Ver logs
docker compose logs -f

# Verificar estado
docker compose ps
```

Servicios disponibles:
- **Backend API**: http://servidor:8000
- **Frontend**: http://servidor:5173
- **PostgreSQL**: puerto 5432
- **Adminer** (DB Admin): http://servidor:8080

### Paso 5: Aplicar Migraciones

```bash
# Entrar al contenedor del backend
docker compose exec backend bash

# Aplicar migraciones
python apply_migration_003_sqlalchemy.py
python apply_migration_004.py

# Salir
exit
```

### Paso 6: Verificar Funcionamiento

```bash
# Probar API
curl http://localhost:8000/

# Ver logs del backend
docker compose logs -f backend

# Ver logs de la base de datos
docker compose logs -f postgres
```

### Comandos Útiles Docker

```bash
# Detener servicios
docker compose down

# Reiniciar servicios
docker compose restart

# Ver logs de un servicio específico
docker compose logs -f backend

# Reconstruir imágenes
docker compose build --no-cache

# Actualizar y reiniciar
git pull
docker compose up -d --build

# Backup de base de datos
docker compose exec postgres pg_dump -U ricoh_admin ricoh_fleet > backup_$(date +%Y%m%d).sql

# Restaurar base de datos
docker compose exec -T postgres psql -U ricoh_admin ricoh_fleet < backup.sql
```

---

## 🔧 Opción 2: Despliegue Tradicional (Sin Docker)

### Ventajas
✅ Mayor control sobre el sistema
✅ Mejor rendimiento (sin overhead de Docker)
✅ Más fácil de debuggear

### Paso 1: Instalar Dependencias del Sistema

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Instalar PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Instalar Nginx
sudo apt install -y nginx

# Instalar Supervisor (para gestionar procesos)
sudo apt install -y supervisor

# Instalar Node.js (para el frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar dependencias para Chrome/Selenium
sudo apt install -y wget gnupg unzip
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install -y google-chrome-stable
```

### Paso 2: Configurar PostgreSQL

```bash
# Cambiar a usuario postgres
sudo -u postgres psql

# Crear base de datos y usuario
CREATE DATABASE ricoh_fleet;
CREATE USER ricoh_admin WITH PASSWORD 'ricoh_secure_2024';
GRANT ALL PRIVILEGES ON DATABASE ricoh_fleet TO ricoh_admin;
\q

# Permitir conexiones locales
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Agregar: local   all   ricoh_admin   md5

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### Paso 3: Configurar Backend

```bash
# Crear directorio
sudo mkdir -p /opt/ricoh-fleet
cd /opt/ricoh-fleet

# Clonar proyecto
git clone <tu-repositorio> .

# Crear entorno virtual
cd backend
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
nano .env
```

Editar `.env`:
```env
DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@localhost:5432/ricoh_fleet
API_HOST=0.0.0.0
API_PORT=8000
DEMO_MODE=false
CORS_ORIGINS=http://tu-servidor.com
ENCRYPTION_KEY=<generar-nueva-clave>
RICOH_ADMIN_USER=admin
RICOH_ADMIN_PASSWORD=
```

```bash
# Aplicar migraciones
python apply_migration_003_sqlalchemy.py
python apply_migration_004.py

# Probar backend
python main.py
# Ctrl+C para detener
```

### Paso 4: Configurar Supervisor (Backend)

```bash
sudo nano /etc/supervisor/conf.d/ricoh-backend.conf
```

Contenido:
```ini
[program:ricoh-backend]
directory=/opt/ricoh-fleet/backend
command=/opt/ricoh-fleet/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/ricoh-backend.err.log
stdout_logfile=/var/log/ricoh-backend.out.log
environment=PATH="/opt/ricoh-fleet/backend/venv/bin"
```

```bash
# Recargar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ricoh-backend

# Ver estado
sudo supervisorctl status ricoh-backend

# Ver logs
sudo tail -f /var/log/ricoh-backend.out.log
```

### Paso 5: Configurar Frontend

```bash
cd /opt/ricoh-fleet

# Instalar dependencias
npm install

# Configurar variables de entorno
nano .env
```

Contenido de `.env`:
```env
VITE_API_URL=http://tu-servidor.com:8000
```

```bash
# Build para producción
npm run build

# Los archivos estarán en dist/
```

### Paso 6: Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/ricoh-fleet
```

Contenido:
```nginx
# Backend API
server {
    listen 80;
    server_name api.tu-servidor.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}

# Frontend
server {
    listen 80;
    server_name tu-servidor.com;
    root /opt/ricoh-fleet/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/ricoh-fleet /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### Paso 7: Configurar Firewall

```bash
# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir SSH (si no está permitido)
sudo ufw allow 22/tcp

# Habilitar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

### Paso 8: Configurar SSL (Opcional pero Recomendado)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-servidor.com -d api.tu-servidor.com

# Renovación automática (ya está configurada)
sudo certbot renew --dry-run
```

---

## 📊 Monitoreo y Mantenimiento

### Ver Logs

```bash
# Backend (Supervisor)
sudo tail -f /var/log/ricoh-backend.out.log
sudo tail -f /var/log/ricoh-backend.err.log

# Backend (Docker)
docker compose logs -f backend

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

### Comandos Útiles

```bash
# Reiniciar servicios (Tradicional)
sudo supervisorctl restart ricoh-backend
sudo systemctl restart nginx
sudo systemctl restart postgresql

# Reiniciar servicios (Docker)
docker compose restart backend
docker compose restart postgres

# Ver estado de servicios
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql

# Actualizar código
cd /opt/ricoh-fleet
git pull
sudo supervisorctl restart ricoh-backend
# O con Docker:
docker compose up -d --build
```

### Backup Automático

Crear script `/opt/ricoh-fleet/backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/ricoh-fleet/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de base de datos
pg_dump -U ricoh_admin ricoh_fleet > $BACKUP_DIR/db_$DATE.sql

# Backup de configuración
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/ricoh-fleet/backend/.env

# Eliminar backups antiguos (más de 7 días)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completado: $DATE"
```

```bash
# Hacer ejecutable
chmod +x /opt/ricoh-fleet/backup.sh

# Agregar a crontab (diario a las 2 AM)
sudo crontab -e
# Agregar: 0 2 * * * /opt/ricoh-fleet/backup.sh >> /var/log/ricoh-backup.log 2>&1
```

---

## 🔒 Seguridad

### Checklist de Seguridad

- [ ] Cambiar contraseñas por defecto
- [ ] Generar nueva ENCRYPTION_KEY
- [ ] Configurar CORS correctamente
- [ ] Habilitar firewall (ufw)
- [ ] Instalar SSL/TLS (Let's Encrypt)
- [ ] Configurar fail2ban
- [ ] Actualizar sistema regularmente
- [ ] Limitar acceso SSH (solo por clave)
- [ ] Configurar backups automáticos
- [ ] Monitorear logs regularmente

### Fail2ban (Protección contra ataques)

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 🆘 Troubleshooting

### Backend no inicia

```bash
# Ver logs
sudo tail -f /var/log/ricoh-backend.err.log

# Verificar que el puerto 8000 esté libre
sudo netstat -tulpn | grep 8000

# Probar manualmente
cd /opt/ricoh-fleet/backend
source venv/bin/activate
python main.py
```

### Error de conexión a base de datos

```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Probar conexión
psql -U ricoh_admin -d ricoh_fleet -h localhost

# Verificar DATABASE_URL en .env
cat /opt/ricoh-fleet/backend/.env | grep DATABASE_URL
```

### Frontend no carga

```bash
# Verificar Nginx
sudo nginx -t
sudo systemctl status nginx

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Verificar archivos de build
ls -la /opt/ricoh-fleet/dist/
```

---

## 📞 Soporte

Para problemas de despliegue:
1. Revisar logs del servicio afectado
2. Verificar configuración de .env
3. Comprobar conectividad de red
4. Revisar permisos de archivos

## ✅ Verificación Final

Después del despliegue, verificar:

```bash
# API funcionando
curl http://localhost:8000/

# Frontend accesible
curl http://localhost/

# Base de datos conectada
psql -U ricoh_admin -d ricoh_fleet -c "SELECT COUNT(*) FROM printers;"

# Logs sin errores
sudo tail -n 50 /var/log/ricoh-backend.out.log
```

¡Despliegue completado! 🎉
