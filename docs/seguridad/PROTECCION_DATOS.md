# 🔒 Protección de Datos - Guía Rápida

## ✅ Ya está Configurado

Tu proyecto ahora tiene protección automática de datos. Ya se creó el primer respaldo.

---

## 🎯 Uso Diario

### Antes de Hacer Cambios Importantes

Ejecuta este comando:

```cmd
backup-db.bat
```

Esto guarda todos tus usuarios e impresoras en un archivo.

### Si Algo Sale Mal

Ejecuta este comando:

```cmd
restore-db.bat
```

Selecciona el respaldo que quieres recuperar.

---

## 📅 Cuándo Crear Respaldos

✅ **Antes de cambiar de computadora**
✅ **Antes de actualizar el código**
✅ **Al final de cada día de trabajo**
✅ **Después de agregar muchos usuarios**
✅ **Antes de probar cosas nuevas**

---

## 💾 Dónde Están los Respaldos

Los archivos se guardan en la carpeta `backups/`

Ejemplo: `backups/ricoh_backup_20260218_143022.sql`

---

## ☁️ Subir a la Nube (Recomendado)

### Opción 1: GitHub (Ya lo tienes)

```cmd
git add backups/
git commit -m "Respaldo de base de datos"
git push
```

### Opción 2: OneDrive (Automático)

1. Copia la carpeta `backups/` a tu OneDrive
2. Se sincroniza automáticamente

### Opción 3: Google Drive

1. Instala Google Drive Desktop
2. Copia la carpeta `backups/` a Google Drive
3. Se sincroniza automáticamente

---

## 🔄 Cambiar de Computadora

### En la Computadora Vieja:

1. Ejecuta `backup-db.bat`
2. Sube a GitHub: `git push`
3. O copia la carpeta `backups/` a USB

### En la Computadora Nueva:

1. Clona el proyecto: `git clone ...`
2. Inicia Docker: `docker-compose up -d`
3. Restaura datos: `restore-db.bat`
4. ¡Listo! Todos tus datos están de vuelta

---

## 📊 Archivos Creados

- ✅ `backup-db.bat` - Crear respaldo (con mensajes)
- ✅ `backup-rapido.bat` - Crear respaldo (rápido, sin pausas)
- ✅ `restore-db.bat` - Restaurar respaldo
- ✅ `backups/` - Carpeta con respaldos
- ✅ `backups/README.md` - Documentación de respaldos
- ✅ Primer respaldo ya creado ✓

---

## 🆘 Ayuda Rápida

### Ver qué hay en la base de datos

```cmd
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT COUNT(*) FROM users;"
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT COUNT(*) FROM printers;"
```

### Ver tamaño de la base de datos

```cmd
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT pg_size_pretty(pg_database_size('ricoh_fleet'));"
```

### Listar todos los respaldos

```cmd
dir backups\*.sql
```

---

## ⚠️ Importante

- Los respaldos son **muy pequeños** (menos de 100 KB normalmente)
- **No ocupan espacio** en GitHub
- Son **archivos de texto** que puedes abrir y ver
- Contienen **toda la información** de usuarios e impresoras

---

## 🎉 ¡Ya Estás Protegido!

Ahora puedes trabajar tranquilo sabiendo que tus datos están seguros.

**Recuerda:** Haz un respaldo antes de cualquier cambio importante.

---

**Fecha:** 18 de Febrero de 2026  
**Estado:** ✅ Configurado y Funcionando
