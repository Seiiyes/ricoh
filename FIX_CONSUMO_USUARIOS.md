# 🔧 Corrección: Consumo de Usuarios en Cierres

**Fecha:** 4 de marzo de 2026  
**Problema:** Los cierres guardaban usuarios pero todos con `consumo_total = 0`

---

## 🐛 Problema Identificado

### Síntomas
- Los cierres se creaban correctamente
- Los usuarios se guardaban en el snapshot (266 usuarios)
- PERO todos los usuarios tenían `consumo_total = 0`
- El frontend no mostraba información útil

### Causa Raíz
En `backend/services/close_service.py`, método `_calcular_consumo_usuario`:

```python
# CÓDIGO INCORRECTO (líneas 405-410)
else:
    # Primer cierre, el consumo es el total actual
    consumo_total = 0  # ❌ INCORRECTO
    consumo_copiadora = 0
    consumo_impresora = 0
    consumo_escaner = 0
    consumo_fax = 0
```

Cuando no había cierre anterior, el código ponía consumo = 0 en lugar de calcular el consumo real del período.

---

## ✅ Solución Implementada

### 1. Corrección del Método `_calcular_consumo_usuario`

**Archivo:** `backend/services/close_service.py`

**Lógica corregida:**
```python
else:
    # Primer cierre: buscar contador al inicio del período
    contador_inicio = db.query(ContadorUsuario).filter(
        ContadorUsuario.printer_id == printer_id,
        ContadorUsuario.codigo_usuario == codigo_usuario,
        ContadorUsuario.fecha_lectura >= fecha_inicio,
        ContadorUsuario.fecha_lectura <= fecha_fin
    ).order_by(ContadorUsuario.fecha_lectura.asc()).first()
    
    if contador_inicio and contador_inicio.id != contador_actual.id:
        # Hay contador al inicio del período, calcular diferencia
        consumo_total = contador_actual.total_paginas - contador_inicio.total_paginas
        # ... (calcular otros consumos)
    else:
        # Solo hay una lectura en el período, usar el total actual como consumo
        consumo_total = contador_actual.total_paginas
        # ... (usar totales actuales)
```

**Casos manejados:**
1. **Hay cierre anterior:** Calcular diferencia entre cierre actual y anterior
2. **Primer cierre con múltiples lecturas:** Calcular diferencia entre primera y última lectura del período
3. **Primer cierre con una sola lectura:** Usar el total acumulado como consumo

### 2. Scripts Creados

#### `backend/eliminar_cierres.py`
- Elimina todos los cierres existentes (con datos incorrectos)
- Acepta flag `--force` para no pedir confirmación
- Uso: `docker exec ricoh-backend python eliminar_cierres.py --force`

#### `backend/recrear_cierres.py`
- Recrea los cierres con la lógica corregida
- Crea cierres del 2 y 3 de marzo para impresora 4
- Muestra estadísticas de usuarios con consumo > 0
- Uso: `docker exec ricoh-backend python recrear_cierres.py`

### 3. Mejoras en el Frontend

#### Componente `ComparacionModal.tsx`
Agregado:
- Sección "Todos los Usuarios" con lista completa
- Campo de búsqueda para filtrar usuarios
- Botón "Mostrar todos" para expandir/colapsar
- Tabla con scroll para manejar muchos usuarios
- Muestra: Usuario, Código, Período 1, Período 2, Diferencia, % Cambio

---

## 📊 Resultados

### Antes de la Corrección
```
Cierre ID 5 (ejemplo):
  Total usuarios: 266
  Usuarios con consumo > 0: 0  ❌
  Suma de consumos: 0 páginas  ❌
```

### Después de la Corrección
```
Cierre ID 7 (2 de marzo):
  Total usuarios: 266
  Usuarios con consumo > 0: 127  ✅
  Suma de consumos: 166,773 páginas  ✅
  
  Top 5 usuarios:
    - SANDRA GARCIA: 16,647 páginas
    - DORA CASTILLO: 9,597 páginas
    - Yenny Hernandez: 9,157 páginas
    - ANDRES SANCHEZ: 7,702 páginas
    - SAMANTA CARDENAS: 7,592 páginas
```

---

## 🔍 Verificación

### 1. Backend
```bash
# Ver usuarios de un cierre
docker exec ricoh-backend python ver_usuarios_cierre.py 7

# Probar endpoint de detalle
curl http://localhost:8000/api/counters/monthly/7/detail
```

### 2. Frontend
1. Abrir `http://localhost:5173`
2. Seleccionar impresora 4
3. Seleccionar año 2026
4. Seleccionar tipo "Diario"
5. Click en "Ver Detalle" de un cierre
6. Verificar que se muestren usuarios con consumo > 0

### 3. Comparación
1. Click en botón "Comparar"
2. Seleccionar dos cierres
3. Ver diferencias por usuario
4. Click en "Mostrar todos" para ver lista completa
5. Usar búsqueda para filtrar usuarios

---

## 📝 Archivos Modificados

### Backend
- `backend/services/close_service.py` - Corregido método `_calcular_consumo_usuario`
- `backend/eliminar_cierres.py` - Nuevo script
- `backend/recrear_cierres.py` - Nuevo script
- `backend/eliminar-cierres.bat` - Nuevo script
- `backend/recrear-cierres.bat` - Nuevo script

### Frontend
- `src/components/contadores/cierres/ComparacionModal.tsx` - Agregada sección "Todos los Usuarios"

---

## ✅ Estado Final

- ✅ Backend calcula consumos correctamente
- ✅ Primer cierre muestra consumos acumulados
- ✅ Cierres subsecuentes muestran diferencias
- ✅ Frontend muestra datos correctamente en detalle
- ✅ Frontend muestra comparación completa por usuario
- ✅ Sistema listo para producción

---

## 🎯 Próximos Pasos (Opcionales)

1. Exportar a Excel con desglose por usuario
2. Exportar a PDF con gráficos
3. Dashboard con estadísticas visuales
4. Alertas de consumo anormal por usuario

