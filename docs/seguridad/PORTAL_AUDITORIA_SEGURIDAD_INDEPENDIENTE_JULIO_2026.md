# Portal de Auditoría de Seguridad Independiente (Puerto 8088)

Este documento detalla el diseño, arquitectura y manual de operación del **Portal de Auditoría de Seguridad** de la Ricoh Suite, implementado como un microservicio completamente aislado en el puerto **`8088`**.

---

## 1. Arquitectura y Decisiones de Diseño

El portal de logs de seguridad y auditoría se diseñó bajo los siguientes pilares de rendimiento y seguridad:

* **Aislamiento de Rendimiento (SQLite)**: Para no degradar el rendimiento de la base de datos principal PostgreSQL transaccional con la escritura masiva de logs (como inicios de sesión, refrescos y validaciones de tokens de toda la Suite), los logs de seguridad se almacenan en una base de datos **SQLite local e independiente** (`/app/logs/security_audit.db`).
* **Volumen Persistente**: El archivo de SQLite reside dentro de un volumen persistente de Docker (`ricoh-backend-logs`), asegurando que las bitácoras no se pierdan ante reinicios del servidor, caídas o recreaciones de los contenedores.
* **Aislamiento de Seguridad (Bcrypt + JWT)**: El acceso al portal no valida contra la base de datos del sistema. En su lugar, utiliza usuarios y contraseñas (encriptadas con bcrypt) definidos en la variable de entorno `AUDIT_USERS` del archivo `.env` del servidor de producción. Al iniciar sesión, el portal expide un token JWT temporal con expiración de 30 minutos.
* **Paginación en Servidor (Server-Side Pagination)**: Si se registran decenas de miles de eventos en un día, abrir el log completo causaría lag en el cliente. El portal realiza consultas SQL optimizadas con índices (`LIMIT` y `OFFSET`) a nivel de backend para retornar únicamente 50 registros por página, garantizando una carga instantánea (menos de 50 milisegundos).

---

## 2. Gestión de Usuarios y Accesos (`AUDIT_USERS`)

Las credenciales para entrar al portal en el puerto `8088` están configuradas en el archivo `.env` del servidor a través de la variable `AUDIT_USERS`. Las contraseñas **no se guardan en texto plano** sino como hashes de bcrypt.

### 2.1 Generar Nuevas Credenciales
Para generar el hash bcrypt de una contraseña e integrarlo al `.env`, se provee el script utilitario local:
* **Archivo**: [generate_bcrypt_hash.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/deployment/generate_bcrypt_hash.py)
* **Comando**:
  ```bash
  python deployment/generate_bcrypt_hash.py
  ```
El script solicitará el usuario y la contraseña, y devolverá la línea exacta con el hash generado que debe colocarse en el `.env` del servidor.

> [!WARNING]
> Debido a que Docker Compose utiliza el signo de dólar (`$`) para la expansión de variables, los signos de dólar del hash bcrypt deben **duplicarse** (`$$`) al escribirse en el archivo `.env` para que se pasen de forma correcta (como un único `$`) al contenedor. El script utilitario realiza este proceso de escape automáticamente al generar el hash para producción.

### 2.2 Formato en el `.env` del Servidor
```env
AUDIT_USERS="nombre_usuario:$$2b$$12$$hash_bcrypt_escapado,otro_usuario:$$2b$$12$$otro_hash"
```

---

## 3. Guía de Uso del Portal Web

1. **Acceso**: Abra en cualquier navegador web la URL:
   `http://192.168.91.131:8088`
2. **Mini-Login**: Ingrese el usuario y la contraseña configurados en el `.env` (credenciales por defecto: `admin_audit` / `ricohLogs2026`).
3. **Listado de Fechas**: En el panel lateral izquierdo aparecerán listados de forma cronológica los días que poseen logs registrados. Haga clic en cualquiera de ellos.
4. **Visualización de Logs**: Se desplegará la bitácora del día seleccionado en el rango exacto de las `00:00:00` a las `23:59:59`.
5. **Detalles Avanzados**: Si un evento posee metadatos complejos en JSON, aparecerá un botón verde **`JSON`** al lado del mensaje. Haga clic en él para expandir y visualizar el contenido estructurado de la petición.
6. **Buscador en Vivo**: Ingrese un término en la barra de búsqueda superior para filtrar instantáneamente por IP, Ejecutor o Acción.
7. **Exportar a CSV**: Haga clic en el botón **`Exportar CSV`** para descargar inmediatamente la hoja de cálculo completa con los logs del día seleccionado.
