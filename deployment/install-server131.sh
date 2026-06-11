#!/bin/bash
# =============================================================================
# SCRIPT DE INSTALACIÓN - Ricoh Equipment Management Suite
# Servidor: 192.168.91.131 (odootic)
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅ $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️  $1${NC}"; }
error() { echo -e "${RED}[$(date '+%H:%M:%S')] ❌ $1${NC}"; exit 1; }

echo ""
echo "============================================================"
echo "  🖨️  Ricoh Equipment Management Suite - Deploy Server 131"
echo "============================================================"
echo ""

# --- 1. Verificar Docker ---
log "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    warn "Docker no está instalado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    sudo systemctl enable docker
    sudo systemctl start docker
    log "Docker instalado exitosamente"
else
    DOCKER_VER=$(docker --version)
    log "Docker encontrado: $DOCKER_VER"
fi

# --- 2. Verificar Docker Compose ---
log "Verificando Docker Compose..."
if ! docker compose version &> /dev/null; then
    warn "Docker Compose plugin no disponible. Intentando docker-compose..."
    if ! command -v docker-compose &> /dev/null; then
        warn "Instalando Docker Compose plugin..."
        sudo apt-get update -q
        sudo apt-get install -y docker-compose-plugin
    fi
fi
log "Docker Compose disponible"

# --- 3. Verificar Git ---
log "Verificando Git..."
if ! command -v git &> /dev/null; then
    warn "Git no está instalado. Instalando..."
    sudo apt-get update -q && sudo apt-get install -y git
fi
log "Git disponible"

# --- 4. Crear directorio de instalación ---
INSTALL_DIR="$HOME/ricoh-app"
log "Directorio de instalación: $INSTALL_DIR"

if [ -d "$INSTALL_DIR" ]; then
    warn "El directorio ya existe. Actualizando..."
    cd "$INSTALL_DIR"
    # Si hay archivos copiados manualmente, no usar git pull
    log "Directorio existente detectado, usando archivos presentes"
else
    mkdir -p "$INSTALL_DIR"
    log "Directorio creado"
fi

cd "$INSTALL_DIR"

# --- 5. Copiar docker-compose específico del servidor ---
if [ -f "deployment/docker-compose.server131.yml" ]; then
    cp deployment/docker-compose.server131.yml docker-compose.yml
    log "docker-compose.yml actualizado para servidor 131"
fi

# --- 6. Detener contenedores previos ---
log "Deteniendo contenedores previos (si existen)..."
docker compose down --remove-orphans 2>/dev/null || true

# --- 7. Limpiar imágenes obsoletas ---
log "Limpiando imágenes obsoletas..."
docker image prune -f 2>/dev/null || true

# --- 8. Construir e iniciar servicios ---
log "Construyendo e iniciando todos los servicios..."
docker compose up --build -d

# --- 9. Esperar que los servicios estén listos ---
log "Esperando que los servicios se inicialicen (60 segundos)..."
sleep 60

# --- 10. Verificar estado ---
echo ""
echo "============================================================"
echo "  Estado de los Contenedores"
echo "============================================================"
docker compose ps

# --- 11. Verificar health del backend ---
log "Verificando salud del backend..."
MAX_RETRIES=10
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        log "Backend responde correctamente (HTTP 200)"
        break
    fi
    RETRY=$((RETRY + 1))
    warn "Backend no disponible aún (intento $RETRY/$MAX_RETRIES, código: $HTTP_CODE). Esperando 10s..."
    sleep 10
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    warn "El backend tardó más de lo esperado. Revisa los logs con: docker compose logs backend"
fi

# --- 12. Mostrar información de acceso ---
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "============================================================"
echo -e "  ${GREEN}✅ DESPLIEGUE COMPLETADO${NC}"
echo "============================================================"
echo ""
echo "  🌐 Frontend:  http://$SERVER_IP:5173"
echo "  🔧 Backend:   http://$SERVER_IP:8000"
echo "  📖 API Docs:  http://$SERVER_IP:8000/docs"
echo ""
echo "  Comandos útiles:"
echo "  - Ver logs:       docker compose logs -f"
echo "  - Reiniciar:      docker compose restart"
echo "  - Detener todo:   docker compose down"
echo ""
echo "============================================================"
