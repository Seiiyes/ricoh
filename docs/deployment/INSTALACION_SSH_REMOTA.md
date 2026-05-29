# 🚀 Instalación Remota via SSH

**Proyecto**: Ricoh Fleet Management  
**Método**: Script automático de instalación

---

## 📋 Opciones Disponibles

### **Opción 1: Script Automático** ⭐ (RECOMENDADO)

Un script bash que instala y configura todo automáticamente.

**Tiempo**: 10-15 minutos  
**Dificultad**: ⭐ Fácil

### **Opción 2: Instalación Guiada Paso a Paso**

Te guío comando por comando, tú ejecutas y me dices qué sale.

**Tiempo**: 20-30 minutos  
**Dificultad**: ⭐⭐ Media

---

## 🔧 Opción 1: Script Automático

### **Paso 1: Conectar al Servidor**

```bash
# Desde tu máquina local
ssh usuario@tu-servidor.com
```

### **Paso 2: Descargar el Script**

```bash
# Opción A: Si tienes el repositorio
git clone https://github.com/tuempresa/ricoh-fleet.git
cd ricoh-fleet/backend
chmod +x install_production.sh

# Opción B: Descargar solo el script
wget https://raw.githubusercontent.com/tuempresa/ricoh-fleet/main/backend/install_production.sh
chmod +x install_production.sh
```

### **Paso 3: Ejecutar el Script**

```bash
./install_production.sh
```

### **Paso 4: Responder Preguntas**

El script te preguntará:

1. **URL del repositorio Git** (opcional)
   ```
   URL: https://github.com/tuempresa/ricoh-fleet.git
   ```

2. **Contraseña admin de impresoras Ricoh**
   ```
   Contraseña: [tu-contraseña-ricoh]
   ```

3. **Dominio de producción**
   ```
   Dominio: ricoh.tuempresa.com
   ```

### **Paso 5: Esperar**

El script hará automáticamente:
- ✅ Actualizar sistema
- ✅ Instalar dependencias (Python, PostgreSQL, Redis, Nginx)
- ✅ Configurar PostgreSQL con usuario y BD
- ✅ Configurar Redis con contraseña
- ✅ Clonar repositorio
- ✅ Crear entorno virtual
- ✅ Instalar dependencias Python
- ✅ Generar claves de seguridad
- ✅ Crear archivo .env
- ✅ Aplicar migraciones
- ✅ Configurar Supervisor
- ✅ Configurar Nginx
- ✅ Verificar instalación

### **Paso 6: Verificar**

Al finalizar verás:

```
========================================
INSTALACIÓN COMPLETADA
========================================

✅ Sistema instalado correctamente

📊 Información del Sistema:
  - Base de datos: ricoh_fleet_prod
  - Usuario BD: ricoh_prod
  - Redis: localhost:6379
  - Backend: http://localhost:8000
  - Dominio: http://ricoh.tuempresa.com

🔐 Credenciales (guardadas en archivos seguros):
  - DB Password: ~/.ricoh_db_password
  - Redis Password: ~/.ricoh_redis_password
  - .env: ~/ricoh-fleet/backend/.env

✅ ¡Instalación completada!
```

---

## 🔧 Opción 2: Instalación Guiada

Si prefieres ir paso a paso, aquí está la guía:

### **1. Conectar al Servidor**

```bash
ssh usuario@tu-servidor.com
```

**Dime**: ¿Conectaste correctamente?

---

### **2. Actualizar Sistema**

```bash
sudo apt update
sudo apt upgrade -y
```

**Dime**: ¿Se actualizó sin errores?

---

### **3. Instalar Dependencias**

```bash
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql-15 \
    redis-server \
    nginx \
    supervisor \
    git \
    curl
```

**Dime**: ¿Se instaló todo correctamente?

---

### **4. Configurar PostgreSQL**

```bash
# Generar contraseña aleatoria
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
echo "Contraseña BD: $DB_PASSWORD"

# Crear usuario y base de datos
sudo -u postgres psql << EOF
CREATE USER ricoh_prod WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE ricoh_fleet_prod OWNER ricoh_prod;
GRANT ALL PRIVILEGES ON DATABASE ricoh_fleet_prod TO ricoh_prod;
\q
EOF

# Guardar contraseña
echo "$DB_PASSWORD" > ~/.ricoh_db_password
chmod 600 ~/.ricoh_db_password
```

**Dime**: ¿Se creó la base de datos? ¿Qué contraseña generó?

---

### **5. Configurar Redis**

```bash
# Generar contraseña
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
echo "Contraseña Redis: $REDIS_PASSWORD"

# Configurar Redis
sudo tee /etc/redis/redis.conf > /dev/null << EOF
bind 127.0.0.1
requirepass $REDIS_PASSWORD
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF

# Reiniciar Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# Guardar contraseña
echo "$REDIS_PASSWORD" > ~/.ricoh_redis_password
chmod 600 ~/.ricoh_redis_password

# Probar
redis-cli -a "$REDIS_PASSWORD" ping
```

**Dime**: ¿Redis responde "PONG"?

---

### **6. Clonar Repositorio**

```bash
cd ~
git clone https://github.com/tuempresa/ricoh-fleet.git
cd ricoh-fleet/backend
```

**Dime**: ¿Se clonó correctamente?

---

### **7. Instalar Dependencias Python**

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Dime**: ¿Se instalaron todas las dependencias?

---

### **8. Crear .env**

```bash
# Generar claves
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Leer contraseñas guardadas
DB_PASSWORD=$(cat ~/.ricoh_db_password)
REDIS_PASSWORD=$(cat ~/.ricoh_redis_password)

# Crear .env
cat > .env << EOF
DATABASE_URL=postgresql://ricoh_prod:$DB_PASSWORD@localhost:5432/ricoh_fleet_prod
REDIS_URL=redis://:$REDIS_PASSWORD@localhost:6379/0
ENCRYPTION_KEY=$ENCRYPTION_KEY
SECRET_KEY=$SECRET_KEY
RICOH_ADMIN_PASSWORD=TU_PASSWORD_RICOH_AQUI
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://ricoh.tuempresa.com
CACHE_TTL_DASHBOARD=300
CACHE_TTL_ANALYTICS=3600
WORKERS=4
EOF

chmod 600 .env

# Editar para agregar contraseña Ricoh
nano .env
```

**Dime**: ¿Editaste el .env con la contraseña de Ricoh?

---

### **9. Aplicar Migraciones**

```bash
python -c "from db.database import init_db; init_db()"
```

**Dime**: ¿Se aplicaron las migraciones?

---

### **10. Configurar Supervisor**

```bash
sudo tee /etc/supervisor/conf.d/ricoh-backend.conf > /dev/null << EOF
[program:ricoh-backend]
command=/home/$USER/ricoh-fleet/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/home/$USER/ricoh-fleet/backend
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ricoh/backend.log
environment=PATH="/home/$USER/ricoh-fleet/backend/venv/bin"
EOF

sudo mkdir -p /var/log/ricoh
sudo chown $USER:$USER /var/log/ricoh

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ricoh-backend
```

**Dime**: ¿El backend está corriendo?

```bash
sudo supervisorctl status ricoh-backend
```

---

### **11. Configurar Nginx**

```bash
sudo tee /etc/nginx/sites-available/ricoh > /dev/null << 'EOF'
upstream ricoh_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name ricoh.tuempresa.com www.ricoh.tuempresa.com;
    
    location / {
        proxy_pass http://ricoh_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/ricoh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Dime**: ¿Nginx se configuró correctamente?

---

### **12. Verificar Instalación**

```bash
# Verificar PostgreSQL
sudo -u postgres psql -d ricoh_fleet_prod -c "SELECT version();"

# Verificar Redis
redis-cli -a "$(cat ~/.ricoh_redis_password)" ping

# Verificar Backend
curl http://localhost:8000/health

# Verificar Nginx
curl http://localhost

# Verificar configuración completa
cd ~/ricoh-fleet/backend
source venv/bin/activate
python verify_production_config.py
```

**Dime**: ¿Todos los servicios están funcionando?

---

## ✅ Verificación Final

Después de la instalación, ejecuta:

```bash
cd ~/ricoh-fleet/backend
source venv/bin/activate
python verify_production_config.py
```

Deberías ver:

```
======================================================================
VERIFICACIÓN DE CONFIGURACIÓN DE PRODUCCIÓN
======================================================================

1. Verificando archivo .env
✅ Archivo .env existe

2. Verificando variables críticas
✅ DATABASE_URL = postgres...
✅ REDIS_URL = redis://...
✅ ENCRYPTION_KEY = ********
✅ SECRET_KEY = ********
✅ RICOH_ADMIN_PASSWORD = ********

3. Verificando configuración de ambiente
✅ ENVIRONMENT = production
✅ DEBUG = false

4. Verificando conexión a Redis
✅ Redis conectado correctamente
   Versión: 7.x
   Memoria: XXX MB
   Keys: 0

5. Verificando conexión a PostgreSQL
✅ PostgreSQL conectado correctamente
   PostgreSQL 15.x

...

RESUMEN DE VERIFICACIÓN
Total de verificaciones: 9
Exitosas: 9
Fallidas: 0
Porcentaje: 100.0%

✅ TODAS LAS VERIFICACIONES PASARON
El sistema está listo para producción
```

---

## 📝 Comandos Útiles Post-Instalación

```bash
# Ver logs del backend
sudo supervisorctl tail -f ricoh-backend

# Reiniciar backend
sudo supervisorctl restart ricoh-backend

# Ver estado de servicios
sudo supervisorctl status

# Ver logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Verificar Redis
redis-cli -a "$(cat ~/.ricoh_redis_password)" INFO stats

# Ver logs de Redis
sudo tail -f /var/log/redis/redis-server.log

# Backup de base de datos
pg_dump -U ricoh_prod ricoh_fleet_prod > backup_$(date +%Y%m%d).sql
```

---

## 🔒 Configurar SSL/HTTPS (Opcional pero Recomendado)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d ricoh.tuempresa.com -d www.ricoh.tuempresa.com

# Renovación automática (ya configurada por defecto)
sudo certbot renew --dry-run
```

---

## 🔥 Configurar Firewall

```bash
# Instalar UFW
sudo apt install -y ufw

# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Habilitar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

---

## 🎯 Próximos Pasos

1. **Configurar SSL/HTTPS** con Let's Encrypt
2. **Configurar firewall** (UFW)
3. **Configurar backups automáticos**
4. **Configurar monitoreo** (opcional: Prometheus, Grafana)
5. **Configurar alertas** (opcional: email, Slack)

---

## 🆘 Troubleshooting

### Backend no inicia

```bash
# Ver logs
sudo supervisorctl tail -f ricoh-backend

# Ver errores
sudo supervisorctl status ricoh-backend

# Reiniciar
sudo supervisorctl restart ricoh-backend
```

### Redis no conecta

```bash
# Verificar que está corriendo
sudo systemctl status redis-server

# Ver logs
sudo tail -f /var/log/redis/redis-server.log

# Probar conexión
redis-cli -a "$(cat ~/.ricoh_redis_password)" ping
```

### PostgreSQL no conecta

```bash
# Verificar que está corriendo
sudo systemctl status postgresql

# Probar conexión
sudo -u postgres psql -d ricoh_fleet_prod -c "SELECT 1;"
```

---

## 📞 Soporte

Si necesitas ayuda:
1. Ejecuta `python verify_production_config.py`
2. Copia el output completo
3. Comparte los logs relevantes
4. Describe el problema específico

---

**¿Qué opción prefieres?**
- **Opción 1**: Ejecutar script automático (10 min)
- **Opción 2**: Instalación guiada paso a paso (30 min)
