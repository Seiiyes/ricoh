# Documentación de Migración: Normalización de Centros de Costo por Empresa

> **Estado:** ✅ COMPLETADA Y APROBADA  
> **Fecha de ejecución:** 29 de mayo de 2026  
> **Versión del Sistema:** v2.5.0  
> **ID de Commit:** `f53ae3d`  
> **Responsable:** Antigravity AI Architect & QA Suite

---

## 1. Contexto y Objetivos

Anteriormente, el campo `centro_costos` se almacenaba como una cadena de texto libre (`VARCHAR(100)`) directamente en la tabla `users`. Esto generaba fragmentación, inconsistencias ortográficas en los reportes analíticos y la imposibilidad de estructurar catálogos limpios por empresa cliente (Multi-Tenancy).

Con esta migración se cumplieron los siguientes objetivos de negocio y técnicos:
1. **Normalización Estructural:** Se creó la nueva entidad `centro_costos` asociada directamente a una empresa (`empresa_id`).
2. **Multi-Tenancy Estricto:** Se habilitó la regla de que cada empresa tiene su propia lista de centros de costo, permitiendo nombres idénticos (ej. `"Contabilidad"`) entre empresas separadas sin colisión y con IDs independientes.
3. **Compatibilidad hacia atrás al 100%:** Se implementó una propiedad dinámica `@property` en el modelo `User` SQLAlchemy para que los JSON devueltos y recibidos por las APIs de cara al frontend sigan usando `"centro_costos"` como string, **evitando reescribir o romper la interfaz en React**.
4. **Ingesta Tolerante a Fallos:** Se dotó al repositorio (`UserRepository`) de lógica inteligente para buscar o crear dinámicamente los centros de costo en caliente si se pasa un string en la creación/edición de usuarios.

---

## 2. Cambios Ejecutados en la Base de Datos

Se creó y ejecutó el script de migración SQL [014_normalizar_centros_costo.sql](file:///c:/Users/juan.lizarazo/Desktop/ricoh/backend/migrations/014_normalizar_centros_costo.sql):

1. **Tabla `centro_costos`:**
   - Columnas: `id` (Serial PK), `nombre` (Varchar 100), `empresa_id` (FK a `empresas(id)`), `is_active` (Boolean), `created_at` (Timestamp) y `updated_at` (Timestamp).
   - Restricción: `CONSTRAINT uq_centro_costo_empresa_nombre UNIQUE (empresa_id, nombre)`.
2. **Tabla `users`:**
   - Se agregó la columna `centro_costo_id` (FK a `centro_costos(id) ON DELETE SET NULL`).
3. **Migración de Datos Existentes (DML):**
   - Se agruparon y migraron todos los strings de `centro_costos` de los usuarios hacia la nueva tabla estructurada en base a su `empresa_id`.
   - Se actualizaron las relaciones de claves foráneas de los usuarios y se eliminó la columna física de texto vieja `centro_costos` de la tabla `users`.
4. **Vistas de Compatibilidad Reconstruidas:**
   - Se eliminaron y reconstruyeron de forma optimizada las vistas `v_users_completo`, `v_contadores_usuario_completo` y `v_cierres_usuarios_completo` incorporando un `LEFT JOIN centro_costos cc ON u.centro_costo_id = cc.id` para que sigan exponiendo la columna `centro_costos` de forma transparente.

---

## 3. Cambios en el Código Fuente (Backend)

### A. Modelos ORM (`backend/db/models.py` y `models_auth.py`)
- Se definió la clase de modelo `CentroCosto` asociada a `Empresa` y `User`.
- Se removió la columna string `centro_costos` de `User` y se sustituyó por `centro_costo_id`.
- Se implementó la propiedad compatible en la clase `User`:
  ```python
  @property
  def centro_costos(self) -> Optional[str]:
      """Propiedad híbrida para mantener compatibilidad string hacia atrás"""
      return self.centro_costo_rel.nombre if self.centro_costo_rel else None
  ```
- Se agregó la relación bidireccional `centros_costo` en la clase `Empresa` en `models_auth.py`.

### B. Repositorio de Datos (`backend/db/repository.py`)
- **`UserRepository.create`:** Se modificó para resolver dinámicamente el `empresa_id` a partir del nombre de la empresa y, con él, buscar o crear automáticamente el `CentroCosto` asignando la FK estructurada.
- **`UserRepository.update`:** Se adaptó para que si la API le envía `"centro_costos"` como string en el payload, resuelva e inserte el correspondiente `centro_costo_id` de forma compatible.

### C. Capa de APIs y Consultas
- **Buscador de Usuarios (`backend/api/users.py`):** Se corrigió un bug latente en la búsqueda de texto libre donde se intentaba acceder al atributo inexistente `User.nombre` en lugar de `User.name`.
- **Top de Consumo (`backend/api/analytics.py`):** Se reescribió la query de ranking `top-users` para incorporar un `LEFT JOIN centro_costos cc ON u.centro_costo_id = cc.id` y agrupar por `cc.nombre`.
- **Filtros de Cierres (`backend/api/counters.py`):** Se refactorizaron las búsquedas y filtrados de texto de `centro_costos` en el listado global de cierres para realizar joins explícitos con la nueva tabla structured.

---

## 4. Evidencia de Pruebas y Validación

Se ejecutaron de forma exitosa las siguientes validaciones automatizadas en caliente dentro del entorno Docker local:

### A. Test Unitario y de Aislamiento Multitenant (`test_multitenant_centro_costos.py`)
Se diseñó un script interactivo para validar las reglas en caliente:
* **Comando:** `docker exec ricoh-backend python /app/test_multitenant_centro_costos.py`
* **Resultados:**
  1. Creó Empresa A y Empresa B.
  2. Creó el centro `"Contabilidad"` en cada una con IDs únicos (`ID=1` e `ID=2`), validando que no colisionaran.
  3. Creó usuarios asignados a sus respectivas empresas y centros.
  4. Comprobó que cada usuario apunta a su correspondiente ID estructurado separado, pero que ambos devuelven `"Contabilidad"` mediante el property compatible de Python.
  5. Limpió la base de datos de forma segura al finalizar.
  - **Estatus:** 🎉 PASÓ al 100% con éxito rotundo.

### B. Suite de Pruebas de API y QA Completa (`qa_bloques_bc.py`)
* **Comando:** `docker exec ricoh-backend python /app/qa_bloques_bc.py`
* **Resultados:** **27/27 checks pasaron con éxito rotundo**, validando cierres, comparaciones, multi-tenancy analítico, e importación de Excel.

### C. Suite de Imports y Arquitectura (`verify_session_29mayo.py`)
* **Comando:** `docker exec ricoh-backend python /app/verify_session_29mayo.py`
* **Resultados:** **10/10 checks pasaron con éxito rotundo**, garantizando la correcta compilación de SQLAlchemy.

---

*Documento técnico de cierre de migración.*  
*Ricoh Fleet Management Suite — 2026.*
