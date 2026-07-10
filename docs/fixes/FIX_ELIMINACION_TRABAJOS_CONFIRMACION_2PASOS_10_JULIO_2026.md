# Corrección del Flujo de Eliminación de Trabajos de Impresión mediante Confirmación en Dos Pasos (WIM)

**Fecha:** 10 de Julio de 2026  
**Área:** Backend (Scraper / Cliente Web Ricoh) & API REST  
**Equipos Afectados:** Impresoras Ricoh (Modelo MP C4503 y similares)  

---

## 1. Contexto del Problema

Se reportó que los trabajos de **Impresión Bloqueada (Locked Print)** enviados por los usuarios no podían ser eliminados desde la interfaz web del sistema, a pesar de que el frontend reportaba éxito. Los trabajos continuaban listados y ocupando memoria en el disco duro físico de las impresoras.

---

## 2. Diagnóstico Técnico y Descubrimiento

1. **Falso Positivo de HTTP 200:**
   El firmware del Web Image Monitor (WIM) de las impresoras Ricoh siempre retorna código de estado `HTTP 200 OK` en cualquier envío POST al endpoint `/web/entry/es/webprinter/storedJob.cgi`, incluso si la acción falla o no se completa.
   
2. **El Flujo de Confirmación Intermedio (Browser vs. Script):**
   * Al hacer clic en "Eliminar" en WIM, el navegador web envía una petición POST inicial. 
   * Sin embargo, esta petición inicial **no elimina el trabajo**; el servidor de la impresora responde con una página HTML de confirmación intermedia que le pregunta al usuario: *¿Desea eliminar los siguientes trabajos?*
   * En esta página de confirmación, se genera un formulario oculto llamado `<form name="hideform">`.
   * El botón "Aceptar" físico de la página ejecuta la función JavaScript `Exec()`, que se encuentra definida en el script `common.js` de la impresora:
     ```javascript
     function Exec() {
       if (document.hideform) {
         document.hideform.mode.value = "3"; // Cambia el mode a "3"
         mysubmit(document.hideform);         // Hace el submit real
       } else {
         location.reload(true);
       }
     }
     ```
   * Al no enviar este segundo POST con `mode=3` y los campos de `hideform` (`baseID`, `kind`, etc.), la impresora descartaba la orden de eliminación.

---

## 3. Solución Implementada

Se actualizó el cliente web en [ricoh_web_client.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/backend/services/ricoh_web_client.py) para automatizar este flujo de dos pasos:

1. **Envío de Petición de Intento Inicial:**
   Se envía la petición POST con los parámetros del listado general (incluyendo el checkbox de selección `ID` y los `display_ID`s).

2. **Detección y Envío de la Confirmación:**
   El backend analiza la respuesta HTML. Si detecta la presencia del formulario `<form name="hideform">`:
   * Extrae dinámicamente todos los elementos `<input>` del formulario de confirmación.
   * Modifica el campo `mode` al valor `'3'` para simular la ejecución del JS `Exec()`.
   * Realiza un segundo POST inmediato al endpoint `storedJob.cgi` con este payload consolidado.

3. **Verificación Real Post-Ejecución:**
   Para evitar falsos positivos, se implementó un tiempo de espera de 2 segundos seguido de un **GET fresco independiente** a la lista de trabajos de impresión, garantizando que el `job_id` realmente haya sido removido de la cola física del equipo.

4. **Tratamiento de Errores e Información al Usuario:**
   Se modificó [api/printers.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/backend/api/printers.py) para que, en caso de fallo real, lance un mensaje descriptivo en el API:
   > *"No fue posible eliminar el trabajo X de la impresora. Los trabajos de IMPRESIÓN BLOQUEADA solo pueden eliminarse desde el panel físico de la impresora o por el usuario que los envió (requiere PIN)."* (En caso de que el firmware rechace la operación por PIN).

---

## 4. Pruebas y Verificación en Producción

* Se ejecutó el script de diagnóstico [diagnose_locked_jobs.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/deployment/diagnose_locked_jobs.py) simulando el flujo de dos pasos y se comprobó la eliminación definitiva.
* Se desplegó el código en caliente y se realizaron pruebas desde el frontend eliminando trabajos reales de usuario **JUANL** (ID 438 y similares) en la impresora `192.168.91.251`.
* **Resultado:** Los trabajos se eliminaron exitosamente y en vivo, y los logs del contenedor backend confirmaron el procesamiento de la confirmación (`mode=3`) y la posterior verificación con GET limpio.
