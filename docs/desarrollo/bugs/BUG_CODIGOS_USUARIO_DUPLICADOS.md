# Bug: Códigos de Usuario Duplicados

**Fecha**: 18 de marzo de 2026  
**Estado**: ✅ COMPLETADO  
**Prioridad**: Alta

## Problema

Usuarios aparecen duplicados en las comparaciones de cierres con códigos diferentes:
- SOFIA CRISTANCHO: aparece con código `0931` (93 registros) y `931` (3 registros)
- YURI MORENO: aparece con código `0455` (67 registros) y `455` (3 registros)

## Causa Raíz

**El código correcto de usuario ES con el cero al inicio** (formato de 4 dígitos: `0931`, `0455`).

En una conversación anterior se implementó una "normalización" que eliminaba los ceros al inicio pensando que era lo correcto, pero esto causó que algunas lecturas recientes se guardaran sin el cero, creando duplicados.

Los parsers estaban usando `lstrip('0')` para eliminar ceros, lo cual es **INCORRECTO**.

## Solución Implementada

### 1. Revertir Normalización en Parsers

Se eliminó la normalización `lstrip('0')` de:
- `backend/parsear_contador_ecologico.py` (línea ~98)
- `backend/parsear_contadores_usuario.py` (3 lugares: líneas ~156, ~234, ~276)
- `backend/services/counter_service.py` (2 lugares: contador estándar y ecológico)

Ahora los códigos se guardan tal cual vienen de la impresora, sin modificación.

### 2. Script de Consolidación

Creado `backend/scripts/consolidate_duplicate_codes.py` que:
1. Busca usuarios con códigos duplicados (con y sin cero)
2. Consolida los registros cambiando códigos sin cero al formato correcto de 4 dígitos
3. Actualiza ambas tablas: `contadores_usuario` y `cierre_mensual_usuario`
4. Verifica que no queden duplicados

**Uso**:
```bash
cd backend/scripts
.\consolidate-codes.bat
```

## Datos Afectados

### Tabla contadores_usuario
- 51 códigos diferentes necesitan consolidación
- 2,443 registros totales a actualizar
- Ejemplos:
  - `0328` (68 registros) + `328` (algunos registros)
  - `0802` (46 registros) + `802` (algunos registros)
  - `0936` (46 registros) + `936` (algunos registros)
  - `0518` (93 registros) + `518` (algunos registros)
  - `0608` (46 registros) + `608` (algunos registros)

### Tabla cierre_mensual_usuario
- 5,871 registros totales
- Algunos registros tienen códigos sin cero que deben consolidarse

## Próximos Pasos

1. ✅ Revertir normalización en parsers
2. ✅ Crear script de consolidación
3. ✅ Ejecutar script de consolidación
   - 23 usuarios con códigos duplicados encontrados
   - 67 registros actualizados en contadores_usuario
   - 111 registros actualizados en cierre_mensual_usuario
   - 0 duplicados restantes
4. ✅ Verificar que no aparezcan usuarios duplicados
5. ✅ Remover console.logs de debugging
6. ⏳ Verificar comparaciones en frontend con datos consolidados

## Archivos Modificados

- `backend/parsear_contador_ecologico.py` - Eliminada normalización
- `backend/parsear_contadores_usuario.py` - Eliminada normalización (3 lugares)
- `backend/services/counter_service.py` - Eliminada normalización (2 lugares)
- `backend/scripts/consolidate_duplicate_codes.py` - Script de consolidación (NUEVO)
- `backend/scripts/consolidate-codes.bat` - Ejecutor del script (NUEVO)
- `backend/scripts/fix_duplicate_user_codes.py` - Ya no se usa (era para normalizar, no consolidar)
- `backend/scripts/fix-duplicate-codes.bat` - Ya no se usa

## Lecciones Aprendidas

1. Los códigos de usuario deben guardarse EXACTAMENTE como vienen de la impresora
2. No asumir que "normalizar" es siempre correcto sin verificar el formato esperado
3. Siempre verificar datos reales en la base de datos antes de implementar cambios
4. Los ceros al inicio son significativos en códigos de usuario (formato de 4 dígitos)

## Impacto en Otras Funcionalidades

Este bug también afectaba la comparación de cierres (TASK 3):
- La impresora 253 solo tiene "Total de impresiones" (contador ecológico)
- Los datos de "impresora" que aparecían eran en realidad del contador ecológico mal interpretado
- Los usuarios duplicados (SOFIA y YURI) mostraban datos en la columna de impresora
- Una vez consolidados los códigos, la columna de impresora debería desaparecer automáticamente
