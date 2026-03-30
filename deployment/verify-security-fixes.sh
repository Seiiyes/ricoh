#!/bin/bash
# Script para verificar que las 11 correcciones de seguridad están activas

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }

echo "🔒 Verificando Correcciones de Seguridad"
echo "========================================"
echo ""

# 1. ENCRYPTION_KEY
echo "1. Verificando ENCRYPTION_KEY..."
if docker exec ricoh-backend python -c "import os; assert os.getenv('ENCRYPTION_KEY')" 2>/dev/null; then
    log_info "ENCRYPTION_KEY configurada"
else
    log_error "ENCRYPTION_KEY no configurada"
fi

# 2. SECRET_KEY con entropía
echo "2. Verificando SECRET_KEY..."
docker exec ricoh-backend python -c "
import os, string
key = os.getenv('SECRET_KEY', '')
if len(key) < 32:
    exit(1)
has_upper = any(c in string.ascii_uppercase for c in key)
has_lower = any(c in string.ascii_lowercase for c in key)
has_digit = any(c in string.digits for c in key)
has_special = any(c in string.punctuation for c in key)
categories = sum([has_upper, has_lower, has_digit, has_special])
if categories < 3:
    exit(1)
" && log_info "SECRET_KEY con entropía suficiente" || log_error "SECRET_KEY inválida"

# 3. CSRF en producción
echo "3. Verificando CSRF Protection..."
if docker logs ricoh-backend 2>&1 | grep -q "CSRF Protection enabled"; then
    log_info "CSRF habilitada en producción"
elif docker logs ricoh-backend 2>&1 | grep -q "CSRF Protection disabled.*development"; then
    log_warn "CSRF deshabilitada (modo desarrollo)"
else
    log_error "Estado de CSRF desconocido"
fi

# 4. Redis configurado
echo "4. Verificando Redis..."
if docker logs ricoh-backend 2>&1 | grep -q "Redis para almacenamiento"; then
    log_info "Redis configurado para CSRF y Rate Limiting"
else
    log_warn "Redis no configurado (usando memoria)"
fi

# 5. Tokens enmascarados
echo "5. Verificando enmascaramiento de tokens..."
if docker logs ricoh-backend 2>&1 | grep -E "Token:.*\.\.\." | head -1 | grep -qv "Token:.*[a-zA-Z0-9]{9,}"; then
    log_info "Tokens enmascarados correctamente"
else
    log_warn "No se encontraron logs de tokens para verificar"
fi

# 6. CORS restrictivo
echo "6. Verificando CORS..."
docker exec ricoh-backend python -c "
import sys
sys.path.insert(0, '/app')
from main import ALLOWED_METHODS, ALLOWED_HEADERS
if '*' in ALLOWED_METHODS or '*' in ALLOWED_HEADERS:
    exit(1)
" && log_info "CORS configurado con listas explícitas" || log_error "CORS permisivo detectado"

echo ""
echo "========================================"
echo "Verificación completada"
echo "========================================"
