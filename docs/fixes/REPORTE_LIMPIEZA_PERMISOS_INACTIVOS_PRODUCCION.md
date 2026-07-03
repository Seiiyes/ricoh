# Reporte de Auditoría y Limpieza: Permisos de Usuarios Desactivados en Producción

**Fecha**: 3 de julio de 2026  
**Problema**: Ciertos usuarios inactivos o desactivados conservaban permisos y asignaciones activas en la base de datos de producción, lo que provocaba inconsistencias de visualización y filtrado.

---

## 1. Diagnóstico

Al auditar la base de datos de producción, se descubrió que:
- El usuario **JUAN LIZARAZO (7104)** y otros usuarios que fueron desactivados previamente, tenían registros en `user_printer_assignments` con permisos en `True` (`func_copier`, `func_printer`, etc.) y estado activo (`is_active = True`).
- Esto ocurrió porque en sesiones anteriores, las desactivaciones no se completaban a nivel físico o lógico debido a que el hilo principal del frontend crasheaba silenciosamente por el error de `createPortal` o por el bloqueo de `window.confirm()` por parte de los navegadores web en HTTP.

---

## 2. Acciones Realizadas

### A. Limpieza de Asignaciones en Base de Datos de Producción
Se ejecutó el script `deployment/clean_inactive_permissions.py` en el servidor de producción. El script forzó la desactivación lógica y la remoción de todos los privilegios para las asignaciones asociadas a usuarios inactivos:

```sql
UPDATE user_printer_assignments 
SET is_active = false,
    func_copier = false,
    func_copier_color = false,
    func_printer = false,
    func_printer_color = false,
    func_document_server = false,
    func_fax = false,
    func_scanner = false,
    func_browser = false
WHERE user_id IN (SELECT id FROM users WHERE is_active = false);
```

**Resultado de la ejecución**: `UPDATE 44`. Se corrigieron y limpiaron con éxito **44 registros inconsistentes** en la base de datos local.

### B. Verificación de Consistencia
Se corrió nuevamente el script de auditoría `deployment/audit_inactive_permissions.py` para validar que ninguna asignación de usuario inactivo tuviera permisos en `True`.  
**Resultado**: `(0 rows)` (consistencia absoluta de base de datos local restablecida).

---

## 3. Conclusión
Todos los usuarios desactivados en la suite de Ricoh han quedado libres de permisos en la base de datos local del backend. Al corregirse la consistencia visual y los filtros en el frontend, estos usuarios ya no aparecerán en la pestaña de "Activos" y sus filas se mostrarán correctamente en la pestaña de "Inactivos" sin iconos de permisos remanentes.
