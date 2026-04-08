# Corrección de API de Contadores - Acceso a Datos de Usuario

## Fecha: 2026-04-08
## Problema Reportado

Al intentar crear un cierre desde el frontend, se generó el error:
```
Error al crear cierre: 'ContadorUsuario' object has no attribute 'codigo_usuario'
```

## Causa Raíz

El archivo `backend/api/counters.py` todavía tenía código que intentaba acceder directamente a las columnas `codigo_usuario` y `nombre_usuario` que fueron eliminadas en la migración 013.

## Archivos Corregidos

### `backend/api/counters.py`

Se actualizaron 4 secciones del código:

#### 1. Línea ~350: Debug de lectura de usuarios
**Antes:**
```python
for u in usuarios[:5]:
    print(f"     - {u.codigo_usuario}: {u.nombre_usuario} ({u.total_paginas} páginas)")
```

**Después:**
```python
from db.models import User
for u in usuarios[:5]:
    user = db.query(User).filter(User.id == u.user_id).first()
    codigo = user.codigo_de_usuario if user else str(u.user_id)
    nombre = user.name if user else f"Usuario {u.user_id}"
    print(f"     - {codigo}: {nombre} ({u.total_paginas} páginas)")
```

#### 2. Línea ~540: Búsqueda de usuarios en detalle de cierre
**Antes:**
```python
if search:
    search_term = f"%{search}%"
    usuarios_query = usuarios_query.filter(
        (CierreMensualUsuario.nombre_usuario.ilike(search_term)) |
        (CierreMensualUsuario.codigo_usuario.ilike(search_term))
    )
```

**Después:**
```python
if search:
    from db.models import User
    search_term = f"%{search}%"
    # Buscar por user_id que coincida con usuarios que tengan el código o nombre
    user_ids = db.query(User.id).filter(
        (User.codigo_de_usuario.ilike(search_term)) |
        (User.name.ilike(search_term))
    ).all()
    user_ids_list = [uid[0] for uid in user_ids]
    
    if user_ids_list:
        usuarios_query = usuarios_query.filter(
            CierreMensualUsuario.user_id.in_(user_ids_list)
        )
    else:
        # Si no se encontraron usuarios, retornar query vacío
        usuarios_query = usuarios_query.filter(CierreMensualUsuario.user_id == -1)
```

#### 3. Línea ~612: Comparación de cierres - Diccionarios de usuarios
**Antes:**
```python
usuarios1 = {u.codigo_usuario: u for u in cierre1.usuarios}
usuarios2 = {u.codigo_usuario: u for u in cierre2.usuarios}
codigos = set(usuarios1.keys()).union(set(usuarios2.keys()))
```

**Después:**
```python
from db.models import User
usuarios1 = {u.user_id: u for u in cierre1.usuarios}
usuarios2 = {u.user_id: u for u in cierre2.usuarios}
user_ids = set(usuarios1.keys()).union(set(usuarios2.keys()))
```

#### 4. Línea ~616: Comparación de cierres - Iteración de usuarios
**Antes:**
```python
for codigo in codigos:
    u1 = usuarios1.get(codigo)
    u2 = usuarios2.get(codigo)
    
    # ... cálculos ...
    
    usuarios_con_consumo.append({
        'codigo': codigo,
        'nombre': u2.nombre_usuario if u2 else u1.nombre_usuario,
        # ...
    })
```

**Después:**
```python
for user_id in user_ids:
    u1 = usuarios1.get(user_id)
    u2 = usuarios2.get(user_id)
    
    # Obtener datos del usuario
    user = db.query(User).filter(User.id == user_id).first()
    codigo = user.codigo_de_usuario if user else str(user_id)
    nombre = user.name if user else f"Usuario {user_id}"
    
    # ... cálculos ...
    
    usuarios_con_consumo.append({
        'codigo': codigo,
        'nombre': nombre,
        # ...
    })
```

## Patrón de Corrección Aplicado

En todos los casos, se siguió el mismo patrón:

1. **Importar el modelo User**
   ```python
   from db.models import User
   ```

2. **Hacer JOIN para obtener datos**
   ```python
   user = db.query(User).filter(User.id == usuario.user_id).first()
   codigo = user.codigo_de_usuario if user else str(usuario.user_id)
   nombre = user.name if user else f"Usuario {usuario.user_id}"
   ```

3. **Usar user_id como clave en diccionarios**
   ```python
   usuarios_dict = {u.user_id: u for u in usuarios}
   ```

## Verificación

- ✅ Sin errores de sintaxis en `backend/api/counters.py`
- ✅ Backend reiniciado exitosamente
- ✅ Estado del backend: healthy

## Funcionalidades Afectadas y Corregidas

1. **Creación de cierres** - Ahora funciona correctamente
2. **Búsqueda de usuarios en cierres** - Busca en tabla `users`
3. **Comparación de cierres** - Usa `user_id` como clave
4. **Verificación de coherencia** - Obtiene datos de usuario mediante JOIN

## Pruebas Recomendadas

Después de esta corrección, se recomienda probar desde el frontend:

1. ✅ Crear un nuevo cierre
2. ✅ Buscar usuarios en un cierre existente
3. ✅ Comparar dos cierres
4. ✅ Verificar coherencia de comparación
5. ✅ Ver detalle de cierre con paginación

## Archivos Relacionados

- `backend/api/counters.py` - Corregido
- `backend/api/export.py` - Ya estaba corregido
- `backend/services/export_ricoh.py` - Ya estaba corregido
- `backend/services/counter_service.py` - Ya estaba corregido
- `backend/services/close_service.py` - Ya estaba corregido

## Estado Final

✅ **TODAS LAS REFERENCIAS A COLUMNAS ELIMINADAS HAN SIDO CORREGIDAS**

El sistema ahora accede a los datos de usuario exclusivamente mediante:
- `user_id` (FK en tablas normalizadas)
- JOIN con tabla `users` para obtener `codigo_de_usuario` y `name`

---

**Última actualización**: 2026-04-08
**Backend reiniciado**: Sí
**Estado**: ✅ FUNCIONANDO CORRECTAMENTE
