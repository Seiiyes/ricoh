# Quick Start - Deployment en Ubuntu Server

Guía rápida para desplegar Ricoh Equipment Management en producción.

## Comandos Rápidos

### 1. Setup Inicial (una sola vez)

```bash
# Como root
sudo bash deployment/setup-ubuntu-server.sh
```

### 2. Clonar y Configurar

```bash
cd /opt/ricoh
git clone <your-repo> .
cp deployment/.env.production.example .env.production
nano .env.production  # Configurar variables
```

### 3. Generar Claves

```bash
# ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. SSL Certificates

```bash
sudo certbot certonly --standalone -d tu-dominio.com -d api.tu-dominio.com
sudo cp /etc/letsencrypt/live/tu-dominio.com/*.pem deployment/ssl/
```

### 5. Deploy

```bash
bash deployment/deploy-production.sh
```

### 6. Inicializar DB

```bash
docker exec ricoh-backend python scripts/init_db.py
docker exec ricoh-backend python scripts/init_superadmin.py
```

### 7. Verificar

```bash
docker exec ricoh-backend python scripts/verify_deployment.py
bash deployment/verify-security-fixes.sh
```

## Verificación Rápida de Seguridad

```bash
# Ver logs de seguridad
docker logs ricoh-backend 2>&1 | grep -E "✅|🛡️|🔴"
```

Debes ver:
- ✅ Servicio de encriptación inicializado
- 🛡️ CSRF Protection enabled
- 🔴 CSRF usando Redis
- 🔴 Rate Limiter usando Redis

## Documentación Completa

Ver `DEPLOYMENT_GUIDE.md` para guía detallada paso a paso.
