# Guía de Deployment - Ricoh Suite

## 📋 Resumen

Esta guía describe el proceso completo de deployment del sistema de autenticación de Ricoh Suite a producción.

---

## ⚙️ Requisitos Previos

### Software Requerido
- Python 3.11+
- PostgreSQL 16+
- Node.js 20+ (para frontend)
- Nginx o Apache (servidor web)
- Certificado SSL/TLS válido

### Accesos Necesarios
- Acceso SSH al servidor de producción
- Acceso a la base de datos PostgreSQL
- Permisos de administrador en el servidor

---

## 🚀 Proceso de Deployment

### Fase 1: Preparación

#### 1.1 Backup de Base de Datos

```bash
# Crear backup completo
pg_dump -U ricoh_admin -h localhost ricoh_fleet > backup_$(date +%Y%m%d_%H%M%S).sql

# Verificar backup
ls -lh backup_*.sql
```

#### 1.2 Configurar Variables de Entorno

Crear archivo `.env` en producción:

```bash
# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://ricoh_admin:SECURE_PASSWORD@localhost:5432/ricoh_fleet

# JWT
SECRET_KEY=GENERATE_SECURE_KEY_HERE_MINIMUM_32_CHARACTERS

# API
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=https://ricoh.tuempresa.com,https://www.ricoh.tuempresa.com

# Session Cleanup
ENABLE_SESSION_CLEANUP=true

# Encryption
ENCRYPTION_KEY=GENERATE_ENCRYPTION_KEY_HERE
```

**Generar SECRET_KEY seguro:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Generar ENCRYPTION_KEY:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### 1.3 Notificar Usuarios

Enviar notificación a usuarios sobre mantenimiento programado:
- Fecha y hora del mantenimiento
- Duración estimada (30-60 minutos)
- Impacto esperado (sistema no disponible)

---

### Fase 2: Deployment Automatizado

#### 2.1 Usar Script de Deployment

**Linux/Mac:**
```bash
cd backend
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**Windows:**
```bash
cd backend
scripts\deploy.bat
```

El script ejecutará automáticamente:
1. ✅ Verificación de configuración
2. 💾 Backup de base de datos
3. 🗄️ Ejecución de migraciones
4. 📦 Instalación de dependencias
5. 🧪 Tests (opcional)
6. 🔄 Reinicio de servicios
7. ✅ Verificación de deployment

---

### Fase 3: Deployment Manual (Alternativa)

Si prefieres deployment manual:

#### 3.1 Backup

```bash
pg_dump -U ricoh_admin -h localhost ricoh_fleet > backup_pre_deploy.sql
```

#### 3.2 Ejecutar Migraciones

```bash
cd backend
python scripts/run_migrations.py
```

Verificar que las migraciones se ejecutaron correctamente:
```sql
SELECT * FROM alembic_version;  -- Si usas Alembic
-- O verificar que las tablas existen
\dt
```

#### 3.3 Instalar Dependencias

```bash
pip install -r requirements.txt
```

#### 3.4 Ejecutar Tests (Opcional)

```bash
python -m pytest tests/ -v
```

#### 3.5 Reiniciar Servicios

**Systemd (Linux):**
```bash
sudo systemctl restart ricoh-api
sudo systemctl status ricoh-api
```

**PM2 (Node.js process manager):**
```bash
pm2 restart ricoh-api
pm2 status
```

**Manual:**
```bash
# Detener proceso actual
pkill -f "uvicorn main:app"

# Iniciar nuevo proceso
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

---

### Fase 4: Configuración de Servidor Web

#### 4.1 Nginx Configuration

Crear archivo `/etc/nginx/sites-available/ricoh`:

```nginx
server {
    listen 80;
    server_name ricoh.tuempresa.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ricoh.tuempresa.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/ricoh.crt;
    ssl_certificate_key /etc/ssl/private/ricoh.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend
    location / {
        root /var/www/ricoh/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Activar configuración:
```bash
sudo ln -s /etc/nginx/sites-available/ricoh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4.2 Apache Configuration

Crear archivo `/etc/apache2/sites-available/ricoh.conf`:

```apache
<VirtualHost *:80>
    ServerName ricoh.tuempresa.com
    Redirect permanent / https://ricoh.tuempresa.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName ricoh.tuempresa.com
    
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/ricoh.crt
    SSLCertificateKeyFile /etc/ssl/private/ricoh.key
    
    # Security Headers
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "DENY"
    Header always set X-XSS-Protection "1; mode=block"
    
    # Backend API
    ProxyPass /api http://localhost:8000/api
    ProxyPassReverse /api http://localhost:8000/api
    
    # Frontend
    DocumentRoot /var/www/ricoh/frontend/dist
    <Directory /var/www/ricoh/frontend/dist>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

Activar configuración:
```bash
sudo a2ensite ricoh
sudo a2enmod ssl proxy proxy_http headers
sudo apache2ctl configtest
sudo systemctl reload apache2
```

---

### Fase 5: Verificación Post-Deployment

#### 5.1 Verificar API

```bash
# Health check
curl https://ricoh.tuempresa.com/api/

# Login test
curl -X POST https://ricoh.tuempresa.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"superadmin","password":"YOUR_PASSWORD"}'
```

#### 5.2 Verificar Base de Datos

```sql
-- Verificar tablas
\dt

-- Verificar superadmin
SELECT username, rol, is_active FROM admin_users WHERE rol = 'superadmin';

-- Verificar sesiones activas
SELECT COUNT(*) FROM admin_sessions WHERE expires_at > NOW();
```

#### 5.3 Verificar Logs

```bash
# Ver logs en tiempo real
tail -f logs/ricoh_api.log

# Buscar errores
grep ERROR logs/ricoh_api.log

# Buscar warnings
grep WARNING logs/ricoh_api.log
```

#### 5.4 Verificar HTTPS

```bash
# Verificar certificado SSL
openssl s_client -connect ricoh.tuempresa.com:443 -servername ricoh.tuempresa.com

# Verificar headers de seguridad
curl -I https://ricoh.tuempresa.com/
```

---

### Fase 6: Monitoreo Post-Deployment

#### 6.1 Monitorear por 1 Hora

- [ ] Verificar logs cada 10 minutos
- [ ] Probar login con diferentes usuarios
- [ ] Probar creación de recursos
- [ ] Verificar que no hay errores 500
- [ ] Verificar que rate limiting funciona
- [ ] Verificar que sesiones se crean correctamente

#### 6.2 Métricas a Monitorear

- **Requests por minuto**: Debe ser estable
- **Tiempo de respuesta**: < 500ms promedio
- **Errores 4xx**: < 5% de requests
- **Errores 5xx**: 0%
- **Sesiones activas**: Crecimiento gradual
- **Uso de CPU**: < 70%
- **Uso de memoria**: < 80%
- **Uso de disco**: < 80%

---

## 🔄 Rollback

Si algo sale mal, seguir estos pasos:

### 1. Detener Servicios

```bash
sudo systemctl stop ricoh-api
```

### 2. Restaurar Backup

```bash
psql -U ricoh_admin -h localhost ricoh_fleet < backup_pre_deploy.sql
```

### 3. Revertir Código

```bash
git checkout <previous_commit>
```

### 4. Reiniciar Servicios

```bash
sudo systemctl start ricoh-api
```

### 5. Verificar

```bash
curl https://ricoh.tuempresa.com/api/
```

---

## 📊 Checklist de Deployment

### Pre-Deployment
- [ ] Backup de base de datos creado
- [ ] Variables de entorno configuradas
- [ ] SECRET_KEY generado (32+ caracteres)
- [ ] ENCRYPTION_KEY generado
- [ ] CORS_ORIGINS configurado con dominios de producción
- [ ] Certificado SSL válido instalado
- [ ] Usuarios notificados sobre mantenimiento

### Deployment
- [ ] Migraciones ejecutadas exitosamente
- [ ] Dependencias instaladas
- [ ] Tests ejecutados (opcional)
- [ ] Servicios reiniciados
- [ ] API respondiendo correctamente

### Post-Deployment
- [ ] Login con superadmin funciona
- [ ] Endpoints principales funcionan
- [ ] HTTPS funciona correctamente
- [ ] Headers de seguridad presentes
- [ ] Logs no muestran errores críticos
- [ ] Monitoreo activo por 1 hora
- [ ] Usuarios notificados que sistema está disponible

---

## 🛡️ Seguridad en Producción

### Checklist de Seguridad
- [ ] HTTPS habilitado y forzado
- [ ] Certificado SSL válido y no expirado
- [ ] SECRET_KEY único y seguro (32+ caracteres)
- [ ] CORS configurado solo con dominios autorizados
- [ ] Headers de seguridad configurados (HSTS, X-Frame-Options, etc.)
- [ ] Rate limiting activo
- [ ] Logs no contienen datos sensibles
- [ ] Base de datos con contraseña fuerte
- [ ] Firewall configurado (solo puertos necesarios abiertos)
- [ ] Acceso SSH con clave pública (no contraseña)
- [ ] Actualizaciones de seguridad del sistema operativo aplicadas

---

## 📞 Soporte

### En Caso de Problemas

1. **Revisar logs**: `tail -f logs/ricoh_api.log`
2. **Revisar audit_log**: Query a tabla `admin_audit_log`
3. **Verificar servicios**: `systemctl status ricoh-api`
4. **Verificar base de datos**: `psql -U ricoh_admin ricoh_fleet`
5. **Contactar equipo de desarrollo**: Si el problema persiste

### Información para Reportar Bugs

- Descripción del problema
- Pasos para reproducir
- Logs relevantes
- Timestamp del incidente
- Usuarios afectados
- Impacto en el sistema

---

**Última actualización**: 20 de Marzo de 2026  
**Versión**: 1.0.0

