# Fix: Error al Asignar Empresa a Impresora

**Fecha**: 25 de marzo de 2026
**Estado**: ✅ RESUELTO
**Problema**: Al intentar asignar una empresa a una impresora desde el modal de edición, se producía un error 500 (Internal Server Error) y no se guardaban los cambios.

## Problema Identificado

El componente `EditPrinterModal` enviaba el nombre de la empresa (string) en lugar del ID de la empresa (número) al backend.

### Error en Logs

```
Error updating printer 7: 'str' object has no attribute '_sa_instance_state'
Update data: {'hostname': 'RNP002673C01D88', 'location': '2DO PISO SARUPETROL', 'empresa': 'SARUPETROL S.A.S', 'serial_number': 'E176M460020'}
```

El backend recibía:
```json
{
  "empresa": "SARUPETROL S.A.S"  // ❌ String (nombre)
}
```

Pero esperaba:
```json
{
  "empresa_id": 7  // ✅ Number (ID)
}
```

## Causa Raíz

### 1. EmpresaAutocomplete Devolvía Solo el Nombre

En `src/components/ui/EmpresaAutocomplete.tsx`:

```typescript
// Código anterior (INCORRECTO)
const handleSelect = (empresa: Empresa) => {
  onChange(empresa.razon_social);  // ❌ Solo devuelve el nombre
  setSearchTerm('');
  setIsOpen(false);
};
```

### 2. EditPrinterModal No Manejaba el ID

En `src/components/fleet/EditPrinterModal.tsx`:

```typescript
// Código anterior (INCORRECTO)
const [empresa, setEmpresa] = useState('');  // ❌ Solo guarda el nombre

await onSave(printer.id, {
  hostname,
  location: location || null,
  empresa: empresa || null,  // ❌ Envía el nombre en lugar del ID
  serial_number: serialNumber || null,
});
```

### 3. Tipos y Schemas Incompletos

- `PrinterDevice` no incluía `empresa_id`
- `PrinterResponse` no devolvía `empresa_id`
- `PrinterUpdate` aceptaba `empresa` (string) en lugar de `empresa_id` (number)

## Solución Implementada

### 1. Modificado EmpresaAutocomplete para Devolver ID y Nombre

**src/components/ui/EmpresaAutocomplete.tsx:**

```typescript
// Interfaz actualizada
interface EmpresaAutocompleteProps {
  label?: string;
  value: string;
  onChange: (value: string, empresaId?: number) => void;  // ✅ Ahora devuelve también el ID
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
}

// Función actualizada
const handleSelect = (empresa: Empresa) => {
  onChange(empresa.razon_social, empresa.id);  // ✅ Devuelve nombre e ID
  setSearchTerm('');
  setIsOpen(false);
};

const handleClear = () => {
  onChange('', undefined);  // ✅ Limpia ambos valores
  setSearchTerm('');
  inputRef.current?.focus();
};
```

### 2. Modificado EditPrinterModal para Manejar el ID

**src/components/fleet/EditPrinterModal.tsx:**

```typescript
// Estados actualizados
const [empresa, setEmpresa] = useState('');
const [empresaId, setEmpresaId] = useState<number | undefined>(undefined);  // ✅ Nuevo estado para el ID

// Inicialización actualizada
useEffect(() => {
  if (printer) {
    setHostname(printer.hostname);
    setLocation(printer.location || '');
    setEmpresa(printer.empresa || '');
    setEmpresaId(printer.empresa_id);  // ✅ Inicializa el ID
    setSerialNumber(printer.serial_number || '');
  }
}, [printer]);

// Guardado actualizado
await onSave(printer.id, {
  hostname,
  location: location || null,
  empresa_id: empresaId || null,  // ✅ Envía el ID en lugar del nombre
  serial_number: serialNumber || null,
});

// Uso del componente actualizado
<EmpresaAutocomplete
  label="Empresa"
  value={empresa}
  onChange={(value, id) => {  // ✅ Recibe ambos valores
    setEmpresa(value);
    setEmpresaId(id);
  }}
  placeholder="Buscar o seleccionar empresa..."
/>
```

### 3. Actualizados Tipos y Schemas

**src/types/index.ts:**
```typescript
interface PrinterDevice {
  id: string;
  hostname: string;
  ip_address: string;
  status: 'online' | 'offline';
  location?: string;
  empresa?: string;
  empresa_id?: number;  // ✅ Agregado
  serial_number?: string;
  // ... otros campos
}
```

**backend/api/schemas.py:**
```python
class PrinterResponse(PrinterBase):
    """Schema for printer response"""
    id: int
    empresa: Optional[str] = None
    empresa_id: Optional[int] = None  # ✅ Agregado
    # ... otros campos

class PrinterUpdate(BaseModel):
    """Schema for updating a printer"""
    hostname: Optional[str] = None
    location: Optional[str] = None
    empresa_id: Optional[int] = None  # ✅ Cambiado de 'empresa' a 'empresa_id'
    serial_number: Optional[str] = None
    # ... otros campos
```

### 4. Agregado Logging en el Backend

**backend/api/printers.py:**
```python
except Exception as e:
    import traceback
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Error updating printer {printer_id}: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    logger.error(f"Update data: {update_data}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to update printer: {str(e)}"
    )
```

## Comportamiento Esperado

### Antes del Fix ❌
1. Usuario selecciona empresa "SARUPETROL S.A.S" del dropdown
2. Frontend envía: `{ empresa: "SARUPETROL S.A.S" }`
3. Backend intenta guardar el string como relación de base de datos
4. Error 500: `'str' object has no attribute '_sa_instance_state'`
5. Cambios no se guardan

### Después del Fix ✅
1. Usuario selecciona empresa "SARUPETROL S.A.S" del dropdown
2. Frontend envía: `{ empresa_id: 7 }`
3. Backend guarda correctamente la relación con la empresa ID 7
4. Cambios se guardan exitosamente
5. Impresora queda asociada a la empresa
6. Al recargar, la impresora muestra la empresa correcta

## Archivos Modificados

### Frontend
- `src/components/ui/EmpresaAutocomplete.tsx`
  - Modificada interfaz para incluir `empresaId` en `onChange`
  - Actualizada función `handleSelect` para devolver ID y nombre
  - Actualizada función `handleClear` para limpiar ambos valores

- `src/components/fleet/EditPrinterModal.tsx`
  - Agregado estado `empresaId`
  - Actualizado `useEffect` para inicializar `empresaId`
  - Modificado `handleSave` para enviar `empresa_id`
  - Actualizado uso de `EmpresaAutocomplete`

- `src/types/index.ts`
  - Agregado campo `empresa_id?: number` a `PrinterDevice`

### Backend
- `backend/api/schemas.py`
  - Agregado `empresa_id` a `PrinterResponse`
  - Cambiado `empresa` por `empresa_id` en `PrinterUpdate`

- `backend/api/printers.py`
  - Agregado logging detallado en `update_printer`

## Pruebas Realizadas

✅ Seleccionar empresa del dropdown → Se guarda correctamente
✅ Limpiar empresa → Se elimina la asociación correctamente
✅ Editar otros campos sin cambiar empresa → Empresa se mantiene
✅ Logs del backend muestran el `empresa_id` correcto
✅ Al recargar la página, la empresa asignada se muestra correctamente

## Notas Técnicas

### Estructura de Datos

**Frontend (antes):**
```typescript
{
  hostname: string;
  location: string;
  empresa: string;  // ❌ Nombre de la empresa
  serial_number: string;
}
```

**Frontend (después):**
```typescript
{
  hostname: string;
  location: string;
  empresa_id: number;  // ✅ ID de la empresa
  serial_number: string;
}
```

**Backend (esperado):**
```python
class PrinterUpdate(BaseModel):
    hostname: Optional[str] = None
    location: Optional[str] = None
    empresa_id: Optional[int] = None  # ✅ Relación con tabla empresas
    serial_number: Optional[str] = None
```

### Relación en Base de Datos

```sql
-- Tabla printers
CREATE TABLE printers (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(255),
    location VARCHAR(255),
    empresa_id INTEGER REFERENCES empresas(id),  -- ✅ Foreign key
    serial_number VARCHAR(255)
);
```

## Lecciones Aprendidas

1. Los componentes de autocompletado deben devolver IDs, no nombres, para relaciones de base de datos
2. Es importante agregar logging detallado en los endpoints para facilitar la depuración
3. Los errores 500 genéricos pueden ocultar problemas de tipo de datos
4. Siempre verificar qué datos se están enviando al backend (usar logs o DevTools)
5. Los componentes reutilizables deben ser flexibles para devolver múltiples valores cuando sea necesario
6. Los tipos TypeScript y schemas Pydantic deben estar sincronizados

## Impacto

Este fix también beneficia a otros componentes que usan `EmpresaAutocomplete`, ya que ahora pueden acceder al ID de la empresa seleccionada si lo necesitan. Los componentes existentes que solo usan el nombre siguen funcionando correctamente (retrocompatibilidad).

## Comandos para Aplicar Cambios

```bash
# Reiniciar backend
docker-compose restart backend

# Refrescar frontend (en el navegador)
Ctrl + Shift + R
```
