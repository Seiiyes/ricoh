# 🚀 Instalación en un Nuevo Equipo

**Guía paso a paso para instalar el sistema en otro equipo desde cero.**

---

## 📋 Requisitos Previos

### Software Necesario

- **Git** - Para clonar el repositorio
- **Docker Desktop** - Para ejecutar con Docker (recomendado)
- **Node.js 20+** - Para el frontend (si no usas Docker)
- **Python 3.11+** - Para el backend (si no usas Docker)
- **PostgreSQL 16** - Para la base de datos (si no usas Docker)

---

## 🔧 Opción 1: Instalación con Docker (Recomendado)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/Seiiyes/ricoh.git
cd ricoh
```

### Paso 2: Configurar Variables de Entorno

**Frontend:**
```bash
# Copiar plantilla
cp .env.example .env

# Editar (opcional, los valores por defecto funcionan)
# notepad .env  # Windows
# nano .env     # Linux/Mac
```

**Backend:**
```bash
# Copiar plantilla
cp backend/.env.example backend/.env

# Editar (opcional, los valores por defecto funcionan)
# notepad backend/.env  # Windows
# nano backend/.env     # Linux/Mac
```

**Valores por defecto (ya configurados en .env.example):**
```env
# Frontend (.env)
VITE_API_URL=http://localhost:8000

# Backend (backend/.env)
DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@postgres:5432/ricoh_fleet
DEMO_MODE=false
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Paso 3: Iniciar con Docker

**Windows:**
```cmd
docker-start.bat
```

**Linux/Mac:**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

### Paso 4: Verificar que Todo Funciona

Abre tu navegador:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer: http://localhost:8080

**¡Listo! El sistema está funcionando.**

---

## 🔧 Opción 2: Instalación Manual (Sin Docker)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/Seiiyes/ricoh.git
cd ricoh
```

### Paso 2: Instalar PostgreSQL

**Windows:**
1. Descarga PostgreSQL 16 desde: https://www.postgresql.org/download/windows/
2. Instala con los valores por defecto
3. Anota la contraseña del usuario `postgres`

**Linux:**
```bash
sudo apt update
sudo apt install postgresql-16
```

**Mac:**
```bash
brew install postgresql@16
```

### Paso 3: Crear Base de Datos

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear usuario y base de datos
CREATE USER ricoh_admin WITH PASSWORD 'ricoh_secure_2024';
CREATE DATABASE ricoh_fleet OWNER ricoh_admin;
\q
```

### Paso 4: Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env

# Editar .env con tu configuración
# notepad .env  # Windows
# nano .env     # Linux/Mac

# Inicializar base de datos
python init_db.py

# Iniciar backend
python main.py
```

El backend estará en: http://localhost:8000

### Paso 5: Configurar Frontend

**En otra terminal:**

```bash
# Volver a la raíz del proyecto
cd ..

# Instalar dependencias
npm install

# Copiar variables de entorno
cp .env.example .env

# Iniciar frontend
npm run dev
```

El frontend estará en: http://localhost:5173

---

## ✅ Verificación de Instalación

### 1. Verificar Backend

Abre: http://localhost:8000

Deberías ver:
```json
{
  "message": "Ricoh Fleet Governance API",
  "version": "3.3",
  "status": "running"
}
```

### 2. Verificar API Docs

Abre: http://localhost:8000/docs

Deberías ver la documentación Swagger con todos los endpoints.

### 3. Verificar Frontend

Abre: http://localhost:5173

Deberías ver la interfaz del sistema con:
- Panel izquierdo: Formulario de usuario
- Panel derecho: Grid de impresoras
- Panel inferior: Registro de actividad

### 4. Verificar Base de Datos

**Con Docker:**
- Abre: http://localhost:8080
- Server: `postgres`
- Username: `ricoh_admin`
- Password: `ricoh_secure_2024`
- Database: `ricoh_fleet`

**Sin Docker:**
```bash
psql -U ricoh_admin -d ricoh_fleet
\dt  # Ver tablas
```

Deberías ver las tablas:
- `users`
- `printers`
- `user_printer_assignments`

---

## 🔍 Solución de Problemas Comunes

### Problema 1: "No se encuentra git"

**Solución:**
```bash
# Instalar Git
# Windows: https://git-scm.com/download/win
# Linux: sudo apt install git
# Mac: brew install git
```

### Problema 2: "No se encuentra docker"

**Solución:**
```bash
# Instalar Docker Desktop
# Windows/Mac: https://www.docker.com/products/docker-desktop
# Linux: https://docs.docker.com/engine/install/
```

### Problema 3: "Puerto 5173 ya está en uso"

**Solución:**
```bash
# Cambiar puerto en vite.config.ts
# O matar el proceso que usa el puerto
# Windows: netstat -ano | findstr :5173
# Linux/Mac: lsof -i :5173
```

### Problema 4: "No se puede conectar a la base de datos"

**Solución:**
```bash
# Verificar que PostgreSQL está corriendo
# Windows: Servicios → PostgreSQL
# Linux: sudo systemctl status postgresql
# Mac: brew services list

# Verificar credenciales en backend/.env
DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@localhost:5432/ricoh_fleet
```

### Problema 5: "npm install falla"

**Solución:**
```bash
# Limpiar cache
npm cache clean --force

# Eliminar node_modules
rm -rf node_modules
# Windows: rmdir /s /q node_modules

# Reinstalar
npm install
```

### Problema 6: "pip install falla"

**Solución:**
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Reinstalar
pip install -r requirements.txt
```

---

## 📦 Archivos que se Regeneran Automáticamente

Estos archivos NO están en el repositorio pero se crean automáticamente:

### Frontend
- `node_modules/` - Se crea con `npm install`
- `dist/` - Se crea con `npm run build`

### Backend
- `__pycache__/` - Se crea automáticamente por Python
- `venv/` - Se crea con `python -m venv venv`
- `*.pyc` - Se crean automáticamente

### Base de Datos
- `postgres_data/` - Se crea con Docker Compose
- Tablas - Se crean con `init_db.py`

### Archivos de Debug
- `provision_response.html` - Se crea durante debugging
- `add_user_form_debug.html` - Se crea durante debugging

---

## 🔐 Configuración de Producción

### Variables de Entorno Importantes

**Backend (.env):**
```env
# IMPORTANTE: Cambiar en producción
SECRET_KEY=tu-clave-secreta-aqui
ENCRYPTION_KEY=tu-clave-de-encriptacion-aqui

# Base de datos
DATABASE_URL=postgresql://usuario:password@host:5432/database

# CORS (agregar dominio de producción)
CORS_ORIGINS=https://tu-dominio.com

# Modo demo (desactivar en producción)
DEMO_MODE=false
```

**Frontend (.env):**
```env
# URL del backend en producción
VITE_API_URL=https://api.tu-dominio.com
```

---

## 📝 Checklist de Instalación

### Antes de Empezar
- [ ] Git instalado
- [ ] Docker instalado (opción 1) O Node.js + Python + PostgreSQL (opción 2)
- [ ] Acceso a GitHub

### Durante la Instalación
- [ ] Repositorio clonado
- [ ] Variables de entorno configuradas
- [ ] Dependencias instaladas
- [ ] Base de datos creada
- [ ] Servicios iniciados

### Verificación Final
- [ ] Backend responde en http://localhost:8000
- [ ] Frontend carga en http://localhost:5173
- [ ] API Docs accesible en http://localhost:8000/docs
- [ ] Base de datos tiene las tablas
- [ ] Puedes crear un usuario de prueba
- [ ] Puedes descubrir impresoras

---

## 🎯 Próximos Pasos Después de Instalar

1. **Descubrir impresoras:**
   - Click en "Descubrir Impresoras"
   - Ingresa rango IP de tu red
   - Registra las impresoras encontradas

2. **Crear usuario de prueba:**
   - Llena el formulario
   - Selecciona una impresora
   - Click en "Enviar Configuración"

3. **Verificar en la impresora:**
   - Abre la interfaz web de la impresora
   - Ve a la libreta de direcciones
   - Verifica que el usuario aparece

---

## 📞 Soporte

Si tienes problemas durante la instalación:

1. Revisa la sección "Solución de Problemas"
2. Verifica los logs:
   ```bash
   # Docker
   docker-compose logs -f
   
   # Manual
   # Ver terminal del backend y frontend
   ```
3. Consulta la documentación completa en el repositorio

---

## 🎉 ¡Instalación Completada!

Si llegaste hasta aquí y todo funciona, ¡felicidades! El sistema está listo para usar.

**Recuerda:**
- Los archivos `.env` son locales (cada equipo tiene los suyos)
- Las dependencias se instalan automáticamente
- La base de datos se crea automáticamente
- Todo está documentado en el repositorio

---

**Última actualización:** 16 de Febrero de 2026  
**Versión del sistema:** 3.3
