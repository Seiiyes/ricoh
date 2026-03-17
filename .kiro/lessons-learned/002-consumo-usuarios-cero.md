# 002 - Consumo de Usuarios en Cero en Primer Cierre

**Fecha:** 4 de marzo de 2026  
**Severidad:** Alta  
**Módulo:** Backend  
**Tags:** #logica-negocio #cierres #calculo #usuarios

---

## 🐛 Descripción del Error

Los cierres se creaban correctamente y guardaban el snapshot de usuarios (266 usuarios), pero TODOS los usuarios tenían `consumo_total = 0`. Esto hacía que el frontend no mostrara información útil sobre cuánto imprimió cada usuario.

## 🔍 Síntomas

- Cierres se crean sin errores
- Snapshot de usuarios se guarda (266 registros)
- TODOS los usuarios tienen `consumo_total = 0`
- Frontend muestra "0 usuarios con consumo > 0"
- Suma de consumos de usuarios = 0
- Diferencia total de impresora > 0 (no coincide)

### Ejemplo Real
```
Cierre ID 5:
  Total usuarios: 266
  Usuarios con consumo > 0: 0  ❌
  Suma de consumos: 0 páginas  ❌
  Diferencia impresora: 4,800 páginas  ✅
```

## 🎯 Causa Raíz

En el método `_calcular_consumo_usuario` del archivo `backend/services/close_service.py`, cuando NO había cierre anterior (primer cierre), el código ponía todos los consumos en 0:

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

### Por qué ocurrió
- Se asumió incorrectamente que el primer cierre no debería tener consumo
- No se consideró que el primer cierre debe mostrar el consumo acumulado hasta ese momento
- La lógica solo funcionaba cuando había un cierre anterior para comparar
- No se probó el caso de "primer cierre" adecuadamente

## ✅ Solución Implementada

Modificar la lógica para que cuando no hay cierre anterior, busque el contador al inicio del período y calcule la diferencia. Si solo hay una lectura, usar el total acumulado como consumo.

### Código Antes
```python
# backend/services/close_service.py
else:
    # Primer cierre, el consumo es el total actual
    consumo_total = 0  # ❌ INCORRECTO
    consumo_copiadora = 0
    consumo_impresora = 0
    consumo_escaner = 0
    consumo_fax = 0
```

### Código Después
```python
# backend/services/close_service.py
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
        consumo_copiadora = (contador_actual.copiadora_bn + contador_actual.copiadora_todo_color) - \
                           (contador_inicio.copiadora_bn + contador_inicio.copiadora_todo_color)
        consumo_impresora = (contador_actual.impresora_bn + contador_actual.impresora_color) - \
                           (contador_inicio.impresora_bn + contador_inicio.impresora_color)
        consumo_escaner = (contador_actual.escaner_bn + contador_actual.escaner_todo_color) - \
                         (contador_inicio.escaner_bn + contador_inicio.escaner_todo_color)
        consumo_fax = contador_actual.fax_bn - contador_inicio.fax_bn
    else:
        # Solo hay una lectura en el período, usar el total actual como consumo
        consumo_total = contador_actual.total_paginas
        consumo_copiadora = contador_actual.copiadora_bn + contador_actual.copiadora_todo_color
        consumo_impresora = contador_actual.impresora_bn + contador_actual.impresora_color
        consumo_escaner = contador_actual.escaner_bn + contador_actual.escaner_todo_color
        consumo_fax = contador_actual.fax_bn
```

### Pasos de Corrección
1. Identificar el problema en el código
2. Modificar el método `_calcular_consumo_usuario`
3. Reiniciar backend: `docker-compose restart backend`
4. Eliminar cierres con datos incorrectos: `python eliminar_cierres.py --force`
5. Recrear cierres: `python recrear_cierres.py`
6. Verificar resultados: `python ver_usuarios_cierre.py 7`

### Resultados Después de la Corrección
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

## 🛡️ Prevención Futura

- [x] Agregar test específico para "primer cierre"
- [x] Documentar casos de uso en código
- [ ] Agregar validación de suma de usuarios vs total impresora
- [ ] Crear test de regresión para este caso
- [ ] Documentar lógica de cálculo de consumo

### Casos de Prueba Requeridos
```python
def test_primer_cierre_con_consumo():
    """Verifica que el primer cierre calcule consumo correctamente"""
    # Crear cierre sin cierres anteriores
    cierre = CloseService.create_close(...)
    
    # Verificar que hay usuarios con consumo > 0
    usuarios_activos = [u for u in cierre.usuarios if u.consumo_total > 0]
    assert len(usuarios_activos) > 0
    
    # Verificar que la suma de usuarios es razonable
    suma_usuarios = sum(u.consumo_total for u in cierre.usuarios)
    assert suma_usuarios > 0

def test_cierre_con_anterior():
    """Verifica que cierres subsecuentes calculen diferencia"""
    # Crear primer cierre
    cierre1 = CloseService.create_close(...)
    
    # Crear segundo cierre
    cierre2 = CloseService.create_close(...)
    
    # Verificar que el segundo cierre tiene diferencias
    assert cierre2.diferencia_total > 0
```

## 📚 Referencias

- [Archivo corregido](../../backend/services/close_service.py)
- [Script de verificación](../../backend/ver_usuarios_cierre.py)
- [Documentación del fix](../../FIX_CONSUMO_USUARIOS.md)

## 💡 Lecciones Clave

1. **Probar casos extremos**: Siempre probar el "primer caso" (sin datos anteriores)
2. **Validar lógica de negocio**: El consumo debe ser > 0 si hay actividad
3. **Comparar totales**: Suma de usuarios debe aproximarse al total de impresora
4. **No asumir datos previos**: El código debe funcionar sin datos históricos
5. **Documentar casos especiales**: Primer cierre es un caso especial que debe documentarse

## 🔧 Validaciones Recomendadas

### En el Código
```python
# Validar que el consumo tiene sentido
if consumo_total == 0 and not cierre_anterior:
    # Advertencia: primer cierre con consumo 0 es sospechoso
    logger.warning(f"Usuario {codigo_usuario} tiene consumo 0 en primer cierre")

# Validar suma de usuarios vs total
suma_usuarios = sum(u.consumo_total for u in usuarios)
if abs(suma_usuarios - diferencia_total) > diferencia_total * 0.1:
    # Advertencia: diferencia > 10%
    logger.warning(f"Diferencia entre suma usuarios ({suma_usuarios}) y total ({diferencia_total})")
```

### En los Tests
```python
def test_consumo_razonable():
    """Verifica que los consumos sean razonables"""
    cierre = crear_cierre_prueba()
    
    # Al menos 10% de usuarios deben tener consumo > 0
    usuarios_activos = [u for u in cierre.usuarios if u.consumo_total > 0]
    assert len(usuarios_activos) >= len(cierre.usuarios) * 0.1
    
    # Suma de usuarios debe estar cerca del total
    suma = sum(u.consumo_total for u in cierre.usuarios)
    assert abs(suma - cierre.diferencia_total) < cierre.diferencia_total * 0.2
```

---

## 📊 Impacto

- **Tiempo de detección:** 2 horas
- **Tiempo de corrección:** 1 hora
- **Cierres afectados:** 3 (eliminados y recreados)
- **Usuarios afectados:** 0 (detectado en desarrollo)
- **Severidad real:** Alta (datos incorrectos en cierres)

---

**Documentado por:** Sistema Kiro  
**Revisado por:** Equipo de desarrollo  
**Estado:** ✅ Resuelto

**Última actualización:** 4 de marzo de 2026
