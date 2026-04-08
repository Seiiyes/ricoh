# Scripts de Backend

**Última actualización**: 2026-04-08

Esta carpeta contiene scripts de utilidad para desarrollo, mantenimiento y operaciones del sistema.

## 📋 Índice

- [Scripts Activos](#-scripts-activos)
- [Scripts Obsoletos](#-scripts-obsoletos)
- [Estructura de Carpetas](#-estructura-de-carpetas)
- [Uso](#-uso)

## ✅ Scripts Activos

### Usuarios y Sincronización

#### `consolidate_duplicate_users.py` ✅
Consolida usuarios duplicados en la tabla `users`.

**Uso**:
```bash
docker exec -it ricoh-backend python scripts/consolidate_duplicate_users.py
```

**Última ejecución**: 2026-04-08  
**Resultado**: 28 usuarios eliminados, 2,539 referencias actualizadas

#### `fix_user_codes_add_leading_zeros.py` ✅
Formatea códigos de usuario a 4 dígitos con ceros a la izquierda.

**Uso**:
```bash
docker exec -it ricoh-backend python scripts/fix_user_codes_add_leading_zeros.py
```

**Nota**: No fue necesario ejecutar (códigos ya correctos)

#### `sync_users_from_addressbooks.py` ✅
Sincroniza usuarios desde libretas de direcciones de impresoras.

**Uso**:
```bash
docker exec -it ricoh-backend python scripts/sync_users_from_addressbooks.py
```

#### `sync_users_masivo.py` ✅
Sincronización masiva de usuarios.

**Uso**:
```bash
docker exec -it ricoh-backend python scripts/sync_users_masivo.py
```

#### `sync_users_simple.py` ✅
Script simple para sincronización masiva de usuarios (versión simplificada).

**Uso**:
```bash
docker exec -it ricoh-backend python scripts/sync_users_simple.py
```

**Nota**: Versión simplificada de `sync_users_masivo.py` con output más limpio.

### Verificación y Testing

#### `verify_all_5_printers.py` ✅
Verifica estado de 5 impresoras principales.

#### `quick_verify_5_printers.py` ✅
Verificación rápida de impresoras.

#### `test_cierre_normalizado.py` ✅
Prueba de cierres con datos normalizados.

#### `test_crear_cierre_nuevo.py` ✅
Test de creación de cierres.

#### `test_crear_cierre_rapido.py` ✅
Test rápido de creación de cierres.

#### `test_integracion_completa_final.py` ✅
Test de integración completa del sistema.

#### `test_normalizacion_completa.py` ✅
Test de normalización de base de datos.

#### `test_exportaciones.py` ✅
Test de funcionalidad de exportaciones.

### Utilidades

#### `run_migrations.py` ✅
Ejecuta migraciones de base de datos.

**Uso**:
```bash
docker exec -it ricoh-backend python scripts/run_migrations.py
```

#### `init_superadmin.py` ✅
Inicializa usuario superadmin.

**Uso**:
```bash
docker exec -it ricoh-backend python scripts/init_superadmin.py
```

#### `check_smb_paths_status.py` ✅
Verifica estado de rutas SMB de usuarios.

#### `analyze_all_printer_formats.py` ✅
Analiza formatos de contadores de impresoras.

#### `verify_deployment.py` ✅
Verifica estado del despliegue.

#### `sync_all_5_printers_to_db.py` ✅
Sincroniza datos de 5 impresoras principales a BD.

### Scripts de Despliegue

#### `deploy.sh` / `deploy.bat` ✅
Scripts de despliegue para Linux/Windows.

#### `start-backend.bat` ✅
Inicia el backend en Windows.

#### `start-api-server.bat` ✅
Inicia el servidor API en Windows.

## ❌ Scripts Obsoletos

Ver `OBSOLETE_SCRIPTS.md` para lista completa.

### Scripts NO Funcionales

- ❌ `fix_duplicate_user_codes.py` - Usa columnas eliminadas + lógica incorrecta
- ❌ `consolidate_duplicate_codes.py` - Usa columnas eliminadas

**Razón**: Estos scripts usan columnas `codigo_usuario` y `nombre_usuario` que fueron eliminadas de `contadores_usuario` y `cierres_mensuales_usuarios` en la Migración 013.

**Alternativa**: Usar `consolidate_duplicate_users.py` (actualizado)

## 📁 Estructura de Carpetas

### `/utilidades/`
Scripts de utilidad general y herramientas de desarrollo.

**Contenido**:
- Scripts de análisis
- Herramientas de comparación
- Utilidades de debugging

## 🚀 Uso

### Ejecución Básica

Desde el contenedor Docker:
```bash
docker exec -it ricoh-backend python scripts/<nombre_script>.py
```

Desde el host (con Python configurado):
```bash
cd backend
python scripts/<nombre_script>.py
```

### Ejecución con Argumentos

Algunos scripts aceptan argumentos:
```bash
docker exec -it ricoh-backend python scripts/sync_users_from_addressbooks.py --printer-id 1
```

### Modo Interactivo

Scripts como `consolidate_duplicate_users.py` requieren confirmación:
```bash
docker exec -it ricoh-backend python scripts/consolidate_duplicate_users.py
# Responder 's' para confirmar
```

### Modo No Interactivo

Para automatización:
```bash
echo "s" | docker exec -i ricoh-backend python scripts/consolidate_duplicate_users.py
```

## ⚠️ Importante

### Scripts One-Time

Estos scripts son principalmente para:
- Uso único (one-time)
- Debugging
- Mantenimiento
- Migraciones de datos

### NO son parte del sistema en producción

Para funcionalidad de producción, usa:
- `backend/api/` - Endpoints REST
- `backend/services/` - Servicios de negocio
- `backend/parsear_*.py` - Parsers de HTML Ricoh

### Precauciones

1. **Backup antes de ejecutar**: Especialmente scripts que modifican datos
2. **Leer documentación**: Ver `OBSOLETE_SCRIPTS.md` antes de usar
3. **Verificar estado**: Algunos scripts están obsoletos
4. **Modo interactivo**: Preferir confirmación manual para operaciones críticas

## 📚 Documentación Relacionada

### Usuarios Duplicados

- **Índice completo**: `docs/desarrollo/soluciones/INDICE_USUARIOS_DUPLICADOS.md`
- **Análisis**: `docs/desarrollo/correcciones/DOCUMENTACION_USUARIOS_DUPLICADOS.md`
- **Solución**: `docs/desarrollo/correcciones/SOLUCION_USUARIOS_DUPLICADOS.md`
- **Verificación**: `docs/desarrollo/verificacion/VERIFICACION_CODIGOS_USUARIO.md`

### Scripts

- **Scripts obsoletos**: `OBSOLETE_SCRIPTS.md` (en esta carpeta)
- **Índice general**: `docs/INDICE_DOCUMENTACION_COMPLETO.md`

## 🔧 Mantenimiento

### Agregar Nuevo Script

1. Crear script en `backend/scripts/`
2. Documentar en este README
3. Agregar a categoría correspondiente
4. Incluir ejemplo de uso

### Marcar Script como Obsoleto

1. Agregar a `OBSOLETE_SCRIPTS.md`
2. Actualizar este README
3. Documentar razón y alternativa
4. NO eliminar (mantener para referencia)

---

**Última revisión**: 2026-04-08  
**Mantenedor**: Sistema de Auditoría
