# 🧪 Guía de Pruebas - Sistema de Provisionamiento Ricoh

## 📋 Índice

1. [Prueba de Conexión con Impresora](#prueba-de-conexión-con-impresora)
2. [Prueba de Provisionamiento Manual](#prueba-de-provisionamiento-manual)
3. [Prueba Completa End-to-End](#prueba-completa-end-to-end)
4. [Solución de Problemas](#solución-de-problemas)

---

## 🔌 Prueba de Conexión con Impresora

### Objetivo
Verificar que el sistema puede conectarse a tu impresora Ricoh y obtener el wimToken necesario.

### Requisitos Previos
- Impresora Ricoh encendida y conectada a la red
- Conocer la IP de la impresora
- Backend instalado con dependencias

### Pasos

1. **Navega al directorio del backend:**
   ```bash
   cd backend
   ```

2. **Ejecuta el script de prueba:**
   ```bash
   python test_ricoh_connection.py <IP_IMPRESORA>
   ```
   
   **Ejemplo:**
   ```bash
   python test_ricoh_connection.py 192.168.91.250
   ```

3. **Resultado esperado:**
   ```
   ============================================================
   🔧 PRUEBA DE CONEXIÓN CON IMPRESORA RICOH
   ============================================================

   📍 IP de la impresora: 192.168.91.250

   📡 Paso 1: Probando acceso básico a la impresora...
      ✅ Impresora accesible (HTTP 200)

   🔑 Paso 2: Intentando obtener wimToken...
      ✅ wimToken obtenido exitosamente: 192268070
      📝 Longitud del token: 9 caracteres

   🌐 Paso 3: Verificando estructura de URLs...
      ✅ http://192.168.91.250/es/websys/webArch/adrsListAll.cgi → HTTP 200
      ✅ http://192.168.91.250/es/websys/webArch/adrsSetUser.cgi → HTTP 200
      ✅ http://192.168.91.250/es/websys/webArch/topPage.cgi → HTTP 200

   ============================================================
   ✅ PRUEBA COMPLETADA EXITOSAMENTE
   ============================================================

   📌 Resumen:
      • Impresora accesible: ✅
      • wimToken obtenido: ✅ (192268070)
      • URL base: http://192.168.91.250/es/websys/webArch/

   💡 El sistema está listo para provisionar usuarios.
   ```

### ❌ Si la prueba falla

**Error: "No se pudo obtener el wimToken"**
- Verifica que la IP sea correcta
- Asegúrate de que la impresora esté encendida
- Verifica que no haya firewall bloqueando el puerto 80

**Error: "Connection timeout"**
- La impresora no está en la misma red
- Verifica la configuración de red de tu computadora
- Prueba hacer ping a la impresora: `ping <IP_IMPRESORA>`

---

## 🧪 Prueba de Provisionamiento Manual

### Objetivo
Provisionar un usuario de prueba directamente usando Python.

### Script de Prueba

Crea un archivo `test_provision_user.py`:

```python
"""
Script para probar el provisionamiento de un usuario de prueba
"""
from services.ricoh_web_client import get_ricoh_web_client
from services.encryption import get_encryption_service

# Configuración de la impresora
PRINTER_IP = "192.168.91.250"  # ⚠️ CAMBIA ESTO A TU IP

# Datos del usuario de prueba
test_user = {
    "nombre": "Usuario Prueba Sistema",
    "codigo_de_usuario": "9999",
    "nombre_usuario_inicio_sesion": "relitelda\\scaner",
    "contrasena_inicio_sesion": "TuContraseñaAqui",  # ⚠️ CAMBIA ESTO
    "funciones_disponibles": {
        "copiadora": False,
        "impresora": False,
        "document_server": False,
        "fax": False,
        "escaner": True,  # Solo escáner habilitado
        "navegador": False
    },
    "carpeta_smb": {
        "protocolo": "SMB",
        "servidor": "10.0.0.5",
        "puerto": 21,
        "ruta": "\\\\10.0.0.5\\scans\\prueba"
    }
}

def main():
    print("\n" + "="*60)
    print("🧪 PRUEBA DE PROVISIONAMIENTO DE USUARIO")
    print("="*60 + "\n")
    
    print(f"📍 Impresora: {PRINTER_IP}")
    print(f"👤 Usuario: {test_user['nombre']}")
    print(f"🔢 Código: {test_user['codigo_de_usuario']}")
    print(f"📁 Carpeta: {test_user['carpeta_smb']['ruta']}\n")
    
    # Obtener cliente
    client = get_ricoh_web_client()
    
    # Provisionar
    print("🔄 Provisionando usuario...")
    success = client.provision_user(PRINTER_IP, test_user)
    
    if success:
        print("\n✅ USUARIO PROVISIONADO EXITOSAMENTE\n")
        print("📝 Verifica en la impresora:")
        print("   1. Ve a la interfaz web de la impresora")
        print("   2. Navega a: Lista de direcciones")
        print("   3. Busca el usuario con código: 9999")
        print("   4. Verifica que tenga la función Escáner habilitada\n")
    else:
        print("\n❌ ERROR AL PROVISIONAR USUARIO\n")
        print("Revisa los logs para más detalles.\n")

if __name__ == "__main__":
    main()
```

### Ejecutar la Prueba

```bash
cd backend
python test_provision_user.py
```

---

## 🎯 Prueba Completa End-to-End

### Objetivo
Probar el flujo completo desde el frontend hasta la impresora.

### Pasos

1. **Inicia el sistema completo:**
   ```bash
   # Windows
   docker-start.bat
   
   # Linux/Mac
   ./docker-start.sh
   ```

2. **Accede al frontend:**
   - Abre tu navegador en: http://localhost:5173

3. **Descubre impresoras:**
   - Haz clic en "Descubrir Impresoras"
   - Ingresa el rango de IP (ej: `192.168.91.0/24`)
   - Haz clic en "Scan Network"
   - Selecciona tu impresora
   - Haz clic en "Register X Printer(s)"

4. **Crea un usuario de prueba:**
   
   **Información Básica:**
   - Nombre Completo: `Juan Prueba`
   - Código de Usuario: `1234`
   
   **Autenticación de Carpeta:**
   - Usuario: `relitelda\scaner` (ya viene por defecto)
   - Contraseña: `[tu contraseña de red]`
   
   **Funciones Disponibles:**
   - ✅ Escáner (marca solo esta)
   
   **Carpeta SMB:**
   - Ruta: `\\10.0.0.5\scans\juan`

5. **Selecciona la impresora:**
   - Haz clic en la tarjeta de tu impresora en el grid
   - Debe aparecer con borde rojo cuando esté seleccionada

6. **Provisiona:**
   - Haz clic en "Enviar Configuración"
   - Observa los logs en la consola inferior

7. **Resultado esperado en la consola:**
   ```
   [14:30:45] Creando usuario: Juan Prueba...
   [14:30:46] Usuario creado: Juan Prueba (ID: 1)
   [14:30:46] Provisionando a 1 impresora(s)...
   [14:30:47] 🔍 Intentando obtener wimToken desde: http://192.168.91.250/es/websys/webArch/adrsListAll.cgi
   [14:30:47] ✅ wimToken obtenido: 192268070 desde http://192.168.91.250/es/websys/webArch/adrsListAll.cgi
   [14:30:47] 📤 Enviando datos de usuario a http://192.168.91.250/es/websys/webArch/adrsSetUser.cgi
   [14:30:48] ✅ Usuario provisionado exitosamente a 192.168.91.250
   [14:30:48] Usuario 'Juan Prueba' provisionado exitosamente a 1/1 impresora(s)
   [14:30:48] ✓ Configuración enviada exitosamente
   ```

8. **Verifica en la impresora:**
   - Accede a la interfaz web: `http://[IP_IMPRESORA]`
   - Ve a: **Lista de direcciones**
   - Busca el usuario "Juan Prueba" con código "1234"
   - Verifica que tenga:
     - ✅ Función Escáner habilitada
     - ✅ Carpeta SMB configurada
     - ✅ Credenciales de red guardadas

---

## 🔍 Solución de Problemas

### Problema: "No se pudo obtener wimToken"

**Causa:** La URL de la impresora no es accesible.

**Solución:**
1. Verifica que la IP sea correcta
2. Prueba acceder manualmente: `http://[IP_IMPRESORA]/es/websys/webArch/adrsListAll.cgi`
3. Si obtienes 404, la estructura de URLs puede ser diferente
4. Comparte el HTML de la página de lista de usuarios

### Problema: "Error 400 - Bad Request"

**Causa:** Los datos enviados no coinciden con lo que espera la impresora.

**Solución:**
1. Verifica que todos los campos requeridos estén completos
2. Revisa que el código de usuario sea numérico (4-8 dígitos)
3. Verifica que la contraseña de red sea correcta
4. Asegúrate de que al menos una función esté habilitada

### Problema: "Error 403 - Forbidden"

**Causa:** La impresora requiere autenticación o el wimToken expiró.

**Solución:**
1. El wimToken se obtiene automáticamente en cada petición
2. Verifica que no haya autenticación adicional en la impresora
3. Revisa la configuración de seguridad de la impresora

### Problema: "Usuario creado pero no aparece en la impresora"

**Causa:** El provisionamiento falló silenciosamente.

**Solución:**
1. Revisa los logs del backend: `docker-compose logs -f backend`
2. Verifica que la respuesta HTTP sea 200 o 302
3. Comprueba que no haya errores en la consola del frontend

### Problema: "Código de usuario ya existe"

**Causa:** Ya hay un usuario con ese código en la impresora.

**Solución:**
1. Usa un código diferente (4-8 dígitos)
2. O elimina el usuario existente desde la interfaz de la impresora
3. Los códigos deben ser únicos por impresora

---

## 📊 Verificación de Logs

### Backend Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f backend

# Ver últimas 100 líneas
docker-compose logs --tail=100 backend
```

**Logs exitosos:**
```
INFO:     🔍 Intentando obtener wimToken desde: http://192.168.91.250/es/websys/webArch/adrsListAll.cgi
INFO:     ✅ wimToken obtenido: 192268070
INFO:     📤 Enviando datos de usuario a http://192.168.91.250/es/websys/webArch/adrsSetUser.cgi
INFO:     ✅ Usuario provisionado exitosamente a 192.168.91.250
```

### Frontend Console

Abre las herramientas de desarrollador (F12) y ve a la pestaña "Console".

**Logs exitosos:**
```
WebSocket connected
User created: Juan Prueba (ID: 1)
Provisioning to 1 printer(s)...
Usuario 'Juan Prueba' provisionado exitosamente a 1/1 impresora(s)
```

---

## ✅ Checklist de Verificación

Antes de considerar el sistema completamente funcional, verifica:

- [ ] Script de conexión ejecuta sin errores
- [ ] wimToken se obtiene correctamente
- [ ] Usuario se crea en la base de datos
- [ ] Usuario aparece en la interfaz web de la impresora
- [ ] Código de usuario es correcto (4-8 dígitos)
- [ ] Funciones habilitadas son correctas
- [ ] Carpeta SMB está configurada
- [ ] Credenciales de red están guardadas
- [ ] Logs muestran éxito en frontend y backend
- [ ] Puedes crear múltiples usuarios sin errores

---

## 🎉 Sistema Completamente Funcional

Si todos los checks anteriores pasan, ¡felicidades! Tu sistema está 100% funcional y listo para producción.

### Próximos Pasos Recomendados

1. **Crear usuarios reales** con códigos únicos
2. **Documentar códigos de usuario** para tu organización
3. **Configurar backup automático** de la base de datos
4. **Establecer política de contraseñas** para usuarios de red
5. **Capacitar usuarios** sobre cómo usar el sistema

---

## 📞 Soporte

Si encuentras problemas no cubiertos en esta guía:

1. Revisa los logs completos del backend
2. Verifica la consola del navegador
3. Comprueba la conectividad de red
4. Verifica la configuración de la impresora

---

**Última actualización:** 2024
**Versión del sistema:** 2.0
