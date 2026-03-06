# Investigación: Datos Inconsistentes en Contadores de Usuario

## Problema Reportado

Usuario reporta que los datos mostrados en el frontend NO coinciden con los datos de la web de la impresora.

### Ejemplo Específico:
- **Usuario**: DAVID SANDOVAL (código 1305)
- **Web de impresora**: Total = 72 páginas
- **Frontend**: Total = 655 páginas

## Análisis del Flujo de Datos

```
Web Impresora → Parser Python → Base de Datos → API Backend → Frontend
```

### 1. Frontend (✅ CORRECTO)
- El frontend muestra los datos EXACTAMENTE como vienen del backend
- No hace ningún cálculo, solo muestra los valores
- Código verificado en `UserCounterTable.tsx`

### 2. API Backend (✅ CORRECTO)
- El endpoint `/api/counters/users/{printer_id}` retorna los datos directamente de la base de datos
- Usa `get_user_counters_latest()` que obtiene todos los registros de la última sesión de lectura
- Código verificado en `backend/api/counters.py` y `backend/services/counter_service.py`

### 3. Base de Datos (❓ VERIFICAR)
- Los datos se guardan en la tabla `contador_usuario`
- Cada lectura crea nuevos registros con el mismo `created_at`
- Necesitamos verificar si los datos guardados son correctos

### 4. Parser Python (⚠️ SOSPECHOSO)
- **Archivo**: `backend/parsear_contadores_usuario.py`
- **Función**: `parse_user_counter_html()`
- Este es el punto más probable de fallo

## Posibles Causas

### A. Parser lee datos de la fila incorrecta
El parser puede estar leyendo datos de otro usuario o de otra sección de la tabla HTML.

### B. Parser suma valores incorrectamente
El parser puede estar sumando valores que no debería sumar (ej: B/N + Color cuando Color ya incluye B/N).

### C. Datos de sesiones anteriores
El backend puede estar mostrando datos de una lectura anterior en lugar de la más reciente.

### D. Paginación incorrecta
El parser puede estar saltando usuarios o duplicando datos al paginar.

## Plan de Acción

### Paso 1: Ejecutar Test de Precisión ✅
```bash
cd backend
python test_user_counters_accuracy.py 4
```

Este script:
1. Lee datos DIRECTOS de la web de la impresora
2. Lee datos del BACKEND (última lectura)
3. Compara usuario por usuario
4. Muestra discrepancias detalladas

### Paso 2: Analizar Resultados
El test mostrará:
- Usuarios que solo están en la web
- Usuarios que solo están en el backend
- Usuarios con totales diferentes
- Desglose completo de cada discrepancia

### Paso 3: Identificar Patrón
Buscar patrones en las discrepancias:
- ¿Todos los usuarios están mal o solo algunos?
- ¿La diferencia es consistente (ej: siempre +583)?
- ¿Los usuarios con discrepancias tienen algo en común?

### Paso 4: Corregir Parser
Según el patrón identificado:
- Ajustar índices de columnas en `parse_user_counter_html()`
- Corregir lógica de suma de totales
- Verificar manejo de paginación

### Paso 5: Verificar Corrección
1. Ejecutar lectura manual: `POST /api/counters/read/4`
2. Ejecutar test de precisión nuevamente
3. Verificar que accuracy = 100%

## Comandos Útiles

### Ver datos directos de la web
```bash
cd backend
python parsear_contadores_usuario.py
```

### Ver datos del backend
```bash
cd backend
python -c "
from db.database import get_db
from db.models import ContadorUsuario
db = next(get_db())
users = db.query(ContadorUsuario).filter(ContadorUsuario.printer_id == 4).order_by(ContadorUsuario.created_at.desc()).limit(10).all()
for u in users:
    print(f'{u.codigo_usuario} - {u.nombre_usuario}: {u.total_paginas}')
"
```

### Ejecutar lectura manual
```bash
curl -X POST http://localhost:8000/api/counters/read/4
```

## Notas Importantes

1. **NO modificar el frontend** - El frontend está mostrando los datos correctamente
2. **NO modificar la API** - La API está retornando los datos correctamente
3. **ENFOCARSE en el parser** - El problema está en cómo se leen los datos de la web

## Estado Actual

- ✅ Auto-reload removido del frontend
- ✅ Script de test creado
- ⏳ Pendiente: Ejecutar test y analizar resultados
- ⏳ Pendiente: Corregir parser según resultados

## Próximos Pasos

1. Usuario debe ejecutar: `backend\test-user-counters-accuracy.bat 4`
2. Compartir resultados completos del test
3. Analizar discrepancias y corregir parser
4. Verificar corrección con nuevo test
