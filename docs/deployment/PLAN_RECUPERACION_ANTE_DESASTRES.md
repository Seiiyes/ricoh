#  Plan de Recuperación ante Desastres (Disaster Recovery Plan - DRP)

Este documento contiene las instrucciones críticas, comandos y procedimientos de respaldo necesarios para restaurar la operatividad de **Ricoh Equipment Manager** en caso de fallos del servidor, corrupción de base de datos o fallas críticas del sistema.

---

##  1. Estrategia de Copias de Seguridad (Backups)

El sistema utiliza dos bases de datos que requieren políticas de respaldo independientes:

### 1.1 Base de Datos PostgreSQL (Datos Operacionales)
PostgreSQL se ejecuta dentro del contenedor `ricoh-postgres`. Su volumen físico se almacena en `ricoh-postgres-data`.

*   **Ubicación de Backups**: `/app/backups/` o raíz del proyecto en local.
*   **Comando de Respaldo Manual**:
    ```bash
    # Ejecuta pg_dump dentro del contenedor y guarda el archivo SQL en el host
    docker exec -t ricoh-postgres pg_dump -U ricoh_admin -d ricoh_fleet > backup_db_$(date +%F).sql
    ```

### 1.2 Base de Datos SQLite (Logs de Auditoría)
La base de datos de auditoría se almacena en el volumen persistente `ricoh-backend-logs` como el archivo `audit.db` dentro del directorio `/app/logs/` del backend.

*   **Comando de Respaldo**:
    ```bash
    # Copia el archivo SQLite de logs a un directorio seguro
    cp ./backend/logs/audit.db backup_audit_$(date +%F).db
    ```

---

##  2. Procedimiento de Restauración (Recovery)

En caso de corrupción de datos o al migrar a un nuevo servidor de producción, sigue estos pasos secuenciales:

### Paso 1: Levantar infraestructura vacía
Inicia los contenedores PostgreSQL y Redis asegurando que no contengan datos corruptos:
```bash
# Apagar contenedores actuales y borrar volúmenes
docker-compose down -v

# Levantar bases de datos limpias
docker-compose up -d postgres redis
```

### Paso 2: Esperar a que la base de datos esté lista
Verifica que PostgreSQL esté respondiendo consultas:
```bash
docker exec -it ricoh-postgres pg_isready -U ricoh_admin
```

### Paso 3: Restaurar el volcado SQL (Dump)
Ejecuta la restauración del último archivo de respaldo válido:
```bash
# Importar el dump SQL al contenedor de base de datos
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet < backup_db_VALIDO.sql
```

### Paso 4: Levantar el resto de servicios
Una vez restaurados los datos operacionales, inicia la aplicación web y el proxy inverso:
```bash
docker-compose up -d backend frontend nginx
```

---

##  3. Diagnóstico y Escenarios Críticos

### Escenario A: El contenedor Postgres no inicia por corrupción en disco
*   **Síntoma**: `docker-compose logs postgres` muestra "database system was not cleanly shut down" o errores de checkpoints corruptos.
*   **Solución**:
    1.  Detén el contenedor: `docker-compose down`.
    2.  Haz copia de seguridad física de la carpeta del volumen: `cp -r /var/lib/docker/volumes/ricoh-postgres-data /var/tmp/`.
    3.  Limpia el volumen: `docker volume rm ricoh-postgres-data`.
    4.  Vuelve a iniciar el contenedor con un volumen limpio: `docker-compose up -d postgres`.
    5.  Restaura desde el último volcado SQL utilizando el **Procedimiento de Restauración**.

### Escenario B: Fuga de memoria en Redis bloquea las peticiones de Rate Limit
*   **Síntoma**: Errores `HTTP 500` con trazas de error de conexión a Redis en los logs de la API.
*   **Solución**:
    1.  Reinicia el servicio de caché:
        ```bash
        docker-compose restart redis
        ```
    2.  Si el problema persiste, vacía el caché almacenado (esto invalidará sesiones y tokens CSRF activos, forzando re-login de usuarios, pero liberará la memoria):
        ```bash
        docker exec -it ricoh-redis redis-cli -a TU_PASSWORD_REDIS flushall
        ```
