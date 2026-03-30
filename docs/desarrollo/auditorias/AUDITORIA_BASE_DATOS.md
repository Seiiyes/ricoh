# 🔍 AUDITORÍA EXHAUSTIVA DE BASE DE DATOS

## 📊 ANÁLISIS REALIZADO

Fecha: 2026-03-03
Sistema: Ricoh Fleet Management
Base de datos: PostgreSQL 16

---

## ✅ ASPECTOS POSITIVOS

### 1. Persistencia de Datos
```yaml
Configuración Docker:
  Volume: postgres_data (named volume)
  Path: /var/lib/postgresql/data/pgdata
  Persistencia: ✅ CORRECTA
  
Ventajas:
  - Los datos persisten después de docker-compose down
  - Volume nombrado (fácil de respaldar)
  - Separado del código (no se borra con rebuild)
```

### 2. Healthcheck
```yaml
Healthcheck configurado:
  Test: pg_isready
  Interval: 10s
  Timeout: 5s
  Retries: 5
  
Ventajas:
  - Backend espera a que DB esté lista
  - Previene errores de conexión al iniciar
```

### 3. Connection Pooling
```python
Engine configurado:
  pool_size: 10
  max_overflow: 20
  pool_pre_ping: True
  
Ventajas:
  - Reutiliza conexiones (más rápido)
  - Verifica conexiones antes de usar
  - Soporta hasta 30 conexiones concurrentes
```

### 4. Migraciones Ordenadas
```
001 - User provisioning fields
002 - Rename to Spanish
003 - Add empresa to printers
004 - Remove serial unique constraint
005 - Add contador tables
006 - Add detailed counter fields

Ventajas:
  - Historial claro de cambios
  - Fácil de rastrear evolución
  - Numeración secuencial
```

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### PROBLEMA 1: Falta de Constraints de Integridad Referencial

**Tablas afectadas**: `contadores_usuario`, `contadores_impresora`

**Problema actual**:
```sql
-- contadores_usuario
printer_id INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE

-- ✅ BIEN: Tiene FK con CASCADE
-- ⚠️  FALTA: No hay constraint para evitar registros huérfanos
```

**Riesgo**:
- Si se borra una impresora, se borran TODOS sus contadores históricos
- Pérdida de datos de facturación

**Solución**: Cambiar a `ON DELETE RESTRICT` o `ON DELETE SET NULL`

### PROBLEMA 2: Falta de Índices Compuestos

**Queries lentos identificados**:

```sql
-- Query 1: Última lectura por usuario
SELECT * FROM contadores_usuario
WHERE printer_id = 4 
  AND codigo_usuario = '9967'
ORDER BY created_at DESC
LIMIT 1;

-- Índices actuales: printer_id, codigo_usuario, created_at (separados)
-- ⚠️  FALTA: Índice compuesto (printer_id, codigo_usuario, created_at DESC)
```

```sql
-- Query 2: Usuarios de un cierre mensual
SELECT * FROM contadores_usuario
WHERE printer_id = 4
  AND created_at <= '2026-03-31 23:59:59'
ORDER BY created_at DESC;

-- ⚠️  FALTA: Índice compuesto (printer_id, created_at DESC)
```

### PROBLEMA 3: Falta de Constraints de Validación

**Datos inválidos posibles**:

```sql
-- contadores_usuario
total_paginas INTEGER DEFAULT 0 NOT NULL

-- ⚠️  FALTA: CHECK (total_paginas >= 0)
-- Permite valores negativos
```

```sql
-- cierres_mensuales
mes INTEGER NOT NULL

-- ⚠️  FALTA: CHECK (mes BETWEEN 1 AND 12)
-- Permite mes = 13, 0, -1, etc.
```

```sql
-- cierres_mensuales
anio INTEGER NOT NULL

-- ⚠️  FALTA: CHECK (anio BETWEEN 2020 AND 2100)
-- Permite año = 1900, 3000, etc.
```

### PROBLEMA 4: Falta de Índices Parciales

**Queries frecuentes con filtros**:

```sql
-- Query: Solo usuarios activos
SELECT * FROM contadores_usuario
WHERE printer_id = 4
  AND total_paginas > 0;

-- ⚠️  FALTA: Índice parcial
-- CREATE INDEX idx_usuarios_activos 
-- ON contadores_usuario(printer_id, total_paginas)
-- WHERE total_paginas > 0;
```

### PROBLEMA 5: Falta de Comentarios en Columnas

**Documentación insuficiente**:

```sql
-- Solo 3 tablas tienen comentarios
COMMENT ON TABLE contadores_impresora IS '...';
COMMENT ON TABLE contadores_usuario IS '...';
COMMENT ON TABLE cierres_mensuales IS '...';

-- ⚠️  FALTA: Comentarios en columnas críticas
-- ⚠️  FALTA: Comentarios en otras tablas (users, printers, etc.)
```

### PROBLEMA 6: Falta de Auditoría

**Sin tracking de cambios**:

```sql
-- Tablas sin auditoría:
-- - users (modificaciones no rastreadas)
-- - printers (modificaciones no rastreadas)
-- - cierres_mensuales (modificaciones no rastreadas)

-- ⚠️  FALTA: Columnas de auditoría
-- modified_at TIMESTAMP
-- modified_by VARCHAR(100)
```

### PROBLEMA 7: Índices Duplicados

**Índices redundantes detectados**:

```sql
-- cierres_mensuales tiene índices duplicados:
idx_cierres_mensuales_anio
ix_cierres_mensuales_anio  -- ❌ DUPLICADO

idx_cierres_mensuales_mes
ix_cierres_mensuales_mes   -- ❌ DUPLICADO

-- Causa: SQLAlchemy crea ix_* automáticamente
-- Migración crea idx_* manualmente
```

### PROBLEMA 8: Falta de Particionamiento

**Tabla grande sin particiones**:

```sql
-- contadores_usuario crecerá a 2M registros/año
-- ⚠️  FALTA: Particionamiento por mes/año
-- Queries serán lentos con el tiempo
```

**Nota**: No crítico ahora, pero necesario cuando > 5 GB

### PROBLEMA 9: Falta de Política de Retención

**Sin limpieza automática**:

```sql
-- contadores_usuario crece indefinidamente
-- ⚠️  FALTA: Política de retención documentada
-- ⚠️  FALTA: Job de limpieza automática
```

### PROBLEMA 10: Configuración de Backup

**Sin backup automático**:

```yaml
# docker-compose.yml
# ⚠️  FALTA: Configuración de backup automático
# ⚠️  FALTA: Script de backup programado
# ⚠️  FALTA: Verificación de backups
```

---

## 🔧 PLAN DE CORRECCIÓN

### Fase 1: Correcciones Críticas (ANTES de implementar cierres)

#### 1.1 Migración 007: Tabla de Snapshot + Correcciones

```sql
-- Migration 007: Add snapshot table and fix critical issues
-- Date: 2026-03-03
-- Description: Adds cierres_mensuales_usuarios and fixes integrity issues

-- ============================================================================
-- PARTE 1: CREAR TABLA DE SNAPSHOT
-- ============================================================================

CREATE TABLE cierres_mensuales_usuarios (
    id SERIAL PRIMARY KEY,
    cierre_mensual_id INTEGER NOT NULL REFERENCES cierres_mensuales(id) ON DELETE CASCADE,
    
    -- Usuario
    codigo_usuario VARCHAR(8) NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    
    -- Contadores al cierre (snapshot)
    total_paginas INTEGER NOT NULL CHECK (total_paginas >= 0),
    total_bn INTEGER NOT NULL CHECK (total_bn >= 0),
    total_color INTEGER NOT NULL CHECK (total_color >= 0),
    
    -- Desglose por función
    copiadora_bn INTEGER NOT NULL CHECK (copiadora_bn >= 0),
    copiadora_color INTEGER NOT NULL CHECK (copiadora_color >= 0),
    impresora_bn INTEGER NOT NULL CHECK (impresora_bn >= 0),
    impresora_color INTEGER NOT NULL CHECK (impresora_color >= 0),
    escaner_bn INTEGER NOT NULL CHECK (escaner_bn >= 0),
    escaner_color INTEGER NOT NULL CHECK (escaner_color >= 0),
    fax_bn INTEGER NOT NULL CHECK (fax_bn >= 0),
    
    -- Consumo del mes (puede ser negativo si hubo reset)
    consumo_total INTEGER NOT NULL,
    consumo_copiadora INTEGER NOT NULL,
    consumo_impresora INTEGER NOT NULL,
    consumo_escaner INTEGER NOT NULL,
    consumo_fax INTEGER NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraints
    CONSTRAINT uk_cierre_usuario UNIQUE(cierre_mensual_id, codigo_usuario)
);

-- Índices para snapshot
CREATE INDEX idx_cierres_usuarios_cierre ON cierres_mensuales_usuarios(cierre_mensual_id);
CREATE INDEX idx_cierres_usuarios_codigo ON cierres_mensuales_usuarios(codigo_usuario);
CREATE INDEX idx_cierres_usuarios_consumo ON cierres_mensuales_usuarios(consumo_total DESC);

-- Comentarios
COMMENT ON TABLE cierres_mensuales_usuarios IS 'Snapshot de contadores por usuario al momento del cierre mensual';
COMMENT ON COLUMN cierres_mensuales_usuarios.consumo_total IS 'Consumo del mes (diferencia con mes anterior)';

-- ============================================================================
-- PARTE 2: AGREGAR CONSTRAINTS DE VALIDACIÓN
-- ============================================================================

-- Validar mes (1-12)
ALTER TABLE cierres_mensuales 
ADD CONSTRAINT chk_mes_valido CHECK (mes BETWEEN 1 AND 12);

-- Validar año (2020-2100)
ALTER TABLE cierres_mensuales 
ADD CONSTRAINT chk_anio_valido CHECK (anio BETWEEN 2020 AND 2100);

-- Validar contadores no negativos
ALTER TABLE cierres_mensuales
ADD CONSTRAINT chk_total_paginas_positivo CHECK (total_paginas >= 0),
ADD CONSTRAINT chk_total_copiadora_positivo CHECK (total_copiadora >= 0),
ADD CONSTRAINT chk_total_impresora_positivo CHECK (total_impresora >= 0),
ADD CONSTRAINT chk_total_escaner_positivo CHECK (total_escaner >= 0),
ADD CONSTRAINT chk_total_fax_positivo CHECK (total_fax >= 0);

-- Validar contadores de usuario no negativos
ALTER TABLE contadores_usuario
ADD CONSTRAINT chk_usuario_total_positivo CHECK (total_paginas >= 0),
ADD CONSTRAINT chk_usuario_bn_positivo CHECK (total_bn >= 0),
ADD CONSTRAINT chk_usuario_color_positivo CHECK (total_color >= 0);

-- Validar contadores de impresora no negativos
ALTER TABLE contadores_impresora
ADD CONSTRAINT chk_impresora_total_positivo CHECK (total >= 0);

-- ============================================================================
-- PARTE 3: AGREGAR ÍNDICES COMPUESTOS
-- ============================================================================

-- Índice para query de última lectura por usuario
CREATE INDEX idx_contadores_usuario_lookup 
ON contadores_usuario(printer_id, codigo_usuario, created_at DESC);

-- Índice para query de cierre mensual
CREATE INDEX idx_contadores_usuario_cierre 
ON contadores_usuario(printer_id, created_at DESC);

-- Índice parcial para usuarios activos
CREATE INDEX idx_contadores_usuario_activos 
ON contadores_usuario(printer_id, total_paginas)
WHERE total_paginas > 0;

-- Índice para query de impresora por fecha
CREATE INDEX idx_contadores_impresora_fecha
ON contadores_impresora(printer_id, created_at DESC);

-- ============================================================================
-- PARTE 4: ELIMINAR ÍNDICES DUPLICADOS
-- ============================================================================

-- Eliminar índices duplicados creados por SQLAlchemy
DROP INDEX IF EXISTS ix_cierres_mensuales_anio;
DROP INDEX IF EXISTS ix_cierres_mensuales_mes;
DROP INDEX IF EXISTS ix_cierres_mensuales_printer_id;
DROP INDEX IF EXISTS ix_contadores_usuario_codigo_usuario;
DROP INDEX IF EXISTS ix_contadores_usuario_fecha_lectura;
DROP INDEX IF EXISTS ix_contadores_usuario_printer_id;
DROP INDEX IF EXISTS ix_contadores_impresora_fecha_lectura;
DROP INDEX IF EXISTS ix_contadores_impresora_printer_id;

-- Los índices idx_* de la migración 005 son suficientes

-- ============================================================================
-- PARTE 5: AGREGAR COLUMNAS DE AUDITORÍA
-- ============================================================================

-- Auditoría en cierres_mensuales
ALTER TABLE cierres_mensuales
ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS modified_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS hash_verificacion VARCHAR(64);

COMMENT ON COLUMN cierres_mensuales.modified_at IS 'Fecha de última modificación (si aplica)';
COMMENT ON COLUMN cierres_mensuales.modified_by IS 'Usuario que modificó el cierre (si aplica)';
COMMENT ON COLUMN cierres_mensuales.hash_verificacion IS 'SHA256 hash para verificar integridad';

-- ============================================================================
-- PARTE 6: AGREGAR COMENTARIOS FALTANTES
-- ============================================================================

-- Comentarios en users
COMMENT ON TABLE users IS 'Usuarios del sistema para aprovisionamiento en impresoras';
COMMENT ON COLUMN users.codigo_de_usuario IS 'Código de usuario de 8 dígitos para autenticación en impresora';
COMMENT ON COLUMN users.empresa IS 'Empresa a la que pertenece el usuario';
COMMENT ON COLUMN users.centro_costos IS 'Centro de costos para facturación';

-- Comentarios en printers
COMMENT ON TABLE printers IS 'Impresoras registradas en el sistema';
COMMENT ON COLUMN printers.tiene_contador_usuario IS 'Indica si la impresora tiene getUserCounter.cgi disponible';
COMMENT ON COLUMN printers.usar_contador_ecologico IS 'Indica si se debe usar getEcoCounter.cgi para contadores de usuario';

-- Comentarios en contadores
COMMENT ON COLUMN contadores_usuario.tipo_contador IS 'Tipo de contador: "usuario" (getUserCounter) o "ecologico" (getEcoCounter)';
COMMENT ON COLUMN contadores_usuario.created_at IS 'Timestamp de cuando se guardó el registro (agrupa lecturas de una sesión)';

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

-- Verificar que todo se creó correctamente
SELECT 
    'Tabla cierres_mensuales_usuarios' as verificacion,
    COUNT(*) as existe
FROM information_schema.tables
WHERE table_name = 'cierres_mensuales_usuarios';

SELECT 
    'Constraints de validación' as verificacion,
    COUNT(*) as total
FROM information_schema.table_constraints
WHERE constraint_type = 'CHECK'
AND table_name IN ('cierres_mensuales', 'contadores_usuario', 'contadores_impresora');

SELECT 
    'Índices compuestos' as verificacion,
    COUNT(*) as total
FROM pg_indexes
WHERE indexname LIKE 'idx_contadores_usuario_%'
AND tablename = 'contadores_usuario';
```

#### 1.2 Actualizar models.py

```python
# Agregar al final de models.py

class CierreMensualUsuario(Base):
    """
    Snapshot de contadores por usuario al momento del cierre mensual
    Permite auditoría y facturación sin depender de datos históricos
    """
    __tablename__ = "cierres_mensuales_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    cierre_mensual_id = Column(Integer, ForeignKey("cierres_mensuales.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Usuario
    codigo_usuario = Column(String(8), nullable=False, index=True)
    nombre_usuario = Column(String(100), nullable=False)
    
    # Contadores al cierre (snapshot)
    total_paginas = Column(Integer, nullable=False)
    total_bn = Column(Integer, nullable=False)
    total_color = Column(Integer, nullable=False)
    
    # Desglose por función
    copiadora_bn = Column(Integer, nullable=False)
    copiadora_color = Column(Integer, nullable=False)
    impresora_bn = Column(Integer, nullable=False)
    impresora_color = Column(Integer, nullable=False)
    escaner_bn = Column(Integer, nullable=False)
    escaner_color = Column(Integer, nullable=False)
    fax_bn = Column(Integer, nullable=False)
    
    # Consumo del mes
    consumo_total = Column(Integer, nullable=False)
    consumo_copiadora = Column(Integer, nullable=False)
    consumo_impresora = Column(Integer, nullable=False)
    consumo_escaner = Column(Integer, nullable=False)
    consumo_fax = Column(Integer, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    cierre = relationship("CierreMensual", back_populates="usuarios")

    def __repr__(self):
        return f"<CierreMensualUsuario(cierre_id={self.cierre_mensual_id}, codigo={self.codigo_usuario}, consumo={self.consumo_total})>"


# Actualizar CierreMensual para agregar relationship
# Agregar después de la línea "printer = relationship("Printer")"
usuarios = relationship("CierreMensualUsuario", back_populates="cierre", cascade="all, delete-orphan")

# Agregar columnas de auditoría
modified_at = Column(DateTime(timezone=True), nullable=True)
modified_by = Column(String(100), nullable=True)
hash_verificacion = Column(String(64), nullable=True)
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Pre-implementación
- [ ] Backup completo de base de datos
- [ ] Verificar que docker volume existe
- [ ] Documentar estado actual

### Implementación
- [ ] Crear migración 007
- [ ] Actualizar models.py
- [ ] Ejecutar migración
- [ ] Verificar constraints
- [ ] Verificar índices
- [ ] Tests de integridad

### Post-implementación
- [ ] Verificar que datos persisten
- [ ] Verificar rendimiento de queries
- [ ] Documentar cambios
- [ ] Actualizar diagramas

---

## ✅ RESULTADO ESPERADO

Después de aplicar todas las correcciones:

```
✅ Persistencia garantizada (volume nombrado)
✅ Integridad referencial (constraints)
✅ Validación de datos (CHECK constraints)
✅ Rendimiento optimizado (índices compuestos)
✅ Sin índices duplicados
✅ Auditoría completa
✅ Documentación completa (comentarios)
✅ Snapshot de cierres (tabla nueva)
✅ Base de datos escalable y mantenible
```

**Estado**: LISTO PARA IMPLEMENTAR CIERRES MENSUALES
