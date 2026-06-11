# Guía de Conexión a DBeaver y Acceso Superadmin

Esta guía detalla los pasos para conectarse a la base de datos remota mediante DBeaver y las credenciales de acceso para el usuario `superadmin` en el servidor **192.168.91.131**.

---

## 1. Conexión a la Base de Datos con DBeaver

El contenedor PostgreSQL en el servidor remoto expone el puerto **5433** para conexiones externas.

### Datos de Conexión
* **Motor / Driver**: PostgreSQL
* **Host / IP**: `192.168.91.131`
* **Puerto**: `5433`
* **Base de Datos (Database)**: `ricoh_fleet`
* **Usuario (Username)**: `ricoh_admin`
* **Contraseña (Password)**: `ricoh_secure_2024`

### Pasos en DBeaver:
1. Abre DBeaver y haz clic en **Nueva conexión de base de datos** (icono de enchufe con un signo +).
2. Selecciona **PostgreSQL** y presiona *Siguiente*.
3. En la pestaña **Main**, ingresa los datos anteriores:
   - Host: `192.168.91.131`
   - Port: `5433`
   - Database: `ricoh_fleet`
   - Username: `ricoh_admin`
   - Password: `ricoh_secure_2024`
4. Haz clic en **Probar conexión (Test Connection)** para comprobar que conecte exitosamente.
5. Presiona *Finalizar* para guardar la conexión.

---

## 2. Acceso a la Aplicación (Superadmin)

La aplicación web está disponible en el puerto HTTP estándar.

* **URL del Frontend**: [http://192.168.91.131](http://192.168.91.131)
* **Usuario**: `superadmin`

### Contraseña del Superadmin
La contraseña actual activa en la base de datos es:
👉 **`zRpKpcqC|A9{C3*w`**

*(Nota: En algunas configuraciones históricas de prueba se utilizó `{:Z75M!=x>9PiPp2`. Si la primera no funciona, puedes probar con esta).*

---

## 3. Cómo Restablecer/Regenerar la Contraseña del Superadmin

Si necesitas regenerar la contraseña del superadmin de forma segura en el servidor, puedes hacerlo ejecutando el script de inicialización desde la consola SSH:

1. Conéctate al servidor vía SSH:
   ```bash
   ssh odootic@192.168.91.131
   # Usa tu contraseña SSH de servidor
   ```

2. Ejecuta el script de inicialización dentro del contenedor backend:
   ```bash
   sudo docker exec -it ricoh-backend python scripts/init_superadmin.py
   ```

3. El comando generará una contraseña nueva y actualizará la base de datos automáticamente. Te mostrará un mensaje en pantalla indicándote que se actualizó.

4. Puedes consultar la contraseña generada en cualquier momento leyendo el archivo de clave temporal que se crea dentro del contenedor:
   ```bash
   sudo docker exec ricoh-backend cat .superadmin_password
   ```
