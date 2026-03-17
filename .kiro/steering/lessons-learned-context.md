---
inclusion: auto
priority: high
---

# 🎓 Lecciones Aprendidas - Contexto Automático

Este documento se carga automáticamente en cada conversación para evitar repetir errores pasados.

---

## ⚠️ ERRORES CRÍTICOS A EVITAR

### 1. Importaciones en Python/FastAPI
**Error:** Usar módulos sin importarlos primero  
**Ejemplo:** Usar `counter_schemas.CierreMensualResponse` sin `from . import counter_schemas`

**Reglas:**
- ✅ SIEMPRE importar módulos antes de usarlos
- ✅ Usar imports relativos en FastAPI: `from . import module`
- ✅ Verificar imports al agregar nuevos endpoints
- ✅ Ejecutar linter antes de commit

**Referencia:** `.kiro/lessons-learned/001-error-importacion-api.md`

---

### 2. Lógica de Negocio - Primer Caso
**Error:** Asumir que siempre hay datos previos  
**Ejemplo:** Poner consumo = 0 cuando no hay cierre anterior

**Reglas:**
- ✅ SIEMPRE probar el "primer caso" (sin datos históricos)
- ✅ Validar que los cálculos funcionen sin datos previos
- ✅ No asumir que existe un registro anterior
- ✅ Documentar casos especiales en el código

**Código correcto para primer cierre:**
```python
if cierre_anterior:
    # Calcular diferencia
    consumo = actual - anterior
else:
    # Primer cierre: buscar inicio del período
    contador_inicio = buscar_inicio_periodo()
    if contador_inicio:
        consumo = actual - contador_inicio
    else:
        # Solo una lectura: usar total acumulado
        consumo = actual
```

**Referencia:** `.kiro/lessons-learned/002-consumo-usuarios-cero.md`

---

### 3. Rutas en FastAPI - Orden y Ambigüedad
**Error:** Definir rutas ambiguas que entran en conflicto  
**Ejemplo:** `/closes/{printer_id}` y `/closes/{cierre_id}` en el mismo router

**Reglas:**
- ✅ Rutas específicas ANTES que rutas generales
- ✅ Evitar rutas con el mismo patrón y tipo de parámetro
- ✅ Usar prefijos diferentes para recursos diferentes
- ✅ Probar cada endpoint individualmente

**Patrones correctos:**
```python
# ✅ CORRECTO - Rutas diferentes
@router.get("/closes/{printer_id}")  # Lista
@router.get("/monthly/{close_id}/detail")  # Detalle

# ✅ CORRECTO - Específica primero
@router.get("/closes/latest")  # Más específica
@router.get("/closes/{close_id}")  # Más general

# ❌ INCORRECTO - Ambiguo
@router.get("/closes/{printer_id}")
@router.get("/closes/{close_id}")  # Nunca se ejecuta
```

**Referencia:** `.kiro/lessons-learned/003-conflicto-rutas-fastapi.md`

---

### 4. Rutas de API en Frontend
**Error:** Asumir prefijos en rutas sin verificar  
**Ejemplo:** Usar `/api/printers` cuando el endpoint es `/printers`

**Reglas:**
- ✅ SIEMPRE verificar rutas reales del backend
- ✅ Consultar documentación de API antes de implementar
- ✅ Usar constantes para rutas (no hardcodear)
- ✅ Probar rutas en navegador/curl antes de integrar

**Patrón correcto:**
```typescript
// ✅ CORRECTO - Usar constantes
export const API_ROUTES = {
  PRINTERS: '/printers',  // Sin /api
  COUNTERS: '/api/counters/closes',  // Con /api
};

// Uso
fetch(`${API_BASE}${API_ROUTES.PRINTERS}`)
```

**Referencia:** `.kiro/lessons-learned/004-ruta-incorrecta-api.md`

---

### 5. Validación de Datos Disponibles
**Error:** Procesar sin verificar que existan datos necesarios  
**Ejemplo:** Crear cierre sin verificar que hay lecturas de usuarios

**Reglas:**
- ✅ SIEMPRE validar que existan datos antes de procesar
- ✅ Mostrar advertencias claras cuando faltan datos
- ✅ Documentar limitaciones del sistema
- ✅ Ofrecer alternativas cuando no hay datos

**Validación recomendada:**
```python
def validar_datos_disponibles(db, printer_id, fecha):
    lecturas = db.query(ContadorUsuario).filter(
        ContadorUsuario.printer_id == printer_id,
        ContadorUsuario.fecha_lectura == fecha
    ).count()
    
    if lecturas == 0:
        raise ValueError(
            f"No hay lecturas de usuarios para {fecha}. "
            "Ejecute sincronización antes de crear cierre."
        )
```

**Referencia:** `.kiro/lessons-learned/005-falta-datos-usuarios.md`

---

## 🎯 CHECKLIST ANTES DE IMPLEMENTAR

### Backend (Python/FastAPI)
- [ ] Todos los módulos están importados
- [ ] Lógica funciona sin datos previos (primer caso)
- [ ] Rutas no son ambiguas
- [ ] Validaciones de datos existen
- [ ] Tests incluyen casos extremos
- [ ] Linter ejecutado sin errores

### Frontend (TypeScript/React)
- [ ] Rutas de API verificadas con backend
- [ ] Constantes usadas para rutas
- [ ] Manejo de errores implementado
- [ ] Estados de carga manejados
- [ ] Validaciones de datos en UI

### Base de Datos
- [ ] Datos necesarios existen
- [ ] Migraciones probadas
- [ ] Índices optimizados
- [ ] Constraints validados

---

## 📚 PATRONES RECOMENDADOS

### 1. Imports en Python
```python
# ✅ CORRECTO
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from db.models import Model1, Model2
from services.service import Service
from . import schemas  # Import relativo
```

### 2. Validación de Datos
```python
# ✅ CORRECTO
def procesar_datos(db, id):
    # Validar que existe
    registro = db.query(Model).filter(Model.id == id).first()
    if not registro:
        raise HTTPException(404, "No encontrado")
    
    # Validar datos relacionados
    if not registro.datos_relacionados:
        raise HTTPException(400, "Faltan datos relacionados")
    
    # Procesar
    return procesar(registro)
```

### 3. Rutas en FastAPI
```python
# ✅ CORRECTO - Sin ambigüedad
@router.get("/resources/{resource_id}")
def get_resource(resource_id: int):
    pass

@router.get("/resources/{resource_id}/details")
def get_resource_details(resource_id: int):
    pass
```

### 4. Constantes en Frontend
```typescript
// ✅ CORRECTO
// src/config/api.ts
export const API_BASE = 'http://localhost:8000';
export const API_ROUTES = {
  PRINTERS: '/printers',
  COUNTERS: {
    LIST: '/api/counters/closes',
    DETAIL: '/api/counters/monthly',
  }
};

// Uso
const url = `${API_BASE}${API_ROUTES.PRINTERS}`;
```

---

## 🚨 SEÑALES DE ALERTA

Si ves alguno de estos patrones, DETENTE y revisa:

### Backend
- ❌ Usar variable sin importar módulo
- ❌ Asumir que existe registro anterior
- ❌ Dos rutas con mismo patrón
- ❌ Procesar sin validar datos
- ❌ No manejar caso "vacío" o "primero"

### Frontend
- ❌ Hardcodear rutas de API
- ❌ No manejar errores de fetch
- ❌ Asumir que datos siempre existen
- ❌ No validar respuestas de API

### General
- ❌ No probar casos extremos
- ❌ No documentar limitaciones
- ❌ No ejecutar linter
- ❌ No leer logs de error

---

## 💡 PRINCIPIOS CLAVE

1. **Validar antes de procesar** - Nunca asumir que los datos existen
2. **Probar casos extremos** - Primer caso, último caso, caso vacío
3. **Ser explícito** - Imports claros, rutas específicas, validaciones obvias
4. **Documentar limitaciones** - Si algo no funciona en ciertos casos, documentarlo
5. **Leer los logs** - Los errores suelen ser muy claros sobre qué falta

---

## 📖 DOCUMENTACIÓN COMPLETA

Para más detalles sobre cada error, consultar:
- `.kiro/lessons-learned/README.md` - Índice completo
- `.kiro/lessons-learned/001-*.md` - Lecciones individuales

---

**Última actualización:** 4 de marzo de 2026  
**Mantenido por:** Sistema Kiro  
**Revisión:** Cada vez que se documenta un nuevo error



---

### 6. Comparación Usando Campo Incorrecto
**Error:** Usar `total_paginas` en lugar de `consumo_total` en comparaciones  
**Ejemplo:** Comparar contadores acumulados en lugar de consumos del período

**Reglas:**
- ✅ SIEMPRE entender qué representa cada campo
- ✅ `total_paginas` = contador acumulado (siempre crece)
- ✅ `consumo_total` = consumo del período (puede variar)
- ✅ Para comparaciones entre cierres, usar `consumo_total`
- ✅ Documentar diferencias entre campos similares

**Diferencia clave:**
```python
# ❌ INCORRECTO - Compara contadores acumulados
consumo1 = u1.total_paginas  # 1,000 (acumulado)
consumo2 = u2.total_paginas  # 1,050 (acumulado)
diferencia = 50  # No refleja el consumo real del período

# ✅ CORRECTO - Compara consumos del período
consumo1 = u1.consumo_total  # 1,000 (consumió ese día)
consumo2 = u2.consumo_total  # 50 (consumió ese día)
diferencia = -950  # Refleja que consumió menos
```

**Cuándo usar cada campo:**
- `consumo_total` → Comparar períodos, ver cambios
- `total_paginas` → Ver contador total, calcular diferencias manualmente

**Referencia:** `.kiro/lessons-learned/006-comparacion-campo-incorrecto.md`

---

## 🚨 SEÑALES DE ALERTA ACTUALIZADAS

### Backend
- ❌ Usar variable sin importar módulo
- ❌ Asumir que existe registro anterior
- ❌ Dos rutas con mismo patrón
- ❌ Procesar sin validar datos
- ❌ No manejar caso "vacío" o "primero"
- ❌ Usar campo incorrecto en comparaciones ⭐ NUEVO
- ❌ No entender diferencia entre campos similares ⭐ NUEVO

---

**Última actualización:** 9 de marzo de 2026
