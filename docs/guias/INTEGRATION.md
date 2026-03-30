# Guía de Integración - Ricoh Multi-Fleet Governance Suite

## 🎯 Resumen

Backend Python (FastAPI) completamente integrado con el frontend React/TypeScript existente.

## 📁 Estructura del Proyecto

```
ricoh-suite/
├── backend/                    # 🆕 Backend Python
│   ├── main.py                # FastAPI app principal
│   ├── models.py              # Pydantic schemas
│   ├── scanner.py             # Lógica de escaneo de red
│   ├── requirements.txt       # Dependencias Python
│   ├── .env.example           # Configuración de ejemplo
│   ├── .gitignore             # Archivos ignorados
│   ├── test_api.py            # Script de pruebas
│   └── README.md              # Documentación del backend
├── src/
│   ├── services/
│   │   └── printerService.ts  # ✅ ACTUALIZADO - Conectado al backend
│   └── components/
│       └── governance/
│           └── ProvisioningPanel.tsx  # ✅ ACTUALIZADO - Botón de escaneo
├── start-dev.bat              # 🆕 Script de inicio Windows
├── start-dev.sh               # 🆕 Script de inicio Linux/Mac
├── .env.example               # 🆕 Variables de entorno frontend
└── INTEGRATION.md             # 🆕 Esta guía
```

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

**Windows:**
```cmd
start-dev.bat
```

**Linux/Mac:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### Opción 2: Manual

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
npm install
npm run dev
```

## 🔗 URLs de Acceso

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## 🧪 Verificar Instalación

### 1. Probar Backend
```bash
cd backend
python test_api.py
```

### 2. Probar Endpoint de Salud
```bash
curl http://localhost:8000/
```

Respuesta esperada:
```json
{
  "service": "Ricoh Fleet Governance API",
  "status": "online",
  "version": "1.0.0",
  "demo_mode": true
}
```

### 3. Probar Escaneo
```bash
curl "http://localhost:8000/scan?ip_range=192.168.1.0/24"
```

## 🎮 Uso desde el Frontend

### 1. Escanear Red

1. Abre http://localhost:5173
2. En el campo "IP Range", ingresa: `192.168.1.0/24`
3. Haz clic en "Scan Network"
4. Verás 3 impresoras demo aparecer en el grid

### 2. Ver Consola en Vivo

Los logs aparecerán en la consola inferior mostrando:
- Inicio de escaneo
- Resultados encontrados
- Errores (si los hay)

### 3. Modo Demo vs Producción

**Modo Demo (por defecto):**
- Retorna 3 impresoras ficticias
- No requiere hardware físico
- Ideal para desarrollo

**Modo Producción:**
```bash
# En backend/.env
DEMO_MODE=false
```
- Escanea red real
- Detecta impresoras por puertos 80, 443, 161
- Requiere permisos de red

## 📡 API Endpoints Disponibles

### GET /scan
Escanea la red en busca de impresoras

**Query Params:**
- `ip_range` (string): Rango CIDR (ej: "192.168.1.0/24")

**Ejemplo:**
```bash
curl "http://localhost:8000/scan?ip_range=192.168.1.0/24"
```

### POST /register
Registra una impresora con nombre personalizado

**Body:**
```json
{
  "ip": "192.168.1.100",
  "assigned_name": "Impresora Oficina Principal"
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"ip":"192.168.1.100","assigned_name":"Impresora Principal"}'
```

### GET /fleet
Obtiene todas las impresoras registradas

**Ejemplo:**
```bash
curl http://localhost:8000/fleet
```

### DELETE /fleet/{ip}
Elimina una impresora del registro

**Ejemplo:**
```bash
curl -X DELETE http://localhost:8000/fleet/192.168.1.100
```

## 🔧 Configuración

### Variables de Entorno - Backend

Archivo: `backend/.env`

```env
DEMO_MODE=true
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Variables de Entorno - Frontend

Archivo: `.env`

```env
VITE_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Backend no inicia

**Error: "ModuleNotFoundError: No module named 'fastapi'"**
```bash
cd backend
pip install -r requirements.txt
```

**Error: "Address already in use"**
```bash
# Cambiar puerto en backend/.env
API_PORT=8001
```

### Frontend no conecta al backend

**Error: "Failed to fetch"**
1. Verifica que el backend esté corriendo: http://localhost:8000
2. Revisa CORS en `backend/main.py`
3. Verifica `.env` tenga `VITE_API_URL=http://localhost:8000`

### No aparecen impresoras

**En modo DEMO:**
- Verifica `DEMO_MODE=true` en `backend/.env`
- Reinicia el backend

**En modo PRODUCCIÓN:**
- Verifica que el rango IP sea correcto
- Asegúrate de tener permisos de red
- Revisa firewall/antivirus

## 📊 Flujo de Datos

```
Frontend (React)
    ↓
printerService.ts
    ↓ HTTP Request
FastAPI Backend
    ↓
scanner.py (async)
    ↓
Network Scan / Demo Data
    ↓ JSON Response
Frontend Store (Zustand)
    ↓
PrinterCard Components
```

## 🔐 Seguridad

### Producción Checklist

- [ ] Cambiar `DEMO_MODE=false`
- [ ] Configurar CORS con dominios específicos
- [ ] Agregar autenticación (JWT)
- [ ] Usar HTTPS
- [ ] Validar rangos IP permitidos
- [ ] Rate limiting en endpoints
- [ ] Logging de auditoría

## 📈 Próximos Pasos

### Backend
- [ ] Implementar consultas SNMP reales
- [ ] Agregar autenticación JWT
- [ ] Conectar base de datos (PostgreSQL)
- [ ] WebSockets para escaneos en tiempo real
- [ ] Health checks periódicos de dispositivos

### Frontend
- [ ] Implementar búsqueda/filtrado de impresoras
- [ ] Agregar modal de registro de impresoras
- [ ] Mostrar progreso de escaneo en tiempo real
- [ ] Agregar notificaciones toast
- [ ] Implementar selección múltiple funcional

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_api.py
```

### Frontend Tests
```bash
npm run test
```

### Integration Test Manual
1. Inicia ambos servicios
2. Abre http://localhost:5173
3. Haz clic en "Scan Network"
4. Verifica que aparezcan 3 impresoras
5. Revisa la consola inferior para logs

## 📚 Recursos

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Pydantic**: https://docs.pydantic.dev
- **React Query** (recomendado para futuro): https://tanstack.com/query
- **Zustand**: https://github.com/pmndrs/zustand

## 💡 Tips de Desarrollo

1. **Hot Reload**: Ambos servicios tienen hot reload activado
2. **API Docs**: Usa http://localhost:8000/docs para probar endpoints
3. **Logs**: Backend muestra logs detallados en consola
4. **Demo Mode**: Mantén activado durante desarrollo
5. **CORS**: Ya está configurado para Vite dev server

## ✅ Checklist de Integración Completada

- [x] Backend FastAPI creado
- [x] Modelos Pydantic definidos
- [x] Scanner asíncrono implementado
- [x] Modo demo funcional
- [x] CORS configurado
- [x] Frontend service actualizado
- [x] Componente ProvisioningPanel actualizado
- [x] Scripts de inicio creados
- [x] Documentación completa
- [x] Tests básicos incluidos

## 🎉 ¡Listo para Usar!

El backend está completamente integrado y listo para desarrollo. Ejecuta `start-dev.bat` (Windows) o `./start-dev.sh` (Linux/Mac) y comienza a trabajar.

Para soporte o preguntas, revisa:
- `backend/README.md` - Documentación detallada del backend
- `README.md` - Documentación del proyecto completo
- http://localhost:8000/docs - API interactiva
