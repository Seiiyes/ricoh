# 🔐 Cómo Cambiar la Contraseña de PostgreSQL

**Fecha**: 6 de Mayo 2026  
**Problema**: PostgreSQL ya existe con contraseña anterior

---

## ⚠️ Situación Actual

**Contraseña Actual en PostgreSQL**: `ricoh_secure_2024`  
**Contraseña Nueva Generada**: `fMWBz1vJKtqXTefOQOWs_pRlsrFir2fMxw`

**Problema**: El contenedor de PostgreSQL ya existe con la contraseña antigua. Cambiar `POSTGRES_PASSWORD` en docker-compose.yml NO actualiza la contraseña en PostgreSQL existente.

---

## ✅ Solución Aplicada (Temporal)

Volvimos a usar la contraseña anterior para que el sistema funcione:

```yaml
POSTGRES_PASSWORD: ricoh_secure_2024
DATABASE_URL: postgresql://ricoh_admin:ricoh_secure_2024@postgres:5432/ricoh_fleet
```

**Estado**: ✅ Sistema funcionando

---

## 🔄 Cómo Cambiar la Contraseña (Cuando Quieras)

### Opción 1: Cambiar Contraseña en PostgreSQL Existente (Recomendado)

**Ventaja**: Mantiene todos los datos  
**Desventaja**: Requiere varios pasos

#### Paso 1: Conectar a PostgreSQL

```bash
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_fleet
```

#### Paso 2: Cambiar Contraseña

```sql
ALTER USER ricoh_admin WITH PASSWORD 'fMWBz1vJKtqXTefOQOWs_pRlsrFir2fMxw';
\q
```

#### Paso 3: Actualizar docker-compose.yml

```yaml
# En postgres service
POSTGRES_PASSWORD: fMWBz1vJKtqXTefOQOWs_pRlsrFir2fMxw

# En backend service
DATABASE_URL: postgresql://ricoh_admin:fMWBz1vJKtqXTefOQOWs_pRlsrFir2fMxw@postgres:5432/ricoh_fleet
```

#### Paso 4: Reiniciar Backend

```bash
docker-compose restart backend
```

---

### Opción 2: Recrear PostgreSQL (Pierde Datos)

**Ventaja**: Limpio y simple  
**Desventaja**: ⚠️ PIERDE TODOS LOS DATOS

#### Paso 1: Hacer Backup (OBLIGATORIO)

```bash
docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > backup_antes_cambio_password.sql
```

#### Paso 2: Detener y Eliminar Contenedor y Volumen

```bash
docker-compose down
docker volume rm ricoh-postgres-data
```

#### Paso 3: Actualizar docker-compose.yml

```yaml
# En postgres service
POSTGRES_PASSWORD: fMWBz1vJKtqXTefOQOWs_pRlsrFir2fMxw

# En backend service
DATABASE_URL: postgresql://ricoh_admin:fMWBz1vJKtqXTefOQOWs_pRlsrFir2fMxw@postgres:5432/ricoh_fleet
```

#### Paso 4: Iniciar Servicios

```bash
docker-compose up -d
```

#### Paso 5: Restaurar Backup

```bash
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet < backup_antes_cambio_password.sql
```

---

## 💡 Recomendación

**Para desarrollo local**: Mantener contraseña actual (`ricoh_secure_2024`)

**Razones**:
- ✅ Sistema ya funciona
- ✅ No hay riesgo de pérdida de datos
- ✅ Contraseña suficientemente segura para desarrollo local
- ✅ Evita complejidad innecesaria

**Para producción**: Usar contraseña nueva cuando migres a servidor

---

## 📊 Comparativa de Contraseñas

| Aspecto | Actual | Nueva |
|---------|--------|-------|
| **Contraseña** | ricoh_secure_2024 | fMWBz1vJKtqXTefOQOWs_pRlsrFir2fMxw |
| **Longitud** | 17 caracteres | 34 caracteres |
| **Entropía** | Media | Alta |
| **Seguridad** | ✅ Buena para desarrollo | ✅ Excelente para producción |
| **Estado** | ✅ Funcionando | ⚠️ Disponible para usar |

---

## ✅ Resumen

### Estado Actual

- **Contraseña PostgreSQL**: `ricoh_secure_2024` ✅
- **Sistema**: Funcionando ✅
- **Datos**: Intactos ✅

### Contraseña Nueva Disponible

- **Contraseña**: `fMWBz1vJKtqXTefOQOWs_pRlsrFir2fMxw`
- **Ubicación**: `CREDENCIALES_SEGURAS_6_MAYO_2026.txt`
- **Uso**: Cuando migres a producción

---

## 🎯 Conclusión

**No es necesario cambiar la contraseña ahora**

La contraseña actual (`ricoh_secure_2024`) es:
- ✅ Suficientemente segura para desarrollo local
- ✅ Ya está funcionando
- ✅ No expuesta públicamente

**Cambiar cuando**:
- Migres a servidor de producción
- Necesites mayor seguridad
- Tengas tiempo para hacer backup y restaurar

---

**Fecha**: 6 de Mayo 2026  
**Estado**: ✅ Sistema funcionando con contraseña actual  
**Contraseña nueva**: Disponible para futuro uso
