#!/bin/bash

# =============================================================================
# Ricoh Equipment Management - Ubuntu Server Setup Script
# =============================================================================
# This script prepares an Ubuntu 22.04/24.04 server for production deployment
# Run as root or with sudo

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root or with sudo"
    exit 1
fi

log_step "🚀 Ricoh Equipment Management - Ubuntu Server Setup"

# Step 1: Update system
log_step "📦 Step 1: Updating system packages"
apt-get update
apt-get upgrade -y
log_info "System updated"

# Step 2: Install Docker
log_step "🐳 Step 2: Installing Docker"

if command -v docker &> /dev/null; then
    log_info "Docker already installed: $(docker --version)"
else
    log_info "Installing Docker..."
    
    # Install prerequisites
    apt-get install -y ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Set up repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    log_info "Docker installed: $(docker --version)"
fi

# Step 3: Install Docker Compose
log_step "🔧 Step 3: Verifying Docker Compose"

if command -v docker-compose &> /dev/null; then
    log_info "Docker Compose already installed: $(docker-compose --version)"
else
    log_info "Installing Docker Compose..."
    apt-get install -y docker-compose
    log_info "Docker Compose installed: $(docker-compose --version)"
fi

# Step 4: Configure firewall
log_step "🔥 Step 4: Configuring UFW firewall"

if command -v ufw &> /dev/null; then
    # Allow SSH
    ufw allow 22/tcp
    log_info "SSH (22) allowed"
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    log_info "HTTP (80) and HTTPS (443) allowed"
    
    # Enable firewall if not already enabled
    ufw --force enable
    log_info "Firewall configured and enabled"
else
    log_warn "UFW not installed, skipping firewall configuration"
fi

# Step 5: Create application directory
log_step "📁 Step 5: Creating application directory"

APP_DIR="/opt/ricoh"
mkdir -p "$APP_DIR"
log_info "Application directory created: $APP_DIR"

# Step 6: Install additional tools
log_step "🛠️  Step 6: Installing additional tools"

apt-get install -y \
    git \
    htop \
    vim \
    curl \
    wget \
    certbot \
    python3-certbot-nginx
log_info "Additional tools installed"

# Step 7: Configure Docker to start on boot
log_step "⚙️  Step 7: Configuring Docker service"

systemctl enable docker
systemctl start docker
log_info "Docker service enabled and started"

# Step 8: Create deployment user
log_step "👤 Step 8: Creating deployment user"

if id "ricoh" &>/dev/null; then
    log_info "User 'ricoh' already exists"
else
    useradd -m -s /bin/bash ricoh
    usermod -aG docker ricoh
    log_info "User 'ricoh' created and added to docker group"
fi

# Step 9: Set up log rotation
log_step "📝 Step 9: Configuring log rotation"

cat > /etc/logrotate.d/ricoh << 'EOF'
/opt/ricoh/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ricoh ricoh
    sharedscripts
    postrotate
        docker exec ricoh-backend kill -USR1 1 2>/dev/null || true
    endscript
}
EOF

log_info "Log rotation configured"

# Step 10: Create systemd service
log_step "🔄 Step 10: Creating systemd service"

cat > /etc/systemd/system/ricoh.service << EOF
[Unit]
Description=Ricoh Equipment Management Suite
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ricoh
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
User=ricoh
Group=ricoh

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ricoh.service
log_info "Systemd service created and enabled"

# Step 11: Configure system limits
log_step "⚡ Step 11: Configuring system limits"

cat >> /etc/security/limits.conf << 'EOF'

# Ricoh application limits
ricoh soft nofile 65536
ricoh hard nofile 65536
ricoh soft nproc 4096
ricoh hard nproc 4096
EOF

log_info "System limits configured"

# Step 12: Configure sysctl for production
log_step "🔧 Step 12: Configuring kernel parameters"

cat >> /etc/sysctl.conf << 'EOF'

# Ricoh production optimizations
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.ip_local_port_range = 10000 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
EOF

sysctl -p
log_info "Kernel parameters configured"

# Summary
log_step "✅ Setup Complete"

echo ""
echo "================================================================================"
echo "                    Ubuntu Server Setup Completed"
echo "================================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Clone your repository to /opt/ricoh:"
echo "   cd /opt/ricoh"
echo "   git clone <your-repo-url> ."
echo ""
echo "2. Create .env.production file:"
echo "   cp deployment/.env.production.example .env.production"
echo "   nano .env.production  # Edit with your production values"
echo ""
echo "3. Generate SSL certificates with Let's Encrypt:"
echo "   certbot certonly --standalone -d your-domain.com -d api.your-domain.com"
echo "   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem deployment/ssl/"
echo "   cp /etc/letsencrypt/live/your-domain.com/privkey.pem deployment/ssl/"
echo ""
echo "4. Generate production secrets:"
echo "   python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
echo "   python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
echo ""
echo "5. Update deployment/nginx/conf.d/ricoh.conf:"
echo "   Replace \${DOMAIN_NAME} and \${API_DOMAIN} with your actual domains"
echo ""
echo "6. Start the application:"
echo "   cd /opt/ricoh"
echo "   docker-compose -f deployment/docker-compose.prod.yml up -d"
echo ""
echo "7. Verify deployment:"
echo "   python3 backend/scripts/verify_deployment.py"
echo ""
echo "8. Monitor logs:"
echo "   docker logs -f ricoh-backend"
echo "   docker logs -f ricoh-nginx"
echo ""
echo "================================================================================"
echo ""
