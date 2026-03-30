# Pre-Deployment Checklist - Producción

**Fecha**: _______________  
**Responsable**: _______________  
**Servidor**: _______________  
**Dominio**: _______________

---

## 1. Preparación del Servidor

- [ ] Ubuntu Server 22.04/24.04 LTS instalado
- [ ] Acceso SSH configurado
- [ ] Dominio DNS apuntando al servidor
- [ ] Firewall configurado (puertos 22, 80, 443)
- [ ] Script `setup-ubuntu-server.sh` ejecutado exitosamente

---

## 2. Variables de Entorno de Seguridad

### Claves Generadas (NO usar valores de desarrollo)

- [ ] **ENCRYPTION_KEY** generada con:
  ```bash
  python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
  Valor: `_______________________________________`

- [ ] **SECRET_KEY** generada con:
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  Valor: `_______________________________________`

- [ ] **POSTGRES_PASSWORD** generada (mínimo 16 caracteres)
  Valor: `_______________________________________`

- [ ] **REDIS_PASSWORD** generada (mínimo 16 caracteres)
  Valor: `_______________________________________`

- [ ] **RICOH_ADMIN_PASSWORD** configurada
  Valor: `_______________________________________`

### Configuración de Aplicación

- [ ] **ENVIRONMENT** = `production`
- [ ] **DEBUG** = `false`
- [ ] **FORCE_HTTPS** = `true`
- [ ] **CORS_ORIGINS** configurado con dominio real
- [ ] **FRONTEND_API_URL** configurado con dominio real
- [ ] **DOMAIN_NAME** configurado
- [ ] **API_DOMAIN** configurado

---

## 3. Certificados SSL

- [ ] Certificados SSL obtenidos con Let's Encrypt
- [ ] `fullchain.pem` copiado a `deployment/ssl/`
- [ ] `privkey.pem` copiado a `deployment/ssl/`
- [ ] Permisos correctos (644 para fullchain, 600 para privkey)
- [ ] Renovación automática configurada en crontab

---

## 4. Configuración de Nginx

- [ ] `deployment/nginx/conf.d/ricoh.conf` actualizado con dominios reales
- [ ] Reemplazado `${DOMAIN_NAME}` con dominio real
- [ ] Reemplazado `${API_DOMAIN}` con subdominio API real
- [ ] Rate limiting configurado
- [ ] Security headers configurados

---

## 5. Verificación de Correcciones de Seguridad

### Gestión de Secretos (4 vulnerabilidades)

- [ ] **V1**: ENCRYPTION_KEY obligatoria en todos los entornos
  - Verificar: Variable configurada en .env.production
  - Verificar: No es el valor de ejemplo

- [ ] **V2**: SECRET_KEY con validación de entropía
  - Verificar: Longitud >= 32 caracteres
  - Verificar: Contiene al menos 3 de 4 categorías de caracteres

- [ ] **V3**: RICOH_ADMIN_PASSWORD obligatoria
  - Verificar: Variable configurada en .env.production
  - Verificar: No está vacía

- [ ] **V4**: DATABASE_URL sin credenciales hardcodeadas
  - Verificar: No contiene `ricoh_secure_2024`
  - Verificar: Usa password generada

### Exposición de Información (3 vulnerabilidades)

- [ ] **V5**: JWT tokens enmascarados en logs
  - Verificar: Logs muestran formato `XXXX...YYYY`

- [ ] **V6**: Contraseñas no expuestas en consola
  - Verificar: init_superadmin.py guarda en archivo

- [ ] **V7**: wimTokens enmascarados en logs
  - Verificar: Logs muestran formato `XXXX...YYYY`

### Configuración Restrictiva (4 vulnerabilidades)

- [ ] **V8**: CORS con listas explícitas
  - Verificar: No usa `["*"]` para métodos o headers

- [ ] **V9**: CSRF habilitada por defecto en producción
  - Verificar: ENVIRONMENT=production
  - Verificar: Logs muestran "CSRF Protection enabled"

- [ ] **V10**: CSRF con Redis
  - Verificar: REDIS_URL configurada
  - Verificar: Logs muestran "CSRF usando Redis"

- [ ] **V11**: Rate limiting con Redis
  - Verificar: REDIS_URL configurada
  - Verificar: Logs muestran "Rate Limiter usando Redis"

---

## 6. Build y Deployment

- [ ] Imágenes Docker construidas exitosamente
  ```bash
  docker-compose -f deployment/docker-compose.prod.yml build
  ```

- [ ] Servicios iniciados correctamente
  ```bash
  docker-compose -f deployment/docker-compose.prod.yml --env-file .env.production up -d
  ```

- [ ] Todos los contenedores en estado "healthy" o "running"
  ```bash
  docker-compose -f deployment/docker-compose.prod.yml ps
  ```

---

## 7. Inicialización de Base de Datos

- [ ] Base de datos inicializada
  ```bash
  docker exec ricoh-backend python scripts/init_db.py
  ```

- [ ] Superadmin creado
  ```bash
  docker exec ricoh-backend python scripts/init_superadmin.py
  ```

- [ ] Contraseña de superadmin guardada de forma segura
  ```bash
  docker exec ricoh-backend cat .superadmin_password
  ```

---

## 8. Verificación Post-Deployment

### Tests Automáticos

- [ ] Script de verificación ejecutado exitosamente
  ```bash
  docker exec ricoh-backend python scripts/verify_deployment.py
  ```

- [ ] Script de verificación de seguridad ejecutado
  ```bash
  bash deployment/verify-security-fixes.sh
  ```

### Tests Manuales

- [ ] Health check del backend responde
  ```bash
  curl https://api.tu-dominio.com/health
  ```

- [ ] Frontend carga correctamente
  ```bash
  curl https://tu-dominio.com/
  ```

- [ ] Login funciona con superadmin
  ```bash
  curl -X POST https://api.tu-dominio.com/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"superadmin","password":"<password>"}'
  ```

- [ ] HTTPS redirect funciona
  ```bash
  curl -I http://tu-dominio.com/
  # Debe retornar 301 redirect a https://
  ```

---

## 9. Monitoreo y Logs

- [ ] Logs del backend revisados (sin errores críticos)
  ```bash
  docker logs ricoh-backend | tail -100
  ```

- [ ] Logs de Nginx revisados
  ```bash
  docker logs ricoh-nginx | tail -100
  ```

- [ ] Logs de PostgreSQL revisados
  ```bash
  docker logs ricoh-postgres | tail -50
  ```

- [ ] Logs de Redis revisados
  ```bash
  docker logs ricoh-redis | tail -50
  ```

---

## 10. Backups

- [ ] Backup automático configurado en crontab
- [ ] Backup manual ejecutado exitosamente
  ```bash
  bash /opt/ricoh/backup.sh
  ```

- [ ] Backup verificado (archivo existe y no está corrupto)
  ```bash
  ls -lh /opt/ricoh/backups/
  ```

---

## 11. Documentación

- [ ] Credenciales guardadas en gestor de contraseñas seguro
- [ ] Documentación de deployment actualizada
- [ ] Contactos de emergencia documentados
- [ ] Procedimiento de rollback documentado

---

## 12. Monitoreo Continuo (Primeras 24 horas)

- [ ] **Hora 1**: Verificar logs cada 15 minutos
- [ ] **Hora 2-4**: Verificar logs cada 30 minutos
- [ ] **Hora 4-24**: Verificar logs cada 2 horas

### Qué buscar en logs:

```bash
# Errores críticos
docker logs ricoh-backend 2>&1 | grep -i "error\|critical\|fatal"

# Autenticación fallida
docker logs ricoh-backend 2>&1 | grep "Authentication failed"

# Rate limiting
docker logs ricoh-backend 2>&1 | grep "Rate limit exceeded"

# CSRF violations
docker logs ricoh-backend 2>&1 | grep "CSRF"
```

---

## Firma de Aprobación

**Preparado por**: _______________  
**Fecha**: _______________  
**Firma**: _______________

**Revisado por**: _______________  
**Fecha**: _______________  
**Firma**: _______________

**Aprobado para producción**: _______________  
**Fecha**: _______________  
**Firma**: _______________

---

## Notas Adicionales

_Espacio para notas específicas del deployment:_

_______________________________________________________________________________

_______________________________________________________________________________

_______________________________________________________________________________
