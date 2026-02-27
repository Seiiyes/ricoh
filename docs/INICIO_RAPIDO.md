# 🚀 Inicio Rápido - Sistema de Gestión Ricoh

## Primera Vez (Instalación)

### 1. Instalar Dependencias Backend
```powershell
cd backend
pip install -r requirements.txt
```
Espera 2-3 minutos a que termine.

### 2. Instalar Dependencias Frontend
```powershell
npm install
```
Espera 1-2 minutos a que termine.

---

## Uso Diario (Cada vez que uses el sistema)

### Paso 1: Iniciar Backend
**Opción A** - Doble click en: `backend\start-backend.bat`

**Opción B** - Línea de comandos:
```powershell
cd backend
python -m uvicorn main:app --reload
```

✅ Verás: `INFO: Uvicorn running on http://127.0.0.1:8000`

⚠️ **IMPORTANTE**: Deja esta ventana abierta

### Paso 2: Iniciar Frontend
**Opción A** - Doble click en: `start-dev.bat`

**Opción B** - Línea de comandos:
```powershell
npm run dev
```

✅ Verás: `Local: http://localhost:5173/`

### Paso 3: Abrir en Navegador
Abre: http://localhost:5173

---

## Verificación Rápida

### ¿Backend funcionando?
Abre: http://localhost:8000/docs
- ✅ Si ves documentación API → Funciona
- ❌ Si no carga → Backend no está corriendo

### ¿Frontend funcionando?
Abre: http://localhost:5173
- ✅ Si ves la interfaz → Funciona
- ❌ Si no carga → Frontend no está corriendo

---

## Solución de Problemas Comunes

### Error: "Error al sincronizar usuarios"
**Causa**: Backend no está corriendo
**Solución**: Inicia el backend con `start-backend.bat`

### Error: "Cannot connect to database"
**Causa**: PostgreSQL no está corriendo
**Solución**: 
```powershell
docker-compose up -d db
```

### Error: "Port 8000 already in use"
**Causa**: Ya hay un backend corriendo
**Solución**: Cierra la otra ventana o usa otro puerto:
```powershell
python -m uvicorn main:app --reload --port 8001
```

---

## Detener el Sistema

1. **Frontend**: Presiona `Ctrl+C` en la terminal
2. **Backend**: Presiona `Ctrl+C` en la terminal
3. **Base de datos** (opcional):
```powershell
docker-compose down
```

---

## Estructura de Carpetas

```
ricoh/
├── backend/              # Servidor Python (FastAPI)
│   ├── start-backend.bat # ← Doble click para iniciar
│   ├── main.py          # Punto de entrada
│   └── requirements.txt # Dependencias
├── src/                 # Frontend React
├── start-dev.bat        # ← Doble click para iniciar frontend
└── docker-compose.yml   # Base de datos PostgreSQL
```

---

## Comandos de Referencia

```powershell
# Backend
cd backend
python -m uvicorn main:app --reload

# Frontend
npm run dev

# Base de datos
docker-compose up -d db
docker-compose down

# Instalar dependencias
cd backend && pip install -r requirements.txt
npm install
```
