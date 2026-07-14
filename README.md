# Ricoh Suite

Sistema integral de gestion de impresoras Ricoh con autentificacion JWT, multi-tenancy y cuatro modulos principales: Governance (Aprovisionamiento), Contadores, Cierres Mensuales y Gestion de Trabajos de Impresion.

**Version**: 4.1.7 | **Estado**: Activado en Produccion | **Ultima actualizacion**: 14 de Julio de 2026

---

## Estado Actual del Sistema

### Servidor de Produccion Activo y Funcionando
*   **Servidor**: Host local en produccion
*   **IP del Servidor**: 192.168.91.131
*   **Acceso Web**: http://192.168.91.131 (redirigido y controlado por Nginx)
*   **Portal de Logs de Auditoria**: http://192.168.91.131:8088

### Servicios de Produccion (Docker Compose)

| Servicio | Estado | Puerto Interno | Salud |
| :--- | :--- | :---: | :--- |
| ricoh-nginx | Running | 80 / 443 | Healthy |
| ricoh-frontend | Running | 80 | Healthy |
| ricoh-backend | Running | 8000 / 8088 | Healthy |
| ricoh-postgres | Running | 5432 | Healthy |
| ricoh-redis | Running | 6379 | Healthy |

---

## Inicio Rapido (Desarrollo Local)

### Opcion 1: Con Docker (Recomendado)
```cmd
docker-start.bat
```
Luego abra: http://localhost:5173

### Opcion 2: Ejecucion Manual Local

1. Iniciar Backend:
   ```cmd
   cd backend
   start-backend.bat
   ```
2. Iniciar Frontend:
   ```cmd
   start-dev.bat
   ```
3. Abrir navegador en: http://localhost:5173

---

## Modulos del Sistema

### 1. Autenticacion JWT y Multi-Tenancy
*   Login seguro con access token y refresh token JWT.
*   Device Binding (Seguridad por IP y navegador) que invalida la sesion si el token es copiado a otro dispositivo.
*   Aislamiento estricto de empresas (los administradores estandar no pueden ver recursos de otras organizaciones).
*   Modulo de administracion de empresas y usuarios administradores de soporte.

### 2. Governance (Aprovisionamiento de Usuarios)
*   Descubrimiento de impresoras activas en la red por escaneo de puertos.
*   Inyeccion automatizada de credenciales de red SMB (Scan-to-Folder) cifradas con AES-256 en la libreta fisica Ricoh.
*   Asignacion fina de privilegios de color (Copia/Impresion) por impresora.
*   Desactivacion logica (Soft Delete) de asignaciones que preserva el entry_index del usuario para evitar colisiones en la libreta.

### 3. Suministros y Contadores
*   Monitoreo visual del nivel de toners (Cyan, Magenta, Amarillo, Negro) y del estado online/offline en el dashboard.
*   Lectura en vivo de contadores del hardware y registro de consumos.

### 4. Cierres Mensuales y Analytics
*   Consolidacion de contadores mediante cierres individuales o cierres masivos concurrentes.
*   Comparativa grafica dinamica entre meses del consumo por usuario y departamento.
*   Exportacion oficial a Excel en tres hojas estructuradas (Resumen, Centros de Costos, Usuarios) con nombres basados en el serial del equipo.
*   Eliminacion de cierres errados protegida por confirmacion de accion irreversible.

### 5. Gestion de Trabajos de Impresion (Print Jobs)
*   Visualizacion consolidada de las colas de impresion de multiples impresoras en paralelo.
*   Eliminacion segura de trabajos (Locked Print/Normal) emulando la confirmacion en dos pasos (mode=3) en la interfaz WIM.

---

## Estructura de Documentacion (Carpeta docs/)

Toda la documentacion de diseño, DevOps y manuales reside en la carpeta `docs/` (y sincronizada en `/home/odootic/ricoh-app/docs/` en produccion):

*   **INDICE_DOCUMENTACION.md**: Indice general de todos los documentos y guias.
*   **CREDENCIALES_SISTEMA.md**: Manual de contraseñas de red, base de datos, backend y servidor.
*   **arquitectura/INFRAESTRUCTURA_Y_STACK_TECNOLOGICO.md**: Detalle de contenedores, redes Docker y volumenes.
*   **arquitectura/ARQUITECTURA_DETALLADA_Y_PATRONES.md**: Capas logicas de software (Clean Architecture) y patrones de diseño.
*   **arquitectura/ADR_DECISIONES_DISENO.md**: Registro historico de decisiones de diseño (ADR).
*   **arquitectura/DIAGRAMA_C4_MODEL.md**: Diagramas C4 del sistema en formato Mermaid.
*   **desarrollo/GUIA_CONFIGURACION_ENTORNO.md**: Setup local, dependencias, variables y formateadores.
*   **guias/HISTORIAS_USUARIO_Y_CRITERIOS_ACEPTACION.md**: Casos de uso e hitos de validacion QA.
*   **guias/GUIA_USUARIO.md**: Manual paso a paso de todas las funciones de la interfaz para el usuario final.
*   **deployment/PLAN_RECUPERACION_ANTE_DESASTRES.md**: Plan DRP de respaldos y restauracion.
*   **deployment/MONITOREO_Y_ALERTAS.md**: Ubicacion de logs de servicios y solucion rapida de incidencias.

---

## Desarrollo y Compilacion

### Requisitos locales:
*   Node.js v20.x
*   Python 3.11+
*   PostgreSQL 16 y Redis 7 (mediante Docker)

### Comandos utiles:
```bash
# Instalar dependencias locales de React
npm install

# Instalar dependencias de Python (activando entorno virtual)
pip install -r backend/requirements.txt

# Ver logs de Docker en vivo
docker-compose logs -f
```
