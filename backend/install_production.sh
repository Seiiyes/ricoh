#!/bin/bash
# =============================================================================
# Script de Instalación Automática para Producción
# Ricoh Fleet Management System
# =============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "No ejecutar como root. Usar un usuario normal con sudo."
    exit 1
fi

print_header "INSTALACIÓN DE RICOH FLEET MANAGEMENT - PRODUCCIÓN"

# =============================================================================
# 1. VERIFICAR SISTEMA OPERATIVO
# =============================================================================
print_header "1. Verificando Sistema Operativo"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    print_success "OS: $NAME $VERSION"
else
    print_error "No se pudo detectar el sistema operativo"
    exit 1
fi

# =============================================================================
# 2. ACTUALIZAR SISTEMA
# =============================================================================
print_header "2. Actualizando Sistema"

print_info "Actualizando paquetes..."
sudo apt update
sudo apt upgrade -y
print_success "Sistema actualizado"

# =============================================================================
# 3. INSTALAR DEPENDENCIAS
# =============================================================================
print_header "3. Instalando Dependencias"

print_info "Instalando dependencias del sistema..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql-15 \
    postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev

print_success "Dependencias instaladas"

# =============================================================================
# 4. CONFIGURAR POSTGRESQL
# =============================================================================
print_header "4. Configurando PostgreSQL"

# Generate random password
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

print_info "Creando base de datos y usuario..."
sudo -u postgres psql << EOF
CREATE USER ricoh_prod WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE ricoh_fleet_prod OWNER ricoh_prod;
GRANT ALL PRIVILEGES ON DATABASE ricoh_fleet_prod TO ricoh_prod;
\q
EOF

print_success "PostgreSQL configurado"
print_info "Usuario: ricoh_prod"
print_info "Base de datos: ricoh_fleet_prod"
print_warning "Contraseña guardada en: ~/.ricoh_db_password"
echo "$DB_PASSWORD" > ~/.ricoh_db_password
chmod 600 ~/.ricoh_db_password

# =============================================================================
# 5. CONFIGURAR REDIS
# =============================================================================
print_header "5. Configurando Redis"

# Generate Redis password
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

print_info "Configurando Redis..."
sudo tee /etc/redis/redis.conf > /dev/null << EOF
bind 127.0.0.1
port 6379
requirepass $REDIS_PASSWORD
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
loglevel notice
logfile /var/log/redis/redis-server.log
EOF

sudo systemctl restart redis-server
sudo systemctl enable redis-server

print_success "Redis configurado"
print_warning "Contraseña guardada en: ~/.ricoh_redis_password"
echo "$REDIS_PASSWORD" > ~/.ricoh_redis_password
chmod 600 ~/.ricoh_redis_password

# Test Redis
if redis-cli -a "$REDIS_PASSWORD" ping > /dev/null 2>&1; then
    print_success "Redis funcionando correctamente"
else
    print_error "Redis no responde"
    exit 1
fi

# =============================================================================
# 6. CLONAR REPOSITORIO
# =============================================================================
print_header "6. Clonando Repositorio"

print_info "¿URL del repositorio Git?"
read -p "URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    print_warning "No se proporcionó URL, usando directorio actual"
    PROJECT_DIR=$(pwd)
else
    print_info "Clonando repositorio..."
    cd ~
    git clone "$REPO_URL" ricoh-fleet
    PROJECT_DIR=~/ricoh-fleet
    print_success "Repositorio clonado en: $PROJECT_DIR"
fi

# =============================================================================
# 7. CONFIGURAR APLICACIÓN
# =============================================================================
print_header "7. Configurando Aplicación"

cd "$PROJECT_DIR/backend"

# Create virtual environment
print_info "Creando entorno virtual..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
print_info "Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Dependencias instaladas"

# =============================================================================
# 8. GENERAR CLAVES DE SEGURIDAD
# =============================================================================
print_header "8. Generando Claves de Seguridad"

ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

print_success "Claves generadas"

# =============================================================================
# 9. CREAR ARCHIVO .env
# =============================================================================
print_header "9. Creando Archivo .env"

print_info "Ingresa la contraseña admin de las impresoras Ricoh:"
read -s RICOH_PASSWORD
echo

print_info "Ingresa el dominio de producción (ej: ricoh.tuempresa.com):"
read DOMAIN

cat > .env << EOF
# =============================================================================
# RICOH FLEET MANAGEMENT - PRODUCCIÓN
# Generado automáticamente: $(date)
# =============================================================================

# Database
DATABASE_URL=postgresql://ricoh_prod:$DB_PASSWORD@localhost:5432/ricoh_fleet_prod

# Redis
REDIS_URL=redis://:$REDIS_PASSWORD@localhost:6379/0
CACHE_TTL_DASHBOARD=300
CACHE_TTL_ANALYTICS=3600

# Security
ENCRYPTION_KEY=$ENCRYPTION_KEY
SECRET_KEY=$SECRET_KEY
RICOH_ADMIN_PASSWORD=$RICOH_PASSWORD

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Performance
WORKERS=4
EOF

chmod 600 .env
print_success "Archivo .env creado"

# =============================================================================
# 10. APLICAR MIGRACIONES
# =============================================================================
print_header "10. Aplicando Migraciones de Base de Datos"

print_info "Aplicando migraciones..."
python -c "from db.database import init_db; init_db()"
print_success "Migraciones aplicadas"

# =============================================================================
# 11. CONFIGURAR SUPERVISOR
# =============================================================================
print_header "11. Configurando Supervisor"

sudo tee /etc/supervisor/conf.d/ricoh-backend.conf > /dev/null << EOF
[program:ricoh-backend]
command=$PROJECT_DIR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=$PROJECT_DIR/backend
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ricoh/backend.log
environment=PATH="$PROJECT_DIR/backend/venv/bin"
EOF

# Create log directory
sudo mkdir -p /var/log/ricoh
sudo chown $USER:$USER /var/log/ricoh

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ricoh-backend

print_success "Supervisor configurado"

# =============================================================================
# 12. CONFIGURAR NGINX
# =============================================================================
print_header "12. Configurando Nginx"

sudo tee /etc/nginx/sites-available/ricoh > /dev/null << EOF
upstream ricoh_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location / {
        proxy_pass http://ricoh_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/ricoh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

print_success "Nginx configurado"

# =============================================================================
# 13. VERIFICAR INSTALACIÓN
# =============================================================================
print_header "13. Verificando Instalación"

sleep 5  # Wait for services to start

# Check PostgreSQL
if sudo -u postgres psql -d ricoh_fleet_prod -c "SELECT 1" > /dev/null 2>&1; then
    print_success "PostgreSQL: OK"
else
    print_error "PostgreSQL: FALLO"
fi

# Check Redis
if redis-cli -a "$REDIS_PASSWORD" ping > /dev/null 2>&1; then
    print_success "Redis: OK"
else
    print_error "Redis: FALLO"
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend: OK"
else
    print_warning "Backend: Verificar logs"
fi

# Check Nginx
if curl -f http://localhost > /dev/null 2>&1; then
    print_success "Nginx: OK"
else
    print_warning "Nginx: Verificar configuración"
fi

# =============================================================================
# RESUMEN
# =============================================================================
print_header "INSTALACIÓN COMPLETADA"

echo -e "${GREEN}✅ Sistema instalado correctamente${NC}\n"

echo "📊 Información del Sistema:"
echo "  - Base de datos: ricoh_fleet_prod"
echo "  - Usuario BD: ricoh_prod"
echo "  - Redis: localhost:6379"
echo "  - Backend: http://localhost:8000"
echo "  - Dominio: http://$DOMAIN"
echo ""

echo "🔐 Credenciales (guardadas en archivos seguros):"
echo "  - DB Password: ~/.ricoh_db_password"
echo "  - Redis Password: ~/.ricoh_redis_password"
echo "  - .env: $PROJECT_DIR/backend/.env"
echo ""

echo "📝 Comandos Útiles:"
echo "  - Ver logs backend: sudo supervisorctl tail -f ricoh-backend"
echo "  - Reiniciar backend: sudo supervisorctl restart ricoh-backend"
echo "  - Ver logs nginx: sudo tail -f /var/log/nginx/access.log"
echo "  - Verificar Redis: redis-cli -a \$(cat ~/.ricoh_redis_password) ping"
echo ""

echo "🔍 Verificar instalación:"
echo "  cd $PROJECT_DIR/backend"
echo "  source venv/bin/activate"
echo "  python verify_production_config.py"
echo ""

echo "🚀 Próximos pasos:"
echo "  1. Configurar SSL/HTTPS con Let's Encrypt"
echo "  2. Configurar firewall (ufw)"
echo "  3. Configurar backups automáticos"
echo "  4. Configurar monitoreo"
echo ""

print_success "¡Instalación completada!"
