# 🔒 Diferencias: Local vs Producción

**Proyecto**: Ricoh Fleet Management  
**Fecha**: 6 de Mayo 2026  
**Versión**: 1.0

---

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Configuración de Seguridad](#configuración-de-seguridad)
3. [Variables de Entorno](#variables-de-entorno)
4. [Servicios y Puertos](#servicios-y-puertos)
5. [Checklist de Cambios](#checklist-de-cambios)
6. [Comandos de Migración](#comandos-de-migración)

---

## 🎯 Resumen Ejecutivo

| Aspecto | Local (Desarrollo) | Producción |
|---------|-------------------|------------|
| **Propósito** | Desarrollo y pruebas | Servicio 24/7 |
| **Seguridad** | Relajada | Máxima |
| **Performance** | Básica | Optimizada |
| **Disponibilidad** | Solo cuando PC encendida | 24/7 |
| **Acceso** | Red local | Internet |
| **Backups** | Manual | Automático |
| **Monitoreo** | Logs básicos | Completo |

---

## 🔒 Configuración de Seguridad

### **1. Variables Críticas**

| Variable | Local | Producción | ⚠️ Acción Requerida |
|----------|-------|------------|---------------------|
| **ENVIRONMENT** | `development` | `production` | ✅ CAMBIAR |
| **DEBUG** | `true` | `false` | ✅ CAMBIAR |
| **ENCRYPTION_KEY** | Ejemplo | Nueva única | ✅ GENERAR NUEVA |
| **SECRET_KEY** | Ejemplo | Nueva única | ✅ GENERAR NUEVA |
| **CORS_ORIGINS** | `*` (todos) | Dominios específicos | ✅ RESTRINGIR |
| **REDIS_PASSWORD** | Sin contraseña | Con contraseña | ✅ CONFIGURAR |
| **DB_PASSWORD** | `ricoh_secure_2024` | Nueva segura | ✅ CAMBIAR |

---

### **2. ENVIRONMENT=development vs production**

#### **Local (development):**
```bash
ENVIRONMENT=development
```

**Efectos:**
- ❌ CSRF Protection: **DESHABILITADO**
- ❌ HTTPS Redirect: **DESHABILITADO**
- ✅ Debug Mode: **HABILITADO**
- ✅ Hot Reload: **HABILITADO**
- ✅ Logs detallados: **HABILITADO**
- ⚠️ Errores completos en respuestas

#### **Producción (production):**
```bash
ENVIRONMENT=production
```

**Efectos:**
- ✅ CSRF Protection: **HABILITADO**
- ✅ HTTPS Redirect: **HABILITADO**
- ❌ Debug Mode: **DESHABILITADO**
- ❌ Hot Reload: **DESHABILITADO**
- ⚠️ Logs solo errores críticos
- ✅ Errores genéricos en respuestas

---

### **3. DEBUG=true vs false**

#### **Local (DEBUG=true):**
```python
DEBUG=true
```

**Efectos:**
- ✅ Stack traces completos en errores
- ✅ Logs de todas las queries SQL
- ✅ Información de variables en errores
- ⚠️ **PELIGRO**: Expone información sensible

#### **Producción (DEBUG=false):**
```python
DEBUG=false
```

**Efectos:**
- ✅ Errores genéricos al usuario
- ✅ Stack traces solo en logs
- ✅ No expone información sensible
- ✅ Mejor performance

---

### **4. CORS_ORIGINS**

#### **Local:**
```bash
CORS_ORIGINS=*
```

**Permite:**
- ✅ Cualquier origen puede hacer requests
- ✅ Útil para desarrollo
- ❌ **INSEGURO** para producción

#### **Producción:**
```bash
CORS_ORIGINS=https://ricoh.tuempresa.com,https://www.ricoh.tuempresa.com
```

**Permite:**
- ✅ Solo dominios específicos
- ✅ Previene ataques CSRF
- ✅ Seguro

---

### **5. Claves de Seguridad**

#### **Local (INSEGURO - Solo para desarrollo):**
```bash
ENCRYPTION_KEY=ynVBzh9ZjawHMoUHu0L9ozXT2j8ebujlVxoNzD91xjE=
SECRET_KEY=ricoh-jwt-secret-key-change-in-production-min-32-chars
```

⚠️ **NUNCA usar estas claves en producción**

#### **Producción (GENERAR NUEVAS):**
```bash
# Generar ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Ejemplo de salida:**
```bash
ENCRYPTION_KEY=X8fK9mN2pQ5rT7vY1wZ3bC6dE8gH0jL4nM7pR9sU2xA=
SECRET_KEY=Kj8mN3pQ6rT9vY2wZ5bC8dF1gH4jL7nM0pR3sU6xA9z
```

---

## ⚙️ Variables de Entorno Completas

### **docker-compose.yml (Local)**

```yaml
environment:
  # Application
  - ENVIRONMENT=development          # ⚠️ CAMBIAR en producción
  - DEMO_MODE=false
  - DEBUG=true                       # ⚠️ CAMBIAR en producción
  - API_HOST=0.0.0.0
  - API_PORT=8000
  
  # Database
  - DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@postgres:5432/ricoh_fleet
  
  # Security
  - ENCRYPTION_KEY=ynVBzh9ZjawHMoUHu0L9ozXT2j8ebujlVxoNzD91xjE=  # ⚠️ CAMBIAR
  - SECRET_KEY=ricoh-jwt-secret-key-change-in-production-min-32-chars  # ⚠️ CAMBIAR
  - CORS_ORIGINS=*                   # ⚠️ RESTRINGIR en producción
  
  # Redis
  - REDIS_URL=redis://redis:6379/0   # ⚠️ Agregar contraseña en producción
  - REDIS_HOST=redis
  - REDIS_PORT=6379
  - REDIS_DB=0
  - REDIS_PASSWORD=                  # ⚠️ CONFIGURAR en producción
  - CACHE_TTL_DASHBOARD=300
  - CACHE_TTL_ANALYTICS=3600
```

---

### **.env.production (Producción)**

```bash
# Application
ENVIRONMENT=production               # ✅ CORRECTO
DEMO_MODE=false
DEBUG=false                          # ✅ CORRECTO
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO                       # ✅ CORRECTO

# Database
DATABASE_URL=postgresql://ricoh_prod_user:NUEVA_PASSWORD_SEGURA@postgres:5432/ricoh_fleet_prod

# Security
ENCRYPTION_KEY=GENERAR_NUEVA_AQUI    # ✅ ÚNICA
SECRET_KEY=GENERAR_NUEVA_AQUI        # ✅ ÚNICA
CORS_ORIGINS=https://ricoh.tuempresa.com,https://www.ricoh.tuempresa.com  # ✅ RESTRINGIDO

# Redis
REDIS_URL=redis://:PASSWORD_SEGURA@redis:6379/0  # ✅ CON CONTRASEÑA
REDIS_PASSWORD=PASSWORD_SEGURA       # ✅ CONFIGURADA
CACHE_TTL_DASHBOARD=300
CACHE_TTL_ANALYTICS=3600

# Ricoh
RICOH_ADMIN_PASSWORD=PASSWORD_RICOH  # ✅ CONFIGURADA

# Performance
WORKERS=4

# Backups
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30

# SSL
FORCE_HTTPS=true
```

---

## 🌐 Servicios y Puertos

### **Local (docker-compose.yml)**

| Servicio | Puerto | Acceso | Seguridad |
|----------|--------|--------|-----------|
| Frontend | 5173 | http://localhost:5173 | ⚠️ HTTP |
| Backend | 8000 | http://localhost:8000 | ⚠️ HTTP |
| PostgreSQL | 5432 | localhost:5432 | ⚠️ Expuesto |
| Redis | 6379 | localhost:6379 | ⚠️ Sin contraseña |
| Adminer | 8080 | http://localhost:8080 | ⚠️ Expuesto |

**Características:**
- ✅ Fácil acceso para desarrollo
- ✅ Hot reload habilitado
- ⚠️ Puertos expuestos
- ⚠️ Sin HTTPS
- ⚠️ Sin contraseñas fuertes

---

### **Producción (docker-compose.production.yml)**

| Servicio | Puerto | Acceso | Seguridad |
|----------|--------|--------|-----------|
| Nginx | 80, 443 | https://ricoh.tuempresa.com | ✅ HTTPS |
| Backend | 8000 | Solo interno | ✅ No expuesto |
| PostgreSQL | 5432 | Solo interno | ✅ No expuesto |
| Redis | 6379 | Solo interno | ✅ Con contraseña |
| Adminer | - | No incluido | ✅ Removido |

**Características:**
- ✅ Solo Nginx expuesto (80, 443)
- ✅ HTTPS obligatorio
- ✅ Servicios internos no accesibles
- ✅ Contraseñas fuertes
- ✅ Firewall configurado

---

## 📊 Comparativa Detallada

### **Redis**

| Aspecto | Local | Producción |
|---------|-------|------------|
| **Contraseña** | ❌ Sin contraseña | ✅ Con contraseña |
| **Comando** | `redis-server` | `redis-server --requirepass PASSWORD` |
| **Acceso** | Público | Solo red interna |
| **Persistencia** | Opcional | ✅ Habilitada (RDB) |
| **Límite memoria** | 256MB | 256MB |
| **Política** | allkeys-lru | allkeys-lru |

---

### **PostgreSQL**

| Aspecto | Local | Producción |
|---------|-------|------------|
| **Usuario** | `ricoh_admin` | `ricoh_prod_user` |
| **Contraseña** | `ricoh_secure_2024` | Nueva segura |
| **Base de datos** | `ricoh_fleet` | `ricoh_fleet_prod` |
| **Puerto expuesto** | ✅ 5432 | ❌ Solo interno |
| **Backups** | Manual | ✅ Automáticos |
| **SSL** | ❌ Deshabilitado | ✅ Habilitado |

---

### **Backend**

| Aspecto | Local | Producción |
|---------|-------|------------|
| **Workers** | 1 (--reload) | 4 |
| **Hot reload** | ✅ Habilitado | ❌ Deshabilitado |
| **Logs** | DEBUG | INFO/WARNING |
| **Errores** | Stack traces completos | Genéricos |
| **CSRF** | ❌ Deshabilitado | ✅ Habilitado |
| **HTTPS** | ❌ HTTP | ✅ HTTPS |
| **Health checks** | Básico | ✅ Completo |

---

### **Frontend**

| Aspecto | Local | Producción |
|---------|-------|------------|
| **Servidor** | Vite dev server | Nginx |
| **Build** | ❌ No | ✅ Optimizado |
| **API URL** | http://192.168.91.34:8000 | https://api.ricoh.tuempresa.com |
| **Hot reload** | ✅ Habilitado | ❌ N/A |
| **Compresión** | ❌ No | ✅ Gzip/Brotli |
| **Caché** | ❌ No | ✅ Habilitado |

---

## ✅ Checklist de Cambios para Producción

### **Antes de Desplegar**

#### **1. Seguridad**
- [ ] Cambiar `ENVIRONMENT=production`
- [ ] Cambiar `DEBUG=false`
- [ ] Generar nueva `ENCRYPTION_KEY`
- [ ] Generar nueva `SECRET_KEY`
- [ ] Configurar `CORS_ORIGINS` con dominios reales
- [ ] Configurar contraseña de Redis
- [ ] Cambiar contraseña de PostgreSQL
- [ ] Configurar `RICOH_ADMIN_PASSWORD`

#### **2. Base de Datos**
- [ ] Crear usuario de producción
- [ ] Crear base de datos de producción
- [ ] Aplicar migraciones
- [ ] Configurar backups automáticos
- [ ] Habilitar SSL

#### **3. Redis**
- [ ] Configurar contraseña
- [ ] Habilitar persistencia (RDB)
- [ ] Configurar límites de memoria
- [ ] Deshabilitar comandos peligrosos

#### **4. Servicios**
- [ ] Configurar Nginx como reverse proxy
- [ ] Obtener certificados SSL (Let's Encrypt)
- [ ] Configurar firewall (UFW)
- [ ] Configurar DNS
- [ ] Remover Adminer

#### **5. Monitoreo**
- [ ] Configurar logs centralizados
- [ ] Configurar alertas
- [ ] Configurar monitoreo de recursos
- [ ] Configurar Sentry (opcional)

#### **6. Performance**
- [ ] Configurar workers (4+)
- [ ] Habilitar compresión
- [ ] Configurar caché de Nginx
- [ ] Optimizar queries de BD

---

## 🔄 Comandos de Migración

### **Generar Claves de Seguridad**

```bash
# ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Redis Password
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25

# PostgreSQL Password
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
```

---

### **Crear .env de Producción**

```bash
cd backend

# Copiar desde ejemplo
cp .env.production.example .env

# Editar con valores reales
nano .env
```

---

### **Verificar Configuración**

```bash
cd backend

# Ejecutar script de verificación
python verify_production_config.py
```

**Output esperado:**
```
✅ TODAS LAS VERIFICACIONES PASARON
El sistema está listo para producción
```

---

### **Desplegar con Docker Compose**

```bash
# Crear archivo .env.docker con las contraseñas
cat > .env.docker << EOF
DB_PASSWORD=tu_password_postgres
REDIS_PASSWORD=tu_password_redis
ENCRYPTION_KEY=tu_encryption_key
SECRET_KEY=tu_secret_key
RICOH_ADMIN_PASSWORD=tu_password_ricoh
CORS_ORIGINS=https://ricoh.tuempresa.com
EOF

# Iniciar servicios
docker-compose -f docker-compose.production.yml up -d

# Ver logs
docker-compose -f docker-compose.production.yml logs -f
```

---

## 🔒 Configuración de Firewall

### **Local (Desarrollo)**
```bash
# No se requiere firewall
# Todos los puertos abiertos en localhost
```

### **Producción**
```bash
# Instalar UFW
sudo apt install -y ufw

# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Habilitar
sudo ufw enable

# Verificar
sudo ufw status
```

---

## 📝 Resumen de Cambios Críticos

| # | Cambio | Local | Producción | Prioridad |
|---|--------|-------|------------|-----------|
| 1 | ENVIRONMENT | development | production | 🔴 CRÍTICO |
| 2 | DEBUG | true | false | 🔴 CRÍTICO |
| 3 | ENCRYPTION_KEY | Ejemplo | Nueva única | 🔴 CRÍTICO |
| 4 | SECRET_KEY | Ejemplo | Nueva única | 🔴 CRÍTICO |
| 5 | CORS_ORIGINS | * | Dominios específicos | 🔴 CRÍTICO |
| 6 | REDIS_PASSWORD | Sin contraseña | Con contraseña | 🟠 ALTA |
| 7 | DB_PASSWORD | Ejemplo | Nueva segura | 🟠 ALTA |
| 8 | HTTPS | HTTP | HTTPS | 🟠 ALTA |
| 9 | Backups | Manual | Automático | 🟡 MEDIA |
| 10 | Monitoreo | Básico | Completo | 🟡 MEDIA |

---

## 🎯 Comandos Rápidos

### **Ver Configuración Actual (Local)**
```bash
docker exec ricoh-backend env | grep -E "ENVIRONMENT|DEBUG|CORS"
```

### **Ver Configuración Actual (Producción)**
```bash
docker exec ricoh_backend_prod env | grep -E "ENVIRONMENT|DEBUG|CORS"
```

### **Comparar Configuraciones**
```bash
# Local
docker-compose config | grep -A 20 "environment:"

# Producción
docker-compose -f docker-compose.production.yml config | grep -A 20 "environment:"
```

---

## 📚 Documentación Relacionada

- `docs/DEPLOYMENT_PRODUCTION.md` - Guía completa de despliegue
- `backend/.env.production.example` - Ejemplo de configuración
- `backend/verify_production_config.py` - Script de verificación
- `backend/install_production.sh` - Instalación automática

---

## ⚠️ Advertencias Finales

### **NUNCA en Producción:**
- ❌ `DEBUG=true`
- ❌ `CORS_ORIGINS=*`
- ❌ Claves de ejemplo
- ❌ Contraseñas débiles
- ❌ Puertos expuestos innecesariamente
- ❌ Adminer u otras herramientas de debug
- ❌ HTTP sin HTTPS

### **SIEMPRE en Producción:**
- ✅ `ENVIRONMENT=production`
- ✅ `DEBUG=false`
- ✅ Claves únicas y seguras
- ✅ CORS restringido
- ✅ HTTPS habilitado
- ✅ Firewall configurado
- ✅ Backups automáticos
- ✅ Monitoreo activo

---

**Última actualización**: 6 de Mayo 2026  
**Versión**: 1.0  
**Mantenedor**: Equipo de Desarrollo Ricoh
