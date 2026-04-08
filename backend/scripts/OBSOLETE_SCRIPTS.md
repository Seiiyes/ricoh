# Scripts Obsoletos y Estado Actual

**Última actualización**: 2026-04-08

Los siguientes scripts están **OBSOLETOS** después de las normalizaciones de la base de datos.

## ❌ Scripts Obsoletos

### 1. `fix_duplicate_user_codes.py`
- **Razón**: 
  - Usa las columnas `codigo_usuario` y `nombre_usuario` que fueron eliminadas de `contadores_usuario` y `cierres_mensuales_usuarios` (Migración 013)
  - Implementa normalización INCORRECTA que elimina ceros a la izquierda
- **Estado**: ⚠️ NO USAR - Obsoleto y con lógica incorrecta
- **Alternativa**: Usar `consolidate_duplicate_users.py` (actualizado)

### 2. `consolidate_duplicate_codes.py`
- **Razón**: Usa las columnas `codigo_usuario` y `nombre_usuario` que fueron eliminadas de `contadores_usuario` y `cierres_mensuales_usuarios`
- **Estado**: ⚠️ NO USAR - No funcional
- **Alternativa**: Usar `consolidate_duplicate_users.py` (actualizado)

## ✅ Scripts Actualizados y Funcionales

### Usuarios y Sincronización

1. **`consolidate_duplicate_users.py`** ✅
   - **Función**: Consolida usuarios duplicados en la tabla `users`
   - **Estado**: Actualizado y probado
   - **Última ejecución**: 2026-04-08
   - **Resultado**: 28 usuarios eliminados, 2,539 referencias actualizadas
   - **Uso**: `python scripts/consolidate_duplicate_users.py`

2. **`fix_user_codes_add_leading_zeros.py`** ✅
   - **Función**: Formatea códigos de usuario a 4 dígitos con ceros a la izquierda
   - **Estado**: Creado y probado
   - **Nota**: No fue necesario ejecutar (códigos ya correctos)
   - **Uso**: `python scripts/fix_user_codes_add_leading_zeros.py`

3. **`sync_users_from_addressbooks.py`** ✅
   - **Función**: Sincroniza usuarios desde libretas de direcciones de impresoras
   - **Estado**: Actualizado con normalización correcta
   - **Uso**: `python scripts/sync_users_from_addressbooks.py`

4. **`sync_users_masivo.py`** ✅
   - **Función**: Sincronización masiva de usuarios
   - **Estado**: Funcional
   - **Uso**: `python scripts/sync_users_masivo.py`

### Verificación y Testing

5. **`verify_all_5_printers.py`** ✅
   - **Función**: Verifica estado de 5 impresoras principales
   - **Estado**: Funcional

6. **`quick_verify_5_printers.py`** ✅
   - **Función**: Verificación rápida de impresoras
   - **Estado**: Funcional

7. **`test_cierre_normalizado.py`** ✅
   - **Función**: Prueba de cierres con datos normalizados
   - **Estado**: Actualizado para normalización

8. **`test_crear_cierre_nuevo.py`** ✅
   - **Función**: Test de creación de cierres
   - **Estado**: Funcional

9. **`test_integracion_completa_final.py`** ✅
   - **Función**: Test de integración completa
   - **Estado**: Funcional

### Utilidades

10. **`run_migrations.py`** ✅
    - **Función**: Ejecuta migraciones de base de datos
    - **Estado**: Funcional

11. **`init_superadmin.py`** ✅
    - **Función**: Inicializa usuario superadmin
    - **Estado**: Funcional

12. **`check_smb_paths_status.py`** ✅
    - **Función**: Verifica estado de rutas SMB
    - **Estado**: Funcional

13. **`analyze_all_printer_formats.py`** ✅
    - **Función**: Analiza formatos de contadores de impresoras
    - **Estado**: Funcional

14. **`verify_deployment.py`** ✅
    - **Función**: Verifica despliegue
    - **Estado**: Funcional

## 📊 Cambios en la Base de Datos

### Migración 013 (Normalización de Referencias)
- Las tablas `contadores_usuario` y `cierres_mensuales_usuarios` solo tienen `user_id` (FK a `users`)
- Los campos `codigo_usuario` y `nombre_usuario` fueron eliminados
- Todos los datos de usuario se obtienen mediante JOIN con la tabla `users`

### Migración 016 (Fix de Usuarios Duplicados - Revertida)
- Se agregó constraint UNIQUE en `users.codigo_de_usuario`
- Posteriormente se eliminó (era incorrecto)
- Los códigos de usuario son de formato fijo de 4 dígitos

## 🔧 Formato de Códigos de Usuario

### Formato Correcto ✅
Los códigos de usuario en Ricoh son de **formato fijo de 4 dígitos**:
- Ejemplos: "0547", "8599", "0037", "1234"
- Los ceros a la izquierda son PARTE del código

### Normalización Incorrecta ❌
NO eliminar ceros a la izquierda:
- "0547" → "547" ❌ INCORRECTO
- "0547" → "0547" ✅ CORRECTO

### Formateo Correcto ✅
Formatear a 4 dígitos con ceros a la izquierda:
- "547" → "0547" ✅ CORRECTO
- "37" → "0037" ✅ CORRECTO

## 📝 Recomendaciones

### Si necesitas trabajar con usuarios:

1. **Usar `consolidate_duplicate_users.py`** para consolidar duplicados
2. **Usar `format_user_code()`** de `user_sync_service.py` para formatear códigos
3. **NO usar** scripts obsoletos que eliminan ceros

### Si necesitas actualizar queries:

1. Usar `user_id` en lugar de `codigo_usuario` en tablas normalizadas
2. Hacer JOIN con la tabla `users` para obtener `codigo_de_usuario` y `name`
3. Usar las vistas de compatibilidad si es necesario: `v_users_completo`, `v_printers_completo`

### Si necesitas crear nuevos scripts:

1. Importar `format_user_code()` de `services.user_sync_service`
2. Usar `user_id` como FK en tablas normalizadas
3. Hacer JOIN con `users` para datos de usuario

## 📚 Documentación Relacionada

- **Análisis completo**: `docs/desarrollo/correcciones/DOCUMENTACION_USUARIOS_DUPLICADOS.md`
- **Solución implementada**: `docs/desarrollo/correcciones/SOLUCION_USUARIOS_DUPLICADOS.md`
- **Corrección final**: `docs/desarrollo/correcciones/CORRECCION_FINAL_CODIGOS_USUARIO.md`
- **Verificación**: `docs/desarrollo/verificacion/VERIFICACION_CODIGOS_USUARIO.md`
- **Índice completo**: `docs/desarrollo/soluciones/INDICE_USUARIOS_DUPLICADOS.md`

---

**Última revisión**: 2026-04-08  
**Estado**: Actualizado con información de usuarios duplicados
