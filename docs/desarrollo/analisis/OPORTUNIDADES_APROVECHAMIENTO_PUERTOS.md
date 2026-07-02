# Oportunidades de Aprovechamiento de Puertos Abiertos — Ricoh Fleet Management

Este documento analiza cómo el proyecto de software actual puede sacar provecho de los puertos y servicios abiertos detectados en las impresoras Ricoh (especialmente la MP C4503 en `192.168.91.251`) para implementar nuevas funcionalidades de valor añadido.

---

## 1. Puerto 80: HTTP (Web Image Monitor)

Actualmente se utiliza para scraping de tóner, lectura y edición AJAX de la libreta de direcciones.

### Nuevas Oportunidades de Integración:
*   **Diagnóstico de Estado Físico en Tiempo Real:**
    *   *Cómo:* Consultar `getStatus.cgi` u otras respuestas AJAX de estado.
    *   *Funcionalidad:* Mostrar en el Dashboard si la impresora tiene atasco de papel, bandeja de papel vacía, puerta abierta o códigos de error del sistema (ej: SC542).
*   **Historial y Auditoría de Trabajos Local:**
    *   *Cómo:* Raspar las tablas de historial de trabajos locales guardados en el disco duro de la impresora.
    *   *Funcionalidad:* Cruzar las impresiones de los usuarios locales que no pasan por el servidor de impresión.
*   **Gestión Centralizada de Energía y Horarios:**
    *   *Cómo:* Simular llamadas POST de configuración a la sección de ahorro de energía.
    *   *Funcionalidad:* Programar apagados automáticos en horario no laboral directamente desde nuestro panel.

---

## 2. Puerto 21: FTP (File Transfer Protocol)

Este puerto está abierto y expone un servidor FTP interno de la impresora.

### Nuevas Oportunidades de Integración:
*   **Impresión Directa Sin Drivers (Direct PDF Print):**
    *   *Cómo:* Las impresoras Ricoh permiten imprimir archivos PDF o PostScript enviándolos directamente al directorio raíz del servidor FTP de la impresora.
    *   *Funcionalidad:* Crear un widget en el frontend donde el usuario arrastre un PDF y nuestro backend lo suba vía FTP a la impresora, imprimiéndolo de inmediato sin necesidad de instalar controladores en el PC del cliente.
*   **Copia de Seguridad Rápida de la Libreta de Direcciones:**
    *   *Cómo:* Acceder a la descarga del archivo de configuración de contactos a través de comandos FTP (en modelos que lo soportan).
    *   *Funcionalidad:* Respaldar toda la agenda de una impresora en un solo archivo binario/CSV en lugar de paginar con Web Image Monitor.

---

## 3. Puerto 23: Telnet (MSH - Ricoh Maintenance Shell)

Está abierto y esperando autenticación de credenciales de CLI.

### Nuevas Oportunidades de Integración (Requiere credenciales CLI):
*   **Comandos de Diagnóstico Ultra-Rápidos:**
    *   *Cómo:* Ejecutar comandos de línea como `status`, `info`, `netstat`, `syslog` o `prtcfg` vía SSH/Telnet.
    *   *Funcionalidad:* Leer datos de red y estado físico en formato de texto plano estructurado en milisegundos, evitando el sobrecosto de procesar pesadas páginas HTML por el puerto 80.
*   **Reinicio Remoto:**
    *   *Cómo:* Enviar el comando `reboot` desde la consola de Telnet.
    *   *Funcionalidad:* Añadir un botón "Reiniciar Equipo" en el panel de administración para liberar la memoria o desbloquear el equipo si queda en estado bloqueado (BUSY) de red local.

---

## 4. Puerto 9100 / 515 / 631: Impresión de Red (RAW, LPR, IPP)

Son los puertos de cola de impresión del dispositivo.

### Nuevas Oportunidades de Integración:
*   **Servidor de Impresión Seguro y Retenida (Print Release / Pull Printing):**
    *   *Cómo:* Configurar nuestro servidor `192.168.91.131` como servidor de impresión central (Spooler) y redireccionar los puertos de impresión.
    *   *Funcionalidad:* El usuario envía a imprimir a la cola del servidor. El trabajo queda retenido (pausado). El usuario va a la impresora, digita su código en nuestra app (o pasa tarjeta RFID) y el servidor libera el archivo directamente al puerto 9100 de la impresora seleccionada.
*   **Contabilidad Exacta de Impresiones por Software:**
    *   *Cómo:* Capturar los flujos de impresión (PCL/PostScript) antes de enviarlos a la impresora para analizar el metadato del archivo (páginas reales, color vs B/N, tamaño de papel).

---

## 5. Salida de Cliente SFTP (Transmisión SFTP en la Impresora)

Aunque el puerto 22 entrante de la impresora está cerrado, el cliente SFTP está **Activo** para transmisiones de salida.

### Nuevas Oportunidades de Integración:
*   **Buzón de Escaneo Centralizado (Scan-to-SFTP Portal):**
    *   *Cómo:* El servidor local (`192.168.91.131`) ya ejecuta un servidor SSH/SFTP. Se pueden registrar perfiles de escaneo SFTP apuntando a nuestro servidor.
    *   *Funcionalidad:* Cuando el usuario escanea en la máquina, el PDF viaja de forma encriptada al servidor y nuestra aplicación web lo almacena e indexa automáticamente en la cuenta del usuario, notificándole en el portal web que tiene un nuevo escaneo disponible para descarga. Esto reemplaza a las carpetas SMB compartidas, las cuales son propensas a fallos de permisos en Windows.
