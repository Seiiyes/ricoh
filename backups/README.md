# 📦 Carpeta de Respaldos

Esta carpeta contiene los respaldos de la base de datos PostgreSQL.

## 🔒 Archivos de Respaldo

Los archivos tienen el formato: `ricoh_backup_AAAAMMDD_HHMMSS.sql`

Ejemplo: `ricoh_backup_20260218_143022.sql`

## 📝 Cómo Usar

### Crear un Respaldo

Ejecuta desde la raíz del proyecto:

```cmd
backup-db.bat
```

Esto creará un archivo `.sql` en esta carpeta con la fecha y hora actual.

### Restaurar un Respaldo

Ejecuta desde la raíz del proyecto:

```cmd
restore-db.bat
```

Sigue las instrucciones en pantalla para seleccionar el archivo a restaurar.

## ⚠️ Importante

- **Guarda estos archivos en un lugar seguro** (GitHub, OneDrive, Google Drive, USB)
- **Crea respaldos regularmente**, especialmente antes de:
  - Cambiar de equipo
  - Actualizar el código
  - Hacer cambios importantes en la base de datos
  - Probar nuevas funcionalidades

## 📊 Contenido de los Respaldos

Cada archivo `.sql` contiene:
- Todos los usuarios registrados
- Todas las impresoras registradas
- Todas las asignaciones usuario-impresora
- Configuraciones y metadatos

## 🔄 Sincronización con GitHub

Por defecto, estos archivos **SÍ se suben a GitHub**.

Si prefieres NO subirlos:
1. Abre `.gitignore` en la raíz del proyecto
2. Descomenta la línea: `# backups/*.sql`
3. Guarda el archivo

## 💾 Tamaño de los Archivos

- Base de datos vacía: ~5 KB
- Con 10 usuarios y 10 impresoras: ~10-20 KB
- Con 100 usuarios y 50 impresoras: ~50-100 KB

Los archivos son muy pequeños, así que no hay problema en subirlos a GitHub.

## 🆘 Recuperación de Emergencia

Si perdiste todos los respaldos:

1. Revisa el historial de Git: `git log --all -- backups/`
2. Busca en tu nube (OneDrive, Google Drive)
3. Revisa el volumen de Docker (puede tener datos antiguos)

---

**Última actualización:** 18 de Febrero de 2026
