# Scripts de Backend

Esta carpeta contiene scripts de utilidad que fueron usados durante el desarrollo y mantenimiento del sistema.

## 📁 Estructura

### `/analisis/`
Scripts para analizar datos CSV y contadores.
- Análisis de estructura de archivos CSV
- Comparación de datos entre períodos
- Detección de inconsistencias

### `/verificacion/`
Scripts para verificar integridad de datos.
- Verificación de importaciones
- Validación de cálculos
- Comprobación de coherencia de datos

### `/importacion/`
Scripts para importar cierres históricos desde CSV.
- Importación de cierres mensuales
- Validación de estructura CSV
- Pre-verificación de datos

### `/utilidades/`
Scripts de utilidad general.
- Corrección de datos
- Extracción de información
- Comparaciones y reportes

## ⚠️ Importante

Estos scripts son principalmente para uso one-time o debugging.
NO son parte del sistema en producción.

Para funcionalidad de producción, usa:
- `backend/api/` - Endpoints REST
- `backend/services/` - Servicios de negocio
- `backend/parsear_*.py` - Parsers de HTML Ricoh
