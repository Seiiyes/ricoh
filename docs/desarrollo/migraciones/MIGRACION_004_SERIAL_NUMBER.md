# Migración 004: Campo Serial Number (ID Máquina)

## Resumen
Se agregó soporte completo para el campo `serial_number` (ID Máquina) en las impresoras, permitiendo su edición manual desde el frontend.

## Cambios Realizados

### 1. Backend

#### Modelo de Datos (`backend/db/models.py`)
- **Modificado**: Campo `serial_number` en modelo `Printer`
  - Removido constraint `unique=True` 
  - Agregado índice para performance
  - Permite valores NULL duplicados (útil cuando no se conoce el serial)

#### Schema de API (`backend/api/schemas.py`)
- **Modificado**: `PrinterUpdate` schema
  - Agregado campo `serial_number: Optional[str]`
  - Permite actualizar el serial desde el frontend

#### Migración de Base de Datos
- **Archivo**: `backend/migrations/004_remove_serial_unique_constraint.sql`
- **Script**: `backend/apply_migration_004.py`
- **Batch**: `backend/run-migration-004.bat`

**Cambios en DB:**
```sql
-- Elimina constraint unique
ALTER TABLE printers DROP CONSTRAINT IF EXISTS printers_serial_number_key;

-- Agrega índice no-único para performance
CREATE INDEX IF NOT EXISTS idx_printers_serial_number ON printers(serial_number);
```

### 2. Frontend

#### Tipos TypeScript (`src/types/index.ts`)
- **Modificado**: Interface `PrinterDevice`
  - Agregado campo `serial_number?: string`

#### Modal de Edición (`src/components/fleet/EditPrinterModal.tsx`)
- **Agregado**: Campo de entrada para Serial Number / ID Máquina
  - Label: "ID Máquina (Serial)"
  - Placeholder: "Ej: RNP0026737FFBB8"
  - Editable manualmente
  - Se envía al backend en el `onSave`

## Cómo Aplicar la Migración

### Opción 1: Usando el script batch (Recomendado)
```bash
cd backend
.\run-migration-004.bat
```

### Opción 2: Manualmente con Python
```bash
cd backend
# Activar entorno virtual
.\venv\Scripts\activate

# Ejecutar migración
python apply_migration_004.py
```

### Opción 3: SQL directo
```bash
psql -U postgres -d ricoh_db -f migrations/004_remove_serial_unique_constraint.sql
```

## Verificación

Después de aplicar la migración, verifica:

1. **Constraint eliminado:**
```sql
SELECT constraint_name 
FROM information_schema.table_constraints 
WHERE table_name = 'printers' 
AND constraint_type = 'UNIQUE'
AND constraint_name LIKE '%serial%';
-- Debe retornar 0 filas
```

2. **Índice creado:**
```sql
SELECT indexname 
FROM pg_indexes 
WHERE tablename = 'printers' 
AND indexname = 'idx_printers_serial_number';
-- Debe retornar 1 fila
```

3. **Impresoras actuales:**
```sql
SELECT id, hostname, ip_address, serial_number 
FROM printers;
```

## Uso en el Frontend

1. Ir a la vista de Equipos
2. Hacer clic en el botón "Editar" de una impresora
3. Verás el campo "ID Máquina (Serial)"
4. Puedes ingresar o modificar el serial manualmente
5. Hacer clic en "Guardar"

## Notas Importantes

### ¿Por qué se removió el constraint unique?

El constraint `unique=True` causaba problemas cuando:
- Múltiples impresoras no tenían serial (NULL)
- PostgreSQL considera cada NULL como único, pero SQLAlchemy puede tener problemas
- Permite flexibilidad para editar manualmente sin conflictos

### ¿De dónde viene el serial?

El serial puede venir de:
1. **Descubrimiento automático**: Durante el escaneo de red, se obtiene desde la interfaz web de Ricoh
2. **SNMP**: Detectado automáticamente si SNMP está habilitado (actualmente deshabilitado)
3. **Manual**: Ingresado manualmente por el usuario en el modal de edición

### Cómo se Obtiene Automáticamente

Durante el descubrimiento de impresoras (`/discovery/scan`), el sistema:

1. Detecta impresoras Ricoh en la red
2. Accede a la interfaz web de cada impresora
3. Busca el "ID máquina" en las páginas de configuración
4. Lo guarda automáticamente en el campo `serial_number`

**Rutas web consultadas:**
- `/web/guest/es/websys/status/configuration.cgi`
- `/web/guest/en/websys/status/configuration.cgi`
- `/web/guest/es/websys/webArch/mainFrame.cgi`

**Patrones buscados:**
- `ID máquina: E174M210096`
- `Machine ID: E174M210096`
- `Serial Number: E174M210096`

### Formato del Serial

**IMPORTANTE**: No confundir con el hostname

- **ID máquina (Serial)**: `E174M210096` ← Este es el serial real que va en este campo
- **Nombre de host (Hostname)**: `RNP0026737FFBB8` ← Este va en el campo `hostname`

Ejemplos de seriales reales (ID máquina):
- `E174M210096`
- `E174M210097`
- `E174M210098`

Ejemplos de hostnames (NO son seriales):
- `RNP0026737FFBB8` ← Este es el hostname, NO el serial
- `RNP00267391F283`
- `RNP002673CA501E`

## Archivos Modificados

```
backend/
├── db/
│   └── models.py                    # Modelo Printer actualizado
├── api/
│   └── schemas.py                   # Schema PrinterUpdate actualizado
├── migrations/
│   └── 004_remove_serial_unique_constraint.sql
├── apply_migration_004.py           # Script de migración
└── run-migration-004.bat            # Batch para Windows

src/
├── types/
│   └── index.ts                     # Interface PrinterDevice actualizada
└── components/
    └── fleet/
        └── EditPrinterModal.tsx     # Modal con campo serial

docs/
└── MIGRACION_004_SERIAL_NUMBER.md   # Este documento
```

## Rollback (Si es necesario)

Si necesitas revertir los cambios:

```sql
-- Eliminar índice
DROP INDEX IF EXISTS idx_printers_serial_number;

-- Limpiar valores duplicados (si existen)
UPDATE printers SET serial_number = NULL WHERE serial_number IN (
    SELECT serial_number FROM printers 
    WHERE serial_number IS NOT NULL 
    GROUP BY serial_number 
    HAVING COUNT(*) > 1
);

-- Restaurar constraint unique
ALTER TABLE printers ADD CONSTRAINT printers_serial_number_key UNIQUE (serial_number);
```

## Estado Actual

✅ Migración completada
✅ Backend actualizado
✅ Frontend actualizado
✅ Documentación creada

**Próximos pasos sugeridos:**
- Ingresar manualmente los seriales de las impresoras existentes
- Verificar que el escaneo SNMP detecte seriales automáticamente (si está habilitado)
