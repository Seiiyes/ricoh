# Solución: Sincronización de Datos de Perfil a Múltiples Impresoras

## Problema Original

Cuando se modifican los datos de perfil de un usuario (carpeta, nombre, código, usuario_red) en la pestaña "Perfil y SMB", estos cambios solo se guardaban en la base de datos pero NO se sincronizaban automáticamente a las impresoras físicas donde el usuario está registrado.

## Solución Implementada

### 1. Endpoint de Sincronización

**Ruta**: `PUT /provisioning/users/{user_id}/sync-to-all-printers`

**Funcionalidad**:
- Recibe una lista de IPs de impresoras en el body: `{"printer_ips": ["192.168.91.251", "192.168.91.252", ...]}`
- Sincroniza SOLO los datos de perfil: `nombre`, `código`, `carpeta`, `usuario_red`
- **NO modifica los permisos** - cada impresora mantiene sus permisos actuales
- Maneja automáticamente casos donde el usuario existe en la impresora pero no hay assignment en la DB

### 2. Flujo de Sincronización

```
1. Obtener usuario de la DB
2. Para cada impresora en printer_ips:
   a. Buscar impresora en DB por IP
   b. Buscar assignment (user_id + printer_id)
   c. Si NO hay assignment o NO tiene entry_index:
      - Buscar usuario directamente en la impresora física
      - Obtener entry_index y permisos actuales
      - Crear/actualizar assignment en DB
   d. Leer permisos actuales de la impresora (si no se proporcionaron)
   e. Actualizar usuario en impresora física manteniendo permisos
3. Retornar resultado con conteo de éxitos/errores
```

### 3. Método `update_user_in_printer()`

**Ubicación**: `backend/services/ricoh_web_client.py`

**Características**:
- Actualización inteligente: solo modifica campos proporcionados
- Si no vienen permisos, LEE los actuales de la impresora y los mantiene
- Lee el formulario actual antes de actualizar (para preservar campos no modificados)
- Usa el flujo correcto de Ricoh: `mode=MODUSER` + `inputSpecifyModeIn=READ/WRITE`

**Campos que sincroniza**:
- ✅ `nombre` (entryNameIn)
- ✅ `código` (userCodeIn)
- ✅ `carpeta` (folderPathNameIn)
- ✅ `usuario_red` (folderAuthUserNameIn)
- ✅ `permisos` (availableFuncIn) - mantiene los actuales si no se especifican

**Campos que NO sincroniza** (solo existen en DB):
- ❌ `empresa` (centro_costos en DB)
- ❌ `centro_costos` (departamento en DB)

### 4. Auto-Discovery de Usuarios

Si un usuario existe en una impresora física pero no hay assignment en la DB:

1. El sistema busca el usuario en la impresora usando `find_specific_user()`
2. Obtiene el `entry_index` y permisos actuales
3. Crea automáticamente el assignment en la DB usando `update_assignment_state()`
4. Procede con la actualización normalmente

Esto permite sincronizar usuarios que fueron creados manualmente en las impresoras.

### 5. Integración Frontend

**Archivo**: `src/components/usuarios/ModificarUsuario.tsx`

Cuando el usuario hace clic en "Aplicar cambios" en la pestaña "Perfil y SMB":

```typescript
// 1. Actualizar en DB
await actualizarUsuario(usuarioId, datosActualizados);

// 2. Sincronizar a impresoras físicas
const printerIps = usuario.impresoras_asignadas.map(p => p.ip);
await sincronizarUsuarioAImpresoras(usuarioId, printerIps);
```

El modal NO se cierra después de aplicar cambios, mostrando un mensaje de éxito por 3 segundos, permitiendo editar múltiples impresoras en secuencia.

## Casos de Uso

### Caso 1: Usuario con Assignments en DB
```
Usuario 7104 tiene assignments en .251 y .252
→ Sincroniza directamente usando entry_index de cada assignment
→ Mantiene permisos actuales de cada impresora
```

### Caso 2: Usuario sin Assignment pero Existe en Impresora
```
Usuario 7104 existe en .252 pero no hay assignment en DB
→ Busca usuario en .252 usando find_specific_user()
→ Obtiene entry_index: "00089"
→ Crea assignment en DB automáticamente
→ Actualiza datos en .252
```

### Caso 3: Usuario No Existe en Impresora
```
Usuario 7104 no existe en .253
→ Registra warning en logs
→ Continúa con las demás impresoras
→ No interrumpe el proceso
```

## Pruebas

### Script de Prueba
```bash
cd backend
python test_sync_profile_data.py
```

### Pruebas Manuales

1. **Modificar datos de perfil**:
   - Abrir modal de usuario
   - Ir a pestaña "Perfil y SMB"
   - Cambiar carpeta o usuario_red
   - Hacer clic en "Aplicar cambios"

2. **Verificar en impresora física**:
   - Acceder a http://192.168.91.251/web/entry/es/address/adrsList.cgi
   - Buscar el usuario por código
   - Verificar que los datos coinciden
   - Verificar que los permisos NO cambiaron

3. **Verificar logs del backend**:
   ```
   🔄 Sincronizando usuario 7104 a 2 impresoras
      IPs: ['192.168.91.251', '192.168.91.252']
      Solo sincronizando: nombre, código, carpeta, usuario_red
      Permisos: se mantienen los actuales de cada impresora
   
   ✅ Actualizado en RICOH-251 (192.168.91.251)
   🔍 No hay assignment, buscando usuario 7104 en 192.168.91.252...
   ✅ Usuario encontrado en impresora con entry_index: 00089
   📝 Creando assignment en DB...
   ✅ Actualizado en RICOH-252 (192.168.91.252)
   ```

## Correcciones Aplicadas

### Error 1: Método Inexistente
```python
# ❌ INCORRECTO - método no existe
AssignmentRepository.create_assignment(...)
```

**Solución**:
```python
# ✅ CORRECTO - usa update_assignment_state que crea o actualiza
AssignmentRepository.update_assignment_state(
    db=db,
    user_id=user_id,
    printer_id=printer.id,
    entry_index=entry_index,
    permissions=user_in_printer.get('permisos', {})
)
```

### Error 2: Búsqueda de Usuarios Fallaba

**Problema**: El parsing de usuarios descartaba códigos que no eran completamente numéricos, causando que usuarios válidos no se encontraran.

**Código original**:
```python
if not codigo or not codigo.isdigit():
    if nombre.isdigit() and not codigo.isdigit():
        nombre, codigo = codigo, nombre
    else: continue  # ❌ Descarta el usuario
```

**Solución**:
```python
# Limpiar espacios
nombre = nombre.strip() if nombre else ""
codigo = codigo.strip() if codigo else ""

# Si el código está vacío o no es numérico, intentar intercambiar con nombre
if not codigo or not codigo.isdigit():
    if nombre and nombre.isdigit():
        nombre, codigo = codigo, nombre

# Si después del intercambio el código sigue sin ser numérico, extraer dígitos
if not codigo or not codigo.isdigit():
    import re
    digits = re.sub(r'\D', '', codigo)
    if digits:
        codigo = digits
    else:
        continue  # Solo descarta si definitivamente no hay código
```

**Mejoras**:
1. Limpia espacios en blanco de nombre y código
2. Intenta intercambiar nombre/código si están invertidos
3. Extrae solo los dígitos del código si contiene caracteres no numéricos
4. Solo descarta el usuario si definitivamente no se puede obtener un código numérico
5. Agrega logging detallado para debugging

### Error 3: Falta de Logging en Búsqueda

**Problema**: Cuando la búsqueda fallaba, no había suficiente información para diagnosticar el problema.

**Solución**: Agregado logging detallado en `find_specific_user()`:
- Muestra total de usuarios encontrados
- Compara códigos con logging debug
- Lista usuarios disponibles si no se encuentra el buscado
- Muestra permisos obtenidos después de encontrar el usuario

## Archivos Modificados

1. **backend/api/provisioning.py** (línea ~509)
   - Cambio de `create_assignment()` a `update_assignment_state()`
   - Simplificación del código eliminando el if/else

2. **backend/services/ricoh_web_client.py** (líneas 1110-1350)
   - Método `update_user_in_printer()` con lectura inteligente de permisos

3. **backend/db/repository.py** (líneas 240-270)
   - Método `update_assignment_state()` que crea o actualiza

4. **src/components/usuarios/ModificarUsuario.tsx**
   - Integración con endpoint de sincronización

5. **src/services/servicioUsuarios.ts**
   - Función `sincronizarUsuarioAImpresoras()`

## Impresoras Soportadas

El sistema sincroniza a las siguientes impresoras Ricoh:
- ✅ 192.168.91.250 (RICOH-250)
- ✅ 192.168.91.251 (RICOH-251)
- ✅ 192.168.91.252 (RICOH-252)
- ✅ 192.168.91.253 (RICOH-253)

**NO sincroniza a**:
- ❌ 192.168.91.248 (Kyocera)
- ❌ 192.168.91.249 (Kyocera)

## Notas Importantes

1. **Permisos se mantienen**: El sistema NUNCA modifica los permisos existentes en cada impresora, solo actualiza datos de perfil.

2. **Campos solo en DB**: `empresa` y `centro_costos` NO existen en la interfaz web de Ricoh, solo en nuestra base de datos.

3. **Sincronización selectiva**: Solo sincroniza a las impresoras especificadas en `printer_ips`, no a todas automáticamente.

4. **Manejo de errores**: Si falla en una impresora, continúa con las demás y reporta el conteo de éxitos/errores.

5. **Auto-discovery**: Si un usuario existe en la impresora pero no en la DB, el sistema lo detecta y crea el assignment automáticamente.

## Próximos Pasos

- ✅ Implementado endpoint de sincronización
- ✅ Implementado auto-discovery de usuarios
- ✅ Corregido error de `create_assignment()`
- ✅ Corregido parsing de códigos de usuario
- ✅ Mejorado logging para debugging
- ⏳ Probar con usuario 7104 en .251 y .252
- ⏳ Verificar que permisos se mantienen correctamente
- ⏳ Documentar casos edge (usuario no existe, impresora offline, etc.)

## Troubleshooting

### Problema: "Usuario no encontrado en impresora"

**Síntomas**:
```
❌ Usuario 7104 no encontrado en 192.168.91.252
```

**Diagnóstico**:
```bash
cd backend
python debug_search_user.py 192.168.91.252 7104
```

Este script mostrará:
1. Total de usuarios en la impresora
2. Primeros 10 usuarios con sus códigos
3. Búsqueda manual del usuario
4. Resultado del método `find_specific_user()`

**Posibles causas**:
1. El código del usuario en la DB no coincide con el de la impresora
2. El parsing está extrayendo el código del campo incorrecto
3. El usuario realmente no existe en esa impresora

**Solución**:
- Verificar que el código en la DB coincide con el de la impresora
- Revisar los logs del script de diagnóstico para ver qué códigos se están parseando
- Si el formato de la impresora es diferente, ajustar el parsing en `read_users_from_printer()`

### Problema: "Error actualizando usuario en impresora"

**Síntomas**:
```
❌ Error actualizando en RICOH-252
```

**Diagnóstico**:
1. Revisar el archivo `update_user_response_{entry_index}.html` generado
2. Buscar mensajes de error en el HTML
3. Verificar que todos los campos obligatorios se están enviando

**Posibles causas**:
1. Falta algún campo obligatorio en el payload
2. El wimToken expiró
3. La sesión se cerró
4. La impresora rechazó los datos (formato incorrecto)

**Solución**:
- Revisar el HTML de respuesta para ver el error específico
- Verificar que el método `update_user_in_printer()` está leyendo el formulario correctamente
- Asegurar que todos los 34 campos obligatorios se están enviando

### Problema: "Los permisos cambiaron después de sincronizar"

**Síntomas**: Los permisos del usuario en la impresora son diferentes después de la sincronización.

**Causa**: El método `update_user_in_printer()` no está leyendo correctamente los permisos actuales.

**Solución**:
1. Verificar que `user_data` NO incluye el campo `permisos`
2. El método debe leer los permisos actuales usando `_get_user_details()`
3. Revisar logs para confirmar: `"🔍 Leyendo permisos actuales de la impresora..."`
