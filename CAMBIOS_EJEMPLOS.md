# 📝 Correcciones de Ejemplos y Valores Predeterminados

**Fecha:** 13 de Febrero de 2026  
**Versión:** 3.2.1

---

## ✅ Correcciones Realizadas

### 1. Typo en Usuario de Red

**Problema:** El valor predeterminado tenía un typo: `relitelda\scaner`  
**Corrección:** Cambiado a `reliteltda\scaner` (con doble 't')

**Archivos corregidos:**
- `src/components/governance/ProvisioningPanel.tsx` - Estado inicial del formulario
- `backend/db/models.py` - Valor por defecto en el modelo
- `backend/api/schemas.py` - Valor por defecto en el schema
- `backend/apply_migration.py` - Script de migración

### 2. Ejemplos Más Genéricos

**Problema:** Los ejemplos usaban nombres específicos  
**Corrección:** Cambiados a ejemplos genéricos

#### Placeholders del Formulario

**Antes:**
- Nombre: `Juan Lizarazo`
- Código: `1014`

**Después:**
- Nombre: `Nombre del Usuario`
- Código: `1234`

**Archivos corregidos:**
- `src/components/governance/ProvisioningPanel.tsx`

#### Datos de Ejemplo en Scripts

**Antes:**
- Nombre: `Juan Lizarazo`
- Ruta: `\\10.0.0.5\scans\juan`

**Después:**
- Nombre: `Usuario Ejemplo`
- Ruta: `\\10.0.0.5\scans\usuario`

**Archivos corregidos:**
- `create_db.py`
- `backend/init_db.py`

---

## 📋 Resumen de Cambios

| Archivo | Cambio | Tipo |
|---------|--------|------|
| `ProvisioningPanel.tsx` | `relitelda` → `reliteltda` | Typo |
| `ProvisioningPanel.tsx` | `Juan Lizarazo` → `Nombre del Usuario` | Placeholder |
| `ProvisioningPanel.tsx` | `1014` → `1234` | Placeholder |
| `db/models.py` | `relitelda` → `reliteltda` | Default |
| `api/schemas.py` | `relitelda` → `reliteltda` | Default |
| `apply_migration.py` | `relitelda` → `reliteltda` | Migration |
| `create_db.py` | `Juan Lizarazo` → `Usuario Ejemplo` | Ejemplo |
| `init_db.py` | `Juan Lizarazo` → `Usuario Ejemplo` | Ejemplo |

---

## 🎯 Impacto

### Usuarios Existentes
Los usuarios ya creados en la base de datos NO se ven afectados. Solo cambian los valores predeterminados para nuevos usuarios.

### Nuevos Usuarios
- El formulario mostrará placeholders más genéricos
- El valor predeterminado del usuario de red será correcto: `reliteltda\scaner`

---

## ✅ Verificación

Para verificar los cambios:

1. **Frontend:** Abre el formulario y verifica los placeholders
   - Nombre: "Nombre del Usuario"
   - Código: "1234"
   - Usuario de red: "reliteltda\scaner"

2. **Backend:** Los valores predeterminados están corregidos en el código

---

**Estado:** ✅ Correcciones aplicadas  
**Versión:** 3.2.1
