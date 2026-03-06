# 🔧 Troubleshooting - Frontend de Cierres

**Problema:** No se visualizan los cierres en el frontend

---

## 📋 Checklist de Verificación

### 1. Backend Funcionando
```bash
# Verificar que el backend esté healthy
docker-compose ps

# Debe mostrar:
# ricoh-backend    Up X minutes (healthy)
```

### 2. Endpoint de Cierres Funcionando
```bash
# Probar endpoint directamente
curl http://localhost:8000/api/counters/closes/4?tipo_periodo=diario&year=2026&limit=100
```

**Respuesta esperada:** JSON con array de cierres

### 3. CORS Configurado
El backend debe tener CORS habilitado para `http://localhost:5173`

**Verificar en:** `backend/main.py`
```python
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,...").split(",")
```

### 4. Frontend Corriendo
```bash
# Verificar que el frontend esté corriendo
docker ps | grep ricoh-frontend

# Debe mostrar:
# ricoh-frontend   Up X minutes   0.0.0.0:5173->5173/tcp
```

---

## 🔍 Debugging en el Navegador

### Paso 1: Abrir Consola del Navegador
1. Abrir `http://localhost:5173`
2. Presionar `F12` para abrir DevTools
3. Ir a la pestaña "Console"

### Paso 2: Verificar Logs
Buscar estos mensajes en la consola:

```
Loading printers from: http://localhost:8000/printers
Printers loaded: [...]
Loading cierres from: http://localhost:8000/api/counters/closes/4?tipo_periodo=diario&year=2026&limit=1000
Cierres loaded: [...]
ListaCierres rendered with: {...}
```

### Paso 3: Verificar Errores
Si hay errores, buscar:
- ❌ `CORS error` → Problema de CORS
- ❌ `404 Not Found` → Endpoint incorrecto
- ❌ `500 Internal Server Error` → Error en backend
- ❌ `Network error` → Backend no está corriendo

---

## 🐛 Problemas Comunes y Soluciones

### Problema 1: No se cargan las impresoras
**Síntomas:**
- Dropdown de impresoras vacío
- Mensaje "Selecciona una impresora"

**Solución:**
```bash
# Verificar endpoint de impresoras
curl http://localhost:8000/printers

# Si falla, reiniciar backend
cd backend
docker-compose restart backend
```

### Problema 2: No se cargan los cierres
**Síntomas:**
- Mensaje "No hay cierres"
- Loading infinito

**Diagnóstico:**
1. Abrir consola del navegador (F12)
2. Buscar el log: `Loading cierres from: ...`
3. Copiar la URL
4. Probar la URL en el navegador o con curl

**Solución A - Endpoint incorrecto:**
```typescript
// Verificar en CierresView.tsx
const url = `${API_BASE}/api/counters/closes/${selectedPrinter}?${params}`;
```

**Solución B - No hay datos:**
```bash
# Verificar que existan cierres en la base de datos
docker exec -it ricoh-backend python -c "
from db.database import get_db
from db.models import CierreMensual

db = next(get_db())
cierres = db.query(CierreMensual).all()
print(f'Total cierres: {len(cierres)}')
for c in cierres:
    print(f'  - ID {c.id}: {c.tipo_periodo} {c.fecha_inicio}')
"
```

### Problema 3: Error de CORS
**Síntomas:**
- Error en consola: `Access to fetch at 'http://localhost:8000/...' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Solución:**
1. Verificar configuración de CORS en `backend/main.py`
2. Reiniciar backend:
```bash
cd backend
docker-compose restart backend
```

### Problema 4: Datos se cargan pero no se muestran
**Síntomas:**
- Logs muestran "Cierres loaded: [...]"
- Pero no aparecen en pantalla

**Diagnóstico:**
```javascript
// En consola del navegador
console.log('Cierres:', cierres);
console.log('Cierres length:', cierres.length);
```

**Solución:**
Verificar que el componente `ListaCierres` esté recibiendo los datos:
```typescript
// Debe mostrar en consola:
ListaCierres rendered with: { printer: {...}, year: 2026, tipoPeriodo: 'diario', cierresCount: 3 }
```

---

## 🔧 Comandos Útiles

### Ver logs del backend
```bash
docker logs ricoh-backend --tail 50
```

### Ver logs del frontend
```bash
docker logs ricoh-frontend --tail 50
```

### Reiniciar todo el stack
```bash
cd backend
docker-compose down
docker-compose up -d
```

### Verificar que los servicios estén corriendo
```bash
docker-compose ps
```

### Probar endpoint de cierres
```bash
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/counters/closes/4?tipo_periodo=diario&year=2026&limit=100" -Method Get | ConvertTo-Json -Depth 5
```

---

## 📊 Verificar Datos en Base de Datos

### Ver cierres existentes
```bash
docker exec -it ricoh-backend python -c "
from db.database import get_db
from db.models import CierreMensual

db = next(get_db())
cierres = db.query(CierreMensual).order_by(CierreMensual.id.desc()).limit(10).all()

print('Últimos 10 cierres:')
for c in cierres:
    print(f'ID: {c.id} | Impresora: {c.printer_id} | Tipo: {c.tipo_periodo} | Fecha: {c.fecha_inicio} a {c.fecha_fin}')
"
```

### Ver impresoras disponibles
```bash
docker exec -it ricoh-backend python -c "
from db.database import get_db
from db.models import Printer

db = next(get_db())
printers = db.query(Printer).all()

print('Impresoras disponibles:')
for p in printers:
    print(f'ID: {p.id} | Hostname: {p.hostname} | IP: {p.ip_address}')
"
```

---

## 🎯 Flujo de Debugging Recomendado

1. **Verificar Backend**
   ```bash
   docker-compose ps
   docker logs ricoh-backend --tail 20
   ```

2. **Probar Endpoints**
   ```bash
   curl http://localhost:8000/printers
   curl http://localhost:8000/api/counters/closes/4?tipo_periodo=diario&year=2026&limit=100
   ```

3. **Abrir Frontend**
   - Ir a `http://localhost:5173`
   - Abrir DevTools (F12)
   - Ir a pestaña "Console"

4. **Verificar Logs en Consola**
   - Buscar "Loading printers from..."
   - Buscar "Printers loaded..."
   - Buscar "Loading cierres from..."
   - Buscar "Cierres loaded..."

5. **Verificar Network Tab**
   - Ir a pestaña "Network" en DevTools
   - Filtrar por "Fetch/XHR"
   - Ver requests a `/printers` y `/closes`
   - Verificar status codes (200 = OK)

6. **Verificar Datos**
   - Si los requests son exitosos pero no se muestran
   - Verificar en consola: `ListaCierres rendered with: {...}`
   - Verificar que `cierresCount` sea > 0

---

## ✅ Checklist Final

- [ ] Backend está healthy
- [ ] Endpoint `/printers` devuelve datos
- [ ] Endpoint `/api/counters/closes/{id}` devuelve datos
- [ ] Frontend está corriendo en puerto 5173
- [ ] No hay errores de CORS en consola
- [ ] Logs muestran "Printers loaded"
- [ ] Logs muestran "Cierres loaded"
- [ ] `cierresCount` > 0 en logs
- [ ] Componente `ListaCierres` se renderiza

---

## 📞 Si Nada Funciona

1. Reiniciar todo:
```bash
cd backend
docker-compose down
docker-compose up -d
```

2. Esperar 30 segundos

3. Verificar que todo esté healthy:
```bash
docker-compose ps
```

4. Abrir navegador en modo incógnito:
```
http://localhost:5173
```

5. Abrir DevTools (F12) y revisar consola

---

**Última actualización:** 4 de marzo de 2026
