#  Registro de Decisiones de Arquitectura (ADR)

Este documento registra de forma histórica las decisiones arquitectónicas clave tomadas en **Ricoh Equipment Manager**, detallando el contexto, las alternativas evaluadas y la justificación técnica de cada elección.

---

## ️ ADR 01: Zustand en lugar de Redux Toolkit para Gestión de Estado

*   **Estado**:  Aceptado
*   **Fecha**: 18 de Marzo de 2026

### Contexto
El frontend de la aplicación (React) gestiona múltiples estados compartidos: listado de impresoras de la flota, usuarios de red, logs en tiempo real vía WebSockets y flujos de selección múltiple. Redux Toolkit fue evaluado debido a su robustez, pero añade un excesivo código repetitivo (actions, reducers, extraReducers) que ralentiza el desarrollo de características ágiles.

### Decisión
Adoptar **Zustand** como la librería principal de gestión de estado global.

### Consecuencias
*   **Positivas**: Reducción del código de estado en más del 65%. Las stores son funciones simples de TypeScript que pueden ser consumidas directamente mediante hooks sin envolver la app en `Providers` redundantes.
*   **Negativas**: Menor madurez en herramientas de depuración comparado con Redux DevTools, pero suficiente para los requisitos del proyecto.

---

## ️ ADR 02: SQLite Aislado para Portal de Auditoría de Seguridad (Puerto 8088)

*   **Estado**:  Aceptado
*   **Fecha**: 07 de Julio de 2026

### Contexto
El sistema requiere registrar eventos de seguridad críticos (logins, fallos de tokens, logs de acceso) en tiempo real. Escribir cada uno de estos accesos en la base de datos principal PostgreSQL podría causar bloqueos o problemas de rendimiento durante auditorías masivas de sincronización de equipos Ricoh.

### Decisión
Diseñar un microservicio ligero ejecutándose de forma aislada en el puerto `8088` utilizando **SQLite** local persistido en volumen de Docker como motor de base de datos único para logs.

### Consecuencias
*   **Positivas**: El portal de logs sigue funcionando incluso si la base de datos PostgreSQL principal se detiene. El rendimiento de escritura no colisiona con el del PostgreSQL principal del negocio.
*   **Negativas**: Los datos de auditoría están descentralizados de la base de datos principal, lo cual requiere respaldos independientes para el archivo SQLite (`audit.db`).

---

## ️ ADR 03: Desactivación Lógica en Impresoras en lugar de Eliminación Física (Preservación de entry_index)

*   **Estado**:  Aceptado
*   **Fecha**: 24 de Junio de 2026

### Contexto
Originalmente, al desasignar un usuario de una impresora en la interfaz, se ejecutaba una eliminación física (`DELETE`) en la libreta de direcciones física de la impresora Ricoh. Esto eliminaba el `entry_index` del usuario asignado. Sin embargo, al reaprovisionar al usuario más adelante, el firmware le asignaba un nuevo índice físico aleatorio, provocando colisiones graves con usuarios existentes u omitidos por el scraper.

### Decisión
Migrar todas las eliminaciones a **desactivación lógica** (`is_active = False` y deshabilitar temporalmente los permisos de color/copias en el firmware), manteniendo el registro y su `entry_index` intacto en la libreta de la impresora.

### Consecuencias
*   **Positivas**: Se eliminaron por completo las colisiones físicas de usuarios al volver a enrolarlos. Las impresoras conservan de forma consistente la identidad física del usuario.
*   **Negativas**: La libreta de direcciones física se llena más rápido con registros "inactivos", pero la flota Ricoh soporta hasta 2000-5000 entradas, lo cual excede por mucho las necesidades de las empresas asignadas.

---

## ️ ADR 04: Scraping de Web Image Monitor (WIM) sobre SNMP/API nativa

*   **Estado**:  Aceptado
*   **Fecha**: 29 de Abril de 2026

### Contexto
Las impresoras Ricoh no exponen una API REST documentada o estándar para la manipulación de usuarios, PINs de acceso y credenciales de escáner SMB de red. El protocolo SNMP (`Simple Network Management Protocol`) solo permite lectura de contadores genéricos e información básica de hardware, pero no permite la escritura ni inyección segura de contraseñas de red.

### Decisión
Construir un cliente web automatizado (`RicohWebClient`) basado en scraping HTTP simulando navegación de usuario (emulando peticiones POST/GET de Web Image Monitor) e integrando Selenium headless para operaciones Javascript complejas.

### Consecuencias
*   **Positivas**: Permite control absoluto sobre las funciones del panel físico Ricoh (PINs, cuotas, restricciones de color, inyección de credenciales de escaneo de red).
*   **Negativas**: Alta dependencia del diseño y firmware web de Ricoh. Si Ricoh actualiza drásticamente la interfaz web de sus modelos, se debe actualizar la lógica del adaptador en el backend.
