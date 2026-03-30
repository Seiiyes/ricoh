# ✅ Checklist de Despliegue a Producción

## 📋 Pre-Despliegue

### Verificación del Código
- [x] Todos los tests pasando (38/38 ✅)
- [x] Frontend actualizado con CSRF y rotación
- [x] Backend con encriptación y sanitización
- [x] Documentación completa
- [x] Sin errores de compilación

### Preparación del Servidor
- [ ] Docker instalado en el servidor
- [ ] Docker Compose instalado
- [ ] Acceso SSH/RDP al servidor
- [ ] Puertos 8000 y 5173 disponibles
- [ ] Mínimo 4GB RAM disponible
- [ ] Mínimo 20GB disco disponible

---

## 🔧 Configuración

### 1. Clonar Repositorio
```bash
# En el servidor
git clone <url_repositorio> /ruta/ricoh
cd /ruta/ricoh
```
- [ ] Repositorio clonado
- [ ] En el directorio correcto

### 2. Generar Claves de Seguridad

#### ENCRYPTION_KEY
```bash
cd backend
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
- [ ] Clave generada
- [ ] Clave copiada (ejemplo: `gAAAAABh...`)

#### SECRET_KEY (si no existe)
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
- [ ] Clave generada
- [ ] Clave copiada

### 3. Configurar .env Principal

Editar `.env` en la raíz:

```bash
# Entorno
ENVIRONMENT=production

# Base de Datos
POSTGRES_USER=ricoh_admin
POSTGRES_PASSWORD=<cambiar_password_seguro>
POSTGRES_DB=ricoh_db

# Seguridad
SECRET_KEY=<clave_generada>
ENCRYPTION_KEY=<clave_generada>
FORCE_HTTPS=false
ENABLE_CSRF=false

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://<ip_servidor>:5173

# Otros
LOG_LEVEL=INFO
DEMO_MODE=false
```

Checklist:
- [ ] `ENVIRONMENT=production`
- [ ] `POSTGRES_PASSWORD` cambiado
- [ ] `SECRET_KEY` configurado
- [ ] `ENCRYPTION_KEY` configurado
- [ ] `CORS_ORIGINS` con IP del servidor
- [ ] `DEMO_MODE=false`

### 4. Configurar backend/.env

Editar `backend/.env`:

```bash
ENVIRONMENT=production
SECRET_KEY=<misma_clave_del_env_principal>
ENCRYPTION_KEY=<misma_clave_del_env_principal>
FORCE_HTTPS=false
ENABLE_CSRF=false
DATABASE_URL=postgresql://ricoh_admin:<password>@postgres:5432/ricoh_db
```

Checklist:
- [ ] Archivo creado
- [ ] Variables copiadas del .env principal
- [ ] `DATABASE_URL` con password correcto

---

## 🚀 Despliegue

### 5. Construir e Iniciar

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Verificar estado
docker-compose ps
```

Checklist:
- [ ] Build exitoso (sin errores)
- [ ] Contenedores iniciados
- [ ] 3 contenedores corriendo: backend, frontend, postgres

### 6. Verificar Logs

```bash
# Ver logs del backend
docker-compose logs backend

# Buscar estos mensajes:
# ✅ Database initialized
# ✅ Servicio de encriptación inicializado
# 🌐 Server ready!
```

Checklist:
- [ ] Backend inició sin errores
- [ ] Mensaje "Server ready!" visible
- [ ] Sin errores de ENCRYPTION_KEY
- [ ] Base de datos conectada

### 7. Verificar Servicios

#### Backend
```bash
curl http://localhost:8000/
```
Debe retornar:
```json
{
  "service": "Ricoh Equipment Management API",
  "status": "online",
  "version": "2.0.0"
}
```
- [ ] Backend responde
- [ ] Status: "online"

#### Frontend
Abrir en navegador: `http://localhost:5173`
- [ ] Página carga correctamente
- [ ] Login visible
- [ ] Sin errores en consola

#### Base de Datos
```bash
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_db -c "\dt"
```
- [ ] Conexión exitosa
- [ ] Tablas creadas (admin_users, empresas, printers, users, etc.)

---

## 👤 Configuración Inicial

### 8. Crear Usuario Superadmin

Opción A - Script automático:
```bash
docker exec -it ricoh-backend python scripts/init_superadmin.py
```

Opción B - Manual:
```bash
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_db

-- Insertar superadmin
INSERT INTO admin_users (username, password_hash, nombre_completo, email, rol, is_active)
VALUES ('superadmin', '$2b$12$...', 'Administrador', 'admin@empresa.com', 'superadmin', true);
```

Checklist:
- [ ] Usuario superadmin creado
- [ ] Credenciales anotadas de forma segura

### 9. Primer Login

1. Abrir `http://localhost:5173`
2. Login con superadmin
3. Verificar acceso al dashboard

Checklist:
- [ ] Login exitoso
- [ ] Dashboard carga
- [ ] Menú visible
- [ ] Sin errores 403

---

## 🌐 Acceso desde Red Local

### 10. Configurar Acceso Remoto

#### Obtener IP del servidor
```bash
# Windows
ipconfig

# Linux
ip addr show
```
- [ ] IP obtenida (ejemplo: 192.168.1.100)

#### Actualizar CORS
Editar `.env`:
```bash
CORS_ORIGINS=http://localhost:5173,http://192.168.1.100:5173
```

Reiniciar backend:
```bash
docker-compose restart backend
```

Checklist:
- [ ] IP agregada a CORS_ORIGINS
- [ ] Backend reiniciado
- [ ] Acceso desde otra PC funciona

---

## 🔐 Seguridad Adicional (Opcional)

### 11. Habilitar CSRF

Editar `.env`:
```bash
ENABLE_CSRF=true
```

Reiniciar:
```bash
docker-compose restart backend
```

Checklist:
- [ ] CSRF habilitado
- [ ] Frontend funciona correctamente
- [ ] Tokens CSRF en headers

### 12. Configurar HTTPS (Si tienes certificado)

1. Configurar nginx/Apache como reverse proxy
2. Instalar certificado SSL
3. Editar `.env`:
```bash
FORCE_HTTPS=true
CORS_ORIGINS=https://<dominio>
```

Checklist:
- [ ] Certificado SSL instalado
- [ ] Reverse proxy configurado
- [ ] HTTPS funcionando
- [ ] Redirección HTTP→HTTPS activa

---

## 📊 Monitoreo

### 13. Configurar Monitoreo

#### Logs en tiempo real
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend
```

#### Verificar salud del sistema
```bash
# Estado de contenedores
docker-compose ps

# Uso de recursos
docker stats
```

Checklist:
- [ ] Logs accesibles
- [ ] Sin errores recurrentes
- [ ] Uso de recursos normal (<80%)

### 14. Configurar Backups

#### Backup manual
```bash
# Crear backup
docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_db > backup_$(date +%Y%m%d).sql
```

#### Backup automático (cron)
```bash
# Editar crontab
crontab -e

# Agregar línea (backup diario a las 2 AM)
0 2 * * * cd /ruta/ricoh && docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_db > backups/backup_$(date +\%Y\%m\%d).sql
```

Checklist:
- [ ] Backup manual probado
- [ ] Backup automático configurado
- [ ] Carpeta de backups creada
- [ ] Restauración probada

---

## ✅ Verificación Final

### 15. Tests de Funcionalidad

- [ ] Login funciona
- [ ] Crear empresa funciona
- [ ] Crear usuario admin funciona
- [ ] Crear impresora funciona
- [ ] Crear usuario de impresora funciona
- [ ] Provisioning funciona
- [ ] Discovery funciona
- [ ] Cierres mensuales cargan
- [ ] Exportar a Excel funciona
- [ ] Logout funciona

### 16. Tests de Seguridad

- [ ] Tokens JWT funcionan
- [ ] Refresh token funciona
- [ ] Rotación automática funciona (esperar 25 min)
- [ ] Encriptación de passwords funciona
- [ ] Sanitización de inputs funciona
- [ ] CSRF tokens funcionan (si habilitado)
- [ ] HTTPS redirect funciona (si habilitado)

### 17. Tests de Rendimiento

- [ ] Página carga en <3 segundos
- [ ] API responde en <500ms
- [ ] Sin memory leaks (verificar después de 1 hora)
- [ ] Base de datos responde rápido

---

## 📝 Documentación

### 18. Documentar Configuración

Crear archivo `CONFIGURACION_SERVIDOR.md` con:
- [ ] IP del servidor
- [ ] Credenciales de superadmin
- [ ] Ubicación de backups
- [ ] Comandos útiles
- [ ] Contactos de soporte

---

## 🎉 Despliegue Completado

### Checklist Final

#### Infraestructura
- [ ] Servidor preparado
- [ ] Docker funcionando
- [ ] Contenedores corriendo
- [ ] Red configurada

#### Configuración
- [ ] Variables de entorno configuradas
- [ ] Claves de seguridad generadas
- [ ] CORS configurado
- [ ] Backups configurados

#### Funcionalidad
- [ ] Backend funcionando
- [ ] Frontend funcionando
- [ ] Base de datos funcionando
- [ ] Todas las features probadas

#### Seguridad
- [ ] Encriptación activa
- [ ] Sanitización activa
- [ ] Tokens JWT funcionando
- [ ] Rotación automática funcionando
- [ ] CSRF configurado (opcional)
- [ ] HTTPS configurado (opcional)

#### Documentación
- [ ] Configuración documentada
- [ ] Credenciales guardadas de forma segura
- [ ] Procedimientos de backup documentados
- [ ] Contactos de soporte definidos

---

## 🚨 Troubleshooting Rápido

### Backend no inicia
```bash
docker-compose logs backend
# Buscar error específico
```

### Error "ENCRYPTION_KEY not set"
```bash
# Verificar .env
cat .env | grep ENCRYPTION_KEY
cat backend/.env | grep ENCRYPTION_KEY
```

### Frontend no conecta
```bash
# Verificar CORS
cat .env | grep CORS_ORIGINS
# Debe incluir IP desde donde accedes
```

### Base de datos no conecta
```bash
# Verificar password
cat .env | grep POSTGRES_PASSWORD
cat backend/.env | grep DATABASE_URL
# Deben coincidir
```

---

**Fecha de Despliegue:** _______________  
**Desplegado por:** _______________  
**Versión:** 1.0.0  
**Estado:** ⬜ En Progreso / ✅ Completado

---

**Documentación Completa:**
- `INSTRUCCIONES_DESPLIEGUE_PRODUCCION.md` - Guía detallada
- `RESUMEN_FINAL_SEGURIDAD.md` - Resumen de implementación
- `docs/CRITICAL_SECURITY_IMPLEMENTATION.md` - Guía técnica
