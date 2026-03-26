# Manual Testing Checklist - Sistema de Autenticación

## 📋 Checklist Completo de Testing Manual

### ✅ Autenticación

#### Login
- [ ] Login con credenciales válidas (superadmin)
- [ ] Login con credenciales válidas (admin)
- [ ] Login con username incorrecto
- [ ] Login con password incorrecta
- [ ] Login con cuenta desactivada
- [ ] Login con cuenta bloqueada (5 intentos fallidos)
- [ ] Verificar que después de 5 intentos fallidos, cuenta se bloquea por 15 minutos
- [ ] Verificar que después de login exitoso, failed_login_attempts se resetea
- [ ] Verificar que tokens se almacenan correctamente
- [ ] Verificar que user info se retorna sin password_hash

#### Logout
- [ ] Logout con token válido
- [ ] Verificar que sesión se invalida en base de datos
- [ ] Verificar que token ya no funciona después de logout

#### Renovación de Token
- [ ] Renovar token con refresh_token válido
- [ ] Renovar token con refresh_token expirado
- [ ] Renovar token con refresh_token inválido
- [ ] Verificar que nuevo access_token funciona correctamente
- [ ] Verificar que renovación automática funciona (antes de 30 min)

#### Cambio de Contraseña
- [ ] Cambiar contraseña con contraseña actual correcta
- [ ] Cambiar contraseña con contraseña actual incorrecta
- [ ] Cambiar contraseña con nueva contraseña débil
- [ ] Verificar que nueva contraseña funciona para login
- [ ] Verificar que contraseña antigua ya no funciona

#### Validación de Contraseña
- [ ] Contraseña < 8 caracteres rechazada
- [ ] Contraseña sin mayúscula rechazada
- [ ] Contraseña sin minúscula rechazada
- [ ] Contraseña sin número rechazada
- [ ] Contraseña sin carácter especial rechazada
- [ ] Contraseña válida aceptada

---

### ✅ Gestión de Empresas (Solo Superadmin)

#### Listar Empresas
- [ ] GET /empresas como superadmin retorna lista
- [ ] GET /empresas como admin retorna 403
- [ ] Paginación funciona correctamente (page, page_size)
- [ ] Búsqueda por razon_social funciona
- [ ] Búsqueda por nombre_comercial funciona
- [ ] Empresas inactivas se muestran con indicador visual

#### Crear Empresa
- [ ] Crear empresa con datos válidos
- [ ] Crear empresa con razon_social duplicada (error 409)
- [ ] Crear empresa con nombre_comercial duplicado (error 409)
- [ ] Crear empresa con nit duplicado (error 409)
- [ ] Crear empresa con email inválido (error 422)
- [ ] Crear empresa con nombre_comercial no kebab-case (error 422)
- [ ] Verificar que empresa se crea con is_active=True por defecto

#### Editar Empresa
- [ ] Editar empresa como superadmin
- [ ] Editar razon_social
- [ ] Editar nombre_comercial
- [ ] Editar datos de contacto
- [ ] Intentar editar con razon_social duplicada (error 409)
- [ ] Intentar editar con nombre_comercial duplicado (error 409)

#### Desactivar Empresa
- [ ] Desactivar empresa sin recursos activos
- [ ] Intentar desactivar empresa con printers activos (error 400)
- [ ] Intentar desactivar empresa con users activos (error 400)
- [ ] Intentar desactivar empresa con admin_users activos (error 400)
- [ ] Verificar que empresa se marca como is_active=False

---

### ✅ Gestión de Usuarios Admin (Solo Superadmin)

#### Listar Usuarios Admin
- [ ] GET /admin-users como superadmin retorna lista
- [ ] GET /admin-users como admin retorna 403
- [ ] Paginación funciona correctamente
- [ ] Búsqueda por username funciona
- [ ] Búsqueda por nombre_completo funciona
- [ ] Búsqueda por email funciona
- [ ] Filtro por rol funciona
- [ ] Filtro por empresa funciona
- [ ] Usuarios inactivos se muestran con indicador visual
- [ ] Badge de rol muestra color correcto (superadmin=rojo, admin=azul)

#### Crear Usuario Admin
- [ ] Crear superadmin sin empresa_id
- [ ] Crear admin con empresa_id
- [ ] Crear usuario con username duplicado (error 409)
- [ ] Crear usuario con email duplicado (error 409)
- [ ] Crear usuario con username inválido (error 422)
- [ ] Crear usuario con email inválido (error 422)
- [ ] Crear usuario con contraseña débil (error 422)
- [ ] Crear superadmin con empresa_id (error 400)
- [ ] Crear admin sin empresa_id (error 400)
- [ ] Verificar que password_hash se genera correctamente

#### Editar Usuario Admin
- [ ] Editar nombre_completo
- [ ] Editar email
- [ ] Editar rol
- [ ] Cambiar empresa_id de admin
- [ ] Intentar cambiar username (debe fallar o no permitirse)
- [ ] Intentar editar con email duplicado (error 409)
- [ ] Cambiar rol de admin a superadmin (debe quitar empresa_id)
- [ ] Cambiar rol de superadmin a admin (debe requerir empresa_id)

#### Desactivar Usuario Admin
- [ ] Desactivar usuario admin
- [ ] Verificar que is_active=False
- [ ] Verificar que todas las sesiones activas se invalidan
- [ ] Intentar login con usuario desactivado (error 403)

---

### ✅ Multi-Tenancy y Filtrado

#### Filtrado Automático - Printers
- [ ] Superadmin ve todas las impresoras de todas las empresas
- [ ] Admin solo ve impresoras de su empresa
- [ ] Admin no puede ver impresoras de otra empresa
- [ ] Admin crea impresora y se asigna automáticamente su empresa_id
- [ ] Admin intenta crear impresora con empresa_id diferente (se fuerza su empresa_id)
- [ ] Admin intenta editar impresora de otra empresa (error 403)
- [ ] Admin intenta eliminar impresora de otra empresa (error 403)

#### Filtrado Automático - Users
- [ ] Superadmin ve todos los usuarios de todas las empresas
- [ ] Admin solo ve usuarios de su empresa
- [ ] Admin no puede ver usuarios de otra empresa
- [ ] Admin crea usuario y se asigna automáticamente su empresa_id
- [ ] Admin intenta editar usuario de otra empresa (error 403)

#### Filtrado Automático - Contadores
- [ ] Superadmin ve contadores de todas las impresoras
- [ ] Admin solo ve contadores de impresoras de su empresa
- [ ] Admin no puede ver contadores de impresoras de otra empresa

#### Filtrado Automático - Cierres Mensuales
- [ ] Superadmin ve cierres de todas las empresas
- [ ] Admin solo ve cierres de su empresa
- [ ] Admin no puede ver cierres de otra empresa

---

### ✅ Seguridad

#### Rate Limiting
- [ ] 5 requests a /auth/login en 1 minuto son permitidos
- [ ] 6to request a /auth/login en 1 minuto retorna 429
- [ ] Headers X-RateLimit-* están presentes en respuestas
- [ ] Después de 1 minuto, contador se resetea
- [ ] Diferentes IPs tienen contadores independientes

#### Headers de Seguridad
- [ ] Header Strict-Transport-Security presente en producción
- [ ] Header X-Content-Type-Options: nosniff presente
- [ ] Header X-Frame-Options: DENY presente
- [ ] Header X-XSS-Protection: 1; mode=block presente

#### CORS
- [ ] Requests desde origen permitido son aceptados
- [ ] Requests desde origen no permitido son rechazados
- [ ] Preflight OPTIONS requests funcionan correctamente
- [ ] Credentials están permitidos

#### Tokens JWT
- [ ] Token con firma inválida es rechazado
- [ ] Token expirado es rechazado
- [ ] Token válido es aceptado
- [ ] Payload incluye user_id, username, rol, empresa_id
- [ ] Access token expira en 30 minutos
- [ ] Refresh token expira en 7 días

#### Contraseñas
- [ ] Contraseñas se hashean con bcrypt
- [ ] Password_hash nunca se retorna en respuestas API
- [ ] Password_hash nunca se loggea completo en logs
- [ ] Contraseñas no se loggean en logs

---

### ✅ Auditoría

#### Registro de Acciones
- [ ] Login exitoso se registra en audit_log
- [ ] Login fallido se registra en audit_log
- [ ] Logout se registra en audit_log
- [ ] Creación de empresa se registra en audit_log
- [ ] Edición de empresa se registra en audit_log
- [ ] Eliminación de empresa se registra en audit_log
- [ ] Creación de usuario admin se registra en audit_log
- [ ] Edición de usuario admin se registra en audit_log
- [ ] Eliminación de usuario admin se registra en audit_log
- [ ] Cambio de contraseña se registra en audit_log
- [ ] Acceso denegado se registra en audit_log

#### Contenido de Audit Log
- [ ] Registro incluye admin_user_id
- [ ] Registro incluye accion
- [ ] Registro incluye modulo
- [ ] Registro incluye entidad_tipo y entidad_id
- [ ] Registro incluye detalles en JSON
- [ ] Registro incluye resultado (exito, error, denegado)
- [ ] Registro incluye ip_address
- [ ] Registro incluye user_agent
- [ ] Registro incluye created_at

---

### ✅ Job de Limpieza de Sesiones

- [ ] Job se ejecuta cada 1 hora
- [ ] Job elimina sesiones con expires_at < NOW()
- [ ] Job no elimina sesiones activas
- [ ] Job registra en logs el número de sesiones eliminadas
- [ ] Job maneja errores sin afectar el sistema principal

---

### ✅ Documentación API (Swagger)

- [ ] Swagger UI accesible en /docs
- [ ] Todos los endpoints están documentados
- [ ] Ejemplos de request están presentes
- [ ] Ejemplos de response están presentes
- [ ] Códigos de error están documentados
- [ ] Schemas están documentados
- [ ] Autenticación está configurada (botón Authorize)

---

### ✅ Compatibilidad de Navegadores

#### Chrome
- [ ] Login funciona
- [ ] Navegación funciona
- [ ] Formularios funcionan
- [ ] Tokens se almacenan en localStorage

#### Firefox
- [ ] Login funciona
- [ ] Navegación funciona
- [ ] Formularios funcionan
- [ ] Tokens se almacenan en localStorage

#### Safari
- [ ] Login funciona
- [ ] Navegación funciona
- [ ] Formularios funcionan
- [ ] Tokens se almacenan en localStorage

#### Edge
- [ ] Login funciona
- [ ] Navegación funciona
- [ ] Formularios funcionan
- [ ] Tokens se almacenan en localStorage

---

### ✅ Responsive Design

#### Desktop (1920x1080)
- [ ] Layout se ve correctamente
- [ ] Tablas son legibles
- [ ] Formularios son usables
- [ ] Navegación funciona

#### Tablet (768x1024)
- [ ] Layout se adapta correctamente
- [ ] Tablas son legibles (scroll horizontal si necesario)
- [ ] Formularios son usables
- [ ] Navegación funciona (hamburger menu si aplica)

#### Mobile (375x667)
- [ ] Layout se adapta correctamente
- [ ] Tablas son legibles (scroll horizontal)
- [ ] Formularios son usables
- [ ] Navegación funciona (hamburger menu)

---

## 📊 Resumen de Testing

### Estadísticas
- **Total de casos de prueba**: 150+
- **Categorías**: 10
- **Tiempo estimado**: 8-12 horas

### Prioridad
1. **Alta**: Autenticación, Multi-Tenancy, Seguridad
2. **Media**: Gestión de Empresas, Gestión de Usuarios Admin, Auditoría
3. **Baja**: Compatibilidad de Navegadores, Responsive Design

### Reporte de Bugs
Documentar cualquier bug encontrado con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado
- Comportamiento actual
- Screenshots (si aplica)
- Navegador y versión
- Prioridad (crítico, alto, medio, bajo)

---

**Última actualización**: 20 de Marzo de 2026
