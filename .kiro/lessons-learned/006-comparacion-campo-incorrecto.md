# 006 - Comparación Usando Campo Incorrecto

**Fecha:** 9 de marzo de 2026  
**Severidad:** Alta  
**Módulo:** Backend  
**Tags:** #logica-negocio #comparacion #campos #api

---

## 🐛 Descripción del Error

La comparación de cierres estaba usando `total_paginas` (contador acumulado) en lugar de `consumo_total` (consumo del período), lo que generaba resultados incorrectos y confusos.

## 🔍 Síntomas

- Comparación entre cierres muestra números que no tienen sentido
- Las diferencias no coinciden con la realidad
- Usuario reporta: "la comparación no trae el desglose por usuario correctamente"
- Los números de diferencia son muy grandes o negativos inesperadamente

### Ejemplo del Problema
```
Cierre 1 (1 marzo):
  Usuario Juan: total_paginas = 1,000

Cierre 2 (2 marzo):
  Usuario Juan: total_paginas = 1,050

Comparación (INCORRECTA):
  Diferencia: 1,050 - 1,000 = 50 páginas

Pero el consumo real fue:
  Cierre 1: consumo_total = 1,000 (primer día)
  Cierre 2: consumo_total = 50 (segundo día)
  
La comparación debería mostrar: 50 - 1,000 = -950 páginas
(Juan imprimió 950 páginas menos el día 2)
```

## 🎯 Causa Raíz

En el endpoint de comparación (`backend/api/counters.py`), se estaba usando el campo equivocado:

```python
# CÓDIGO INCORRECTO
consumo1 = u1.total_paginas if u1 else 0  # ❌ Contador acumulado
consumo2 = u2.total_paginas if u2 else 0  # ❌ Contador acumulado
diferencia = consumo2 - consumo1
```

### Por qué ocurrió
- No se entendió la diferencia entre `total_paginas` y `consumo_total`
- No se revisó la documentación del modelo de datos
- No se probó la comparación con datos reales
- Se asumió que `total_paginas` era el consumo del período

### Diferencia entre Campos

#### `total_paginas` (Contador Acumulado)
- Contador total desde que se instaló la impresora
- Siempre crece (nunca disminuye)
- Ejemplo: Usuario tiene 10,000 páginas acumuladas

#### `consumo_total` (Consumo del Período) ⭐
- Cuánto imprimió en ESTE período específico
- Se calcula: `total_actual - total_anterior`
- Ejemplo: Usuario imprimió 50 páginas este mes

## ✅ Solución Implementada

Cambiar el código para usar `consumo_total` en lugar de `total_paginas`.

### Código Antes (Incorrecto)
```python
# backend/api/counters.py - Línea ~605
for codigo in codigos_usuarios:
    u1 = usuarios1.get(codigo)
    u2 = usuarios2.get(codigo)
    
    consumo1 = u1.total_paginas if u1 else 0  # ❌ INCORRECTO
    consumo2 = u2.total_paginas if u2 else 0  # ❌ INCORRECTO
    diferencia = consumo2 - consumo1
```

### Código Después (Correcto)
```python
# backend/api/counters.py - Línea ~605
for codigo in codigos_usuarios:
    u1 = usuarios1.get(codigo)
    u2 = usuarios2.get(codigo)
    
    # USAR CONSUMO_TOTAL en lugar de total_paginas
    consumo1 = u1.consumo_total if u1 else 0  # ✅ CORRECTO
    consumo2 = u2.consumo_total if u2 else 0  # ✅ CORRECTO
    diferencia = consumo2 - consumo1
```

### Pasos de Corrección
1. Identificar el campo correcto en el modelo
2. Modificar el código de comparación
3. Reiniciar backend: `docker-compose restart backend`
4. Probar comparación con datos reales
5. Documentar la diferencia entre campos

## 🛡️ Prevención Futura

- [x] Documentar diferencia entre campos en modelo
- [x] Crear documento explicativo del sistema
- [ ] Agregar comentarios en código sobre qué campo usar
- [ ] Agregar test que valide la comparación
- [ ] Documentar en API reference qué campo se usa

### Reglas para Comparaciones

#### ✅ Usar `consumo_total` cuando:
- Comparas períodos diferentes
- Quieres saber cuánto cambió el consumo
- Necesitas diferencias entre cierres

#### ✅ Usar `total_paginas` cuando:
- Necesitas el contador acumulado total
- Quieres saber cuántas páginas lleva en total
- Calculas diferencias manualmente (total2 - total1)

### Comentarios Recomendados en Código
```python
# Comparación de cierres
# IMPORTANTE: Usar consumo_total (consumo del período)
# NO usar total_paginas (contador acumulado)
consumo1 = u1.consumo_total if u1 else 0
consumo2 = u2.consumo_total if u2 else 0
```

## 📚 Referencias

- [Modelo de datos](../../backend/db/models.py)
- [Endpoint corregido](../../backend/api/counters.py)
- [Explicación del sistema](../../COMO_FUNCIONA_SISTEMA_CIERRES.md)

## 💡 Lecciones Clave

1. **Entender el modelo de datos**: Saber qué representa cada campo
2. **Leer la documentación**: Revisar docs antes de implementar
3. **Probar con datos reales**: No asumir que funciona sin probar
4. **Documentar diferencias**: Explicar campos similares pero diferentes
5. **Comentar código crítico**: Indicar qué campo usar y por qué

## 🔧 Validación Recomendada

### Test de Comparación
```python
def test_comparacion_usa_consumo_correcto():
    """Verifica que la comparación use consumo_total"""
    # Crear dos cierres
    cierre1 = crear_cierre(fecha="2026-03-01")
    cierre2 = crear_cierre(fecha="2026-03-02")
    
    # Comparar
    comparacion = compare_closes(cierre1.id, cierre2.id)
    
    # Verificar que use consumo_total
    usuario = comparacion.top_usuarios_aumento[0]
    
    # El consumo debe ser del período, no acumulado
    assert usuario.consumo_cierre1 == cierre1.usuarios[0].consumo_total
    assert usuario.consumo_cierre2 == cierre2.usuarios[0].consumo_total
```

### Documentación en Modelo
```python
class CierreMensualUsuario(Base):
    """
    Snapshot de un usuario en un cierre
    """
    # Contador acumulado (total desde instalación)
    total_paginas = Column(Integer, nullable=False)
    
    # Consumo del período (cuánto imprimió en este cierre)
    # USAR ESTE CAMPO para comparaciones entre cierres
    consumo_total = Column(Integer, nullable=False)
```

---

## 📊 Impacto

- **Tiempo de detección:** 1 hora
- **Tiempo de corrección:** 15 minutos
- **Endpoints afectados:** 1 (comparación)
- **Usuarios afectados:** 0 (detectado en desarrollo)
- **Severidad real:** Alta (datos incorrectos en comparación)

---

## 🔄 Verificación Post-Corrección

### Script de Verificación
```python
from db.database import get_db
from db.models import CierreMensual, CierreMensualUsuario

db = next(get_db())

# Obtener dos cierres
cierre1 = db.query(CierreMensual).filter(CierreMensual.id == 7).first()
cierre2 = db.query(CierreMensual).filter(CierreMensual.id == 8).first()

# Obtener usuarios
usuarios1 = {u.codigo_usuario: u for u in db.query(CierreMensualUsuario).filter(
    CierreMensualUsuario.cierre_mensual_id == 7
).all()}

usuarios2 = {u.codigo_usuario: u for u in db.query(CierreMensualUsuario).filter(
    CierreMensualUsuario.cierre_mensual_id == 8
).all()}

# Verificar un usuario
codigo = list(usuarios1.keys())[0]
u1 = usuarios1[codigo]
u2 = usuarios2.get(codigo)

print(f"Usuario: {u1.nombre_usuario}")
print(f"Cierre 1 - total_paginas: {u1.total_paginas:,}")
print(f"Cierre 1 - consumo_total: {u1.consumo_total:,}")
if u2:
    print(f"Cierre 2 - total_paginas: {u2.total_paginas:,}")
    print(f"Cierre 2 - consumo_total: {u2.consumo_total:,}")
    print()
    print(f"Diferencia usando total_paginas: {u2.total_paginas - u1.total_paginas:,}")
    print(f"Diferencia usando consumo_total: {u2.consumo_total - u1.consumo_total:,}")
```

---

**Documentado por:** Sistema Kiro  
**Revisado por:** Equipo de desarrollo  
**Estado:** ✅ Resuelto

**Última actualización:** 9 de marzo de 2026
