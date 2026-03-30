#!/bin/bash

# =============================================================================
# Ricoh Equipment Management - Production Deployment Script
# =============================================================================
# This script deploys the application to production with all security fixes
# Run from /opt/ricoh directory as ricoh user

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_step() { echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n${BLUE}$1${NC}\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"; }

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/ricoh_backup_pre_deploy_${TIMESTAMP}.sql"
ENV_FILE=".env.production"

log_step "🚀 Ricoh Equipment Management - Production Deployment"

# Pre-flight checks
log_step "📋 Step 1: Pre-deployment checks"

# Check if running from correct directory
if [ ! -f "docker-compose.yml" ]; then
    log_error "Must run from /opt/ricoh directory"
    exit 1
fi
log_info "Running from correct directory"

# Check if .env.production exists
if [ ! -f "$ENV_FILE" ]; then
    log_error "$ENV_FILE not found!"
    echo "Create it from: cp deployment/.env.production.example $ENV_FILE"
    exit 1
fi
log_info "$ENV_FILE found"

# Check critical environment variables
source "$ENV_FILE"

if [ -z "$ENCRYPTION_KEY" ] || [ "$ENCRYPTION_KEY" = "GENERATE_NEW_KEY_FOR_PRODUCTION" ]; then
    log_error "ENCRYPTION_KEY not configured in $ENV_FILE"
    echo "Generate with: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    exit 1
fi
log_info "ENCRYPTION_KEY configured"

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "GENERATE_NEW_KEY_FOR_PRODUCTION" ]; then
    log_error "SECRET_KEY not configured in $ENV_FILE"
    echo "Generate with: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
    exit 1
fi
log_info "SECRET_KEY configured"

if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "CHANGE_THIS_STRONG_PASSWORD_FOR_PRODUCTION" ]; then
    log_error "POSTGRES_PASSWORD not configured in $ENV_FILE"
    exit 1
fi
log_info "POSTGRES_PASSWORD configured"

if [ -z "$REDIS_PASSWORD" ] || [ "$REDIS_PASSWORD" = "CHANGE_THIS_REDIS_PASSWORD_FOR_PRODUCTION" ]; then
    log_error "REDIS_PASSWORD not configured in $ENV_FILE"
    exit 1
fi
log_info "REDIS_PASSWORD configured"

# Check if SSL certificates exist
if [ ! -f "deployment/ssl/fullchain.pem" ] || [ ! -f "deployment/ssl/privkey.pem" ]; then
    log_warn "SSL certificates not found in deployment/ssl/"
    log_warn "Application will start but HTTPS won't work"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    log_info "SSL certificates found"
fi

# Create backup
log_step "💾 Step 2: Creating database backup"

mkdir -p "$BACKUP_DIR"

if docker ps | grep -q ricoh-postgres; then
    log_info "Creating backup: $BACKUP_FILE"
    docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > "$BACKUP_FILE" 2>/dev/null || log_warn "Backup failed (database may not exist yet)"
    
    if [ -f "$BACKUP_FILE" ]; then
        gzip "$BACKUP_FILE"
        log_info "Backup created: ${BACKUP_FILE}.gz ($(du -h "${BACKUP_FILE}.gz" | cut -f1))"
    fi
else
    log_warn "PostgreSQL not running, skipping backup"
fi

# Pull latest code
log_step "📥 Step 3: Pulling latest code"

log_info "Fetching latest changes..."
git fetch origin

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
log_info "Current branch: $CURRENT_BRANCH"

read -p "Pull latest changes from origin/$CURRENT_BRANCH? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git pull origin "$CURRENT_BRANCH"
    log_info "Code updated"
else
    log_warn "Skipping code update"
fi

# Build images
log_step "🏗️  Step 4: Building Docker images"

log_info "Building production images..."
docker-compose -f deployment/docker-compose.prod.yml build --no-cache

log_info "Images built successfully"

# Stop services
log_step "🛑 Step 5: Stopping current services"

if docker ps | grep -q ricoh-backend; then
    log_info "Stopping services..."
    docker-compose -f deployment/docker-compose.prod.yml down
    log_info "Services stopped"
else
    log_info "No services running"
fi

# Start services
log_step "🚀 Step 6: Starting production services"

log_info "Starting services..."
docker-compose -f deployment/docker-compose.prod.yml --env-file "$ENV_FILE" up -d

log_info "Waiting for services to be healthy..."
sleep 10

# Check service health
log_step "🏥 Step 7: Checking service health"

SERVICES=("ricoh-postgres" "ricoh-redis" "ricoh-backend" "ricoh-nginx")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
        log_info "$service is running"
    else
        log_error "$service is not running"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = false ]; then
    log_error "Some services failed to start"
    echo ""
    echo "Check logs with:"
    echo "  docker logs ricoh-backend"
    echo "  docker logs ricoh-postgres"
    echo "  docker logs ricoh-redis"
    exit 1
fi

# Verify security configurations
log_step "🔒 Step 8: Verifying security configurations"

log_info "Checking ENCRYPTION_KEY..."
docker exec ricoh-backend python -c "import os; assert os.getenv('ENCRYPTION_KEY'), 'ENCRYPTION_KEY not set'" && log_info "ENCRYPTION_KEY: OK" || log_error "ENCRYPTION_KEY: FAIL"

log_info "Checking security logs..."
sleep 5

# Check for security initialization messages
if docker logs ricoh-backend 2>&1 | grep -q "Servicio de encriptación inicializado"; then
    log_info "Encryption service: ✅ Initialized"
else
    log_warn "Encryption service: Not initialized (check logs)"
fi

if docker logs ricoh-backend 2>&1 | grep -q "CSRF Protection enabled"; then
    log_info "CSRF Protection: ✅ Enabled"
else
    log_warn "CSRF Protection: Not enabled (check ENVIRONMENT variable)"
fi

if docker logs ricoh-backend 2>&1 | grep -q "Redis para almacenamiento"; then
    log_info "Redis Storage: ✅ Configured"
else
    log_warn "Redis Storage: Not configured (check REDIS_URL)"
fi

# Test API endpoint
log_step "🧪 Step 9: Testing API endpoint"

log_info "Testing health endpoint..."
sleep 3

if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    log_info "API health check: ✅ OK"
else
    log_error "API health check: ❌ FAIL"
    echo "Check logs: docker logs ricoh-backend"
fi

# Summary
log_step "✅ Deployment Summary"

echo ""
echo "================================================================================"
echo "                    Deployment Completed Successfully"
echo "================================================================================"
echo ""
echo "Services Status:"
docker-compose -f deployment/docker-compose.prod.yml ps
echo ""
echo "Next steps:"
echo ""
echo "1. Initialize database (if first deployment):"
echo "   docker exec ricoh-backend python scripts/init_db.py"
echo ""
echo "2. Create superadmin user (if first deployment):"
echo "   docker exec ricoh-backend python scripts/init_superadmin.py"
echo "   docker exec ricoh-backend cat .superadmin_password"
echo ""
echo "3. Verify deployment:"
echo "   docker exec ricoh-backend python scripts/verify_deployment.py"
echo ""
echo "4. Monitor logs:"
echo "   docker logs -f ricoh-backend"
echo ""
echo "5. Test application:"
echo "   curl https://api.${DOMAIN_NAME}/health"
echo "   curl https://${DOMAIN_NAME}/"
echo ""
echo "Backup location: ${BACKUP_FILE}.gz"
echo ""
echo "================================================================================"
echo ""
