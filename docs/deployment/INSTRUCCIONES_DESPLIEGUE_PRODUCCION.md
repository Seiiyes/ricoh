# 🚀 Instrucciones de Despliegue a Producción

## 📋 Resumen

Este documento describe los pasos necesarios para desplegar el sistema Ricoh Equipment Management en el servidor de la empresa (PC 24/7).

---

## ✅ Estado Actual

Todo está implementado y listo para producción:

- ✅ 5 mejoras críticas de seguridad implementadas
- ✅ Frontend actualizado con soporte CSRF y rotación de tokens
- ✅ Backend con encriptación y sanitización integradas
- ✅ 38 tests unitarios pasando (100%)
- ✅ Documentación completa

**Solo falta:** Configurar variables de entorno en el servidor de producción.

---

## 🖥️ Requisitos del Servidor

### Hardware Mínimo
- CPU: 2 cores
- RAM: 4 GB
- Disco: 20 GB libres
- Red: Conexión estable

### Software Requerido
- Docker y Docker Compose
- Sistema operativo: Windows/Linux
- Acceso a red local de la empresa

---

## 📝 Pasos de Despliegue

### 1. Preparar el Servidor

```bash
# Clonar el repositorio en el servidor
git clone <url_del_repositorio> /ruta/en/servidor
cd /ruta/en/servidor
```

### 2. Configurar Variables de Entorno

Crear/editar el archivo `.env` en la raíz del proyecto:

```bash
# ============================================
# CONFIGURACIÓN DE PRODUCCIÓN
# ============================================

# Entorno
ENVIRONMENT=production

# Base de Datos PostgreSQL
POSTGRES_USER=ricoh_admin
POSTGRES_PASSWORD=<cambiar_por_password_seguro>
POSTGRES_DB=ricoh_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# API Backend
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://<ip_del_servidor>:5173

# Seguridad - JWT
SECRET_KEY=<generar_clave_segura_minimo_32_caracteres>

# Seguridad - Encriptación (NUEVO)
ENCRYPTION_KEY=<generar_con_comando_abajo>

# Seguridad - HTTPS (NUEVO)
FORCE_HTTPS=false  # Cambiar a true si tienes certificado SSL

# Seguridad - CSRF (NUEVO - OPCIONAL)
ENABLE_CSRF=false  # Cambiar a true para habilitar protección CSRF

# Logging
LOG_LEVEL=INFO

# Demo Mode
DEMO_MODE=false
```

### 3. Generar Claves de Seguridad

#### Generar ENCRYPTION_KEY:

```bash
# En el servidor, ejecutar:
cd backend
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Copiar el resultado y pegarlo en .env como ENCRYPTION_KEY
```

#### Generar SECRET_KEY (si no existe):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copiar el resultado y pegarlo en .env como SECRET_KEY
```

### 4. Configurar Backend (.env en /backend)

Crear/editar `backend/.env`:

```bash
# Copiar las mismas variables del .env principal
ENVIRONMENT=production
SECRET_KEY=<misma_clave_del_env_principal>
ENCRYPTION_KEY=<misma_clave_del_env_principal>
FORCE_HTTPS=false
ENABLE_CSRF=false

# Base de datos
DATABASE_URL=postgresql://ricoh_admin:<password>@postgres:5432/ricoh_db
```

### 5. Iniciar el Sistema

```bash
# Construir e iniciar contenedores
docker-compose up -d --build

# Verificar que los contenedores están corriendo
docker-compose ps

# Ver logs
docker-compose logs -f backend
```

### 6. Verificar el Despliegue

#### Backend:
```bash
# Verificar que el backend responde
curl http://localhost:8000/

# Debería retornar:
# {
#   "service": "Ricoh Equipment Management API",
#   "status": "online",
#   "version": "2.0.0"
# }
```

#### Frontend:
```bash
# Abrir en navegador
http://localhost:5173

# O desde otra PC en la red:
http://<ip_del_servidor>:5173
```

#### Base de Datos:
```bash
# Conectar a PostgreSQL
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_db

# Verificar tablas
\dt

# Salir
\q
```

### 7. Crear Usuario Superadmin

```bash
# Ejecutar script de inicialización
docker exec -it ricoh-backend python scripts/init_superadmin.py

# O manualmente en la base de datos
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_db

# Insertar superadmin (el password ya está hasheado)
INSERT INTO admin_users (username, password_hash, nombre_completo, email, rol, is_active)
VALUES ('superadmin', '<hash_bcrypt>', 'Administrador Principal', 'admin@empresa.com', 'superadmin', true);
```

---

## 🔐 Configuración de Seguridad Adicional

### Habilitar HTTPS (Recomendado)

Si tienes un certificado SSL:

1. Configurar nginx o Apache como reverse proxy
2. Configurar certificado SSL
3. Cambiar en `.env`:
   ```bash
   FORCE_HTTPS=true
   CORS_ORIGINS=https://<dominio_empresa>
   ```

### Habilitar CSRF (Opcional)

Para mayor seguridad:

```bash
# En .env
ENABLE_CSRF=true
```

El frontend ya está preparado para manejar tokens CSRF automáticamente.

---

## 📊 Monitoreo y Mantenimiento

### Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo base de datos
docker-compose logs -f postgres
```

### Backup de Base de Datos

```bash
# Crear backup
docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker exec -i ricoh-postgres psql -U ricoh_admin ricoh_db < backup_20260320.sql
```

### Actualizar el Sistema

```bash
# Detener servicios
docker-compose down

# Actualizar código
git pull

# Reconstruir e iniciar
docker-compose up -d --build
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar solo backend
docker-compose restart backend
```

---

## 🔧 Troubleshooting

### Backend no inicia

```bash
# Ver logs detallados
docker-compose logs backend

# Verificar variables de entorno
docker exec ricoh-backend env | grep ENCRYPTION_KEY

# Verificar conexión a BD
docker exec ricoh-backend python -c "from db.database import engine; print(engine.url)"
```

### Error "ENCRYPTION_KEY not set"

```bash
# Verificar que ENCRYPTION_KEY está en .env
cat .env | grep ENCRYPTION_KEY

# Regenerar si es necesario
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Reiniciar backend
docker-compose restart backend
```

### Frontend no conecta con Backend

```bash
# Verificar CORS_ORIGINS en .env
cat .env | grep CORS_ORIGINS

# Debe incluir la IP/dominio desde donde accedes
CORS_ORIGINS=http://localhost:5173,http://192.168.1.100:5173
```

### Base de datos no inicia

```bash
# Ver logs
docker-compose logs postgres

# Verificar volumen
docker volume ls | grep ricoh

# Recrear volumen (CUIDADO: borra datos)
docker-compose down -v
docker-compose up -d
```

---

## 📱 Acceso desde Otras PCs

Para acceder desde otras computadoras en la red local:

1. Obtener IP del servidor:
   ```bash
   # Windows
   ipconfig
   
   # Linux
   ip addr show
   ```

2. Agregar IP a CORS_ORIGINS en `.env`:
   ```bash
   CORS_ORIGINS=http://localhost:5173,http://192.168.1.100:5173
   ```

3. Reiniciar backend:
   ```bash
   docker-compose restart backend
   ```

4. Acceder desde otra PC:
   ```
   http://192.168.1.100:5173
   ```

---

## ✅ Checklist de Despliegue

- [ ] Servidor preparado con Docker instalado
- [ ] Repositorio clonado en el servidor
- [ ] Archivo `.env` configurado con todas las variables
- [ ] `ENCRYPTION_KEY` generada y configurada
- [ ] `SECRET_KEY` generada y configurada
- [ ] `backend/.env` configurado
- [ ] Contenedores iniciados con `docker-compose up -d`
- [ ] Backend responde en `http://localhost:8000`
- [ ] Frontend accesible en `http://localhost:5173`
- [ ] Base de datos inicializada
- [ ] Usuario superadmin creado
- [ ] Acceso desde otras PCs configurado (si aplica)
- [ ] Backup automático configurado (recomendado)

---

## 📞 Soporte

Si encuentras problemas durante el despliegue:

1. Revisa los logs: `docker-compose logs -f`
2. Consulta `TROUBLESHOOTING_DOCKER.md`
3. Verifica la documentación en `docs/`

---

**Fecha:** 20 de Marzo de 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para Producción
