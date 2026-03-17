# 008 - Cierre Sin Filtrar Lecturas Por Fecha

**Fecha:** 9 de marzo de 2026  
**Severidad:** Crítica  
**Módulo:** Backend / Servicio de Cierre  
**Tags:** #logica-negocio #cierres #filtrado #fechas #bug-critico

---

## 🐛 Descripción del Error

El servicio de cierre (`close_service.py`) NO estaba filtrando las lecturas de usuarios por fecha al crear los cierres. Esto causaba que todos los cierres usaran el contador más reciente del usuario (sin importar la fecha del cierre), resultando en `consumo_total = 0` para todos los usuarios.

## 🔍 Síntomas

- Cierres creados correctamente pero con `consumo_total = 0` para todos los usuarios
- La suma de consumos de usuarios NO coincide con la diferencia total de la impresora
- Comparación entre cierres muestra 0 usuarios con aumento
- Usuario reporta: "los datos de los cierres debe salir el desglose de las páginas que consumió"

### Ejemplo del Problema
```
Cierre 12 (2 marzo):
  - Usuario LINA: total_paginas = 6, consumo_total = 6
  - Usa contador del 2 de marzo

Cierre 13 (3 marzo):
  - Usuario LINA: total_paginas = 6, consumo_total = 0 ❌
  - Usa el MISMO contador del 3 de marzo (el más reciente)
  - Como ambos cierres usan el mismo contador, diferencia = 0

Resultado:
  - Suma consumo usuarios: 0
  - Diferencia impresora: 517
  - ❌ NO COINCIDE
```

## 🎯 Causa Raíz

En el método `_calcular_consumo_usuario` de `backend/services/close_service.py`, se estaba buscando el contador más reciente del usuario SIN filtrar por fecha:

```python
# CÓDIGO INCORRECTO
contador_actual = db.query(ContadorUsuario).filter(
    ContadorUsuario.printer_id == printer_id,
    ContadorUsuario.codigo_usuario == codigo_usuario
).order_by(ContadorUsuario.fecha_lectura.desc()).first()
```

### Por qué ocurrió
- No se consideró que las lecturas tienen timestamp completo (fecha + hora)
- Se asumió que el contador más reciente era el correcto para cualquier cierre
- No se probó con múltiples cierres de diferentes fechas
- No se validó que la suma de consumos coincidiera con la diferencia total

### Impacto
- **Todos los cierres creados tenían datos incorrectos**
- **La comparación entre cierres no funcionaba**
- **El desglose por usuario era inútil**
- **Los reportes de consumo eran incorrectos**

## ✅ Solución Implementada

Agregar filtro por fecha al buscar el contador del usuario, usando la fecha de fin del período del cierre.

### Código Antes (Incorrecto)
```python
# backend/services/close_service.py - Línea ~361
@staticmethod
def _calcular_consumo_usuario(
    db: Session,
    printer_id: int,
    codigo_usuario: str,
    fecha_inicio: date,
    fecha_fin: date,
    cierre_anterior: Optional[CierreMensual]
) -> Optional[Dict]:
    """
    Calcula el consumo de un usuario en un período
    """
    # ❌ INCORRECTO - No filtra por fecha
    contador_actual = db.query(ContadorUsuario).filter(
        ContadorUsuario.printer_id == printer_id,
        ContadorUsuario.codigo_usuario == codigo_usuario
    ).order_by(ContadorUsuario.fecha_lectura.desc()).first()
    
    if not contador_actual:
        return None
```

### Código Después (Correcto)
```python
# backend/services/close_service.py - Línea ~361
@staticmethod
def _calcular_consumo_usuario(
    db: Session,
    printer_id: int,
    codigo_usuario: str,
    fecha_inicio: date,
    fecha_fin: date,
    cierre_anterior: Optional[CierreMensual]
) -> Optional[Dict]:
    """
    Calcula el consumo de un usuario en un período
    """
    from sqlalchemy import cast, Date
    
    # ✅ CORRECTO - Filtra por fecha de fin del período
    fecha_fin_datetime = datetime.combine(fecha_fin, datetime.max.time())
    
    contador_actual = db.query(ContadorUsuario).filter(
        ContadorUsuario.printer_id == printer_id,
        ContadorUsuario.codigo_usuario == codigo_usuario,
        ContadorUsuario.fecha_lectura <= fecha_fin_datetime  # ⭐ FILTRO POR FECHA
    ).order_by(ContadorUsuario.fecha_lectura.desc()).first()
    
    if not contador_actual:
        return None
```

### Pasos de Corrección
1. Identificar que el contador no se filtraba por fecha
2. Agregar filtro `fecha_lectura <= fecha_fin_datetime`
3. Reiniciar backend: `docker-compose restart backend`
4. Eliminar cierres incorrectos: `python eliminar_cierres.py --force`
5. Recrear cierres con lógica corregida: `python test_sistema_unificado.py`
6. Verificar que suma de consumos coincida con diferencia total

## 🛡️ Prevención Futura

- [x] Agregar filtro por fecha en búsqueda de contadores
- [x] Validar que suma de consumos coincida con diferencia total
- [ ] Agregar test que valide múltiples cierres de diferentes fechas
- [ ] Agregar test que valide consistencia de consumos
- [ ] Documentar en código la importancia del filtro por fecha

### Reglas para Búsqueda de Contadores

#### ✅ SIEMPRE filtrar por fecha cuando:
- Creas un cierre de un período específico
- Buscas el contador de un usuario en una fecha
- Calculas consumo entre dos fechas
- Comparas períodos diferentes

#### ✅ Usar fecha_fin_datetime correctamente:
```python
# Convertir date a datetime con hora máxima
fecha_fin_datetime = datetime.combine(fecha_fin, datetime.max.time())

# Filtrar lecturas hasta el final del día
ContadorUsuario.fecha_lectura <= fecha_fin_datetime
```

### Comentarios Recomendados en Código
```python
# Buscar contador del usuario al final del período
# IMPORTANTE: Filtrar por fecha para obtener el contador correcto
# NO usar el contador más reciente global
fecha_fin_datetime = datetime.combine(fecha_fin, datetime.max.time())
contador_actual = db.query(ContadorUsuario).filter(
    ContadorUsuario.printer_id == printer_id,
    ContadorUsuario.codigo_usuario == codigo_usuario,
    ContadorUsuario.fecha_lectura <= fecha_fin_datetime  # Filtro crítico
).order_by(ContadorUsuario.fecha_lectura.desc()).first()
```

## 📚 Referencias

- [Servicio de cierre](../../backend/services/close_service.py)
- [Modelo de datos](../../backend/db/models.py)
- [Script de prueba](../../backend/test_sistema_unificado.py)

## 💡 Lecciones Clave

1. **SIEMPRE filtrar por fecha** - Cuando trabajas con datos temporales, el filtro por fecha es crítico
2. **Validar consistencia** - La suma de consumos debe coincidir con la diferencia total
3. **Probar con múltiples períodos** - Un solo cierre no revela este bug
4. **Timestamp vs Date** - Entender la diferencia entre fecha (date) y fecha+hora (datetime)
5. **Verificar datos reales** - No asumir que funciona sin verificar los datos guardados

## 🔧 Validación Recomendada

### Test de Consistencia
```python
def test_cierre_consistencia_consumos():
    """Verifica que la suma de consumos coincida con diferencia total"""
    # Crear dos cierres
    cierre1 = crear_cierre(fecha="2026-03-02")
    cierre2 = crear_cierre(fecha="2026-03-03")
    
    # Sumar consumos de usuarios
    suma_consumos = sum(u.consumo_total for u in cierre2.usuarios)
    
    # Verificar que coincida con diferencia total (con margen de error)
    diferencia = abs(suma_consumos - cierre2.diferencia_total)
    assert diferencia < 100, f"Diferencia muy grande: {diferencia}"
```

### Script de Verificación
```python
from db.database import get_db
from db.models import CierreMensual, CierreMensualUsuario

db = next(get_db())

# Verificar todos los cierres
cierres = db.query(CierreMensual).all()

for cierre in cierres:
    usuarios = db.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.cierre_mensual_id == cierre.id
    ).all()
    
    suma_consumos = sum(u.consumo_total for u in usuarios)
    diferencia = abs(suma_consumos - cierre.diferencia_total)
    
    print(f"Cierre {cierre.id} ({cierre.fecha_inicio}):")
    print(f"  Suma consumos: {suma_consumos:,}")
    print(f"  Diferencia total: {cierre.diferencia_total:,}")
    print(f"  Diferencia: {diferencia:,}")
    
    if diferencia > 100:
        print(f"  ⚠️  INCONSISTENCIA DETECTADA")
    else:
        print(f"  ✅ Consistente")
    print()
```

---

## 📊 Impacto

- **Tiempo de detección:** 2 horas
- **Tiempo de corrección:** 30 minutos
- **Cierres afectados:** Todos los cierres creados antes de la corrección
- **Usuarios afectados:** Todos (datos incorrectos)
- **Severidad real:** Crítica (datos completamente incorrectos)

---

## 🔄 Verificación Post-Corrección

### Resultado Antes (Incorrecto)
```
Cierre 13 (3 marzo):
  Total impresora: 373,502
  Diferencia total: 517
  Suma consumo usuarios: 0 ❌
  Diferencia: 517 (100%)
```

### Resultado Después (Correcto)
```
Cierre 13 (3 marzo):
  Total impresora: 373,502
  Diferencia total: 517
  Suma consumo usuarios: 518 ✅
  Diferencia: 1 (0.2%)
```

### Comparación Funcionando
```
Top usuarios con mayor consumo:
  1. ADRIANA MAQUILLO: 70 páginas
  2. Yenny Hernandez: 61 páginas
  3. LEIDY SANCHEZ: 50 páginas
  4. JONATHAN ALFONSO: 42 páginas
  5. JOHANNA YATE: 42 páginas
```

---

**Documentado por:** Sistema Kiro  
**Revisado por:** Equipo de desarrollo  
**Estado:** ✅ Resuelto

**Última actualización:** 9 de marzo de 2026
