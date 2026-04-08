# Documentación: Problema de Usuarios Duplicados

## 📋 Resumen del Problema

Se detectó que usuarios están apareciendo duplicados en la base de datos con códigos diferentes que representan al mismo usuario (ej: "0547" y "547" para ADRIANA MAQUILLO).

## 🔍 Causa Raíz

### 1. Inconsistencia en Códigos de Usuario desde Impresoras

Las impresoras Ricoh pueden enviar códigos de usuario con o sin ceros a la izquierda:
- Algunas veces: `"0547"`
- Otras veces: `"547"`
- Ambos representan al mismo usuario

### 2. Flujo de Creación de Usuarios

```
Impresora → Parser → sync_user_from_counter() → Base de Datos
```

**Paso 1: Parser extrae datos**
- `backend/services/parsers/user_counter_parser.py`
- `backend/services/parsers/eco_counter_parser.py`
- Extraen el código TAL COMO viene del HTML: `codigo_usuario = cells[X].get_text(strip=True)`
- NO normalizan el código (no eliminan ceros a la izquierda)

**Paso 2: CounterService llama a sync**
- `backend/services/counter_service.py` líneas 153 y 223
- Convierte a string: `codigo_usuario=str(user['codigo_usuario'])`
- Pasa el código sin normalizar a `sync_user_from_counter()`

**Paso 3: UserSyncService busca o crea usuario**
- `backend/services/user_sync_service.py` línea 48
- Busca usuario existente: `User.codigo_de_usuario == codigo_usuario`
- Si no encuentra coincidencia EXACTA, crea un nuevo usuario
- **PROBLEMA**: "0547" ≠ "547" → Se crean 2 usuarios

### 3. Modelo de Base de Datos

```python
# backend/db/models.py línea 37
codigo_de_usuario = Column(String(8), nullable=False, index=True)
```

- NO tiene constraint UNIQUE
- Permite múltiples usuarios con códigos diferentes
- Index solo mejora búsquedas, no previene duplicados

## 📊 Evidencia del Problema

### Usuarios Duplicados Detectados

```sql
-- ADRIANA MAQUILLO aparece 2 veces
SELECT id, name, codigo_de_usuario FROM users WHERE name ILIKE '%ADRIANA%';
 id  |       name       | codigo_de_usuario 
-----+------------------+-------------------
 197 | ADRIANA MAQUILLO | 0547
 296 | ADRIANA MAQUILLO | 547
```

### Códigos Duplicados en Sistema

```sql
SELECT codigo_de_usuario, COUNT(*) as count 
FROM users 
GROUP BY codigo_de_usuario 
HAVING COUNT(*) > 1;

 codigo_de_usuario | count 
-------------------+-------
 5353              |     2
 2202              |     2
 6793              |     2
 0328              |     2
 4848              |     2
```

## 🛠️ Solución Implementada

### 1. Normalización de Códigos

Implementar función de normalización que:
- Elimina ceros a la izquierda: `"0547"` → `"547"`
- Maneja casos especiales: `"0000"` → `"0"`
- Se aplica ANTES de buscar/crear usuarios

```python
def normalize_user_code(code: str) -> str:
    """
    Normaliza código de usuario eliminando ceros a la izquierda.
    
    Args:
        code: Código de usuario (puede tener ceros a la izquierda)
    
    Returns:
        Código normalizado sin ceros a la izquierda
    
    Examples:
        "0547" → "547"
        "8599" → "8599"
        "0000" → "0"
    """
    if not code or not code.strip():
        return "0"
    
    normalized = code.strip().lstrip('0')
    return normalized if normalized else "0"
```

### 2. Actualización de sync_user_from_counter()

```python
@staticmethod
def sync_user_from_counter(
    codigo_usuario: str,
    nombre_usuario: str,
    db: Session,
    printer_id: Optional[int] = None,
    smb_path: Optional[str] = None
) -> int:
    # ✓ NORMALIZAR código antes de buscar
    codigo_normalizado = normalize_user_code(codigo_usuario)
    
    # Buscar usuario existente por código NORMALIZADO
    user = db.query(User).filter(
        User.codigo_de_usuario == codigo_normalizado
    ).first()
    
    if user:
        return user.id
    
    # Crear usuario con código NORMALIZADO
    new_user = User(
        name=nombre_usuario,
        codigo_de_usuario=codigo_normalizado,  # ← Código normalizado
        # ... resto de campos
    )
```

### 3. Constraint UNIQUE en Base de Datos

```sql
-- Agregar constraint para prevenir duplicados futuros
ALTER TABLE users 
ADD CONSTRAINT users_codigo_de_usuario_unique 
UNIQUE (codigo_de_usuario);
```

### 4. Script de Corrección de Duplicados Existentes

Script para consolidar usuarios duplicados:
1. Identificar usuarios con códigos que normalizan al mismo valor
2. Seleccionar usuario "principal" (el más antiguo o con más datos)
3. Actualizar todas las referencias FK a apuntar al usuario principal
4. Eliminar usuarios duplicados

## 📝 Archivos Modificados

### Archivos a Actualizar

1. **backend/services/user_sync_service.py**
   - Agregar función `normalize_user_code()`
   - Actualizar `sync_user_from_counter()` para normalizar códigos
   - Actualizar `sync_users_from_printer_addressbook()` para normalizar códigos

2. **backend/services/counter_service.py**
   - Ya pasa el código a `sync_user_from_counter()` correctamente
   - No requiere cambios (la normalización se hace en UserSyncService)

3. **backend/db/models.py**
   - Documentar que `codigo_de_usuario` debe estar normalizado
   - Agregar comentario sobre constraint UNIQUE

4. **backend/migrations/016_fix_duplicate_users.sql** (NUEVO)
   - Script SQL para consolidar usuarios duplicados
   - Agregar constraint UNIQUE

5. **backend/scripts/consolidate_duplicate_users.py** (NUEVO)
   - Script Python para consolidar usuarios duplicados
   - Actualizar todas las referencias FK

## 🚀 Plan de Implementación

### Fase 1: Corrección de Duplicados Existentes ✅ PENDIENTE

1. Ejecutar script de consolidación de usuarios duplicados
2. Verificar que no quedan duplicados
3. Aplicar migración 016 (constraint UNIQUE)

### Fase 2: Prevención de Duplicados Futuros ✅ PENDIENTE

1. Actualizar `UserSyncService.sync_user_from_counter()`
2. Actualizar `UserSyncService.sync_users_from_printer_addressbook()`
3. Agregar tests unitarios para normalización

### Fase 3: Verificación ✅ PENDIENTE

1. Ejecutar tests
2. Leer contadores de impresoras
3. Verificar que no se crean duplicados
4. Verificar que usuarios existentes se reutilizan correctamente

## 🔒 Prevención Futura

### Reglas de Negocio

1. **SIEMPRE normalizar códigos de usuario antes de buscar/crear**
2. **NUNCA crear usuario sin verificar código normalizado**
3. **Constraint UNIQUE en base de datos previene duplicados a nivel DB**

### Checklist para Nuevas Funcionalidades

Cuando se agregue código que cree o busque usuarios:

- [ ] ¿Se normaliza el código antes de buscar?
- [ ] ¿Se normaliza el código antes de crear?
- [ ] ¿Se maneja el caso de código vacío o "0000"?
- [ ] ¿Se tiene test unitario para normalización?

## 📚 Referencias

- **Modelo User**: `backend/db/models.py` línea 27
- **UserSyncService**: `backend/services/user_sync_service.py`
- **CounterService**: `backend/services/counter_service.py`
- **Parsers**: `backend/services/parsers/`

## 🐛 Debugging

### Verificar Duplicados

```sql
-- Ver usuarios duplicados por código normalizado
SELECT 
    LTRIM(codigo_de_usuario, '0') as codigo_normalizado,
    STRING_AGG(id::text || ':' || name || ':' || codigo_de_usuario, ', ') as usuarios,
    COUNT(*) as count
FROM users
GROUP BY LTRIM(codigo_de_usuario, '0')
HAVING COUNT(*) > 1
ORDER BY count DESC;
```

### Verificar Normalización

```python
from services.user_sync_service import normalize_user_code

# Tests
assert normalize_user_code("0547") == "547"
assert normalize_user_code("8599") == "8599"
assert normalize_user_code("0000") == "0"
assert normalize_user_code("") == "0"
```

## ⚠️ Notas Importantes

1. **NO ejecutar script de normalización antiguo** (`backend/scripts/fix_duplicate_user_codes.py`)
   - Ese script normaliza códigos en `contadores_usuario` y `cierre_mensual_usuario`
   - Esas tablas YA NO TIENEN esos campos (migración 013)
   - El script está obsoleto

2. **Orden de ejecución**
   - Primero: Consolidar usuarios duplicados
   - Segundo: Agregar constraint UNIQUE
   - Tercero: Actualizar código de sincronización
   - Cuarto: Verificar con lecturas reales

3. **Backup antes de consolidar**
   - Hacer backup de tabla `users` antes de consolidar
   - Hacer backup de tablas con FK a `users`

---

**Fecha de Documentación**: 2026-04-08
**Autor**: Sistema de Auditoría
**Estado**: Documentado - Pendiente de Implementación
