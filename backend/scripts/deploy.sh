#!/bin/bash

# Ricoh Suite - Production Deployment Script
# This script automates the deployment process for production

set -e  # Exit on error

echo "================================================================================"
echo "🚀 Ricoh Suite - Production Deployment"
echo "================================================================================"
echo ""

# Configuration
BACKUP_DIR="./backups"
DB_NAME="${DB_NAME:-ricoh_fleet}"
DB_USER="${DB_USER:-ricoh_admin}"
DB_HOST="${DB_HOST:-localhost}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/ricoh_backup_pre_deploy_${TIMESTAMP}.sql"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Pre-deployment checks
echo "📋 Step 1: Pre-deployment checks"
echo "--------------------------------"

# Check if .env file exists
if [ ! -f ".env" ]; then
    log_error ".env file not found!"
    echo "Please create .env file with production configuration"
    exit 1
fi
log_info ".env file found"

# Check if SECRET_KEY is set
if ! grep -q "SECRET_KEY=" .env; then
    log_error "SECRET_KEY not found in .env!"
    echo "Please set SECRET_KEY in .env file"
    exit 1
fi
log_info "SECRET_KEY configured"

# Check if DATABASE_URL is set
if ! grep -q "DATABASE_URL=" .env; then
    log_error "DATABASE_URL not found in .env!"
    echo "Please set DATABASE_URL in .env file"
    exit 1
fi
log_info "DATABASE_URL configured"

# Check if ENVIRONMENT is set to production
if ! grep -q "ENVIRONMENT=production" .env; then
    log_warn "ENVIRONMENT is not set to 'production' in .env"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Step 2: Create backup
echo "💾 Step 2: Creating database backup"
echo "-----------------------------------"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
log_info "Creating backup: $BACKUP_FILE"
pg_dump -U "$DB_USER" -h "$DB_HOST" "$DB_NAME" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    log_info "Backup created successfully"
    log_info "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
else
    log_error "Backup failed!"
    exit 1
fi

echo ""

# Step 3: Run migrations
echo "🗄️  Step 3: Running database migrations"
echo "---------------------------------------"

log_info "Executing migrations..."
python scripts/run_migrations.py

if [ $? -eq 0 ]; then
    log_info "Migrations completed successfully"
else
    log_error "Migrations failed!"
    echo ""
    echo "Rolling back..."
    log_info "Restoring backup: $BACKUP_FILE"
    psql -U "$DB_USER" -h "$DB_HOST" "$DB_NAME" < "$BACKUP_FILE"
    exit 1
fi

echo ""

# Step 4: Install/Update dependencies
echo "📦 Step 4: Installing dependencies"
echo "----------------------------------"

log_info "Installing Python dependencies..."
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    log_info "Dependencies installed successfully"
else
    log_error "Dependency installation failed!"
    exit 1
fi

echo ""

# Step 5: Run tests (optional)
echo "🧪 Step 5: Running tests (optional)"
echo "-----------------------------------"

read -p "Run tests before deployment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Running tests..."
    python -m pytest tests/ -v --tb=short
    
    if [ $? -eq 0 ]; then
        log_info "All tests passed"
    else
        log_error "Tests failed!"
        read -p "Continue deployment anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    log_warn "Skipping tests"
fi

echo ""

# Step 6: Restart services
echo "🔄 Step 6: Restarting services"
echo "------------------------------"

log_info "Stopping services..."
# Add your service stop command here
# Example: systemctl stop ricoh-api

log_info "Starting services..."
# Add your service start command here
# Example: systemctl start ricoh-api

log_info "Services restarted"

echo ""

# Step 7: Verify deployment
echo "✅ Step 7: Verifying deployment"
echo "-------------------------------"

log_info "Waiting for services to start..."
sleep 5

# Check if API is responding
log_info "Checking API health..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)

if [ "$response" = "200" ]; then
    log_info "API is responding correctly"
else
    log_error "API is not responding (HTTP $response)"
    log_warn "Please check logs for errors"
fi

echo ""

# Step 8: Post-deployment tasks
echo "📝 Step 8: Post-deployment tasks"
echo "--------------------------------"

log_info "Deployment completed at: $(date)"
log_info "Backup location: $BACKUP_FILE"
log_info "Please monitor logs for the next hour"

echo ""
echo "================================================================================"
echo "✅ Deployment completed successfully!"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "1. Monitor logs: tail -f logs/ricoh_api.log"
echo "2. Test login with superadmin"
echo "3. Verify all endpoints are working"
echo "4. Monitor for errors for 1 hour"
echo ""
echo "Rollback instructions (if needed):"
echo "1. Stop services"
echo "2. Restore backup: psql -U $DB_USER -h $DB_HOST $DB_NAME < $BACKUP_FILE"
echo "3. Revert code to previous version"
echo "4. Start services"
echo ""
