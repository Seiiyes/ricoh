# 004 - Ruta Incorrecta de API en Frontend

**Fecha:** 4 de marzo de 2026  
**Severidad:** Media  
**Módulo:** Frontend  
**Tags:** #frontend #api #routing #integracion

---

## 🐛 Descripción del Error

El frontend no cargaba la lista de impresoras. El dropdown de impresoras aparecía vacío con el mensaje "Selecciona una impresora". La consola del navegador mostraba error 404 al intentar cargar las impresoras.

## 🔍 Síntomas

- Dropdown de impresoras vacío
- Error 404 en consola del navegador
- Request a `/api/printers` falla
- Frontend no puede cargar datos
- Mensaje "Selecciona una impresora" permanente

### Error en Consola
```
GET http://localhost:8000/api/printers 404 (Not Found)
```

## 🎯 Causa Raíz

El frontend estaba usando la ruta `/api/printers` pero el backend tiene el endpoint en `/printers` (sin el prefijo `/api`).

### Rutas del Backend
```python
# backend/main.py
app.include_router(printers.router, prefix="", tags=["printers"])
# Endpoint: /printers

app.include_router(counters.router, prefix="/api/counters", tags=["counters"])
# Endpoints: /api/counters/*
```

El endpoint de impresoras NO tiene el prefijo `/api`, pero el de contadores SÍ.

### Por qué ocurrió
- Se asumió que todos los endpoints tenían el prefijo `/api`
- No se verificó la configuración real del backend
- No se consultó la documentación de la API
- Se copió código de otro endpoint que sí usa `/api`

## ✅ Solución Implementada

Corregir la ruta en el frontend para usar `/printers` en lugar de `/api/printers`.

### Código Antes
```typescript
// src/components/contadores/cierres/CierresView.tsx
const loadPrinters = async () => {
  try {
    const response = await fetch(`${API_BASE}/api/printers`);  // ❌ Ruta incorrecta
    // ...
  }
}
```

### Código Después
```typescript
// src/components/contadores/cierres/CierresView.tsx
const loadPrinters = async () => {
  try {
    const response = await fetch(`${API_BASE}/printers`);  // ✅ Ruta correcta
    // ...
  }
}
```

## 🛡️ Prevención Futura

- [x] Documentar todas las rutas de la API
- [x] Crear constantes para rutas en el frontend
- [ ] Agregar test de integración frontend-backend
- [ ] Validar rutas antes de usar
- [ ] Usar OpenAPI/Swagger para documentación

### Mejores Prácticas

#### ✅ Usar Constantes para Rutas
```typescript
// src/config/api.ts
export const API_ROUTES = {
  PRINTERS: '/printers',
  COUNTERS: {
    CLOSES: '/api/counters/closes',
    CLOSE_DETAIL: '/api/counters/monthly',
  }
};

// Uso
fetch(`${API_BASE}${API_ROUTES.PRINTERS}`)
```

#### ✅ Validar Rutas en Desarrollo
```typescript
// src/utils/api.ts
const validateRoute = (route: string) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(`API Request: ${API_BASE}${route}`);
  }
};
```

## 📚 Referencias

- [API Reference](../../docs/API_REFERENCE_CIERRES.md)
- [Archivo corregido](../../src/components/contadores/cierres/CierresView.tsx)
- [Backend routes](../../backend/main.py)

## 💡 Lecciones Clave

1. **Verificar rutas reales**: No asumir prefijos en las rutas
2. **Consultar documentación**: Revisar la API reference antes de implementar
3. **Usar constantes**: Centralizar rutas en un archivo de configuración
4. **Probar en navegador**: Verificar que las rutas funcionen antes de integrar
5. **Consistencia**: Mantener consistencia en prefijos de rutas

---

**Documentado por:** Sistema Kiro  
**Estado:** ✅ Resuelto
