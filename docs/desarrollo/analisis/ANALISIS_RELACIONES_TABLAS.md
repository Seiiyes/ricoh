# 🔗 ANÁLISIS DE RELACIONES ENTRE TABLAS

## 📊 DIAGRAMA DE RELACIONES

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SISTEMA DE GESTIÓN                            │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐                    ┌──────────────┐
│    users     │                    │   printers   │
│──────────────│                    │──────────────│
│ id (PK)      │                    │ id (PK)      │
│ name         │                    │ hostname     │
│ codigo_de_   │                    │ ip_address   │
│   usuario    │                    │ empresa      │
│ empresa      │                    │ ...          │
│ ...          │                    └──────┬───────┘
└──────┬───────┘                           │
       │                                   │
       │ N                             N   │
       │                                   │
       └───────────────┬───────────────────┘
                       │
                       │ 1
              ┌────────▼────────────┐
              │ user_printer_       │
              │   assignments       │
              │─────────────────────│
              │ id (PK)             │
              │ user_id (FK)        │
              │ printer_id (FK)     │
              │ func_copier         │
              │ func_printer        │
              │ ...                 │
              └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     SISTEMA DE CONTADORES                            │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │   printers   │
                    │──────────────│
                    │ id (PK)      │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           │ N             │ N             │ N
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
    │ contadores_ │ │ contadores_ │ │  cierres_  │
    │  impresora  │ │   usuario   │ │  mensuales │
    │─────────────│ │─────────────│ │────────────│
    │ id (PK)     │ │ id (PK)     │ │ id (PK)    │
    │ printer_id  │ │ printer_id  │ │ printer_id │
    │   (FK)      │ │   (FK)      │ │   (FK)     │
    │ total       │ │ codigo_     │ │ anio       │
    │ ...         │ │   usuario   │ │ mes        │
    └─────────────┘ │ total_      │ │ ...        │
                    │   paginas   │ └─────┬──────┘
                    │ ...         │       │
                    └─────────────┘       │ 1
                                          │
                                          │ N
                              ┌───────────▼──────────┐
                              │ cierres_mensuales_   │
                              │      usuarios        │
                              │──────────────────────│
                              │ id (PK)              │
                              │ cierre_mensual_id    │
                              │   (FK)               │
                              │ codigo_usuario       │
                              │ nombre_usuario       │
                              │ total_paginas        │
                              │ consumo_total        │
                              │ ...                  │
                              └──────────────────────┘
```

---

## 🔍 ANÁLISIS DETALLADO DE RELACIONES

### 1. Sistema de Administración de Usuarios

#### Relación: users ↔ printers (Many-to-Many)

```python
# Tabla intermedia: user_printer_assignments

User.printer_assignments → UserPrinterAssignment
UserPrinterAssignment.user → User
UserPrinterAssignment.printer → Printer
Printer.user_assignments → UserPrinterAssignment
```

**Propósito**: 
- Rastrear qué usuarios están aprovisionados en qué impresoras
- Guardar funciones específicas por impresora
- Auditoría de aprovisionamiento

**Integridad**:
- ✅ FK con CASCADE: Si se borra usuario, se borran asignaciones
- ✅ FK con CASCADE: Si se borra impresora, se borran asignaciones
- ✅ Relationship bidireccional

**Independencia con Contadores**:
- ⚠️ NO hay relación directa entre `users` y `contadores_usuario`
- ✅ CORRECTO: Son sistemas independientes
- `users` = Usuarios del sistema de gestión
- `contadores_usuario` = Usuarios de las impresoras (leídos del hardware)

---

### 2. Sistema de Contadores de Impresora

#### Relación: printers → contadores_impresora (One-to-Many)

```python
ContadorImpresora.printer_id → Printer.id
ContadorImpresora.printer → Printer (relationship)
```

**Propósito**:
- Almacenar histórico de contadores totales
- Múltiples lecturas por impresora

**Integridad**:
- ✅ FK con CASCADE: Si se borra impresora, se borran contadores
- ⚠️ RIESGO: Pérdida de datos históricos
- 💡 SOLUCIÓN: Cambiar a RESTRICT o guardar en cierres primero

**Índices**:
- ✅ idx_contadores_impresora_printer_id
- ✅ idx_contadores_impresora_fecha_lectura
- ✅ idx_contadores_impresora_fecha (compuesto, migración 007)

---

### 3. Sistema de Contadores por Usuario

#### Relación: printers → contadores_usuario (One-to-Many)

```python
ContadorUsuario.printer_id → Printer.id
ContadorUsuario.printer → Printer (relationship)
```

**Propósito**:
- Almacenar histórico de contadores por usuario
- Múltiples lecturas por usuario por impresora

**Integridad**:
- ✅ FK con CASCADE: Si se borra impresora, se borran contadores
- ⚠️ RIESGO: Pérdida de datos históricos
- 💡 SOLUCIÓN: Cambiar a RESTRICT o guardar en cierres primero

**Índices**:
- ✅ idx_contadores_usuario_printer_id
- ✅ idx_contadores_usuario_codigo
- ✅ idx_contadores_usuario_fecha_lectura
- ✅ idx_contadores_usuario_lookup (compuesto, migración 007)
- ✅ idx_contadores_usuario_cierre (compuesto, migración 007)
- ✅ idx_contadores_usuario_activos (parcial, migración 007)

**Relación con users**:
- ❌ NO hay FK entre contadores_usuario.codigo_usuario y users.codigo_de_usuario
- ✅ CORRECTO: Son independientes
- `contadores_usuario.codigo_usuario` = Código leído del hardware
- `users.codigo_de_usuario` = Código en sistema de gestión
- Pueden coincidir pero no es obligatorio

---

### 4. Sistema de Cierres Mensuales

#### Relación: printers → cierres_mensuales (One-to-Many)

```python
CierreMensual.printer_id → Printer.id
CierreMensual.printer → Printer (relationship)
```

**Propósito**:
- Un cierre por mes por impresora
- Histórico de cierres

**Integridad**:
- ✅ FK con CASCADE: Si se borra impresora, se borran cierres
- ✅ UNIQUE(printer_id, anio, mes): No duplicados
- ⚠️ RIESGO: Pérdida de datos de facturación
- 💡 SOLUCIÓN: Cambiar a RESTRICT

**Índices**:
- ✅ idx_cierres_mensuales_printer_id
- ✅ idx_cierres_mensuales_anio
- ✅ idx_cierres_mensuales_mes

---

### 5. Sistema de Snapshot de Usuarios en Cierres (NUEVO)

#### Relación: cierres_mensuales → cierres_mensuales_usuarios (One-to-Many)

```python
CierreMensualUsuario.cierre_mensual_id → CierreMensual.id
CierreMensualUsuario.cierre → CierreMensual (relationship)
CierreMensual.usuarios → CierreMensualUsuario (relationship)
```

**Propósito**:
- Snapshot inmutable de usuarios al momento del cierre
- Permite facturación sin depender de histórico
- Auditoría completa

**Integridad**:
- ✅ FK con CASCADE: Si se borra cierre, se borran usuarios
- ✅ CORRECTO: Los usuarios del snapshot son parte del cierre
- ✅ UNIQUE(cierre_mensual_id, codigo_usuario): No duplicados
- ✅ Relationship bidireccional

**Índices**:
- ✅ idx_cierres_usuarios_cierre
- ✅ idx_cierres_usuarios_codigo
- ✅ idx_cierres_usuarios_consumo

**Relación con contadores_usuario**:
- ❌ NO hay FK entre cierres_mensuales_usuarios y contadores_usuario
- ✅ CORRECTO: Es un snapshot independiente
- Los datos se copian al momento del cierre
- No depende de que existan los registros originales

---

## ⚠️ RIESGOS IDENTIFICADOS

### RIESGO 1: CASCADE DELETE en Contadores

**Problema**:
```sql
-- Si se borra una impresora:
DELETE FROM printers WHERE id = 4;

-- Se borran automáticamente:
- Todos los contadores_impresora (histórico completo)
- Todos los contadores_usuario (histórico completo)
- Todos los cierres_mensuales (datos de facturación)
- Todos los cierres_mensuales_usuarios (snapshots)
```

**Impacto**: CRÍTICO - Pérdida total de datos históricos

**Solución**:
```sql
-- Cambiar a RESTRICT para prevenir borrado accidental
ALTER TABLE contadores_impresora
DROP CONSTRAINT contadores_impresora_printer_id_fkey,
ADD CONSTRAINT contadores_impresora_printer_id_fkey
FOREIGN KEY (printer_id) REFERENCES printers(id) ON DELETE RESTRICT;

ALTER TABLE contadores_usuario
DROP CONSTRAINT contadores_usuario_printer_id_fkey,
ADD CONSTRAINT contadores_usuario_printer_id_fkey
FOREIGN KEY (printer_id) REFERENCES printers(id) ON DELETE RESTRICT;

ALTER TABLE cierres_mensuales
DROP CONSTRAINT cierres_mensuales_printer_id_fkey,
ADD CONSTRAINT cierres_mensuales_printer_id_fkey
FOREIGN KEY (printer_id) REFERENCES printers(id) ON DELETE RESTRICT;
```

**Alternativa**: Soft delete en printers
```python
class Printer(Base):
    # ... campos existentes ...
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String(100), nullable=True)
```

### RIESGO 2: Inconsistencia entre users y contadores_usuario

**Problema**:
- `users.codigo_de_usuario` puede no coincidir con `contadores_usuario.codigo_usuario`
- Usuario puede estar en sistema pero no en impresora
- Usuario puede estar en impresora pero no en sistema

**Impacto**: MEDIO - Confusión en reportes

**Solución**: Documentar claramente que son independientes
```python
# En documentación:
"""
users.codigo_de_usuario: Código en sistema de gestión
contadores_usuario.codigo_usuario: Código leído del hardware

Pueden coincidir pero no es obligatorio.
Para vincular, usar código como clave de búsqueda.
"""
```

---

## ✅ VALIDACIÓN DE RELACIONES

### Checklist de Integridad

- [x] users ↔ user_printer_assignments: Bidireccional ✅
- [x] printers ↔ user_printer_assignments: Bidireccional ✅
- [x] printers → contadores_impresora: Unidireccional ✅
- [x] printers → contadores_usuario: Unidireccional ✅
- [x] printers → cierres_mensuales: Unidireccional ✅
- [x] cierres_mensuales ↔ cierres_mensuales_usuarios: Bidireccional ✅

### Checklist de Constraints

- [x] FK con CASCADE donde corresponde ✅
- [ ] ⚠️ Considerar RESTRICT en contadores (recomendado)
- [x] UNIQUE constraints en lugares correctos ✅
- [x] CHECK constraints para validación ✅

---

## 📊 RESUMEN

### Relaciones Correctas ✅

1. **Sistema de Administración**: users ↔ printers (Many-to-Many)
   - ✅ Relationship bidireccional
   - ✅ Cascade correcto

2. **Sistema de Contadores**: printers → contadores (One-to-Many)
   - ✅ Relationship unidireccional
   - ⚠️ Cascade podría ser RESTRICT

3. **Sistema de Cierres**: cierres ↔ usuarios (One-to-Many)
   - ✅ Relationship bidireccional
   - ✅ Cascade correcto

### Independencias Correctas ✅

1. **users vs contadores_usuario**: Independientes
   - ✅ No hay FK (correcto)
   - ✅ Código puede coincidir pero no es obligatorio

2. **cierres_mensuales_usuarios vs contadores_usuario**: Independientes
   - ✅ No hay FK (correcto)
   - ✅ Snapshot no depende de histórico

### Recomendaciones

1. **Considerar RESTRICT en lugar de CASCADE** para:
   - contadores_impresora.printer_id
   - contadores_usuario.printer_id
   - cierres_mensuales.printer_id

2. **Implementar soft delete** en printers:
   - Evita pérdida accidental de datos
   - Mantiene integridad referencial

3. **Documentar claramente** la independencia entre:
   - users y contadores_usuario
   - Sistema de gestión vs sistema de contadores

**Estado**: ✅ RELACIONES CORRECTAS Y BIEN DISEÑADAS
