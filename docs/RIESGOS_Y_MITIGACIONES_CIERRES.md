# ⚠️ RIESGOS Y MITIGACIONES: Sistema de Cierres Mensuales

## 🎯 OBJETIVO

Identificar TODOS los riesgos potenciales al implementar el sistema de cierres mensuales y definir estrategias de mitigación.

---

## 🚨 RIESGOS CRÍTICOS

### RIESGO 1: Pérdida de Datos Durante Limpieza

**Descripción**: Al borrar datos antiguos de `contadores_usuario`, se podría perder información si el cierre no se guardó correctamente.

**Probabilidad**: MEDIA
**Impacto**: CRÍTICO (pérdida de datos de facturación)

**Escenario de fallo**:
```
1. Se ejecuta cierre mensual de marzo
2. Falla al guardar snapshot de usuarios (error de BD)
3. El cierre se marca como "completado" (inconsistencia)
4. Se ejecuta limpieza automática
5. Se borran datos de marzo
6. ❌ PÉRDIDA TOTAL de datos de usuarios de marzo
```

**Mitigación**:

```python
def close_month_safe(db, printer_id, year, month, cerrado_por, notas):
    """
    Cierre mensual con transacción atómica y validación
    """
    try:
        # Iniciar transacción
        db.begin_nested()
        
        # 1. Crear cierre mensual
        cierre = CierreMensual(...)
        db.add(cierre)
        db.flush()  # Obtener ID sin commit
        
        # 2. Guardar snapshot de usuarios
        usuarios_snapshot = []
        for usuario in obtener_usuarios(db, printer_id, year, month):
            usuario_cierre = CierreMensualUsuario(
                cierre_mensual_id=cierre.id,
                ...
            )
            usuarios_snapshot.append(usuario_cierre)
        
        if not usuarios_snapshot:
            raise ValueError("No hay usuarios para guardar en snapshot")
        
        db.bulk_save_objects(usuarios_snapshot)
        db.flush()
        
        # 3. Validar que se guardaron correctamente
        count = db.query(CierreMensualUsuario).filter(
            CierreMensualUsuario.cierre_mensual_id == cierre.id
        ).count()
        
        if count != len(usuarios_snapshot):
            raise ValueError(
                f"Error de integridad: se esperaban {len(usuarios_snapshot)} usuarios, "
                f"se guardaron {count}"
            )
        
        # 4. Validar suma de consumos vs total del cierre
        suma_consumos = db.query(
            func.sum(CierreMensualUsuario.consumo_total)
        ).filter(
            CierreMensualUsuario.cierre_mensual_id == cierre.id
        ).scalar() or 0
        
        # Permitir diferencia de hasta 5% (por redondeos)
        diferencia_porcentual = abs(suma_consumos - cierre.diferencia_total) / cierre.diferencia_total
        if diferencia_porcentual > 0.05:
            raise ValueError(
                f"Inconsistencia: suma de consumos ({suma_consumos}) "
                f"no coincide con total del cierre ({cierre.diferencia_total})"
            )
        
        # 5. TODO OK - Commit
        db.commit()
        
        return cierre
        
    except Exception as e:
        # Rollback completo
        db.rollback()
        raise Exception(f"Error al cerrar mes: {e}")


def limpiar_datos_seguros(db, meses_retencion=3):
    """
    Limpieza con validación de cierres
    """
    fecha_limite = datetime.now() - timedelta(days=meses_retencion * 30)
    
    # Solo borrar períodos con cierre VALIDADO
    cierres = db.query(CierreMensual).filter(
        CierreMensual.fecha_cierre < fecha_limite
    ).all()
    
    for cierre in cierres:
        # VALIDAR que el cierre tiene usuarios
        usuarios_count = db.query(CierreMensualUsuario).filter(
            CierreMensualUsuario.cierre_mensual_id == cierre.id
        ).count()
        
        if usuarios_count == 0:
            print(f"⚠️  ADVERTENCIA: Cierre {cierre.id} no tiene usuarios, NO se borrará")
            continue
        
        # Calcular fecha límite para este cierre
        fecha_fin_mes = datetime(
            cierre.anio, 
            cierre.mes,
            calendar.monthrange(cierre.anio, cierre.mes)[1],
            23, 59, 59
        )
        
        # Borrar contadores
        deleted = db.query(ContadorUsuario).filter(
            ContadorUsuario.printer_id == cierre.printer_id,
            ContadorUsuario.created_at <= fecha_fin_mes
        ).delete()
        
        print(f'✅ Borrados {deleted} registros de {cierre.anio}-{cierre.mes:02d}')
    
    db.commit()
```

**Checklist de validación**:
- [ ] Transacción atómica (todo o nada)
- [ ] Validar count de usuarios guardados
- [ ] Validar suma de consumos
- [ ] No borrar si cierre no tiene usuarios
- [ ] Backup antes de limpieza
- [ ] Log de auditoría

---

### RIESGO 2: Contador Reseteado en Hardware

**Descripción**: Si el contador de la impresora se resetea (mantenimiento, cambio de placa), los cálculos de consumo serán negativos.

**Probabilidad**: BAJA
**Impacto**: ALTO (facturación incorrecta)

**Escenario de fallo**:
```
Febrero: Contador = 100,000 páginas
Marzo (después de reset): Contador = 5,000 páginas
Consumo calculado: 5,000 - 100,000 = -95,000 ❌
```

**Mitigación**:

```python
def detectar_reset_contador(db, printer_id, contador_actual):
    """
    Detecta si el contador fue reseteado
    """
    ultimo_contador = db.query(ContadorImpresora).filter(
        ContadorImpresora.printer_id == printer_id
    ).order_by(ContadorImpresora.fecha_lectura.desc()).first()
    
    if ultimo_contador:
        # Si el contador actual es menor que el anterior, hubo reset
        if contador_actual.total < ultimo_contador.total:
            return {
                'reset_detectado': True,
                'contador_anterior': ultimo_contador.total,
                'contador_actual': contador_actual.total,
                'diferencia': contador_actual.total - ultimo_contador.total
            }
    
    return {'reset_detectado': False}


def close_month_con_validacion_reset(db, printer_id, year, month, cerrado_por, notas):
    """
    Cierre mensual con detección de reset
    """
    # Obtener último contador
    ultimo_contador = db.query(ContadorImpresora).filter(
        ContadorImpresora.printer_id == printer_id
    ).order_by(ContadorImpresora.fecha_lectura.desc()).first()
    
    # Obtener cierre anterior
    if month > 1:
        mes_anterior = month - 1
        anio_anterior = year
    else:
        mes_anterior = 12
        anio_anterior = year - 1
    
    cierre_anterior = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer_id,
        CierreMensual.anio == anio_anterior,
        CierreMensual.mes == mes_anterior
    ).first()
    
    # Validar reset
    if cierre_anterior and ultimo_contador.total < cierre_anterior.total_paginas:
        raise ValueError(
            f"⚠️  RESET DE CONTADOR DETECTADO\n"
            f"Contador anterior: {cierre_anterior.total_paginas:,}\n"
            f"Contador actual: {ultimo_contador.total:,}\n"
            f"Diferencia: {ultimo_contador.total - cierre_anterior.total_paginas:,}\n\n"
            f"ACCIÓN REQUERIDA:\n"
            f"1. Verificar si hubo mantenimiento en la impresora\n"
            f"2. Contactar al técnico para confirmar reset\n"
            f"3. Ajustar manualmente el cierre con el consumo real\n"
            f"4. Documentar el incidente en 'notas'"
        )
    
    # Continuar con cierre normal
    return close_month_safe(db, printer_id, year, month, cerrado_por, notas)
```

**Estrategia de recuperación**:
1. Detectar reset automáticamente
2. Bloquear cierre automático
3. Notificar al administrador
4. Permitir cierre manual con ajuste
5. Documentar en notas del cierre

**Checklist de validación**:
- [ ] Detectar contador menor que anterior
- [ ] Bloquear cierre automático
- [ ] Notificar administrador
- [ ] Permitir ajuste manual
- [ ] Documentar en notas

---

### RIESGO 3: Cierre Duplicado por Concurrencia

**Descripción**: Dos usuarios intentan cerrar el mismo mes simultáneamente.

**Probabilidad**: BAJA
**Impacto**: MEDIO (datos duplicados, confusión)

**Escenario de fallo**:
```
Usuario A: Inicia cierre de marzo (10:00:00)
Usuario B: Inicia cierre de marzo (10:00:01)
Usuario A: Guarda cierre (10:00:05)
Usuario B: Guarda cierre (10:00:06)
Resultado: 2 cierres para marzo ❌
```

**Mitigación**:

```sql
-- Ya existe en migración 005
CONSTRAINT uk_printer_periodo UNIQUE(printer_id, anio, mes)
```

```python
def close_month_con_lock(db, printer_id, year, month, cerrado_por, notas):
    """
    Cierre mensual con lock de base de datos
    """
    try:
        # 1. Intentar adquirir lock exclusivo
        # pg_advisory_lock usa un número único por (printer_id, year, month)
        lock_id = printer_id * 1000000 + year * 100 + month
        
        db.execute(text(f"SELECT pg_advisory_lock({lock_id})"))
        
        # 2. Verificar que no existe cierre (doble check)
        existing = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id,
            CierreMensual.anio == year,
            CierreMensual.mes == month
        ).first()
        
        if existing:
            raise ValueError(
                f"Ya existe un cierre para {year}-{month:02d}. "
                f"Cerrado por: {existing.cerrado_por} "
                f"Fecha: {existing.fecha_cierre}"
            )
        
        # 3. Crear cierre
        cierre = close_month_safe(db, printer_id, year, month, cerrado_por, notas)
        
        # 4. Liberar lock
        db.execute(text(f"SELECT pg_advisory_unlock({lock_id})"))
        
        return cierre
        
    except Exception as e:
        # Liberar lock en caso de error
        db.execute(text(f"SELECT pg_advisory_unlock({lock_id})"))
        raise e
```

**Checklist de validación**:
- [ ] Constraint UNIQUE en base de datos
- [ ] Lock de base de datos (pg_advisory_lock)
- [ ] Doble verificación antes de crear
- [ ] Mensaje claro si ya existe
- [ ] Liberar lock en caso de error

---

### RIESGO 4: Inconsistencia entre Total y Suma de Usuarios

**Descripción**: La suma de contadores de usuarios no coincide con el contador total de la impresora.

**Probabilidad**: MEDIA
**Impacto**: MEDIO (confusión, auditoría fallida)

**Escenario de fallo**:
```
Contador total impresora: 100,000 páginas
Suma de usuarios: 95,000 páginas
Diferencia: 5,000 páginas sin asignar ❌

Causas posibles:
- Impresiones sin autenticación
- Usuarios borrados del sistema
- Errores de lectura
```

**Mitigación**:

```python
def validar_consistencia_cierre(db, cierre_id):
    """
    Valida que la suma de usuarios coincida con el total
    """
    cierre = db.query(CierreMensual).filter(
        CierreMensual.id == cierre_id
    ).first()
    
    # Suma de consumos de usuarios
    suma_usuarios = db.query(
        func.sum(CierreMensualUsuario.consumo_total)
    ).filter(
        CierreMensualUsuario.cierre_mensual_id == cierre_id
    ).scalar() or 0
    
    # Diferencia
    diferencia = cierre.diferencia_total - suma_usuarios
    porcentaje_diferencia = (diferencia / cierre.diferencia_total * 100) if cierre.diferencia_total > 0 else 0
    
    return {
        'total_impresora': cierre.diferencia_total,
        'suma_usuarios': suma_usuarios,
        'diferencia': diferencia,
        'porcentaje': porcentaje_diferencia,
        'consistente': abs(porcentaje_diferencia) < 10  # Permitir 10% de diferencia
    }


def close_month_con_reporte_diferencias(db, printer_id, year, month, cerrado_por, notas):
    """
    Cierre mensual con reporte de diferencias
    """
    # Crear cierre
    cierre = close_month_safe(db, printer_id, year, month, cerrado_por, notas)
    
    # Validar consistencia
    validacion = validar_consistencia_cierre(db, cierre.id)
    
    if not validacion['consistente']:
        # Agregar nota automática
        nota_diferencia = (
            f"\n\n⚠️  ADVERTENCIA DE CONSISTENCIA:\n"
            f"Total impresora: {validacion['total_impresora']:,} páginas\n"
            f"Suma usuarios: {validacion['suma_usuarios']:,} páginas\n"
            f"Diferencia: {validacion['diferencia']:,} páginas ({validacion['porcentaje']:.1f}%)\n"
            f"Posibles causas: impresiones sin autenticación, usuarios borrados"
        )
        
        cierre.notas = (cierre.notas or "") + nota_diferencia
        db.commit()
    
    return cierre, validacion
```

**Estrategia**:
1. Calcular diferencia automáticamente
2. Permitir hasta 10% de diferencia (normal)
3. Si > 10%, agregar nota de advertencia
4. Mostrar en reporte de cierre
5. Investigar causas si es recurrente

**Checklist de validación**:
- [ ] Calcular suma de usuarios
- [ ] Comparar con total de impresora
- [ ] Permitir margen de error (10%)
- [ ] Documentar diferencias
- [ ] Alertar si > 10%

---

## ⚠️ RIESGOS MEDIOS

### RIESGO 5: Cierre sin Lectura Reciente

**Descripción**: Se intenta cerrar el mes con contadores de hace semanas.

**Mitigación**: Ya implementada en validaciones (ver ANALISIS_CIERRE_MENSUAL.md)

### RIESGO 6: Cierre Fuera de Secuencia

**Descripción**: Se intenta cerrar marzo sin haber cerrado febrero.

**Mitigación**: Ya implementada en validaciones (ver ANALISIS_CIERRE_MENSUAL.md)

### RIESGO 7: Borrado Accidental de Cierres

**Descripción**: Usuario borra un cierre mensual por error.

**Mitigación**:
```python
# Agregar soft delete
class CierreMensual(Base):
    # ... campos existentes ...
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String(100), nullable=True)

def delete_cierre_soft(db, cierre_id, deleted_by):
    """Soft delete de cierre"""
    cierre = db.query(CierreMensual).filter(
        CierreMensual.id == cierre_id
    ).first()
    
    cierre.deleted_at = datetime.now()
    cierre.deleted_by = deleted_by
    db.commit()

# En queries, filtrar deleted_at IS NULL
```

---

## 🔒 RIESGOS DE SEGURIDAD

### RIESGO 8: Modificación No Autorizada de Cierres

**Descripción**: Usuario sin permisos modifica un cierre.

**Mitigación**:
```python
# Agregar permisos
def puede_cerrar_mes(user, printer_id):
    """Verifica si el usuario puede cerrar mes"""
    return user.role in ['admin', 'contador']

def puede_modificar_cierre(user, cierre_id):
    """Verifica si el usuario puede modificar cierre"""
    return user.role == 'admin'

# En endpoint
@router.post("/close-month")
def create_monthly_close(
    request: CierreMensualRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not puede_cerrar_mes(current_user, request.printer_id):
        raise HTTPException(403, "No tiene permisos para cerrar mes")
    
    # ... resto del código
```

### RIESGO 9: Inyección SQL en Queries Dinámicos

**Descripción**: Queries dinámicos podrían ser vulnerables a SQL injection.

**Mitigación**:
```python
# ❌ MAL - Vulnerable
query = f"SELECT * FROM cierres WHERE anio = {year}"

# ✅ BIEN - Usar parámetros
query = db.query(CierreMensual).filter(CierreMensual.anio == year)

# ✅ BIEN - Si necesitas SQL raw, usar parámetros
db.execute(text("SELECT * FROM cierres WHERE anio = :year"), {"year": year})
```

---

## 📊 MATRIZ DE RIESGOS

| Riesgo | Probabilidad | Impacto | Prioridad | Mitigación |
|--------|--------------|---------|-----------|------------|
| Pérdida de datos en limpieza | MEDIA | CRÍTICO | 🔴 ALTA | Transacción atómica + validación |
| Contador reseteado | BAJA | ALTO | 🟡 MEDIA | Detección automática + bloqueo |
| Cierre duplicado | BAJA | MEDIO | 🟡 MEDIA | UNIQUE constraint + lock |
| Inconsistencia total/usuarios | MEDIA | MEDIO | 🟡 MEDIA | Validación + reporte |
| Cierre sin lectura reciente | MEDIA | MEDIO | 🟡 MEDIA | Validación de antigüedad |
| Cierre fuera de secuencia | BAJA | MEDIO | 🟡 MEDIA | Validación de secuencia |
| Borrado accidental | BAJA | MEDIO | 🟢 BAJA | Soft delete |
| Modificación no autorizada | BAJA | ALTO | 🟡 MEDIA | Control de permisos |
| Inyección SQL | BAJA | CRÍTICO | 🟡 MEDIA | Parámetros en queries |

---

## ✅ CHECKLIST FINAL DE SEGURIDAD

Antes de lanzar a producción:

### Validaciones
- [ ] Transacción atómica en cierre
- [ ] Validación de count de usuarios
- [ ] Validación de suma de consumos
- [ ] Detección de reset de contador
- [ ] Validación de antigüedad de lectura
- [ ] Validación de secuencia de cierres
- [ ] Validación de duplicados

### Seguridad
- [ ] Control de permisos implementado
- [ ] Queries parametrizados (no SQL injection)
- [ ] Soft delete de cierres
- [ ] Log de auditoría
- [ ] Hash de verificación de integridad

### Recuperación
- [ ] Backup antes de limpieza
- [ ] Rollback en caso de error
- [ ] Plan de recuperación documentado
- [ ] Tests de recuperación ejecutados

### Monitoreo
- [ ] Alertas de crecimiento anormal
- [ ] Alertas de inconsistencias
- [ ] Alertas de reset de contador
- [ ] Dashboard de métricas

---

## 🚀 CONCLUSIÓN

Los riesgos identificados son manejables con las mitigaciones propuestas. Los más críticos son:

1. **Pérdida de datos en limpieza** - Mitigado con transacciones atómicas
2. **Contador reseteado** - Mitigado con detección automática
3. **Modificación no autorizada** - Mitigado con control de permisos

Con todas las mitigaciones implementadas, el sistema será robusto y confiable para producción.