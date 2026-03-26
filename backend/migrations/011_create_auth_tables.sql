-- ============================================================================
-- MIGRACIÓN 011: Crear Tablas de Autenticación
-- ============================================================================
-- Descripción: Crea las tablas necesarias para el sistema de autenticación
--              con roles y multi-tenancy
--
-- Tablas:
-- 1. admin_users: Usuarios administradores del sistema
-- 2. admin_sessions: Sesiones activas con JWT tokens
-- 3. admin_audit_log: Registro de auditoría de acciones
-- ============================================================================

BEGIN;

-- ============================================================================
-- TABLA 1: admin_users
-- ============================================================================

CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    rol VARCHAR(20) NOT NULL,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT chk_rol_valido CHECK (rol IN ('superadmin', 'admin', 'viewer', 'operator')),
    CONSTRAINT chk_superadmin_sin_empresa CHECK (
        (rol = 'superadmin' AND empresa_id IS NULL) OR 
        (rol != 'superadmin' AND empresa_id IS NOT NULL)
    ),
    CONSTRAINT chk_username_formato CHECK (username ~ '^[a-z0-9_-]{3,}$'),
    CONSTRAINT chk_email_formato CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_password_hash_length CHECK (LENGTH(password_hash) >= 60),
    CONSTRAINT chk_failed_attempts_positive CHECK (failed_login_attempts >= 0)
);

-- Índices para admin_users
CREATE INDEX idx_admin_users_username ON admin_users(username);
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_empresa_id ON admin_users(empresa_id);
CREATE INDEX idx_admin_users_rol ON admin_users(rol);
CREATE INDEX idx_admin_users_active ON admin_users(is_active) WHERE is_active = TRUE;

-- Trigger para updated_at
CREATE TRIGGER update_admin_users_updated_at 
BEFORE UPDATE ON admin_users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentarios
COMMENT ON TABLE admin_users IS 'Usuarios administradores del sistema (NO usuarios de impresoras)';
COMMENT ON COLUMN admin_users.username IS 'Nombre de usuario único (formato: lowercase alphanumeric con underscores/hyphens)';
COMMENT ON COLUMN admin_users.password_hash IS 'Hash bcrypt de la contraseña (60+ caracteres)';
COMMENT ON COLUMN admin_users.rol IS 'Rol del usuario: superadmin (sin empresa, ve todo), admin (asignado a empresa)';
COMMENT ON COLUMN admin_users.empresa_id IS 'Empresa asignada (NULL para superadmin, NOT NULL para otros roles)';
COMMENT ON COLUMN admin_users.failed_login_attempts IS 'Contador de intentos fallidos de login (resetea a 0 en login exitoso)';
COMMENT ON COLUMN admin_users.locked_until IS 'Timestamp hasta el cual la cuenta está bloqueada (NULL si no está bloqueada)';

-- ============================================================================
-- TABLA 2: admin_sessions
-- ============================================================================

CREATE TABLE admin_sessions (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    refresh_token VARCHAR(500) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    refresh_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_expires_at_future CHECK (expires_at > created_at)
);

-- Índices para admin_sessions
CREATE INDEX idx_admin_sessions_user_id ON admin_sessions(admin_user_id);
CREATE INDEX idx_admin_sessions_token ON admin_sessions(token);
CREATE INDEX idx_admin_sessions_expires_at ON admin_sessions(expires_at);

-- Comentarios
COMMENT ON TABLE admin_sessions IS 'Sesiones activas de usuarios administradores con JWT tokens';
COMMENT ON COLUMN admin_sessions.token IS 'Access token JWT (30 min de expiración)';
COMMENT ON COLUMN admin_sessions.refresh_token IS 'Refresh token JWT (7 días de expiración)';
COMMENT ON COLUMN admin_sessions.ip_address IS 'Dirección IP del cliente (IPv4 o IPv6)';
COMMENT ON COLUMN admin_sessions.user_agent IS 'User agent del navegador';
COMMENT ON COLUMN admin_sessions.last_activity IS 'Timestamp de la última actividad (actualizado en cada request)';

-- ============================================================================
-- TABLA 3: admin_audit_log
-- ============================================================================

CREATE TABLE admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL,
    accion VARCHAR(50) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    entidad_tipo VARCHAR(50),
    entidad_id INTEGER,
    detalles JSONB,
    resultado VARCHAR(20) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_resultado_valido CHECK (resultado IN ('exito', 'error', 'denegado'))
);

-- Índices para admin_audit_log
CREATE INDEX idx_admin_audit_log_user_id ON admin_audit_log(admin_user_id);
CREATE INDEX idx_admin_audit_log_accion ON admin_audit_log(accion);
CREATE INDEX idx_admin_audit_log_modulo ON admin_audit_log(modulo);
CREATE INDEX idx_admin_audit_log_created_at ON admin_audit_log(created_at DESC);
CREATE INDEX idx_admin_audit_log_entidad ON admin_audit_log(entidad_tipo, entidad_id);
CREATE INDEX idx_admin_audit_log_detalles ON admin_audit_log USING gin(detalles);

-- Comentarios
COMMENT ON TABLE admin_audit_log IS 'Registro inmutable de auditoría de todas las acciones administrativas';
COMMENT ON COLUMN admin_audit_log.accion IS 'Acción realizada: login, logout, crear, editar, eliminar, exportar, ver';
COMMENT ON COLUMN admin_audit_log.modulo IS 'Módulo del sistema: auth, empresas, admin_users, printers, users, contadores, cierres';
COMMENT ON COLUMN admin_audit_log.entidad_tipo IS 'Tipo de entidad afectada: empresa, admin_user, printer, user, contador, cierre';
COMMENT ON COLUMN admin_audit_log.entidad_id IS 'ID de la entidad afectada';
COMMENT ON COLUMN admin_audit_log.detalles IS 'Detalles adicionales en formato JSON (valores anteriores/nuevos, errores, etc.)';
COMMENT ON COLUMN admin_audit_log.resultado IS 'Resultado de la acción: exito, error, denegado';

-- ============================================================================
-- PASO 4: Crear superadmin inicial (placeholder)
-- ============================================================================
-- Nota: El password_hash real se generará desde Python después de la migración
-- usando el script init_superadmin.py

INSERT INTO admin_users (
    username,
    password_hash,
    nombre_completo,
    email,
    rol,
    empresa_id,
    is_active
) VALUES (
    'superadmin',
    '$2b$12$placeholder.hash.will.be.replaced.by.init.script.xxxxxxxxxxxxxxxxxxxxxx',
    'Super Administrador',
    'admin@ricohsuite.local',
    'superadmin',
    NULL,
    TRUE
)
ON CONFLICT (username) DO NOTHING;

COMMIT;

-- ============================================================================
-- Verificación
-- ============================================================================

DO $$
DECLARE
    total_admin_users INTEGER;
    superadmin_exists BOOLEAN;
BEGIN
    SELECT COUNT(*) INTO total_admin_users FROM admin_users;
    SELECT EXISTS(SELECT 1 FROM admin_users WHERE username = 'superadmin') INTO superadmin_exists;
    
    RAISE NOTICE '✅ Migración 011 completada exitosamente';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Tablas de autenticación creadas:';
    RAISE NOTICE '   - admin_users (usuarios administradores)';
    RAISE NOTICE '   - admin_sessions (sesiones activas)';
    RAISE NOTICE '   - admin_audit_log (registro de auditoría)';
    RAISE NOTICE '';
    RAISE NOTICE '👤 Usuarios administradores: %', total_admin_users;
    
    IF superadmin_exists THEN
        RAISE NOTICE '   ✅ Superadmin creado (username: superadmin)';
        RAISE NOTICE '';
        RAISE NOTICE '⚠️  IMPORTANTE: Ejecutar script init_superadmin.py para generar contraseña';
        RAISE NOTICE '   Comando: python backend/scripts/init_superadmin.py';
    ELSE
        RAISE NOTICE '   ⚠️  Superadmin NO creado (conflicto o error)';
    END IF;
END $$;
