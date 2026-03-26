# Estructura Actual de la Base de Datos - Ricoh Suite

**Fecha:** 18 de marzo de 2026  
**Base de datos:** ricoh_fleet  
**Motor:** PostgreSQL 16

---

## 📊 Resumen de Tablas

| Tabla | Registros | Propósito |
|-------|-----------|-----------|
| `users` | - | Usuarios de impresoras (para aprovisionamiento) |
| `printers` | - | Impresoras registradas en el sistema |
| `user_printer_assignments` | - | Asignaciones de usuarios a impresoras |
| `contadores_impresora` | - | Contadores totales por impresora |
| `contadores_usuario` | - | Contadores individuales por usuario |
| `cierres_mensuales` | - | Cierres de contadores (snapshots) |
| `cierres_mensuales_usuarios` | - | Detalle de usuarios en cada cierre |
| `backup_cierres_mensuales_20260316` | - | Backup de cierres (tabla temporal) |

---

## 📋 Detalle de Tablas

### 1. `users` - Usuarios de Impresoras (21 columnas)

**Propósito:** Almacena usuarios que se aprovisionan en las impresoras Ricoh (NO son usuarios del sistema de login)

| Columna | Tipo | Nullable | Descripción |
|---------|------|----------|-------------|
| `id` | integer | NO | ID único del usuario |
| `name` | varchar(100) | NO | Nombre del usuario |
| `codigo_de_usuario` | varchar(8) | NO | Código de usuario (PIN) para la impresora |
| `network_username` | varchar(255) | NO | Usuario de red para autenticación |
| `network_password_encrypted` | text | NO | Contraseña encriptada |
| `smb_server` | varchar(255) | NO | Servidor SMB |
| `smb_port` | integer | NO | Puerto SMB |
| `smb_path` | varchar(500) | NO | Ruta SMB completa |
| `func_copier` | boolean | NO | Función copiadora habilitada |
| `func_copier_color` | boolean | NO | Función copiadora color habilitada |
| `func_printer` | boolean | NO | Función impresora habilitada |
| `func_printer_color` | boolean | NO | Función impresora color habilitada |
| `func_document_server` | boolean | NO | Función document server habilitada |
| `func_fax` | boolean | NO | Función fax habilitada |
| `func_scanner` | boolean | NO | Función escáner habilitada |
| `func_browser` | boolean | NO | Función navegador habilitada |
| `empresa` | varchar(255) | YES | Empresa a la que pertenece el usuario |
| `centro_costos` | varchar(100) | YES | Centro de costos |
| `is_active` | boolean | YES | Usuario activo/inactivo |
| `created_at` | timestamp | YES | Fecha de creación |
| `updated_at` | timestamp | YES | Fecha de última actualización |

**Índices:**
- `users_pkey` (PRIMARY KEY) en `id`
- `ix_users_name` en `name`
- `ix_users_codigo_de_usuario` en `codigo_de_usuario`
- `ix_users_empresa` en `empresa`
- `ix_users_centro_costos` en `centro_costos`

---

### 2. `printers` - Impresoras (24 columnas)

**Propósito:** Almacena información de las impresoras Ricoh registradas

| Columna | Tipo | Nullable | Descripción |
|---------|------|----------|-------------|
| `id` | integer | NO | ID único de la impresora |
| `hostname` | varchar(255) | NO | Nombre del host |
| `ip_address` | varchar(45) | NO | Dirección IP (UNIQUE) |
| `location` | varchar(255) | YES | Ubicación física |
| `status` | enum | YES | Estado: online, offline, error, maintenance |
| `detected_model` | varchar(100) | YES | Modelo detectado |
| `serial_number` | varchar(100) | YES | Número de serie |
| `has_color` | boolean | YES | Tiene capacidad de color |
| `has_scanner` | boolean | YES | Tiene escáner |
| `has_fax` | boolean | YES | Tiene fax |
| `toner_cyan` | integer | YES | Nivel de tóner cian (0-100) |
| `toner_magenta` | integer | YES | Nivel de tóner magenta (0-100) |
| `toner_yellow` | integer | YES | Nivel de tóner amarillo (0-100) |
| `toner_black` | integer | YES | Nivel de tóner negro (0-100) |
| `last_seen` | timestamp | YES | Última vez vista |
| `notes` | text | YES | Notas adicionales |
| `created_at` | timestamp | YES | Fecha de creación |
| `updated_at` | timestamp | YES | Fecha de última actualización |
| `empresa` | varchar(255) | YES | **Empresa a la que pertenece** |
| `tiene_contador_usuario` | boolean | NO | Tiene getUserCounter.cgi |
| `usar_contador_ecologico` | boolean | NO | Usar getEcoCounter.cgi |
| `formato_contadores` | varchar(50) | YES | Formato: estandar, simplificado, ecologico |
| `capabilities_json` | jsonb | YES | Capacidades en formato JSON |
| `inconsistency_count` | integer | YES | Contador de inconsistencias |

**Índices:**
- `printers_pkey` (PRIMARY KEY) en `id`
- `printers_ip_address_key` (UNIQUE) en `ip_address`
- `ix_printers_hostname` en `hostname`
- `ix_printers_empresa` en `empresa` ⭐

---

### 3. `user_printer_assignments` - Asignaciones (15 columnas)

**Propósito:** Relación muchos-a-muchos entre usuarios e impresoras

| Columna | Tipo | Nullable | Descripción |
|---------|------|----------|-------------|
| `id` | integer | NO | ID único de la asignación |
| `user_id` | integer | NO | FK a users.id |
| `printer_id` | integer | NO | FK a printers.id |
| `provisioned_at` | timestamp | YES | Fecha de aprovisionamiento |
| `is_active` | boolean | YES | Asignación activa |
| `notes` | text | YES | Notas |
| `entry_index` | varchar(10) | YES | ID físico en la impresora |
| `func_copier` | boolean | YES | Función copiadora en esta impresora |
| `func_copier_color` | boolean | NO | Función copiadora color en esta impresora |
| `func_printer` | boolean | YES | Función impresora en esta impresora |
| `func_printer_color` | boolean | NO | Función impresora color en esta impresora |
| `func_document_server` | boolean | YES | Función document server en esta impresora |
| `func_fax` | boolean | YES | Función fax en esta impresora |
| `func_scanner` | boolean | YES | Función escáner en esta impresora |
| `func_browser` | boolean | YES | Función navegador en esta impresora |

---

### 4. `contadores_impresora` - Contadores Totales (21 columnas)

**Propósito:** Almacena lecturas de contadores totales por impresora

| Columna | Tipo | Nullable | Descripción |
|---------|------|----------|-------------|
| `id` | integer | NO | ID único |
| `printer_id` | integer | NO | FK a printers.id |
| `total` | integer | NO | Contador total |
| `copiadora_bn` | integer | NO | Copiadora B/N |
| `copiadora_color` | integer | NO | Copiadora color |
| `copiadora_color_personalizado` | integer | NO | Copiadora color personalizado |
| `copiadora_dos_colores` | integer | NO | Copiadora dos colores |
| `impresora_bn` | integer | NO | Impresora B/N |
| `impresora_color` | integer | NO | Impresora color |
| `impresora_color_personalizado` | integer | NO | Impresora color personalizado |
| `impresora_dos_colores` | integer | NO | Impresora dos colores |
| `fax_bn` | integer | NO | Fax B/N |
| `enviar_total_bn` | integer | NO | Enviar total B/N |
| `enviar_total_color` | integer | NO | Enviar total color |
| `transmision_fax_total` | integer | NO | Transmisión fax total |
| `envio_escaner_bn` | integer | NO | Envío escáner B/N |
| `envio_escaner_color` | integer | NO | Envío escáner color |
| `otras_a3_dlt` | integer | NO | Otras A3 DLT |
| `otras_duplex` | integer | NO | Otras dúplex |
| `fecha_lectura` | timestamp | NO | Fecha de lectura |
| `created_at` | timestamp | YES | Fecha de creación |

---

### 5. `contadores_usuario` - Contadores por Usuario (31 columnas)

**Propósito:** Almacena lecturas de contadores individuales por usuario

| Columna | Tipo | Nullable | Descripción |
|---------|------|----------|-------------|
| `id` | integer | NO | ID único |
| `printer_id` | integer | NO | FK a printers.id |
| `codigo_usuario` | varchar(8) | NO | Código del usuario |
| `nombre_usuario` | varchar(100) | NO | Nombre del usuario |
| `total_paginas` | integer | NO | Total de páginas |
| `total_bn` | integer | NO | Total B/N |
| `total_color` | integer | NO | Total color |
| `copiadora_bn` | integer | NO | Copiadora B/N |
| `copiadora_mono_color` | integer | NO | Copiadora mono color |
| `copiadora_dos_colores` | integer | NO | Copiadora dos colores |
| `copiadora_todo_color` | integer | NO | Copiadora todo color |
| `copiadora_hojas_2_caras` | integer | NO | Copiadora hojas 2 caras |
| `copiadora_paginas_combinadas` | integer | NO | Copiadora páginas combinadas |
| `impresora_bn` | integer | NO | Impresora B/N |
| `impresora_mono_color` | integer | NO | Impresora mono color |
| `impresora_dos_colores` | integer | NO | Impresora dos colores |
| `impresora_color` | integer | NO | Impresora color |
| `impresora_hojas_2_caras` | integer | NO | Impresora hojas 2 caras |
| `impresora_paginas_combinadas` | integer | NO | Impresora páginas combinadas |
| `escaner_bn` | integer | NO | Escáner B/N |
| `escaner_todo_color` | integer | NO | Escáner todo color |
| `fax_bn` | integer | NO | Fax B/N |
| `fax_paginas_transmitidas` | integer | NO | Fax páginas transmitidas |
| `revelado_negro` | integer | NO | Revelado negro |
| `revelado_color_ymc` | integer | NO | Revelado color YMC |
| `eco_uso_2_caras` | varchar(50) | YES | Uso 2 caras (ecológico) |
| `eco_uso_combinar` | varchar(50) | YES | Uso combinar (ecológico) |
| `eco_reduccion_papel` | varchar(50) | YES | Reducción papel (ecológico) |
| `tipo_contador` | varchar(20) | NO | Tipo: usuario o ecologico |
| `fecha_lectura` | timestamp | NO | Fecha de lectura |
| `created_at` | timestamp | YES | Fecha de creación |

---

### 6. `cierres_mensuales` - Cierres de Contadores (24 columnas)

**Propósito:** Snapshots inmutables de contadores para auditoría

| Columna | Tipo | Nullable | Descripción |
|---------|------|----------|-------------|
| `id` | integer | NO | ID único |
| `printer_id` | integer | NO | FK a printers.id |
| `tipo_periodo` | varchar(20) | NO | diario, semanal, mensual, personalizado |
| `fecha_inicio` | date | NO | Fecha inicio del período |
| `fecha_fin` | date | NO | Fecha fin del período |
| `anio` | integer | NO | Año del cierre |
| `mes` | integer | NO | Mes del cierre (1-12) |
| `total_paginas` | integer | NO | Total páginas al cierre |
| `total_copiadora` | integer | NO | Total copiadora al cierre |
| `total_impresora` | integer | NO | Total impresora al cierre |
| `total_escaner` | integer | NO | Total escáner al cierre |
| `total_fax` | integer | NO | Total fax al cierre |
| `diferencia_total` | integer | NO | Diferencia vs cierre anterior |
| `diferencia_copiadora` | integer | NO | Diferencia copiadora |
| `diferencia_impresora` | integer | NO | Diferencia impresora |
| `diferencia_escaner` | integer | NO | Diferencia escáner |
| `diferencia_fax` | integer | NO | Diferencia fax |
| `fecha_cierre` | timestamp | NO | Fecha del cierre |
| `cerrado_por` | varchar(100) | YES | Usuario que hizo el cierre |
| `notas` | text | YES | Notas del cierre |
| `created_at` | timestamp | YES | Fecha de creación |
| `modified_at` | timestamp | YES | Fecha de modificación |
| `modified_by` | varchar(100) | YES | Usuario que modificó |
| `hash_verificacion` | varchar(64) | YES | Hash para verificación de integridad |

---

### 7. `cierres_mensuales_usuarios` - Detalle de Usuarios en Cierres (20 columnas)

**Propósito:** Snapshot de contadores por usuario en cada cierre

| Columna | Tipo | Nullable | Descripción |
|---------|------|----------|-------------|
| `id` | integer | NO | ID único |
| `cierre_mensual_id` | integer | NO | FK a cierres_mensuales.id |
| `codigo_usuario` | varchar(8) | NO | Código del usuario |
| `nombre_usuario` | varchar(100) | NO | Nombre del usuario |
| `total_paginas` | integer | NO | Total páginas al cierre |
| `total_bn` | integer | NO | Total B/N al cierre |
| `total_color` | integer | NO | Total color al cierre |
| `copiadora_bn` | integer | NO | Copiadora B/N al cierre |
| `copiadora_color` | integer | NO | Copiadora color al cierre |
| `impresora_bn` | integer | NO | Impresora B/N al cierre |
| `impresora_color` | integer | NO | Impresora color al cierre |
| `escaner_bn` | integer | NO | Escáner B/N al cierre |
| `escaner_color` | integer | NO | Escáner color al cierre |
| `fax_bn` | integer | NO | Fax B/N al cierre |
| `consumo_total` | integer | NO | Consumo del período |
| `consumo_copiadora` | integer | NO | Consumo copiadora del período |
| `consumo_impresora` | integer | NO | Consumo impresora del período |
| `consumo_escaner` | integer | NO | Consumo escáner del período |
| `consumo_fax` | integer | NO | Consumo fax del período |
| `created_at` | timestamp | YES | Fecha de creación |

---

## 🔑 Relaciones entre Tablas

```
users (1) ←→ (N) user_printer_assignments (N) ←→ (1) printers
                                                        ↓
                                                   (1) ↓ (N)
                                              contadores_impresora
                                                        ↓
                                                   (1) ↓ (N)
                                              contadores_usuario
                                                        ↓
                                                   (1) ↓ (N)
                                              cierres_mensuales
                                                        ↓
                                                   (1) ↓ (N)
                                        cierres_mensuales_usuarios
```

---

## ⚠️ IMPORTANTE: Distinción de Usuarios

**Actualmente hay UN SOLO tipo de usuario en la DB:**

- **`users` table** = Usuarios de impresoras (para aprovisionamiento)
  - Estos NO son usuarios del sistema
  - Son usuarios que se crean EN las impresoras Ricoh
  - Tienen códigos de usuario, PINs, rutas SMB, etc.

**NO EXISTE actualmente:**
- Tabla de usuarios administradores del sistema
- Tabla de sesiones/autenticación
- Sistema de roles/permisos

---

## 🎯 Campos Clave para Multi-Tenancy

**Ya implementados:**
- ✅ `printers.empresa` - Empresa a la que pertenece la impresora
- ✅ `users.empresa` - Empresa del usuario de impresora

**Estos campos son perfectos para implementar el filtrado por empresa en el sistema de autenticación.**

---

## 📝 Próximos Pasos para Sistema de Login

Para implementar el sistema de autenticación necesitamos crear:

1. **Nueva tabla `admin_users`** - Usuarios del sistema (superadmin, admin)
2. **Nueva tabla `admin_sessions`** - Sesiones de autenticación
3. **Nueva tabla `admin_permissions`** (opcional) - Permisos granulares
4. **Nueva tabla `admin_audit_log`** (recomendado) - Auditoría de acciones

---

**Documento generado:** 18 de marzo de 2026  
**Base de datos:** ricoh_fleet (PostgreSQL 16)
