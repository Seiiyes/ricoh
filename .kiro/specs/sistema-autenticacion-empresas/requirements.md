# Requirements Document - Sistema de Autenticación y Gestión de Empresas

## Introduction

Este documento define los requisitos para implementar un sistema completo de autenticación con roles y multi-tenancy basado en empresas para Ricoh Suite. El sistema permitirá gestionar múltiples empresas, usuarios administradores con diferentes roles, y garantizar el aislamiento de datos entre empresas.

El sistema actual NO tiene autenticación y los campos de empresa en las tablas `users` y `printers` no están normalizados (VARCHAR sin integridad referencial). Este feature implementará:

1. Normalización de empresas en tabla dedicada
2. Sistema de autenticación JWT con roles (superadmin, admin)
3. Filtrado automático por empresa según el rol del usuario
4. Auditoría completa de acciones
5. Gestión de usuarios administradores y empresas

## Glossary

- **Sistema_Autenticacion**: Sistema completo de login, gestión de sesiones y control de acceso
- **Empresa**: Organización cliente que usa Ricoh Suite (tenant en arquitectura multi-tenant)
- **Usuario_Admin**: Usuario del sistema con acceso al panel de administración (NO es usuario de impresora)
- **Usuario_Impresora**: Usuario que se aprovisiona en impresoras Ricoh (tabla `users` existente)
- **Superadmin**: Rol con acceso total al sistema, sin empresa asignada, puede gestionar todas las empresas
- **Admin**: Rol asignado a una empresa específica, solo puede ver/gestionar datos de su empresa
- **Sesion**: Período de tiempo en que un usuario está autenticado, representado por JWT token
- **JWT**: JSON Web Token usado para autenticación stateless
- **Refresh_Token**: Token de larga duración usado para renovar access tokens
- **Access_Token**: Token de corta duración usado para autenticar requests API
- **Multi_Tenancy**: Arquitectura donde múltiples empresas comparten la misma aplicación con datos aislados
- **Filtrado_Empresa**: Mecanismo que restringe queries de base de datos según la empresa del usuario
- **Auditoria**: Registro inmutable de todas las acciones realizadas por usuarios administradores
- **Migracion_Datos**: Proceso de convertir campos VARCHAR de empresa a foreign keys normalizadas
- **Bloqueo_Cuenta**: Mecanismo de seguridad que deshabilita temporalmente una cuenta tras intentos fallidos
- **Rate_Limiting**: Limitación de número de requests por unidad de tiempo para prevenir ataques

## Requirements

### Requirement 1: Normalización de Empresas

**User Story:** Como desarrollador del sistema, quiero normalizar los campos de empresa en una tabla dedicada, para garantizar integridad referencial y consistencia de datos.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear una tabla `empresas` con campos: id, razon_social, nombre_comercial, nit, direccion, telefono, email, contacto_nombre, contacto_cargo, logo_url, config_json, is_active, created_at, updated_at
2. THE Sistema_Autenticacion SHALL garantizar que razon_social sea UNIQUE y NOT NULL
3. THE Sistema_Autenticacion SHALL garantizar que nombre_comercial sea UNIQUE, NOT NULL y siga formato kebab-case
4. THE Sistema_Autenticacion SHALL agregar columna empresa_id (INTEGER FK) a tabla `printers`
5. THE Sistema_Autenticacion SHALL agregar columna empresa_id (INTEGER FK) a tabla `users`
6. WHEN se ejecute la migración, THE Sistema_Autenticacion SHALL insertar empresas únicas desde los campos VARCHAR existentes
7. WHEN se ejecute la migración, THE Sistema_Autenticacion SHALL actualizar printers.empresa_id con el id correspondiente de la tabla empresas
8. WHEN se ejecute la migración, THE Sistema_Autenticacion SHALL actualizar users.empresa_id con el id correspondiente de la tabla empresas
9. WHEN la migración esté completa, THE Sistema_Autenticacion SHALL eliminar las columnas VARCHAR antiguas (printers.empresa, users.empresa)
10. THE Sistema_Autenticacion SHALL crear índices en empresa_id para printers y users
11. THE Sistema_Autenticacion SHALL garantizar que printers.empresa_id sea NOT NULL
12. THE Sistema_Autenticacion SHALL permitir que users.empresa_id sea NULL (usuarios sin empresa asignada)
13. THE Sistema_Autenticacion SHALL configurar ON DELETE RESTRICT en las foreign keys de empresa_id

### Requirement 2: Tabla de Usuarios Administradores

**User Story:** Como arquitecto del sistema, quiero una tabla dedicada para usuarios administradores, para separar usuarios del sistema de usuarios de impresoras.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear una tabla `admin_users` con campos: id, username, password_hash, nombre_completo, email, rol, empresa_id, is_active, created_at, updated_at, last_login, failed_login_attempts, locked_until
2. THE Sistema_Autenticacion SHALL garantizar que username sea UNIQUE, NOT NULL y siga formato [a-z0-9_-]{3,}
3. THE Sistema_Autenticacion SHALL garantizar que email sea UNIQUE, NOT NULL y tenga formato válido de email
4. THE Sistema_Autenticacion SHALL garantizar que password_hash sea NOT NULL y tenga longitud mínima de 60 caracteres
5. THE Sistema_Autenticacion SHALL validar que rol sea uno de: superadmin, admin, viewer, operator
6. THE Sistema_Autenticacion SHALL garantizar que superadmin tenga empresa_id NULL
7. THE Sistema_Autenticacion SHALL garantizar que admin, viewer, operator tengan empresa_id NOT NULL
8. THE Sistema_Autenticacion SHALL inicializar failed_login_attempts en 0
9. THE Sistema_Autenticacion SHALL permitir que locked_until sea NULL cuando la cuenta no esté bloqueada
10. THE Sistema_Autenticacion SHALL crear índices en username, email, empresa_id, rol, is_active
11. THE Sistema_Autenticacion SHALL configurar foreign key empresa_id → empresas(id) con ON DELETE RESTRICT
12. THE Sistema_Autenticacion SHALL crear un trigger para actualizar updated_at automáticamente

### Requirement 3: Hashing de Contraseñas

**User Story:** Como administrador de seguridad, quiero que las contraseñas se almacenen hasheadas con bcrypt, para proteger credenciales de usuarios.

#### Acceptance Criteria

1. WHEN se cree un usuario administrador, THE Sistema_Autenticacion SHALL hashear la contraseña usando bcrypt con 12 rounds
2. THE Sistema_Autenticacion SHALL validar que la contraseña en texto plano tenga mínimo 8 caracteres
3. THE Sistema_Autenticacion SHALL validar que la contraseña contenga al menos una letra mayúscula
4. THE Sistema_Autenticacion SHALL validar que la contraseña contenga al menos una letra minúscula
5. THE Sistema_Autenticacion SHALL validar que la contraseña contenga al menos un número
6. THE Sistema_Autenticacion SHALL validar que la contraseña contenga al menos un carácter especial
7. THE Sistema_Autenticacion SHALL almacenar solo el hash bcrypt en password_hash
8. THE Sistema_Autenticacion SHALL nunca almacenar contraseñas en texto plano
9. THE Sistema_Autenticacion SHALL nunca retornar password_hash en respuestas API
10. WHEN se actualice una contraseña, THE Sistema_Autenticacion SHALL generar un nuevo hash bcrypt

### Requirement 4: Tabla de Sesiones

**User Story:** Como desarrollador del sistema, quiero una tabla para gestionar sesiones activas, para poder invalidar tokens y rastrear actividad.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear una tabla `admin_sessions` con campos: id, admin_user_id, token, refresh_token, ip_address, user_agent, expires_at, refresh_expires_at, created_at, last_activity
2. THE Sistema_Autenticacion SHALL garantizar que token sea UNIQUE y NOT NULL
3. THE Sistema_Autenticacion SHALL garantizar que refresh_token sea UNIQUE cuando no sea NULL
4. THE Sistema_Autenticacion SHALL configurar foreign key admin_user_id → admin_users(id) con ON DELETE CASCADE
5. THE Sistema_Autenticacion SHALL crear índices en admin_user_id, token, expires_at
6. THE Sistema_Autenticacion SHALL crear índice parcial para sesiones activas (expires_at > NOW())
7. THE Sistema_Autenticacion SHALL almacenar ip_address del cliente (IPv4 o IPv6)
8. THE Sistema_Autenticacion SHALL almacenar user_agent del navegador
9. THE Sistema_Autenticacion SHALL actualizar last_activity en cada request autenticado
10. THE Sistema_Autenticacion SHALL validar que expires_at sea mayor que created_at

### Requirement 5: Tabla de Auditoría

**User Story:** Como auditor del sistema, quiero un registro inmutable de todas las acciones, para cumplir con requisitos de compliance y seguridad.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear una tabla `admin_audit_log` con campos: id, admin_user_id, accion, modulo, entidad_tipo, entidad_id, detalles, resultado, ip_address, user_agent, created_at
2. THE Sistema_Autenticacion SHALL configurar foreign key admin_user_id → admin_users(id) con ON DELETE SET NULL
3. THE Sistema_Autenticacion SHALL validar que resultado sea uno de: exito, error, denegado
4. THE Sistema_Autenticacion SHALL almacenar detalles en formato JSONB
5. THE Sistema_Autenticacion SHALL crear índices en admin_user_id, accion, modulo, created_at, entidad_tipo, entidad_id
6. THE Sistema_Autenticacion SHALL crear índice GIN en detalles (JSONB)
7. WHEN un usuario realice cualquier acción, THE Sistema_Autenticacion SHALL crear un registro de auditoría
8. THE Sistema_Autenticacion SHALL registrar acciones de: login, logout, crear, editar, eliminar, exportar, ver
9. THE Sistema_Autenticacion SHALL almacenar valores anteriores y nuevos en detalles para acciones de edición
10. THE Sistema_Autenticacion SHALL nunca permitir modificación o eliminación de registros de auditoría
11. THE Sistema_Autenticacion SHALL almacenar ip_address y user_agent en cada registro
12. THE Sistema_Autenticacion SHALL registrar intentos de login fallidos con resultado "error"
13. THE Sistema_Autenticacion SHALL registrar accesos denegados con resultado "denegado"

### Requirement 6: Endpoint de Login

**User Story:** Como usuario administrador, quiero poder iniciar sesión con username y password, para acceder al sistema.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL exponer endpoint POST /auth/login
2. WHEN se reciba un request de login, THE Sistema_Autenticacion SHALL validar que username y password estén presentes
3. WHEN se reciba un request de login, THE Sistema_Autenticacion SHALL buscar el usuario por username
4. IF el usuario no existe, THEN THE Sistema_Autenticacion SHALL retornar error 401 con mensaje genérico "Credenciales inválidas"
5. IF el usuario existe pero is_active es FALSE, THEN THE Sistema_Autenticacion SHALL retornar error 403 con mensaje "Cuenta desactivada"
6. IF el usuario está bloqueado (locked_until > NOW()), THEN THE Sistema_Autenticacion SHALL retornar error 403 con mensaje "Cuenta bloqueada temporalmente"
7. WHEN se valide la contraseña, THE Sistema_Autenticacion SHALL usar bcrypt.verify con el password_hash almacenado
8. IF la contraseña es incorrecta, THEN THE Sistema_Autenticacion SHALL incrementar failed_login_attempts
9. IF failed_login_attempts alcanza 5, THEN THE Sistema_Autenticacion SHALL establecer locked_until a NOW() + 15 minutos
10. IF la contraseña es correcta, THEN THE Sistema_Autenticacion SHALL resetear failed_login_attempts a 0
11. IF la contraseña es correcta, THEN THE Sistema_Autenticacion SHALL generar un access_token JWT con expiración de 30 minutos
12. IF la contraseña es correcta, THEN THE Sistema_Autenticacion SHALL generar un refresh_token JWT con expiración de 7 días
13. IF la contraseña es correcta, THEN THE Sistema_Autenticacion SHALL crear un registro en admin_sessions
14. IF la contraseña es correcta, THEN THE Sistema_Autenticacion SHALL actualizar last_login del usuario
15. IF la contraseña es correcta, THEN THE Sistema_Autenticacion SHALL crear registro de auditoría con accion "login" y resultado "exito"
16. IF el login falla, THEN THE Sistema_Autenticacion SHALL crear registro de auditoría con accion "login" y resultado "error"
17. THE Sistema_Autenticacion SHALL retornar access_token, refresh_token, user info (sin password_hash) y empresa info
18. THE Sistema_Autenticacion SHALL aplicar rate limiting de 5 intentos por minuto por IP

### Requirement 7: Endpoint de Logout

**User Story:** Como usuario administrador, quiero poder cerrar sesión, para invalidar mi token y proteger mi cuenta.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL exponer endpoint POST /auth/logout
2. WHEN se reciba un request de logout, THE Sistema_Autenticacion SHALL validar el access_token en el header Authorization
3. IF el token es válido, THEN THE Sistema_Autenticacion SHALL eliminar el registro correspondiente de admin_sessions
4. IF el token es válido, THEN THE Sistema_Autenticacion SHALL crear registro de auditoría con accion "logout" y resultado "exito"
5. THE Sistema_Autenticacion SHALL retornar status 200 con mensaje "Sesión cerrada exitosamente"
6. IF el token es inválido o expirado, THEN THE Sistema_Autenticacion SHALL retornar error 401

### Requirement 8: Endpoint de Refresh Token

**User Story:** Como usuario administrador, quiero poder renovar mi access token sin volver a hacer login, para mantener mi sesión activa.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL exponer endpoint POST /auth/refresh
2. WHEN se reciba un request de refresh, THE Sistema_Autenticacion SHALL validar el refresh_token en el body
3. IF el refresh_token no existe en admin_sessions, THEN THE Sistema_Autenticacion SHALL retornar error 401
4. IF el refresh_token está expirado (refresh_expires_at < NOW()), THEN THE Sistema_Autenticacion SHALL eliminar la sesión y retornar error 401
5. IF el usuario asociado tiene is_active FALSE, THEN THE Sistema_Autenticacion SHALL eliminar la sesión y retornar error 403
6. IF el refresh_token es válido, THEN THE Sistema_Autenticacion SHALL generar un nuevo access_token con expiración de 30 minutos
7. IF el refresh_token es válido, THEN THE Sistema_Autenticacion SHALL actualizar el campo token en admin_sessions
8. IF el refresh_token es válido, THEN THE Sistema_Autenticacion SHALL actualizar last_activity en admin_sessions
9. THE Sistema_Autenticacion SHALL retornar el nuevo access_token
10. THE Sistema_Autenticacion SHALL mantener el mismo refresh_token (no rotarlo)

### Requirement 9: Middleware de Autenticación

**User Story:** Como desarrollador del sistema, quiero un middleware que valide tokens JWT en todos los endpoints protegidos, para garantizar que solo usuarios autenticados accedan.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear un middleware de autenticación para FastAPI
2. WHEN se reciba un request a un endpoint protegido, THE Sistema_Autenticacion SHALL extraer el token del header Authorization
3. THE Sistema_Autenticacion SHALL validar que el header Authorization tenga formato "Bearer {token}"
4. IF el header Authorization no está presente, THEN THE Sistema_Autenticacion SHALL retornar error 401 con mensaje "Token no proporcionado"
5. IF el formato del header es inválido, THEN THE Sistema_Autenticacion SHALL retornar error 401 con mensaje "Formato de token inválido"
6. WHEN se extraiga el token, THE Sistema_Autenticacion SHALL verificar la firma JWT usando la SECRET_KEY
7. IF la firma es inválida, THEN THE Sistema_Autenticacion SHALL retornar error 401 con mensaje "Token inválido"
8. IF el token está expirado, THEN THE Sistema_Autenticacion SHALL retornar error 401 con mensaje "Token expirado"
9. WHEN el token sea válido, THE Sistema_Autenticacion SHALL extraer el user_id del payload
10. WHEN el token sea válido, THE Sistema_Autenticacion SHALL buscar el usuario en admin_users
11. IF el usuario no existe, THEN THE Sistema_Autenticacion SHALL retornar error 401 con mensaje "Usuario no encontrado"
12. IF el usuario tiene is_active FALSE, THEN THE Sistema_Autenticacion SHALL retornar error 403 con mensaje "Cuenta desactivada"
13. WHEN el usuario sea válido, THE Sistema_Autenticacion SHALL verificar que existe una sesión activa en admin_sessions
14. IF no existe sesión activa, THEN THE Sistema_Autenticacion SHALL retornar error 401 con mensaje "Sesión inválida"
15. WHEN la validación sea exitosa, THE Sistema_Autenticacion SHALL inyectar el objeto usuario en el request context
16. WHEN la validación sea exitosa, THE Sistema_Autenticacion SHALL actualizar last_activity en admin_sessions
17. THE Sistema_Autenticacion SHALL permitir que el endpoint acceda al usuario autenticado mediante dependency injection

### Requirement 10: Filtrado Automático por Empresa

**User Story:** Como desarrollador del sistema, quiero que las queries se filtren automáticamente por empresa según el rol del usuario, para garantizar aislamiento de datos.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear un mecanismo de filtrado automático para queries de base de datos
2. WHEN un usuario con rol "superadmin" realice una query, THE Sistema_Autenticacion SHALL retornar datos de todas las empresas
3. WHEN un usuario con rol "admin" realice una query, THE Sistema_Autenticacion SHALL filtrar por empresa_id del usuario
4. WHEN un usuario con rol "admin" realice una query, THE Sistema_Autenticacion SHALL agregar WHERE empresa_id = {user.empresa_id} automáticamente
5. THE Sistema_Autenticacion SHALL aplicar filtrado en queries de: printers, users, contadores_impresora, contadores_usuario, cierres_mensuales
6. WHEN un admin intente acceder a un recurso de otra empresa, THE Sistema_Autenticacion SHALL retornar error 403 con mensaje "Acceso denegado"
7. THE Sistema_Autenticacion SHALL crear un dependency de FastAPI para inyectar el filtro de empresa
8. THE Sistema_Autenticacion SHALL validar empresa_id en operaciones de CREATE para usuarios admin
9. WHEN un admin cree un recurso, THE Sistema_Autenticacion SHALL forzar empresa_id = user.empresa_id
10. THE Sistema_Autenticacion SHALL prevenir que un admin modifique empresa_id de recursos existentes

### Requirement 11: Endpoints CRUD de Empresas

**User Story:** Como superadmin, quiero gestionar empresas (crear, editar, listar, desactivar), para administrar los tenants del sistema.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL exponer endpoint GET /empresas (solo superadmin)
2. THE Sistema_Autenticacion SHALL exponer endpoint POST /empresas (solo superadmin)
3. THE Sistema_Autenticacion SHALL exponer endpoint GET /empresas/{id} (solo superadmin)
4. THE Sistema_Autenticacion SHALL exponer endpoint PUT /empresas/{id} (solo superadmin)
5. THE Sistema_Autenticacion SHALL exponer endpoint DELETE /empresas/{id} (solo superadmin, soft delete)
6. WHEN un usuario no-superadmin intente acceder a estos endpoints, THE Sistema_Autenticacion SHALL retornar error 403
7. WHEN se cree una empresa, THE Sistema_Autenticacion SHALL validar que razon_social sea única
8. WHEN se cree una empresa, THE Sistema_Autenticacion SHALL validar que nombre_comercial sea único y formato kebab-case
9. WHEN se cree una empresa, THE Sistema_Autenticacion SHALL validar formato de email si se proporciona
10. WHEN se cree una empresa, THE Sistema_Autenticacion SHALL validar formato de NIT si se proporciona
11. WHEN se elimine una empresa (soft delete), THE Sistema_Autenticacion SHALL establecer is_active = FALSE
12. WHEN se elimine una empresa, THE Sistema_Autenticacion SHALL validar que no tenga impresoras o usuarios activos
13. IF la empresa tiene recursos activos, THEN THE Sistema_Autenticacion SHALL retornar error 400 con mensaje descriptivo
14. THE Sistema_Autenticacion SHALL crear registro de auditoría para todas las operaciones CRUD de empresas
15. THE Sistema_Autenticacion SHALL retornar lista paginada en GET /empresas con parámetros page y page_size

### Requirement 12: Endpoints CRUD de Usuarios Admin

**User Story:** Como superadmin, quiero gestionar usuarios administradores (crear, editar, listar, desactivar), para controlar quién tiene acceso al sistema.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL exponer endpoint GET /admin-users (solo superadmin)
2. THE Sistema_Autenticacion SHALL exponer endpoint POST /admin-users (solo superadmin)
3. THE Sistema_Autenticacion SHALL exponer endpoint GET /admin-users/{id} (solo superadmin)
4. THE Sistema_Autenticacion SHALL exponer endpoint PUT /admin-users/{id} (solo superadmin)
5. THE Sistema_Autenticacion SHALL exponer endpoint DELETE /admin-users/{id} (solo superadmin, soft delete)
6. WHEN se cree un usuario admin, THE Sistema_Autenticacion SHALL validar que username sea único
7. WHEN se cree un usuario admin, THE Sistema_Autenticacion SHALL validar que email sea único
8. WHEN se cree un usuario admin, THE Sistema_Autenticacion SHALL validar la contraseña según Requirement 3
9. WHEN se cree un usuario admin, THE Sistema_Autenticacion SHALL hashear la contraseña con bcrypt
10. WHEN se cree un usuario con rol "admin", THE Sistema_Autenticacion SHALL validar que empresa_id esté presente
11. WHEN se cree un usuario con rol "superadmin", THE Sistema_Autenticacion SHALL validar que empresa_id sea NULL
12. WHEN se edite un usuario admin, THE Sistema_Autenticacion SHALL permitir cambiar: nombre_completo, email, rol, empresa_id, is_active
13. WHEN se edite un usuario admin, THE Sistema_Autenticacion SHALL NO permitir cambiar username
14. WHEN se cambie la contraseña, THE Sistema_Autenticacion SHALL validar y hashear la nueva contraseña
15. WHEN se desactive un usuario (soft delete), THE Sistema_Autenticacion SHALL establecer is_active = FALSE
16. WHEN se desactive un usuario, THE Sistema_Autenticacion SHALL invalidar todas sus sesiones activas
17. THE Sistema_Autenticacion SHALL crear registro de auditoría para todas las operaciones CRUD de usuarios admin
18. THE Sistema_Autenticacion SHALL nunca retornar password_hash en respuestas API

### Requirement 13: Página de Login (Frontend)

**User Story:** Como usuario administrador, quiero una página de login profesional, para acceder al sistema de forma segura.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear una página de login en /login
2. THE Sistema_Autenticacion SHALL mostrar un formulario con campos: username, password
3. THE Sistema_Autenticacion SHALL mostrar un botón "Iniciar Sesión"
4. THE Sistema_Autenticacion SHALL mostrar un checkbox "Recordarme" (opcional)
5. WHEN el usuario envíe el formulario, THE Sistema_Autenticacion SHALL validar que ambos campos estén completos
6. WHEN el usuario envíe el formulario, THE Sistema_Autenticacion SHALL llamar a POST /auth/login
7. IF el login es exitoso, THEN THE Sistema_Autenticacion SHALL almacenar access_token en localStorage
8. IF el login es exitoso, THEN THE Sistema_Autenticacion SHALL almacenar refresh_token en localStorage
9. IF el login es exitoso, THEN THE Sistema_Autenticacion SHALL almacenar user info en localStorage o Zustand store
10. IF el login es exitoso, THEN THE Sistema_Autenticacion SHALL redirigir al usuario a /dashboard
11. IF el login falla, THEN THE Sistema_Autenticacion SHALL mostrar mensaje de error descriptivo
12. IF la cuenta está bloqueada, THEN THE Sistema_Autenticacion SHALL mostrar mensaje con tiempo restante de bloqueo
13. THE Sistema_Autenticacion SHALL mostrar indicador de carga durante el request
14. THE Sistema_Autenticacion SHALL deshabilitar el botón durante el request para prevenir doble submit
15. THE Sistema_Autenticacion SHALL mostrar/ocultar contraseña con un ícono de ojo
16. THE Sistema_Autenticacion SHALL aplicar estilos del sistema de diseño existente (Industrial Clarity)
17. THE Sistema_Autenticacion SHALL ser responsive (mobile, tablet, desktop)
18. THE Sistema_Autenticacion SHALL mostrar logo de Ricoh Suite
19. THE Sistema_Autenticacion SHALL tener fondo con gradiente o imagen corporativa

### Requirement 14: Middleware de Autenticación (Frontend)

**User Story:** Como desarrollador del frontend, quiero un middleware que valide autenticación en rutas protegidas, para redirigir usuarios no autenticados al login.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear un componente ProtectedRoute para React Router
2. WHEN un usuario intente acceder a una ruta protegida, THE Sistema_Autenticacion SHALL verificar si existe access_token en localStorage
3. IF no existe access_token, THEN THE Sistema_Autenticacion SHALL redirigir a /login
4. IF existe access_token, THEN THE Sistema_Autenticacion SHALL verificar si está expirado
5. IF el access_token está expirado, THEN THE Sistema_Autenticacion SHALL intentar renovarlo con refresh_token
6. IF el refresh_token también está expirado, THEN THE Sistema_Autenticacion SHALL redirigir a /login
7. IF la renovación es exitosa, THEN THE Sistema_Autenticacion SHALL actualizar access_token en localStorage
8. IF la renovación es exitosa, THEN THE Sistema_Autenticacion SHALL permitir acceso a la ruta
9. THE Sistema_Autenticacion SHALL agregar access_token al header Authorization en todos los requests API
10. THE Sistema_Autenticacion SHALL interceptar respuestas 401 y redirigir a /login
11. THE Sistema_Autenticacion SHALL limpiar localStorage al recibir 401
12. THE Sistema_Autenticacion SHALL mostrar un loading spinner durante la validación de token

### Requirement 15: Módulo de Gestión de Empresas (Frontend)

**User Story:** Como superadmin, quiero un módulo para gestionar empresas desde el frontend, para administrar tenants fácilmente.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear una página /empresas (solo visible para superadmin)
2. THE Sistema_Autenticacion SHALL mostrar una tabla con todas las empresas
3. THE Sistema_Autenticacion SHALL mostrar columnas: razon_social, nombre_comercial, nit, contacto_nombre, is_active, acciones
4. THE Sistema_Autenticacion SHALL mostrar un botón "Nueva Empresa"
5. WHEN el usuario haga clic en "Nueva Empresa", THE Sistema_Autenticacion SHALL abrir un modal con formulario
6. THE Sistema_Autenticacion SHALL validar campos requeridos: razon_social, nombre_comercial
7. THE Sistema_Autenticacion SHALL validar formato de email si se proporciona
8. THE Sistema_Autenticacion SHALL validar formato de NIT si se proporciona
9. WHEN el usuario guarde, THE Sistema_Autenticacion SHALL llamar a POST /empresas
10. IF la creación es exitosa, THEN THE Sistema_Autenticacion SHALL cerrar el modal y recargar la tabla
11. THE Sistema_Autenticacion SHALL mostrar botones de acción: Editar, Desactivar
12. WHEN el usuario haga clic en Editar, THE Sistema_Autenticacion SHALL abrir modal con datos pre-cargados
13. WHEN el usuario haga clic en Desactivar, THE Sistema_Autenticacion SHALL mostrar confirmación
14. THE Sistema_Autenticacion SHALL aplicar paginación con 20 empresas por página
15. THE Sistema_Autenticacion SHALL permitir búsqueda por razon_social o nombre_comercial
16. THE Sistema_Autenticacion SHALL mostrar indicador visual para empresas inactivas

### Requirement 16: Módulo de Gestión de Usuarios Admin (Frontend)

**User Story:** Como superadmin, quiero un módulo para gestionar usuarios administradores desde el frontend, para controlar accesos al sistema.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear una página /admin-users (solo visible para superadmin)
2. THE Sistema_Autenticacion SHALL mostrar una tabla con todos los usuarios admin
3. THE Sistema_Autenticacion SHALL mostrar columnas: username, nombre_completo, email, rol, empresa, is_active, last_login, acciones
4. THE Sistema_Autenticacion SHALL mostrar un botón "Nuevo Usuario Admin"
5. WHEN el usuario haga clic en "Nuevo Usuario Admin", THE Sistema_Autenticacion SHALL abrir un modal con formulario
6. THE Sistema_Autenticacion SHALL validar campos requeridos: username, password, nombre_completo, email, rol
7. THE Sistema_Autenticacion SHALL validar formato de username (solo minúsculas, números, guiones)
8. THE Sistema_Autenticacion SHALL validar formato de email
9. THE Sistema_Autenticacion SHALL validar fortaleza de contraseña según Requirement 3
10. THE Sistema_Autenticacion SHALL mostrar indicador visual de fortaleza de contraseña
11. WHEN el rol sea "admin", THE Sistema_Autenticacion SHALL requerir selección de empresa
12. WHEN el rol sea "superadmin", THE Sistema_Autenticacion SHALL deshabilitar campo empresa
13. WHEN el usuario guarde, THE Sistema_Autenticacion SHALL llamar a POST /admin-users
14. THE Sistema_Autenticacion SHALL mostrar botones de acción: Editar, Desactivar, Cambiar Contraseña
15. WHEN el usuario haga clic en Cambiar Contraseña, THE Sistema_Autenticacion SHALL abrir modal específico
16. THE Sistema_Autenticacion SHALL aplicar paginación con 20 usuarios por página
17. THE Sistema_Autenticacion SHALL permitir búsqueda por username, nombre_completo o email
18. THE Sistema_Autenticacion SHALL mostrar badge con el rol del usuario
19. THE Sistema_Autenticacion SHALL mostrar indicador visual para usuarios inactivos

### Requirement 17: Filtrado de Datos en Frontend

**User Story:** Como usuario admin, quiero ver solo los datos de mi empresa en todos los módulos, para trabajar con información relevante.

#### Acceptance Criteria

1. WHEN un usuario admin acceda al módulo de Impresoras, THE Sistema_Autenticacion SHALL mostrar solo impresoras de su empresa
2. WHEN un usuario admin acceda al módulo de Usuarios de Impresoras, THE Sistema_Autenticacion SHALL mostrar solo usuarios de su empresa
3. WHEN un usuario admin acceda al módulo de Contadores, THE Sistema_Autenticacion SHALL mostrar solo contadores de impresoras de su empresa
4. WHEN un usuario admin acceda al módulo de Cierres Mensuales, THE Sistema_Autenticacion SHALL mostrar solo cierres de impresoras de su empresa
5. WHEN un superadmin acceda a cualquier módulo, THE Sistema_Autenticacion SHALL mostrar datos de todas las empresas
6. WHEN un superadmin acceda a cualquier módulo, THE Sistema_Autenticacion SHALL mostrar un filtro dropdown para seleccionar empresa
7. THE Sistema_Autenticacion SHALL aplicar el filtro de empresa automáticamente en todas las queries API
8. THE Sistema_Autenticacion SHALL mostrar el nombre de la empresa del usuario en el header/navbar
9. WHEN un admin intente crear un usuario de impresora, THE Sistema_Autenticacion SHALL pre-seleccionar su empresa y deshabilitar el campo
10. WHEN un superadmin intente crear un usuario de impresora, THE Sistema_Autenticacion SHALL permitir seleccionar cualquier empresa

### Requirement 18: Navbar con Información de Usuario

**User Story:** Como usuario autenticado, quiero ver mi información en el navbar, para saber con qué cuenta estoy logueado.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL mostrar el nombre completo del usuario en el navbar
2. THE Sistema_Autenticacion SHALL mostrar el rol del usuario con un badge
3. THE Sistema_Autenticacion SHALL mostrar el nombre de la empresa (si aplica)
4. THE Sistema_Autenticacion SHALL mostrar un dropdown al hacer clic en el nombre del usuario
5. THE Sistema_Autenticacion SHALL mostrar opciones en el dropdown: Mi Perfil, Cerrar Sesión
6. WHEN el usuario haga clic en "Cerrar Sesión", THE Sistema_Autenticacion SHALL llamar a POST /auth/logout
7. WHEN el logout sea exitoso, THE Sistema_Autenticacion SHALL limpiar localStorage
8. WHEN el logout sea exitoso, THE Sistema_Autenticacion SHALL redirigir a /login
9. THE Sistema_Autenticacion SHALL mostrar un avatar con las iniciales del usuario
10. THE Sistema_Autenticacion SHALL aplicar color diferente al badge según el rol (superadmin: rojo, admin: azul)

### Requirement 19: Seguridad - Rate Limiting

**User Story:** Como administrador de seguridad, quiero rate limiting en endpoints sensibles, para prevenir ataques de fuerza bruta.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL implementar rate limiting en POST /auth/login
2. THE Sistema_Autenticacion SHALL limitar a 5 intentos de login por minuto por IP
3. IF se excede el límite, THEN THE Sistema_Autenticacion SHALL retornar error 429 con mensaje "Demasiados intentos, intente más tarde"
4. THE Sistema_Autenticacion SHALL implementar rate limiting en POST /auth/refresh
5. THE Sistema_Autenticacion SHALL limitar a 10 intentos de refresh por minuto por usuario
6. THE Sistema_Autenticacion SHALL usar Redis o memoria para almacenar contadores de rate limiting
7. THE Sistema_Autenticacion SHALL resetear contadores después del período de tiempo especificado
8. THE Sistema_Autenticacion SHALL incluir headers de rate limiting en las respuestas: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset

### Requirement 20: Seguridad - HTTPS y CORS

**User Story:** Como administrador de seguridad, quiero que el sistema use HTTPS en producción y tenga CORS configurado correctamente, para proteger datos en tránsito.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL requerir HTTPS en ambiente de producción
2. THE Sistema_Autenticacion SHALL redirigir HTTP a HTTPS en producción
3. THE Sistema_Autenticacion SHALL configurar CORS para permitir solo orígenes autorizados
4. THE Sistema_Autenticacion SHALL validar que el origen del request esté en la lista de orígenes permitidos
5. THE Sistema_Autenticacion SHALL permitir métodos: GET, POST, PUT, DELETE, OPTIONS
6. THE Sistema_Autenticacion SHALL permitir headers: Authorization, Content-Type
7. THE Sistema_Autenticacion SHALL configurar Access-Control-Allow-Credentials: true
8. THE Sistema_Autenticacion SHALL configurar Access-Control-Max-Age: 3600
9. THE Sistema_Autenticacion SHALL agregar header Strict-Transport-Security en producción
10. THE Sistema_Autenticacion SHALL agregar header X-Content-Type-Options: nosniff
11. THE Sistema_Autenticacion SHALL agregar header X-Frame-Options: DENY
12. THE Sistema_Autenticacion SHALL agregar header X-XSS-Protection: 1; mode=block

### Requirement 21: Migración de Datos Segura

**User Story:** Como DBA, quiero que la migración de datos sea segura y reversible, para minimizar riesgo de pérdida de datos.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear un script de migración SQL con transacciones
2. WHEN se ejecute la migración, THE Sistema_Autenticacion SHALL crear un backup completo de la base de datos
3. THE Sistema_Autenticacion SHALL ejecutar toda la migración dentro de una transacción
4. IF ocurre un error durante la migración, THEN THE Sistema_Autenticacion SHALL hacer ROLLBACK completo
5. THE Sistema_Autenticacion SHALL validar integridad de datos después de cada paso de migración
6. THE Sistema_Autenticacion SHALL crear un script de rollback para revertir cambios si es necesario
7. THE Sistema_Autenticacion SHALL registrar logs detallados de cada paso de la migración
8. THE Sistema_Autenticacion SHALL validar que no haya datos huérfanos después de la migración
9. THE Sistema_Autenticacion SHALL validar que todos los foreign keys estén correctamente asignados
10. THE Sistema_Autenticacion SHALL crear índices después de insertar datos para mejor rendimiento

### Requirement 22: Limpieza Automática de Sesiones Expiradas

**User Story:** Como administrador del sistema, quiero que las sesiones expiradas se eliminen automáticamente, para mantener la base de datos limpia.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear un job programado para limpiar sesiones expiradas
2. THE Sistema_Autenticacion SHALL ejecutar el job cada 1 hora
3. WHEN se ejecute el job, THE Sistema_Autenticacion SHALL eliminar registros de admin_sessions donde expires_at < NOW()
4. THE Sistema_Autenticacion SHALL registrar en logs el número de sesiones eliminadas
5. THE Sistema_Autenticacion SHALL usar un índice para optimizar la query de limpieza
6. THE Sistema_Autenticacion SHALL ejecutar la limpieza en una transacción separada
7. IF el job falla, THEN THE Sistema_Autenticacion SHALL registrar el error en logs pero no afectar el sistema

### Requirement 23: Endpoint de Información de Usuario Actual

**User Story:** Como usuario autenticado, quiero obtener mi información actual, para mostrarla en el frontend y validar permisos.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL exponer endpoint GET /auth/me
2. WHEN se reciba un request, THE Sistema_Autenticacion SHALL validar el access_token
3. IF el token es válido, THEN THE Sistema_Autenticacion SHALL retornar información del usuario: id, username, nombre_completo, email, rol, empresa_id, empresa (objeto completo)
4. THE Sistema_Autenticacion SHALL nunca retornar password_hash
5. THE Sistema_Autenticacion SHALL retornar información de la empresa si el usuario tiene empresa_id
6. THE Sistema_Autenticacion SHALL retornar permisos del usuario (módulos a los que tiene acceso)
7. IF el token es inválido o expirado, THEN THE Sistema_Autenticacion SHALL retornar error 401

### Requirement 24: Validación de Permisos por Rol

**User Story:** Como desarrollador del sistema, quiero validar permisos según el rol del usuario, para controlar acceso a funcionalidades.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL crear un decorator @require_role para endpoints
2. WHEN se use @require_role("superadmin"), THE Sistema_Autenticacion SHALL validar que el usuario tenga rol superadmin
3. IF el usuario no tiene el rol requerido, THEN THE Sistema_Autenticacion SHALL retornar error 403 con mensaje "Permisos insuficientes"
4. THE Sistema_Autenticacion SHALL permitir múltiples roles: @require_role(["superadmin", "admin"])
5. THE Sistema_Autenticacion SHALL validar permisos antes de ejecutar la lógica del endpoint
6. THE Sistema_Autenticacion SHALL crear registro de auditoría cuando se deniegue acceso
7. THE Sistema_Autenticacion SHALL aplicar @require_role a todos los endpoints de gestión de empresas y usuarios admin

### Requirement 25: Configuración de JWT

**User Story:** Como administrador de seguridad, quiero que los JWT estén configurados correctamente, para garantizar seguridad de tokens.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL usar algoritmo HS256 para firmar JWT
2. THE Sistema_Autenticacion SHALL usar una SECRET_KEY de al menos 32 caracteres
3. THE Sistema_Autenticacion SHALL almacenar SECRET_KEY en variable de entorno
4. THE Sistema_Autenticacion SHALL nunca hardcodear SECRET_KEY en el código
5. THE Sistema_Autenticacion SHALL incluir en el payload del JWT: user_id, username, rol, empresa_id, exp, iat
6. THE Sistema_Autenticacion SHALL establecer exp (expiration) en 30 minutos para access_token
7. THE Sistema_Autenticacion SHALL establecer exp en 7 días para refresh_token
8. THE Sistema_Autenticacion SHALL incluir iat (issued at) con timestamp de creación
9. THE Sistema_Autenticacion SHALL validar que exp sea mayor que iat
10. THE Sistema_Autenticacion SHALL usar una SECRET_KEY diferente para refresh_tokens (opcional pero recomendado)

### Requirement 26: Endpoint de Cambio de Contraseña

**User Story:** Como usuario administrador, quiero poder cambiar mi contraseña, para mantener mi cuenta segura.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL exponer endpoint POST /auth/change-password
2. WHEN se reciba un request, THE Sistema_Autenticacion SHALL validar el access_token
3. THE Sistema_Autenticacion SHALL requerir campos: current_password, new_password
4. WHEN se reciba el request, THE Sistema_Autenticacion SHALL validar que current_password sea correcta
5. IF current_password es incorrecta, THEN THE Sistema_Autenticacion SHALL retornar error 400 con mensaje "Contraseña actual incorrecta"
6. THE Sistema_Autenticacion SHALL validar que new_password cumpla con los requisitos de Requirement 3
7. THE Sistema_Autenticacion SHALL validar que new_password sea diferente de current_password
8. WHEN la validación sea exitosa, THE Sistema_Autenticacion SHALL hashear new_password con bcrypt
9. WHEN la validación sea exitosa, THE Sistema_Autenticacion SHALL actualizar password_hash en admin_users
10. WHEN la validación sea exitosa, THE Sistema_Autenticacion SHALL invalidar todas las sesiones activas del usuario excepto la actual
11. WHEN la validación sea exitosa, THE Sistema_Autenticacion SHALL crear registro de auditoría con accion "cambio_password"
12. THE Sistema_Autenticacion SHALL retornar status 200 con mensaje "Contraseña actualizada exitosamente"

### Requirement 27: Inicialización del Sistema

**User Story:** Como administrador del sistema, quiero que se cree automáticamente un superadmin inicial, para poder acceder al sistema por primera vez.

#### Acceptance Criteria

1. WHEN se ejecute la migración inicial, THE Sistema_Autenticacion SHALL verificar si existe algún usuario en admin_users
2. IF no existe ningún usuario, THEN THE Sistema_Autenticacion SHALL crear un superadmin con username "superadmin"
3. THE Sistema_Autenticacion SHALL generar una contraseña temporal aleatoria de 16 caracteres
4. THE Sistema_Autenticacion SHALL imprimir la contraseña temporal en los logs del sistema
5. THE Sistema_Autenticacion SHALL hashear la contraseña temporal con bcrypt
6. THE Sistema_Autenticacion SHALL crear el superadmin con: username="superadmin", nombre_completo="Super Administrador", email="admin@ricoh-suite.local", rol="superadmin", empresa_id=NULL, is_active=TRUE
7. THE Sistema_Autenticacion SHALL crear una empresa por defecto "Sin Asignar" para recursos sin empresa
8. THE Sistema_Autenticacion SHALL registrar en logs la creación del superadmin inicial
9. THE Sistema_Autenticacion SHALL recomendar cambiar la contraseña en el primer login

### Requirement 28: Documentación de API

**User Story:** Como desarrollador frontend, quiero documentación clara de los endpoints de autenticación, para integrar correctamente el sistema.

#### Acceptance Criteria

1. THE Sistema_Autenticacion SHALL documentar todos los endpoints en OpenAPI/Swagger
2. THE Sistema_Autenticacion SHALL incluir ejemplos de request y response para cada endpoint
3. THE Sistema_Autenticacion SHALL documentar todos los códigos de error posibles
4. THE Sistema_Autenticacion SHALL documentar el formato del JWT y su payload
5. THE Sistema_Autenticacion SHALL documentar el flujo completo de autenticación
6. THE Sistema_Autenticacion SHALL documentar cómo usar el middleware de autenticación
7. THE Sistema_Autenticacion SHALL documentar los roles y sus permisos
8. THE Sistema_Autenticacion SHALL incluir ejemplos de uso con curl y JavaScript
9. THE Sistema_Autenticacion SHALL estar disponible en /docs (FastAPI Swagger UI)
10. THE Sistema_Autenticacion SHALL incluir un diagrama de flujo de autenticación

---

## Iteration and Feedback

Este documento de requirements está listo para revisión. Por favor, revisa cada requisito y proporciona feedback sobre:

1. ¿Hay requisitos faltantes o incompletos?
2. ¿Hay requisitos ambiguos que necesitan clarificación?
3. ¿Hay conflictos entre requisitos?
4. ¿Las prioridades están correctas?
5. ¿Hay consideraciones de seguridad adicionales?

Una vez aprobado, procederemos a crear el documento de diseño técnico.

---

**Documento creado:** {{fecha}}  
**Feature:** sistema-autenticacion-empresas  
**Workflow:** requirements-first  
**Estado:** Pendiente de revisión
