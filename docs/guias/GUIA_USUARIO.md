# Guía de Usuario - Sistema de Autenticación Ricoh Suite

## 👋 Bienvenido

Esta guía te ayudará a usar el sistema de autenticación y gestión de empresas de Ricoh Suite.

---

## 🚀 Inicio Rápido para Superadmin

### 1. Primer Login

Al iniciar el sistema por primera vez, usa las credenciales del superadmin:

```
Usuario: superadmin
Contraseña: {:Z75M!=x>9PiPp2
```

**⚠️ IMPORTANTE**: Cambia esta contraseña inmediatamente después del primer login.

### 2. Cambiar Contraseña

1. Haz clic en tu nombre en la esquina superior derecha
2. Selecciona "Cambiar Contraseña"
3. Ingresa tu contraseña actual
4. Ingresa tu nueva contraseña (debe cumplir requisitos de seguridad)
5. Confirma la nueva contraseña
6. Haz clic en "Guardar"

**Requisitos de contraseña:**
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número
- Al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?)

---

## 🏢 Gestión de Empresas (Solo Superadmin)

### Crear una Empresa

1. Ve a "Gestión de Empresas" en el menú lateral
2. Haz clic en el botón "Nueva Empresa"
3. Completa el formulario:
   - **Razón Social**: Nombre legal de la empresa (ej: "Mi Empresa S.A.S.")
   - **Nombre Comercial**: Identificador único en formato kebab-case (ej: "mi-empresa")
   - **NIT**: Número de identificación tributaria (ej: "900123456-7")
   - **Dirección**: Dirección física de la empresa
   - **Teléfono**: Número de contacto
   - **Email**: Correo electrónico de contacto
   - **Nombre de Contacto**: Persona de contacto
   - **Cargo de Contacto**: Cargo de la persona de contacto
4. Haz clic en "Guardar"

**Notas:**
- La razón social debe ser única
- El nombre comercial debe ser único y en formato kebab-case (minúsculas con guiones)
- El NIT debe ser único

### Editar una Empresa

1. Ve a "Gestión de Empresas"
2. Busca la empresa que deseas editar
3. Haz clic en el botón "Editar" (ícono de lápiz)
4. Modifica los campos necesarios
5. Haz clic en "Guardar"

### Desactivar una Empresa

1. Ve a "Gestión de Empresas"
2. Busca la empresa que deseas desactivar
3. Haz clic en el botón "Desactivar" (ícono de papelera)
4. Confirma la acción

**⚠️ IMPORTANTE**: No puedes desactivar una empresa que tenga:
- Impresoras activas
- Usuarios activos
- Usuarios administradores activos

Primero debes desactivar o reasignar estos recursos.

### Buscar Empresas

1. Ve a "Gestión de Empresas"
2. Usa la barra de búsqueda en la parte superior
3. Escribe parte de la razón social o nombre comercial
4. Los resultados se filtrarán automáticamente

---

## 👥 Gestión de Usuarios Administradores (Solo Superadmin)

### Crear un Usuario Admin

1. Ve a "Gestión de Usuarios Admin" en el menú lateral
2. Haz clic en el botón "Nuevo Usuario Admin"
3. Completa el formulario:
   - **Username**: Nombre de usuario único (minúsculas, números, guiones y guiones bajos)
   - **Contraseña**: Contraseña segura (cumplir requisitos)
   - **Nombre Completo**: Nombre y apellido del usuario
   - **Email**: Correo electrónico único
   - **Rol**: Selecciona el rol apropiado
   - **Empresa**: Selecciona la empresa (solo si el rol no es superadmin)
4. Haz clic en "Guardar"

**Roles disponibles:**
- **Superadmin**: Acceso total al sistema, gestiona empresas y usuarios admin
- **Admin**: Acceso solo a su empresa, gestiona recursos de su empresa
- **Viewer**: Solo lectura (preparado para futuro)
- **Operator**: Operaciones limitadas (preparado para futuro)

**Notas:**
- El username debe ser único
- El email debe ser único
- Los superadmin NO tienen empresa asignada
- Los admin, viewer y operator DEBEN tener empresa asignada

### Editar un Usuario Admin

1. Ve a "Gestión de Usuarios Admin"
2. Busca el usuario que deseas editar
3. Haz clic en el botón "Editar" (ícono de lápiz)
4. Modifica los campos necesarios
5. Haz clic en "Guardar"

**Notas:**
- No puedes cambiar el username
- Si cambias el rol de admin a superadmin, la empresa se quitará automáticamente
- Si cambias el rol de superadmin a admin, debes asignar una empresa

### Desactivar un Usuario Admin

1. Ve a "Gestión de Usuarios Admin"
2. Busca el usuario que deseas desactivar
3. Haz clic en el botón "Desactivar" (ícono de papelera)
4. Confirma la acción

**Efecto:**
- El usuario no podrá iniciar sesión
- Todas las sesiones activas del usuario se invalidarán inmediatamente
- El usuario seguirá visible en el sistema pero marcado como inactivo

### Cambiar Contraseña de un Usuario

1. Ve a "Gestión de Usuarios Admin"
2. Busca el usuario
3. Haz clic en el botón "Cambiar Contraseña"
4. Ingresa la nueva contraseña
5. Confirma la nueva contraseña
6. Haz clic en "Guardar"

**Nota:** El usuario deberá usar la nueva contraseña en su próximo login.

### Filtrar Usuarios

Puedes filtrar usuarios por:
- **Rol**: Selecciona un rol específico
- **Empresa**: Selecciona una empresa específica
- **Búsqueda**: Escribe parte del username, nombre completo o email

---

## 🔐 Seguridad y Mejores Prácticas

### Contraseñas Seguras

✅ **Buenas prácticas:**
- Usa al menos 12 caracteres
- Combina mayúsculas, minúsculas, números y símbolos
- No uses información personal (nombre, fecha de nacimiento, etc.)
- No reutilices contraseñas de otros sistemas
- Cambia tu contraseña periódicamente (cada 90 días)

❌ **Evita:**
- Contraseñas comunes (123456, password, admin, etc.)
- Palabras del diccionario
- Secuencias de teclado (qwerty, asdfgh, etc.)
- Información personal

### Sesiones

- Tu sesión expira después de 30 minutos de inactividad
- El sistema renovará automáticamente tu sesión si estás activo
- Si tu sesión expira, deberás iniciar sesión nuevamente
- Puedes tener múltiples sesiones activas en diferentes dispositivos

### Bloqueo de Cuenta

- Después de 5 intentos fallidos de login, tu cuenta se bloqueará por 15 minutos
- Durante el bloqueo, no podrás iniciar sesión incluso con la contraseña correcta
- Después de 15 minutos, el bloqueo se levantará automáticamente
- Si olvidas tu contraseña, contacta al superadmin

---

## 📊 Uso del Sistema como Admin

### Vista de Datos

Como usuario admin, solo verás datos de tu empresa:
- **Impresoras**: Solo las impresoras asignadas a tu empresa
- **Usuarios**: Solo los usuarios de impresoras de tu empresa
- **Contadores**: Solo los contadores de impresoras de tu empresa
- **Cierres Mensuales**: Solo los cierres de tu empresa

### Crear Recursos

Cuando creas un nuevo recurso (impresora, usuario, etc.), automáticamente se asignará a tu empresa. No puedes crear recursos para otras empresas.

### Editar/Eliminar Recursos

Solo puedes editar o eliminar recursos que pertenecen a tu empresa. Si intentas acceder a un recurso de otra empresa, recibirás un error de "Acceso denegado".

---

## ❓ Preguntas Frecuentes (FAQ)

### ¿Olvidé mi contraseña, qué hago?

Contacta al superadmin para que te restablezca la contraseña.

### ¿Por qué mi cuenta está bloqueada?

Tu cuenta se bloquea automáticamente después de 5 intentos fallidos de login. Espera 15 minutos y vuelve a intentar.

### ¿Puedo cambiar mi username?

No, el username no se puede cambiar. Si necesitas un username diferente, el superadmin debe crear una nueva cuenta.

### ¿Puedo ver datos de otras empresas?

No, como usuario admin solo puedes ver datos de tu propia empresa. Solo los superadmin pueden ver datos de todas las empresas.

### ¿Qué significa "kebab-case"?

Es un formato de texto donde las palabras se escriben en minúsculas y se separan con guiones. Ejemplo: "mi-empresa-sas"

### ¿Puedo tener múltiples sesiones activas?

Sí, puedes iniciar sesión en múltiples dispositivos o navegadores simultáneamente.

### ¿Cuánto tiempo dura mi sesión?

Tu sesión dura 30 minutos desde tu última actividad. Si estás activo, el sistema renovará automáticamente tu sesión.

### ¿Qué pasa si desactivo un usuario admin?

El usuario no podrá iniciar sesión y todas sus sesiones activas se invalidarán inmediatamente.

### ¿Puedo reactivar una empresa o usuario desactivado?

Sí, el superadmin puede reactivar empresas y usuarios desactivados editándolos y marcándolos como activos.

### ¿Se registran mis acciones en el sistema?

Sí, todas las acciones administrativas se registran en el sistema de auditoría, incluyendo:
- Inicios de sesión
- Creación, edición y eliminación de recursos
- Cambios de contraseña
- Accesos denegados

---

## 🆘 Soporte

Si tienes problemas o preguntas:

1. **Revisa esta guía**: La mayoría de las preguntas comunes están respondidas aquí
2. **Contacta al superadmin**: Para problemas de acceso o permisos
3. **Revisa los logs**: El superadmin puede revisar los logs del sistema para diagnosticar problemas

---

## 📱 Acceso desde Dispositivos Móviles

El sistema es completamente responsive y funciona en:
- **Smartphones**: iPhone, Android
- **Tablets**: iPad, Android tablets
- **Computadoras**: Windows, Mac, Linux

Usa el mismo URL y credenciales en cualquier dispositivo.

---

## 🔄 Actualizaciones del Sistema

El sistema se actualiza periódicamente con nuevas características y mejoras de seguridad. Las actualizaciones se realizan durante ventanas de mantenimiento programadas y se notificarán con anticipación.

---

**Última actualización**: 20 de Marzo de 2026  
**Versión del sistema**: 2.0.0

