# Corrección de Compatibilidad en Contraseña de Escáner y Permisos de Color

**Fecha:** 08 de Julio de 2026  
**Área:** Backend (Servicios Web Ricoh) & Frontend (Suite de Administración)  
**Equipos Afectados:** Impresoras multifuncionales Ricoh (Gamas 250, 252, 253, 251)  

---

## 1. Contexto del Problema

Se reportaron incidencias críticas en dos flujos principales relacionados con la libreta de direcciones en las impresoras físicas:
1. **Permisos de Color Indeseados:** Al sincronizar usuarios con permisos exclusivamente en Blanco y Negro, las impresoras terminaban con casillas de color intermedias como "Dos colores" (`TC`) y "Color personalizado" (`MC`) activadas.
2. **Fallo en Autenticación de Escáner:** Al enviar los permisos/carpeta desde el sistema web, el escáner a carpeta local (`SMB`) dejaba de funcionar de inmediato en las impresoras, arrojando el error *"Verifique el acceso"* o *"Error de Autenticación"*. Sin embargo, al configurar manualmente la misma contraseña mediante Web Image Monitor (WIM), el escáner funcionaba correctamente.

---

## 2. Diagnóstico Técnico y Solución

Tras una auditoría detallada de las peticiones HTTP/POST en WIM y trazas capturadas en vivo, se identificaron y solucionaron las siguientes causas:

### A. Mapeo de Permisos de Color (`TC` y `MC`)
* **Causa:** En la lógica de mapeo del backend, las opciones de color intermedio `TC` (Dos colores) y `MC` (Color personalizado) estaban erróneamente condicionadas al permiso básico de copiadora en blanco y negro.
* **Solución:** Se ajustaron las condiciones de negocio en [ricoh_web_client.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/backend/services/ricoh_web_client.py) para que tanto `TC` como `MC` dependan de manera estricta del flag `copiadora_color`. Si el usuario no tiene color en la Suite, estas opciones de color se desmarcan y desactivan de inmediato en la impresora.

### B. Mapeo Universal de Campos de Contraseña WIM
* **Causa:** El backend enviaba la contraseña codificada en Base64 utilizando los campos `wkpasswordIn` y `wkpasswordConfirmIn`. Los modelos de Ricoh más recientes ignoran estas variables (esperando `passwordIn` / `passwordConfirmIn`), lo que provocaba que se guardara una contraseña vacía.
* **Solución:** Se actualizó [ricoh_password_flow.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/backend/services/ricoh_password_flow.py) para enviar la clave Base64 en ambas variaciones de forma simultánea, garantizando la compatibilidad universal en todas las gamas de impresoras.

### C. Consolidación de Contraseña Temporal
* **Causa:** En el guardado final consolidado (`adrsSetUser.cgi`), el backend enviaba el parámetro `'isFolderAuthPasswordUpdated': 'true'`. En modelos de Ricoh nuevos, este flag le dice a la impresora que busque y lea la contraseña de nuevo en el mismo payload del POST. Al no venir en ese formulario, la impresora sobrescribía la contraseña temporal que se ingresó en la subpantalla y la dejaba vacía.
* **Solución:** Cambiamos el parámetro a `'isFolderAuthPasswordUpdated': 'false'` para emular el comportamiento exacto del navegador web. Con esto, la impresora consolida y bloquea de manera fidedigna la contraseña temporal guardada previamente en la subpantalla.

### D. Resiliencia ante Estados `BUSY` / `TIMEOUT`
* **Validación de Integridad:** Si la impresora devuelve una página WIM vacía o corrupta por timeout de sesión web, el parser detecta la ausencia de los inputs del formulario y aborta el intento marcándolo como `TIMEOUT` en lugar de guardar datos vacíos o inconsistentes.
* **Persistencia Aumentada:** Incrementamos la lógica de reintentos para impresoras ocupadas de **4 a 12 intentos consecutivos** (esperando 4 segundos entre ellos), permitiendo al backend esperar hasta un minuto completo a que se libere la libreta de direcciones antes de fallar.
* **Fallo Estricto:** La función `update_user_in_printer` ahora propaga un `False` real si la contraseña de carpeta falla, lo que obliga al API a registrar el error y reintentar, en lugar de continuar silenciosamente.

### E. Feedback Visual en Frontend
* Modificamos [ModificarUsuario.tsx](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/components/usuarios/ModificarUsuario.tsx) para actualizar el mensaje de notificación de éxito:
  * *Individual:* `"Los permisos y la contraseña de la carpeta de escaneo se enviaron y configuraron exitosamente en vivo..."`
  * *Masivo:* `"El perfil del usuario fue guardado y sus permisos base junto con la contraseña del escáner se aplicaron con éxito en todas las impresoras..."`

---

## 3. Impacto y Verificación de Pruebas

Las correcciones se desplegaron en producción y se verificaron con pruebas en vivo junto con el usuario:
* **Prueba de Autenticación de Escáner:** Se comprobó físicamente en las impresoras **`192.168.91.250`** y **`192.168.91.252`** usando la ruta de red `\\TIC0264\Escaner`.
* **Resultado:** La inyección de la contraseña de carpeta se ejecutó con éxito en WIM en el primer intento sin reportar error de autenticación, y **los escaneos llegaron de inmediato y sin problemas al PC del usuario**.
