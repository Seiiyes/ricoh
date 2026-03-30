# Solución: Error al Sincronizar Usuarios

## Problema Identificado

El error "❌ Error al sincronizar usuarios desde las impresoras" ocurre porque **el servidor backend NO está corriendo**.

## Solución Rápida (3 pasos)

### 1. Instalar Dependencias (solo primera vez)

```powershell
cd C:\Users\juan.lizarazo\Desktop\ricoh\backend
pip install -r requirements.txt
```

**NOTA**: Si falla con error de Rust/pydantic-core, ya actualicé el archivo `requirements.txt` para usar una versión compatible. Intenta de nuevo.

### 2. Iniciar el Servidor Backend

**Opción A - Doble click (más fácil)**:
1. Ve a la carpeta `backend/`
2. Doble click en `start-backend.bat`
3. Deja la ventana abierta

**Opción B - Línea de comandos**:
```powershell
cd C:\Users\juan.lizarazo\Desktop\ricoh\backend
python -m uvicorn main:app --reload
```

**IMPORTANTE**: Deja esta terminal/ventana abierta. Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### 3. Probar la Sincronización

Ahora desde el frontend, haz clic en "Sincronizar Todos" nuevamente. Debería funcionar.

---

## Solución al Error de Rust/pydantic-core

Si al instalar dependencias ves este error:
```
Cargo, the Rust package manager, is not installed or is not on PATH.
This package requires Rust and Cargo to compile extensions.
```

**Solución**: Ya actualicé `requirements.txt` para usar `pydantic==2.9.2` que tiene wheels pre-compilados para Windows. 

Simplemente ejecuta de nuevo:
```powershell
pip install -r requirements.txt
```

---

## Si Aún Hay Errores

### Opción A: Probar el Endpoint Directamente

1. Abre http://localhost:8000/docs
2. Busca `POST /discovery/sync-users-from-printers`
3. Click en "Try it out"
4. Click en "Execute"
5. Mira la respuesta

### Opción B: Ver los Logs del Backend

En la terminal donde está corriendo `uvicorn`, verás los logs en tiempo real. Si hay un error, aparecerá en rojo con el traceback completo.

### Opción C: Probar con Script

```powershell
cd backend
python test_sync_endpoint.py
```

Este script te dirá si el endpoint responde correctamente.

## Comandos Útiles

### Iniciar Backend (Forma Rápida)
```powershell
cd backend
python -m uvicorn main:app --reload
```

### Iniciar Backend + Frontend
```powershell
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2 - Frontend
npm run dev
```

### Ver si el Backend Está Corriendo
```powershell
curl http://localhost:8000/docs
```

## Notas Importantes

1. **El backend DEBE estar corriendo** antes de usar el frontend
2. **Las dependencias DEBEN estar instaladas** (`pip install -r requirements.txt`)
3. **PostgreSQL DEBE estar corriendo** (si usas Docker: `docker-compose up -d db`)

## Verificación Final

Una vez que el backend esté corriendo correctamente:

1. Abre el frontend
2. Ve a la sección de Usuarios
3. Click en "Sincronizar Todos"
4. Deberías ver un mensaje como:
   ```
   ✅ Se encontraron X usuarios únicos en Y impresora(s)
   💾 Z en DB | 🖨️ W solo en impresoras
   ```

## Si el Problema Persiste

Comparte:
1. Los logs completos del backend (la terminal donde corre uvicorn)
2. El resultado de `python test_sync_endpoint.py`
3. Captura de pantalla del error en el frontend


## Verificación Visual

### ✅ Backend Corriendo Correctamente
Cuando el backend está corriendo, verás en la terminal:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Puedes verificar abriendo en tu navegador: http://localhost:8000/docs

### ✅ Sincronización Exitosa
Cuando sincronices desde el frontend, verás:
```
✅ Se encontraron X usuarios únicos en Y impresora(s)
💾 Z en DB | 🖨️ W solo en impresoras
```

### ❌ Backend NO está corriendo
Si ves este error en el frontend:
```
❌ Error al sincronizar usuarios desde las impresoras
```

Significa que el backend NO está corriendo. Inicia el servidor con `start-backend.bat`.

---

## Comandos de Referencia Rápida

```powershell
# Instalar dependencias (solo primera vez)
cd C:\Users\juan.lizarazo\Desktop\ricoh\backend
pip install -r requirements.txt

# Iniciar backend
cd C:\Users\juan.lizarazo\Desktop\ricoh\backend
python -m uvicorn main:app --reload

# O simplemente doble click en:
backend\start-backend.bat
```

---

## Preguntas Frecuentes

**P: ¿Tengo que iniciar el backend cada vez?**
R: Sí, cada vez que reinicies tu computadora o cierres la terminal.

**P: ¿Puedo cerrar la ventana del backend?**
R: No, si la cierras el backend se detiene y el frontend no funcionará.

**P: ¿Cómo sé si el backend está corriendo?**
R: Abre http://localhost:8000/docs en tu navegador. Si ves la documentación de la API, está corriendo.

**P: ¿Qué hago si el puerto 8000 está ocupado?**
R: Cambia el puerto: `python -m uvicorn main:app --reload --port 8001`
