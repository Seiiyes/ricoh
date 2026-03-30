# 📘 Guía de Uso - Sistema de Aprovisionamiento Ricoh

## 🎯 Descripción General

Este sistema permite crear usuarios y provisionarlos automáticamente a una o múltiples impresoras Ricoh de forma simultánea mediante una interfaz web intuitiva.

---

## 🚀 Inicio Rápido

### 1. Iniciar el Sistema

**Windows:**
```cmd
start-dev.bat
```

**Linux/Mac:**
```bash
./start-dev.sh
```

Esto iniciará:
- Backend (FastAPI) en `http://localhost:8000`
- Frontend (React) en `http://localhost:5173`
- Base de datos PostgreSQL

### 2. Acceder a la Interfaz

Abre tu navegador en: `http://localhost:5173`

---

## 📋 Flujo de Trabajo Completo

### Paso 1: Descubrir Impresoras

1. Haz clic en el botón **"Descubrir Impresoras"** (esquina superior izquierda)
2. Ingresa el rango de red (ejemplo: `192.168.91.0/24`)
3. El sistema escaneará la red y detectará impresoras Ricoh automáticamente
4. Las impresoras descubiertas aparecerán en la cuadrícula

### Paso 2: Crear y Configurar Usuario

En el panel izquierdo, completa los siguientes campos:

#### **Información Básica**
- **Nombre Completo**: Nombre del usuario (ej: "Juan Lizarazo")
- **Código de Usuario**: 4-8 dígitos numéricos (ej: "7104")

#### **Autenticación de Carpeta**
- **Nombre de usuario de inicio de sesión**: Usuario de red (ej: "reliteltda\scaner")
- **Contraseña de inicio de sesión**: Contraseña de la cuenta de red

#### **Funciones Disponibles**
Selecciona las funciones que el usuario podrá usar:

- ☑️ **Copiadora**
  - Si se habilita, elige: A todo color o Blanco y Negro
- ☑️ **Impresora**
  - Si se habilita, elige: Color o Blanco y Negro
- ☑️ **Document Server**
- ☑️ **Fax**
- ☑️ **Escáner** (recomendado por defecto)
- ☑️ **Navegador**

> ⚠️ **Importante**: Habilita color solo cuando sea necesario. La mayoría de usuarios solo necesitan B/N.

#### **Carpeta SMB**
- **Ruta**: Ruta UNC de la carpeta de destino (ej: `\\TIC0596\Escaner`)
  - El servidor y puerto se extraen automáticamente

### Paso 3: Seleccionar Impresoras

1. En la cuadrícula de impresoras, haz clic en las tarjetas de las impresoras donde deseas provisionar el usuario
2. Las impresoras seleccionadas se resaltarán con un borde rojo
3. El contador mostrará: "Seleccionadas: X impresora(s)"

**Opciones:**
- **Seleccionar una impresora**: Haz clic en una sola tarjeta
- **Seleccionar múltiples**: Haz clic en varias tarjetas
- **Deseleccionar**: Haz clic nuevamente en una tarjeta seleccionada

### Paso 4: Enviar Configuración

1. Verifica que todos los campos estén completos
2. Verifica que al menos una impresora esté seleccionada
3. Haz clic en el botón **"Enviar Configuración"**

El sistema:
1. Creará el usuario en la base de datos
2. Provisionará el usuario a cada impresora seleccionada
3. Mostrará el progreso en la consola en vivo (parte inferior)

---

## 🖥️ Consola en Vivo

La consola en la parte inferior muestra eventos en tiempo real:

- 🟢 **Verde**: Operaciones exitosas
- 🔴 **Rojo**: Errores
- 🟡 **Amarillo**: Advertencias
- ⚪ **Blanco**: Información general

---

## 🔧 Funciones Adicionales

### Editar Impresora

1. Haz clic en el ícono de lápiz en una tarjeta de impresora
2. Modifica los campos necesarios (nombre, ubicación, etc.)
3. Guarda los cambios

### Refrescar Datos SNMP

1. Haz clic en el ícono de actualización en una tarjeta de impresora
2. El sistema consultará los datos actuales vía SNMP
3. La información se actualizará automáticamente

---

## ✅ Verificación

### Verificar en la Impresora

1. Accede a la interfaz web de la impresora: `http://[IP_IMPRESORA]/web/entry/es/address/adrsList.cgi`
2. Inicia sesión con las credenciales de administrador (usuario: `admin`, contraseña: vacía)
3. Busca el usuario por su código o nombre
4. Verifica que todos los campos estén correctos

### Verificar en la Base de Datos

El sistema guarda:
- **Usuarios**: Tabla `users` con toda la configuración
- **Impresoras**: Tabla `printers` con información de los equipos
- **Asignaciones**: Tabla `user_printer_assignments` con las relaciones usuario-impresora

---

## 🧪 Pruebas

### Prueba de Aprovisionamiento Simple

```bash
cd backend
python test_final_v2.py
```

Este script:
- Genera un usuario de prueba con código aleatorio
- Lo provisiona a una impresora específica
- Muestra el resultado

### Prueba de Aprovisionamiento Múltiple

```bash
cd backend
python test_multi_printer_provisioning.py
```

Este script:
- Genera un usuario de prueba
- Lo provisiona a múltiples impresoras
- Muestra un resumen de resultados

---

## 🔐 Seguridad

- Las contraseñas de red se almacenan **encriptadas** en la base de datos usando AES-256
- Las contraseñas solo se desencriptan durante el aprovisionamiento
- Las sesiones con las impresoras se manejan de forma segura

---

## 📊 Campos Técnicos

### Funciones Disponibles (Mapeo)

| Frontend | Backend | Ricoh |
|----------|---------|-------|
| Copiadora | `func_copier` | `COPY` |
| Impresora | `func_printer` | `PRT` |
| Document Server | `func_document_server` | `DOC_SERVER` |
| Fax | `func_fax` | `FAX` |
| Escáner | `func_scanner` | `SCAN` |
| Navegador | `func_browser` | `BROWSER` |

### Configuración SMB

- **Protocolo**: Siempre SMB
- **Puerto**: 21 (fijo)
- **Servidor**: Se extrae automáticamente de la ruta
- **Ruta**: Formato UNC (ej: `\\servidor\carpeta`)

---

## ❓ Solución de Problemas

### El usuario no aparece en la impresora

1. Verifica que la impresora esté accesible en la red
2. Revisa la consola en vivo para ver errores específicos
3. Verifica las credenciales de administrador de la impresora
4. Ejecuta el script de prueba: `python backend/test_final_v2.py`

### Error "Tiempo de sesión agotado"

Este error ya está resuelto en la versión actual. Si aparece:
1. Verifica que estés usando la última versión del código
2. Revisa que `ricoh_web_client.py` tenga la implementación correcta

### Error de conexión a la base de datos

1. Verifica que Docker esté ejecutándose
2. Ejecuta: `docker-compose up -d`
3. Verifica las variables de entorno en `.env`

---

## 📞 Soporte

Para más información técnica, consulta:
- `ESTADO_ACTUAL.md` - Estado del proyecto
- `backend/TESTING_GUIDE.md` - Guía de pruebas
- `ARCHITECTURE.md` - Arquitectura del sistema
