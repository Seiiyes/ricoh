# Credenciales de Seguridad del Sistema

Este documento contiene un registro unificado de todas las credenciales de seguridad, usuarios y claves utilizadas en el proyecto Ricoh Equipment Manager para los entornos de desarrollo local y el servidor de produccion.

---

## 1. Servidor de Produccion (Acceso SSH)

Estas son las credenciales para conectarse de forma remota a la maquina host del servidor:

*   **Direccion IP (Host)**: 192.168.91.131
*   **Puerto**: 22 (SSH estandar)
*   **Usuario**: odootic
*   **Contrasena**: Zuly152325*
*   **Ubicacion del Proyecto**: `/home/odootic/ricoh-app/`

---

## 2. Aplicacion Web (Usuarios del Negocio)

Estas credenciales corresponden a las cuentas para ingresar a la interfaz web de administracion:

*   **Superadministrador (Local y Produccion)**:
    *   Usuario: `superadmin`
    *   Contrasena: `ricoh2026`
*   **Administrador de Empresa (Prueba local)**:
    *   Usuario: `admin`
    *   Contrasena: `ricoh2026`

---

## 3. Microservicio de Auditoria de Seguridad (Audit Portal - Puerto 8088)

Portal independiente para consultar los logs operacionales guardados en SQLite:

*   **Acceso Web**: `http://192.168.91.131:8088` (en produccion) o `http://localhost:8088` (en local)
*   **Usuario por defecto**: `admin_audit`
*   **Contrasena por defecto**: `ricohLogs2026`
*   **Hash Bcrypt correspondiente**: `$2b$12$Kk6d3G1S...` (generado mediante script utilitario)
*   **Formato de definicion en .env**:
    `AUDIT_USERS="admin_audit:$$2b$$12$$X2ZfJpYt3H6K9rD3Q6L8u.Zz7vJ8Q2Bv8g2K6h7o3p1q4r5s6t7u8"` (los signos de dolar se duplican para evitar conflictos con Docker Compose).

---

## 4. Documentacion de la API (Swagger / ReDoc)

Los endpoints de documentacion interactiva de FastAPI estan protegidos con autenticacion basica:

*   **Ruta**: `http://localhost:8000/docs` o `http://localhost:8000/redoc`
*   **Usuario**: `admin`
*   **Contrasena**: `ricoh_docs_2026`

---

## 5. Contenedores de Base de Datos y Cache (Local / Docker Compose)

Estas son las contraseñas utilizadas internamente para la intercomunicacion de servicios en local:

### 5.1 PostgreSQL 16 (Base de Datos Operacional)
*   **Base de datos**: `ricoh_fleet`
*   **Usuario**: `ricoh_admin`
*   **Contrasena**: `ricoh_secure_2024`
*   **Puerto de exposicion local**: `5433` (mapeado al `5432` interno)
*   **URL de Conexion**: `postgresql://ricoh_admin:ricoh_secure_2024@postgres:5432/ricoh_fleet`

### 5.2 Redis 7 (Cache y Limiter)
*   **Contrasena**: `aoRJay23ZiakmfggESo5ASkYWG52ohk_lg`
*   **URL de Conexion**: `redis://:aoRJay23ZiakmfggESo5ASkYWG52ohk_lg@redis:6379/0`

### 5.3 Claves de Firmado y Cifrado (JWT & AES-256)
*   **Clave de Cifrado AES-256 (ENCRYPTION_KEY)**: `jcM2RoP9ztYz5Ffg73TeoStDUPtY9CqwHStMheQ3Bn0=` (se usa para proteger las credenciales SMB de los usuarios en base de datos).
*   **Clave de Firmado JWT (SECRET_KEY)**: `MHbJvvYdMZFrzuBsaW6XmjaaiRWJD8f8AUUQecUbP6s`

---

## 6. Impresoras Fisicas Ricoh (Web Image Monitor)

*   **Contrasena de administrador Ricoh (por defecto)**: `Admin123!` o `admin` (inyectada por el backend en las conexiones WIM mediante la variable de entorno `RICOH_ADMIN_PASSWORD`).
