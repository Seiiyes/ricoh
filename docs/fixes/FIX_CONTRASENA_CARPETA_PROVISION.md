# Fix: Contraseña de Carpeta No Se Configuraba al Crear Usuario

**Fecha**: 25 de marzo de 2026
**Estado**: ✅ RESUELTO
**Problema**: Al crear un usuario nuevo en una impresora, el sistema no configuraba la contraseña de inicio de sesión de carpeta ("Temporal2021"), lo que impedía que el usuario pudiera escanear documentos a su carpeta de red.

## Problema Identificado

Cuando se creaba un usuario nuevo en la impresora (ya sea desde "Agregar dispositivo" en Administración de Usuarios o mediante provisioning automático), el sistema:

1. ✅ Creaba el usuario correctamente
2. ✅ Habilitaba las funciones (copiadora, impresora, escáner, etc.)
3. ❌ NO configuraba la contraseña de inicio de sesión de carpeta

### Síntoma

El usuario no podía escanear documentos porque la impresora requiere una contraseña de carpeta configurada para autenticarse en el servidor SMB. El usuario tenía que:

1. Ir manualmente a la impresora
2. Editar el usuario
3. Ir a "Autenticación de carpeta"
4. Hacer clic en "Cambiar" en "Contraseña de inicio de sesión"
5. Establecer "Temporal2021"
6. Dar "Aceptar"
7. Volver al formulario anterior y dar "Aceptar" nuevamente

Solo después de este proceso manual, el escaneo funcionaba correctamente.

## Causa Raíz

En `backend/services/ricoh_web_client.py`, la función `provision_user` tenía dos problemas:

### 1. Contraseña Opcional

```python
# Código anterior (INCORRECTO)
network_password = user_config.get('contrasena_inicio_sesion', '')

# Only add password fields if password is provided
if network_password:
    form_data.append(('folderAuthPasswordIn', network_password))
    form_data.append(('folderAuthPasswordConfirmIn', network_password))
```

Si no se proporcionaba contraseña, simplemente NO se enviaban los campos de contraseña, dejando el campo vacío en la impresora.

### 2. Campo isFolderAuthPasswordUpdated Siempre en False

```python
# Código anterior (INCORRECTO)
('isFolderAuthPasswordUpdated', 'false'),  # Always false when no password
```

Este campo le indica a la impresora si se está actualizando la contraseña. Al estar siempre en `false`, la impresora ignoraba los campos de contraseña incluso si se enviaban.

## Solución Implementada

### 1. Contraseña por Defecto "Temporal2021"

```python
# Si no hay contraseña, usar "Temporal2021" por defecto
if not network_password:
    network_password = 'Temporal2021'
    logger.info(f"⚠️  No se proporcionó contraseña, usando 'Temporal2021' por defecto")

# Determinar si se debe marcar como actualizada la contraseña
is_password_updated = 'true' if network_password else 'false'
```

Ahora, si no se proporciona una contraseña explícita, el sistema usa "Temporal2021" automáticamente.

### 2. Campo isFolderAuthPasswordUpdated Dinámico

```python
('isFolderAuthPasswordUpdated', is_password_updated),  # true si hay contraseña
```

El campo ahora se establece en `'true'` cuando hay contraseña, indicando a la impresora que debe actualizar el campo.

### 3. Campos de Contraseña Siempre Presentes

```python
# Always add password fields (using Temporal2021 if not provided)
form_data.append(('folderAuthPasswordIn', network_password))
form_data.append(('folderAuthPasswordConfirmIn', network_password))

logger.info(f"🔐 Contraseña de carpeta configurada: {'***' if network_password else '(vacía)'}")
```

Los campos de contraseña ahora SIEMPRE se envían, usando "Temporal2021" si no se proporciona otra.

## Comportamiento Esperado

### Caso 1: Usuario con Contraseña Personalizada
- Usuario proporciona contraseña: "MiPassword123"
- Sistema envía: `folderAuthPasswordIn=MiPassword123`, `isFolderAuthPasswordUpdated=true`
- Resultado: Usuario creado con contraseña "MiPassword123"

### Caso 2: Usuario sin Contraseña (Más Común) ✅
- Usuario NO proporciona contraseña (campo vacío o null)
- Sistema usa por defecto: "Temporal2021"
- Sistema envía: `folderAuthPasswordIn=Temporal2021`, `isFolderAuthPasswordUpdated=true`
- Resultado: Usuario creado con contraseña "Temporal2021"
- Usuario puede escanear inmediatamente sin configuración manual

## Archivos Modificados

- `backend/services/ricoh_web_client.py` (función `provision_user`, líneas ~360-380)
  - Agregada lógica para usar "Temporal2021" por defecto
  - Cambiado `isFolderAuthPasswordUpdated` a dinámico
  - Campos de contraseña siempre presentes

## Pruebas Realizadas

✅ Crear usuario sin contraseña → Se establece "Temporal2021" automáticamente
✅ Usuario puede escanear inmediatamente sin configuración manual
✅ Logs muestran: "⚠️  No se proporcionó contraseña, usando 'Temporal2021' por defecto"
✅ Logs muestran: "🔐 Contraseña de carpeta configurada: ***"

## Notas Técnicas

### ¿Por qué "Temporal2021"?

Esta es la contraseña estándar que se usa manualmente en todas las impresoras de la organización. Al automatizar su configuración, se mantiene la consistencia y se elimina el paso manual.

### Campos Críticos para Autenticación de Carpeta

```python
('folderAuthAccountIn', 'AUTH_ASSIGNMENT_O'),  # Usar credenciales de asignación
('folderAuthUserNameIn', user_config.get('nombre_usuario_inicio_sesion', '')),  # Usuario de red
('folderAuthPasswordIn', network_password),  # Contraseña
('folderAuthPasswordConfirmIn', network_password),  # Confirmación
('isFolderAuthPasswordUpdated', 'true'),  # Indicar que se está actualizando
```

Todos estos campos deben estar presentes y correctos para que la autenticación de carpeta funcione.

### Impacto en Usuarios Existentes

Este fix solo afecta la CREACIÓN de nuevos usuarios. Los usuarios existentes mantienen sus contraseñas actuales. Si un usuario existente necesita actualizar su contraseña, debe hacerse mediante la función de actualización (que es un caso diferente).

## Lecciones Aprendidas

1. La impresora Ricoh requiere TODOS los campos de autenticación de carpeta para que el escaneo funcione
2. El campo `isFolderAuthPasswordUpdated` es crítico - debe ser `'true'` para que la impresora acepte la contraseña
3. Es mejor tener una contraseña por defecto que dejar el campo vacío
4. Los logs de debug son esenciales para identificar qué campos se están enviando
