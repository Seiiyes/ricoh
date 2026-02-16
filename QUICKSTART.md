# 🚀 Quick Start - Ricoh Multi-Fleet Governance Suite

## ⚡ Inicio en 3 Pasos

### 1️⃣ Clonar e Instalar

```bash
# Ya tienes el proyecto, solo instala dependencias
npm install
```

### 2️⃣ Iniciar Servicios

**Opción A - Script Automático (Recomendado):**

Windows:
```cmd
start-dev.bat
```

Linux/Mac:
```bash
./start-dev.sh
```

**Opción B - Manual:**

Terminal 1 (Backend):
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
```

Terminal 2 (Frontend):
```bash
npm run dev
```

### 3️⃣ Abrir y Usar

1. Abre http://localhost:5173
2. Haz clic en "Scan Network"
3. ¡Verás 3 impresoras demo aparecer!

## 🎯 Primeros Pasos

### Ver API Docs
http://localhost:8000/docs

### Probar Endpoint Manualmente
```bash
curl "http://localhost:8000/scan?ip_range=192.168.1.0/24"
```

### Cambiar Rango de IP
En el frontend, cambia el campo "IP Range (CIDR)" a tu red local, por ejemplo:
- `10.0.0.0/24`
- `172.16.0.0/24`
- `192.168.0.0/24`

## 🔧 Configuración Rápida

### Activar Modo Producción (Escaneo Real)

1. Edita `backend/.env`:
```env
DEMO_MODE=false
```

2. Reinicia el backend

### Cambiar Puerto del Backend

1. Edita `backend/.env`:
```env
API_PORT=8001
```

2. Edita `.env` (frontend):
```env
VITE_API_URL=http://localhost:8001
```

3. Reinicia ambos servicios

## 🐛 Problemas Comunes

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
cd backend
pip install -r requirements.txt
```

### "Failed to fetch" en el frontend
1. Verifica que el backend esté corriendo: http://localhost:8000
2. Revisa que `.env` tenga `VITE_API_URL=http://localhost:8000`

### Puerto 8000 ya en uso
```bash
# Encuentra el proceso
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Mata el proceso o cambia el puerto en backend/.env
```

## 📚 Siguiente Paso

Lee [INTEGRATION.md](INTEGRATION.md) para documentación completa.

## ✅ Checklist de Verificación

- [ ] Backend corriendo en http://localhost:8000
- [ ] Frontend corriendo en http://localhost:5173
- [ ] API docs accesible en http://localhost:8000/docs
- [ ] Botón "Scan Network" funciona
- [ ] Aparecen 3 impresoras demo
- [ ] Logs aparecen en consola inferior

## 🎉 ¡Listo!

Ya tienes el sistema completo funcionando. Explora la interfaz y prueba las funcionalidades.
