# 📊 RESUMEN: Snapshot de Usuarios en Cierres Mensuales

## 🔍 INVESTIGACIÓN REALIZADA

### ✅ DATOS ACTUALES EN EL SISTEMA

**Verificación en base de datos**:
- ✅ **11,207 registros** históricos de contadores de usuarios
- ✅ **63 lecturas distintas** registradas
- ✅ Rango de fechas: 2026-03-02 a 2026-03-03 (2 días de datos)
- ✅ Histórico completo por usuario disponible

**Ejemplo real de usuario con actividad**:
```
Usuario: RECEPCION (1805) - Impresora 7
Histórico de 11 lecturas en 2 días:

1. 2026-03-03 14:36 - 68,389 páginas
2. 2026-03-03 14:29 - 68,384 páginas (+5)
3. 2026-03-03 14:00 - 68,344 páginas (+40)
4. 2026-03-02 20:59 - 68,028 páginas (+316)
5. 2026-03-02 19:39 - 67,900 páginas (+128)
...

Consumo total en 2 días: 1,744 páginas
```

## ✅ CONCLUSIÓN PRINCIPAL

**SÍ SE PUEDE CALCULAR EL CONSUMO MENSUAL POR USUARIO** con los datos actuales.

Los datos históricos en la tabla `contadores_usuario` son suficientes para:
- ✅ Calcular consumo mensual por usuario
- ✅ Generar reportes de facturación
- ✅ Auditar consumo individual
- ✅ Identificar usuarios con más actividad

## ⚠️ PERO HAY UN PROBLEMA DE ARQUITECTURA

### Situación Actual

```
┌─────────────────────────────────────────────────────────────┐
│ TABLA: cierres_mensuales                                    │
├─────────────────────────────────────────────────────────────┤
│ id | printer_id | anio | mes | total_paginas | ...          │
│  1 |     4      | 2026 |  3  |   372,600     | ...          │
└─────────────────────────────────────────────────────────────┘
                           ❌ NO HAY VÍNCULO
┌─────────────────────────────────────────────────────────────┐
│ TABLA: contadores_usuario                                   │
├─────────────────────────────────────────────────────────────┤
│ id | printer_id | codigo | nombre | total | created_at      │
│ 1  |     4      | 9967   | SANDRA | 16647 | 2026-03-02...  │
│ 2  |     4      | 9967   | SANDRA | 16650 | 2026-03-03...  │
│ 3  |     4      | 1234   | JUAN   | 5432  | 2026-03-02...  │
└─────────────────────────────────────────────────────────────┘
```

**Problemas**:
1. ⚠️ No hay vínculo directo entre un cierre y sus usuarios
2. ⚠️ Para obtener usuarios de un cierre, hay que hacer query complejo
3. ⚠️ Si se borran datos antiguos de `contadores_usuario`, se pierde capacidad de auditar
4. ⚠️ No hay snapshot inmutable al momento del cierre

### Arquitectura Recomendada

```
┌─────────────────────────────────────────────────────────────┐
│ TABLA: cierres_mensuales                                    │
├─────────────────────────────────────────────────────────────┤
│ id | printer_id | anio | mes | total_paginas | ...          │
│  1 |     4      | 2026 |  3  |   372,600     | ...          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ ✅ VÍNCULO DIRECTO
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ TABLA: cierres_mensuales_usuarios (NUEVA)                   │
├─────────────────────────────────────────────────────────────┤
│ id | cierre_id | codigo | nombre | total | consumo_mes     │
│ 1  |     1     | 9967   | SANDRA | 16650 |    +48          │
│ 2  |     1     | 1234   | JUAN   | 5450  |    +18          │
│ 3  |     1     | 5678   | MARIA  | 8920  |    +125         │
└─────────────────────────────────────────────────────────────┘
        ▲
        │ SNAPSHOT INMUTABLE al momento del cierre
        │ Se crea UNA VEZ cuando se cierra el mes
```

**Ventajas**:
1. ✅ Snapshot inmutable (no cambia después del cierre)
2. ✅ Query simple: `SELECT * FROM cierres_mensuales_usuarios WHERE cierre_id = 1`
3. ✅ Se pueden borrar datos antiguos de `contadores_usuario` sin perder histórico
4. ✅ Vínculo directo con el cierre mensual
5. ✅ Facilita auditorías y reportes
6. ✅ Permite exportar a Excel/PDF fácilmente

## 🎯 RECOMENDACIÓN FINAL

### Opción A: Implementación Rápida (Sin nueva tabla)
**Tiempo**: 10-12 horas
**Pros**:
- ✅ Funcional inmediatamente
- ✅ No requiere migración de base de datos
- ✅ Usa datos existentes

**Contras**:
- ⚠️ Queries más complejos
- ⚠️ No se pueden borrar datos antiguos
- ⚠️ No hay snapshot inmutable
- ⚠️ Más lento para reportes históricos

### Opción B: Implementación Completa (Con nueva tabla) ⭐ RECOMENDADA
**Tiempo**: 17-24 horas
**Pros**:
- ✅ Solución robusta y escalable
- ✅ Queries simples y rápidos
- ✅ Permite limpieza de datos antiguos
- ✅ Auditoría completa
- ✅ Snapshot inmutable
- ✅ Facilita exportación y reportes

**Contras**:
- ⚠️ Requiere migración de base de datos
- ⚠️ Más tiempo de desarrollo inicial

## 📋 IMPLEMENTACIÓN RECOMENDADA

### 1. Crear Migración (30 min)

```sql
-- Migration 007: Add cierres_mensuales_usuarios table
CREATE TABLE cierres_mensuales_usuarios (
    id SERIAL PRIMARY KEY,
    cierre_mensual_id INTEGER NOT NULL REFERENCES cierres_mensuales(id) ON DELETE CASCADE,
    
    -- Usuario
    codigo_usuario VARCHAR(8) NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    
    -- Contadores al cierre
    total_paginas INTEGER NOT NULL,
    total_bn INTEGER NOT NULL,
    total_color INTEGER NOT NULL,
    
    -- Desglose por función
    copiadora_bn INTEGER NOT NULL,
    copiadora_color INTEGER NOT NULL,
    impresora_bn INTEGER NOT NULL,
    impresora_color INTEGER NOT NULL,
    escaner_bn INTEGER NOT NULL,
    escaner_color INTEGER NOT NULL,
    fax_bn INTEGER NOT NULL,
    
    -- Consumo del mes (diferencia con mes anterior)
    consumo_total INTEGER NOT NULL,
    consumo_copiadora INTEGER NOT NULL,
    consumo_impresora INTEGER NOT NULL,
    consumo_escaner INTEGER NOT NULL,
    consumo_fax INTEGER NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    CONSTRAINT idx_cierre_usuario UNIQUE(cierre_mensual_id, codigo_usuario)
);

CREATE INDEX idx_cierres_usuarios_cierre ON cierres_mensuales_usuarios(cierre_mensual_id);
CREATE INDEX idx_cierres_usuarios_codigo ON cierres_mensuales_usuarios(codigo_usuario);
```

### 2. Actualizar Modelo (15 min)

```python
class CierreMensualUsuario(Base):
    __tablename__ = "cierres_mensuales_usuarios"
    
    id = Column(Integer, primary_key=True)
    cierre_mensual_id = Column(Integer, ForeignKey("cierres_mensuales.id"), nullable=False)
    
    codigo_usuario = Column(String(8), nullable=False)
    nombre_usuario = Column(String(100), nullable=False)
    
    # ... campos de contadores ...
    
    # Relationship
    cierre = relationship("CierreMensual", back_populates="usuarios")
```

### 3. Actualizar CounterService.close_month (2-3 horas)

```python
def close_month(db, printer_id, year, month, cerrado_por, notas):
    # ... código existente ...
    
    # NUEVO: Guardar snapshot de usuarios
    usuarios_snapshot = []
    
    # Obtener todos los usuarios activos
    usuarios = db.query(ContadorUsuario.codigo_usuario).filter(
        ContadorUsuario.printer_id == printer_id
    ).distinct().all()
    
    for usuario in usuarios:
        # Calcular consumo mensual
        consumo = calcular_consumo_mensual_usuario(
            db, printer_id, usuario.codigo_usuario, year, month
        )
        
        if consumo:
            usuario_cierre = CierreMensualUsuario(
                cierre_mensual_id=cierre.id,
                codigo_usuario=consumo['codigo_usuario'],
                nombre_usuario=consumo['nombre_usuario'],
                total_paginas=consumo['contador_actual'],
                consumo_total=consumo['consumo_total'],
                # ... más campos ...
            )
            usuarios_snapshot.append(usuario_cierre)
    
    # Guardar todos los usuarios del cierre
    db.bulk_save_objects(usuarios_snapshot)
    db.commit()
    
    return cierre
```

### 4. Crear Endpoint para Usuarios de Cierre (1 hora)

```python
@router.get("/monthly/{printer_id}/{year}/{month}/users")
def get_monthly_close_users(printer_id: int, year: int, month: int):
    """Obtiene los usuarios de un cierre mensual específico"""
    
    cierre = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer_id,
        CierreMensual.anio == year,
        CierreMensual.mes == month
    ).first()
    
    if not cierre:
        raise HTTPException(404, "Cierre no encontrado")
    
    usuarios = db.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.cierre_mensual_id == cierre.id
    ).order_by(CierreMensualUsuario.consumo_total.desc()).all()
    
    return usuarios
```

## 🚀 SIGUIENTE PASO

¿Quieres que implemente la **Opción B (Completa)** con la nueva tabla?

Esto incluiría:
1. ✅ Migración de base de datos
2. ✅ Modelo actualizado
3. ✅ Lógica de snapshot en cierre
4. ✅ Endpoint para obtener usuarios de cierre
5. ✅ Frontend para mostrar usuarios en cierre

Tiempo estimado: 17-24 horas de desarrollo
