# 🔒 Auditoría de Seguridad - Ricoh Fleet Management

**Fecha**: 6 de Mayo 2026  
**Hora**: 20:30 (UTC-5)  
**Auditor**: Sistema Automatizado  
**Versión**: 1.0

---

## 📊 Resumen Ejecutivo

### Estado Actual: ✅ DESARROLLO LOCAL
- **Ambiente**: Development
- **Seguridad**: Configuración básica
- **Accesibilidad**: Red local (192.168.91.34)
- **Disponibilidad**: Solo cuando PC encendida

### Verificaciones Realizadas

| # | Verificación | Estado | Prioridad | Acción Requerida |
|---|--------------|--------|-----------|------------------|
| 1 | ENVIRONMENT | ⚠️ development | 🔴 CRÍTICA | Cambiar a `production` |
| 2 | DEBUG | ⚠️ true | 🔴 CRÍTICA | Cambiar a `false` |
| 3 | ENCRYPTION_KEY | ❌ Ejemplo | 🔴 CRÍTICA | Generar nueva única |
| 4 | SECRET_KEY | ❌ Ejemplo | 🔴 CRÍTICA | Generar nueva única |
| 5 | CORS_ORIGINS | ⚠️ * (todos) | 🔴 CRÍTICA | Restringir dominios |
| 6 | REDIS_PASSWORD | ⚠️ Sin contraseña | 🟠 ALTA | Configurar contraseña |
| 7 | DATABASE_URL | ⚠️ Ejemplo | 🟠 ALTA | Cambiar contraseña |
| 8 | RICOH_PASSWORD | ⚠️ No configurada | 🟡 MEDIA | Configurar |
| 9 | HTTPS | ℹ️ HTTP | 🟠 ALTA | Habilitar HTTPS |
| 10 | Backups | ℹ️ Manual | 🟡 MEDIA | Automatizar |

**Resultado**: 5/10 verificaciones pasadas (50%)  
**Conclusión**: ✅ Correcto para DESARROLLO, ❌ NO listo para PRODUCCIÓN

---

## 🔍 Detalles de Configuración Actual

### 1️⃣ Variables de Entorno (Docker Container)

```bash
ENVIRONMENT=development          # ⚠️ CAMBIAR en producción
DEBUG=true                       # ⚠️ CAMBIAR en producción
CORS_ORIGINS=*                   # ⚠️ RESTRINGIR en producción
ENCRYPTION_KEY=ynVBzh9ZjawHMoUHu0L9ozXT2j8ebujlVxoNzD91xjE=  # ❌ EJEMPLO
SECRET_KEY=ricoh-jwt-secret-key-change-in-production-min-32-chars  # ❌ EJEMPLO
REDIS_PASSWORD=                  # ⚠️ Sin contraseña
DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@postgres:5432/ricoh_fleet
```

### 2️⃣ Servicios Activos

| Servicio | Estado | Puerto | Acceso | Seguridad |
|----------|--------|--------|--------|-----------|
| **Frontend** | ✅ Running | 5173 | http://192.168.91.34:5173 | ⚠️ HTTP |
| **Backend** | ✅ Running | 8000 | http://192.168.91.34:8000 | ⚠️ HTTP |
| **PostgreSQL** | ✅ Running | 5432 | localhost:5432 | ⚠️ Expuesto |
| **Redis** | ✅ Running | 6379 | localhost:6379 | ⚠️ Sin contraseña |
| **Adminer** | ✅ Running | 8080 | http://localhost:8080 | ⚠️ Expuesto |

### 3️⃣ Logs del Backend

```
✅ Redis conectado y operativo
   Backend: Redis
   Caché distribuido: Habilitado

⚠️ CSRF Protection disabled (ENVIRONMENT=development, not recommended for production)
🔓 HTTPS redirect disabled (development mode)
```

---

## ⚠️ Problemas Identificados

### 🔴 CRÍTICOS (Bloquean producción)

#### 1. ENCRYPTION_KEY de Ejemplo
**Problema**: Usando clave de ejemplo del repositorio
```bash
ENCRYPTION_KEY=ynVBzh9ZjawHMoUHu0L9ozXT2j8ebujlVxoNzD91xjE=
```

**Riesgo**: 
- ❌ Cualquiera con acceso al código puede desencriptar datos sensibles
- ❌ Contraseñas de usuarios comprometidas
- ❌ Datos de impresoras expuestos

**Solución**:
```bash
# Generar nueva clave ÚNICA
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Ejemplo de salida:
# X8fK9mN2pQ5rT7vY1wZ3bC6dE8gH0jL4nM7pR9sU2xA=
```

---

#### 2. SECRET_KEY de Ejemplo
**Problema**: Usando clave de ejemplo del repositorio
```bash
SECRET_KEY=ricoh-jwt-secret-key-change-in-production-min-32-chars
```

**Riesgo**:
- ❌ Tokens JWT pueden ser falsificados
- ❌ Sesiones de usuarios comprometidas
- ❌ Acceso no autorizado al sistema

**Solución**:
```bash
# Generar nueva clave ÚNICA
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Ejemplo de salida:
# Kj8mN3pQ6rT9vY2wZ5bC8dF1gH4jL7nM0pR3sU6xA9z
```

---

#### 3. CORS_ORIGINS=* (Permite Todos)
**Problema**: Cualquier sitio web puede hacer requests
```bash
CORS_ORIGINS=*
```

**Riesgo**:
- ❌ Ataques CSRF desde cualquier origen
- ❌ Robo de datos de usuarios
- ❌ Acceso no autorizado desde sitios maliciosos

**Solución**:
```bash
# Producción: Solo dominios específicos
CORS_ORIGINS=https://ricoh.tuempresa.com,https://www.ricoh.tuempresa.com
```

---

#### 4. DEBUG=true en Producción
**Problema**: Modo debug expone información sensible
```bash
DEBUG=true
```

**Riesgo**:
- ❌ Stack traces completos visibles al usuario
- ❌ Información de variables y configuración expuesta
- ❌ Rutas de archivos del servidor reveladas
- ❌ Queries SQL visibles en logs

**Solución**:
```bash
DEBUG=false
```

---

#### 5. ENVIRONMENT=development
**Problema**: Protecciones de seguridad deshabilitadas
```bash
ENVIRONMENT=development
```

**Efectos**:
- ❌ CSRF Protection: DESHABILITADO
- ❌ HTTPS Redirect: DESHABILITADO
- ❌ Rate Limiting: RELAJADO
- ❌ Logs detallados: HABILITADOS

**Solución**:
```bash
ENVIRONMENT=production
```

---

### 🟠 ALTA PRIORIDAD (Recomendado antes de producción)

#### 6. Redis Sin Contraseña
**Problema**: Redis accesible sin autenticación
```bash
REDIS_PASSWORD=
```

**Riesgo**:
- ⚠️ Acceso no autorizado a caché
- ⚠️ Manipulación de sesiones
- ⚠️ Robo de datos en caché

**Solución**:
```bash
# Generar contraseña segura
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25

# Configurar en Redis
REDIS_PASSWORD=tu_password_generada
REDIS_URL=redis://:tu_password_generada@redis:6379/0
```

---

#### 7. Contraseña de Base de Datos
**Problema**: Usando contraseña de ejemplo
```bash
DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@postgres:5432/ricoh_fleet
```

**Riesgo**:
- ⚠️ Contraseña predecible
- ⚠️ Acceso no autorizado a BD
- ⚠️ Robo o modificación de datos

**Solución**:
```bash
# Generar contraseña segura
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25

# Actualizar DATABASE_URL
DATABASE_URL=postgresql://ricoh_prod_user:NUEVA_PASSWORD@postgres:5432/ricoh_fleet_prod
```

---

#### 8. HTTP en lugar de HTTPS
**Problema**: Comunicación sin encriptar
```bash
FORCE_HTTPS=false
```

**Riesgo**:
- ⚠️ Contraseñas transmitidas en texto plano
- ⚠️ Tokens JWT interceptables
- ⚠️ Ataques Man-in-the-Middle

**Solución**:
```bash
# Habilitar HTTPS
FORCE_HTTPS=true

# Configurar certificados SSL (Let's Encrypt)
# Ver: docs/DEPLOYMENT_PRODUCTION.md
```

---

### 🟡 MEDIA PRIORIDAD (Mejorar seguridad)

#### 9. Contraseña Ricoh No Configurada
**Problema**: No configurada para aprovisionamiento
```bash
RICOH_ADMIN_PASSWORD=
```

**Solución**:
```bash
RICOH_ADMIN_PASSWORD=tu_password_ricoh_segura
```

---

#### 10. Backups Manuales
**Problema**: Sin backups automáticos
```bash
BACKUP_ENABLED=false
```

**Solución**:
```bash
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *  # Diario a las 2 AM
BACKUP_RETENTION_DAYS=30
```

---

## 📋 Checklist de Migración a Producción

### Fase 1: Seguridad Crítica (OBLIGATORIO)

- [ ] **1. Generar ENCRYPTION_KEY nueva**
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

- [ ] **2. Generar SECRET_KEY nueva**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- [ ] **3. Cambiar ENVIRONMENT=production**
  ```bash
  ENVIRONMENT=production
  ```

- [ ] **4. Cambiar DEBUG=false**
  ```bash
  DEBUG=false
  ```

- [ ] **5. Restringir CORS_ORIGINS**
  ```bash
  CORS_ORIGINS=https://ricoh.tuempresa.com
  ```

---

### Fase 2: Infraestructura (RECOMENDADO)

- [ ] **6. Configurar contraseña de Redis**
  ```bash
  REDIS_PASSWORD=tu_password_generada
  ```

- [ ] **7. Cambiar contraseña de PostgreSQL**
  ```bash
  DATABASE_URL=postgresql://ricoh_prod_user:NUEVA_PASSWORD@postgres:5432/ricoh_fleet_prod
  ```

- [ ] **8. Habilitar HTTPS**
  ```bash
  FORCE_HTTPS=true
  ```

- [ ] **9. Configurar certificados SSL**
  - Obtener certificados de Let's Encrypt
  - Configurar Nginx como reverse proxy

- [ ] **10. Configurar firewall**
  ```bash
  sudo ufw allow ssh
  sudo ufw allow http
  sudo ufw allow https
  sudo ufw enable
  ```

---

### Fase 3: Operaciones (OPCIONAL)

- [ ] **11. Configurar backups automáticos**
  ```bash
  BACKUP_ENABLED=true
  BACKUP_SCHEDULE=0 2 * * *
  ```

- [ ] **12. Configurar monitoreo**
  - Sentry para errores
  - Prometheus para métricas
  - Grafana para dashboards

- [ ] **13. Configurar logs centralizados**
  - ELK Stack o similar
  - Retención de logs

- [ ] **14. Configurar alertas**
  - Email/SMS para errores críticos
  - Alertas de disponibilidad

---

## 🚀 Comandos de Despliegue

### Opción A: Servidor Dedicado (Recomendado)

```bash
# 1. Clonar repositorio en servidor
git clone https://github.com/tuempresa/ricoh-fleet.git
cd ricoh-fleet

# 2. Crear archivo .env de producción
cp backend/.env.production.example backend/.env

# 3. Editar con valores reales
nano backend/.env

# 4. Generar claves de seguridad
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 5. Actualizar .env con las claves generadas

# 6. Desplegar con Docker Compose
docker-compose -f docker-compose.production.yml up -d

# 7. Verificar logs
docker-compose -f docker-compose.production.yml logs -f

# 8. Verificar seguridad
docker exec ricoh_backend_prod python security_audit.py
```

---

### Opción B: Mantener en PC Local (NO RECOMENDADO)

⚠️ **ADVERTENCIA**: Si apagas tu PC, todo el sistema se cae

**Limitaciones**:
- ❌ Disponibilidad: Solo cuando PC encendida
- ❌ Acceso: Solo red local (192.168.91.34)
- ❌ Backups: Manuales
- ❌ Monitoreo: Limitado
- ❌ Escalabilidad: No soporta múltiples usuarios concurrentes

**Si decides continuar en local**:
```bash
# 1. Actualizar docker-compose.yml con valores más seguros
# 2. Generar nuevas claves (ENCRYPTION_KEY, SECRET_KEY)
# 3. Restringir CORS a IPs específicas
# 4. Configurar contraseña de Redis
# 5. Cambiar contraseña de PostgreSQL

# Reiniciar servicios
docker-compose down
docker-compose up -d
```

---

## 📊 Comparativa: Local vs Producción

| Aspecto | Local (Actual) | Producción (Requerido) |
|---------|----------------|------------------------|
| **Disponibilidad** | Solo cuando PC encendida | 24/7 |
| **Acceso** | Red local (192.168.91.34) | Internet (dominio) |
| **HTTPS** | ❌ HTTP | ✅ HTTPS |
| **ENCRYPTION_KEY** | ❌ Ejemplo | ✅ Única |
| **SECRET_KEY** | ❌ Ejemplo | ✅ Única |
| **CORS** | ❌ * (todos) | ✅ Dominios específicos |
| **Redis Password** | ❌ Sin contraseña | ✅ Con contraseña |
| **DB Password** | ⚠️ Ejemplo | ✅ Segura |
| **DEBUG** | ⚠️ true | ✅ false |
| **ENVIRONMENT** | ⚠️ development | ✅ production |
| **Backups** | ❌ Manual | ✅ Automático |
| **Monitoreo** | ❌ Básico | ✅ Completo |
| **Firewall** | ❌ No | ✅ Configurado |
| **Logs** | ⚠️ DEBUG | ✅ INFO/WARNING |

---

## 🎯 Recomendaciones Finales

### Para Desarrollo Local (Actual)
✅ **Tu configuración actual es CORRECTA para desarrollo**

**Mantener**:
- ENVIRONMENT=development
- DEBUG=true
- CORS_ORIGINS=*
- Redis sin contraseña
- HTTP (no HTTPS)

**Mejorar** (opcional):
- Generar ENCRYPTION_KEY y SECRET_KEY únicas (aunque sean de desarrollo)
- Documentar que son claves de desarrollo

---

### Para Producción (Futuro)
❌ **Tu configuración actual NO es segura para producción**

**OBLIGATORIO cambiar**:
1. ENVIRONMENT=production
2. DEBUG=false
3. ENCRYPTION_KEY (nueva única)
4. SECRET_KEY (nueva única)
5. CORS_ORIGINS (dominios específicos)

**RECOMENDADO cambiar**:
6. Redis con contraseña
7. PostgreSQL con contraseña segura
8. Habilitar HTTPS
9. Configurar firewall
10. Backups automáticos

---

## 📚 Documentación Relacionada

- **Guía Completa**: `docs/DEPLOYMENT_PRODUCTION.md`
- **Diferencias Local vs Producción**: `docs/DIFERENCIAS_LOCAL_VS_PRODUCCION.md`
- **Ejemplo de Configuración**: `backend/.env.production.example`
- **Script de Verificación**: `backend/verify_production_config.py`
- **Script de Auditoría**: `backend/security_audit.py`

---

## 🔐 Generación de Claves Seguras

### ENCRYPTION_KEY
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Ejemplo de salida**:
```
X8fK9mN2pQ5rT7vY1wZ3bC6dE8gH0jL4nM7pR9sU2xA=
```

---

### SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Ejemplo de salida**:
```
Kj8mN3pQ6rT9vY2wZ5bC8dF1gH4jL7nM0pR3sU6xA9z
```

---

### Redis Password
```bash
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
```

**Ejemplo de salida**:
```
Hj7kL9mN2pQ5rT8vY1wZ3bC6d
```

---

### PostgreSQL Password
```bash
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
```

**Ejemplo de salida**:
```
Fj6kL8mN1pQ4rT7vY0wZ2bC5d
```

---

## ✅ Verificación Post-Despliegue

### 1. Verificar Variables de Entorno
```bash
docker exec ricoh_backend_prod python -c "import os; print('ENVIRONMENT:', os.getenv('ENVIRONMENT')); print('DEBUG:', os.getenv('DEBUG'))"
```

**Esperado**:
```
ENVIRONMENT: production
DEBUG: false
```

---

### 2. Ejecutar Auditoría de Seguridad
```bash
docker exec ricoh_backend_prod python security_audit.py
```

**Esperado**:
```
✅ TODAS LAS VERIFICACIONES PASARON
El sistema está listo para producción
```

---

### 3. Verificar HTTPS
```bash
curl -I https://ricoh.tuempresa.com
```

**Esperado**:
```
HTTP/2 200
strict-transport-security: max-age=31536000
```

---

### 4. Verificar CORS
```bash
curl -H "Origin: https://sitio-malicioso.com" https://ricoh.tuempresa.com/api/health
```

**Esperado**:
```
Error: CORS policy blocked
```

---

## 📞 Contacto y Soporte

**Documentación**: `docs/`  
**Issues**: GitHub Issues  
**Email**: soporte@tuempresa.com

---

**Última actualización**: 6 de Mayo 2026, 20:30  
**Próxima auditoría**: Antes de despliegue a producción  
**Versión**: 1.0
