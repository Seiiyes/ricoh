# 📊 Diagrama de Flujo del Sistema

## 🔄 Flujo Completo de Aprovisionamiento

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIO                                  │
│                                                                  │
│  1. Completa formulario de usuario                              │
│     • Nombre: "Juan Lizarazo"                                   │
│     • Código: "7104"                                            │
│     • Usuario red: "reliteltda\scaner"                          │
│     • Contraseña: "********"                                    │
│     • Funciones: [Escáner, Copiadora]                           │
│     • Carpeta SMB: "\\TIC0596\Escaner"                          │
│                                                                  │
│  2. Selecciona impresoras (clic en tarjetas)                    │
│     ┌─────────┐  ┌─────────┐  ┌─────────┐                      │
│     │ ✓ IP1   │  │ ✓ IP2   │  │   IP3   │  ← Seleccionadas: 2  │
│     └─────────┘  └─────────┘  └─────────┘                      │
│                                                                  │
│  3. Clic en "Enviar Configuración"                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                              │
│                                                                  │
│  • Valida formulario                                            │
│  • Construye payload:                                           │
│    {                                                            │
│      name: "Juan Lizarazo",                                     │
│      codigo_de_usuario: "7104",                                 │
│      network_credentials: {...},                                │
│      smb_config: {...},                                         │
│      available_functions: {...}                                 │
│    }                                                            │
│                                                                  │
│  • POST /api/users (crear usuario)                              │
│  • POST /api/provisioning/provision                             │
│    {                                                            │
│      user_id: 123,                                              │
│      printer_ids: [1, 2]  ← IDs de impresoras seleccionadas    │
│    }                                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│                                                                  │
│  API: /api/users                                                │
│  ├─ Valida datos                                                │
│  ├─ Encripta contraseña (AES-256)                               │
│  ├─ Guarda en BD:                                               │
│  │  INSERT INTO users (name, codigo_de_usuario, ...)           │
│  └─ Retorna: { id: 123, name: "Juan Lizarazo", ... }           │
│                                                                  │
│  API: /api/provisioning/provision                               │
│  ├─ Obtiene usuario de BD (id: 123)                             │
│  ├─ Obtiene impresoras de BD (ids: [1, 2])                      │
│  ├─ Desencripta contraseña                                      │
│  ├─ Construye payload Ricoh                                     │
│  └─ Llama a ProvisioningService                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              PROVISIONING SERVICE                                │
│                                                                  │
│  provision_user_to_printers(user_id, printer_ids)               │
│                                                                  │
│  FOR EACH printer_id IN [1, 2]:                                 │
│    │                                                            │
│    ├─ Obtiene printer de BD                                     │
│    │  • id: 1, ip: "192.168.91.250"                             │
│    │                                                            │
│    ├─ Llama a RicohWebClient.provision_user()                   │
│    │                                                            │
│    ├─ Si éxito:                                                 │
│    │  • Crea asignación en BD:                                  │
│    │    INSERT INTO user_printer_assignments                    │
│    │    (user_id, printer_id)                                   │
│    │  • Incrementa contador de éxitos                           │
│    │                                                            │
│    └─ Si error:                                                 │
│       • Registra error                                          │
│       • Continúa con siguiente impresora                        │
│                                                                  │
│  Retorna resumen:                                               │
│  {                                                              │
│    success: true,                                               │
│    printers_provisioned: 2,                                     │
│    message: "Usuario provisionado a 2/2 impresoras"            │
│  }                                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              RICOH WEB CLIENT                                    │
│                                                                  │
│  provision_user(printer_ip, user_config)                        │
│                                                                  │
│  PARA CADA IMPRESORA:                                           │
│                                                                  │
│  1. AUTENTICACIÓN                                               │
│     ├─ GET /web/guest/es/websys/webArch/authForm.cgi            │
│     │  • Extrae wimToken                                        │
│     ├─ POST /web/guest/es/websys/webArch/login.cgi              │
│     │  • userid: base64(admin)                                  │
│     │  • password: base64("")                                   │
│     │  • wimToken                                               │
│     └─ Obtiene cookies de sesión                                │
│                                                                  │
│  2. OBTENER WIMTOKEN FRESCO                                     │
│     ├─ GET /web/entry/es/address/adrsList.cgi                   │
│     │  • Extrae wimToken inicial                                │
│     ├─ POST /web/entry/es/address/adrsGetUser.cgi               │
│     │  • mode: ADDUSER                                          │
│     │  • outputSpecifyModeIn: DEFAULT                           │
│     │  • wimToken: [token inicial]                              │
│     └─ Extrae wimToken FRESCO del formulario                    │
│                                                                  │
│  3. PROVISIONAR USUARIO                                         │
│     └─ POST /web/entry/es/address/adrsSetUser.cgi               │
│        • Headers:                                               │
│          - X-Requested-With: XMLHttpRequest                     │
│          - Content-Type: application/x-www-form-urlencoded      │
│        • Form data (lista de tuplas):                           │
│          - wimToken: [token fresco]                             │
│          - mode: ADDUSER                                        │
│          - entryNameIn: "Juan Lizarazo"                         │
│          - userCodeIn: "7104"                                   │
│          - folderAuthUserNameIn: "reliteltda\scaner"            │
│          - folderAuthPasswordIn: "********"                     │
│          - isFolderAuthPasswordUpdated: false                   │
│          - availableFuncIn: SCAN                                │
│          - availableFuncIn: COPY                                │
│          - folderPathNameIn: "\\TIC0596\Escaner"                │
│          - ... (más campos)                                     │
│                                                                  │
│  4. VERIFICAR RESPUESTA                                         │
│     ├─ Status 200/302: ✅ ÉXITO                                 │
│     └─ Otro: ❌ ERROR                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IMPRESORA RICOH                               │
│                                                                  │
│  • Recibe configuración                                         │
│  • Crea usuario en libreta de direcciones                       │
│  • Usuario disponible en panel de la impresora                  │
│                                                                  │
│  Verificación:                                                  │
│  http://[IP]/web/entry/es/address/adrsList.cgi                  │
│  └─ Usuario "Juan Lizarazo" (código: 7104) visible             │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONSOLA EN VIVO                               │
│                                                                  │
│  [10:30:15] ✅ Usuario creado: Juan Lizarazo (ID: 123)          │
│  [10:30:15] 📡 Provisionando a 2 impresora(s)...                │
│  [10:30:16] 🔐 Autenticando con impresora 192.168.91.250...     │
│  [10:30:17] ✅ Usuario provisionado a 192.168.91.250            │
│  [10:30:18] 🔐 Autenticando con impresora 192.168.91.251...     │
│  [10:30:19] ✅ Usuario provisionado a 192.168.91.251            │
│  [10:30:19] ✅ Configuración enviada exitosamente               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Puntos Clave

### 1. Selección Múltiple
- El usuario puede seleccionar **1 o más impresoras**
- Cada clic en una tarjeta la selecciona/deselecciona
- El contador muestra cuántas están seleccionadas

### 2. Aprovisionamiento Secuencial
- El sistema provisiona a cada impresora **una por una**
- Si una falla, continúa con las siguientes
- Retorna un resumen con éxitos y errores

### 3. Autenticación por Impresora
- Cada impresora requiere autenticación independiente
- Las sesiones se mantienen durante el proceso
- El wimToken debe ser fresco (obtenido inmediatamente antes de usar)

### 4. Manejo de Errores
- Errores por impresora no detienen el proceso completo
- Cada error se registra y se muestra en la consola
- El resumen final indica cuántas fueron exitosas

---

## 📊 Flujo de Datos

```
Usuario → Frontend → Backend → BD (crear usuario)
                              ↓
                         BD (obtener impresoras)
                              ↓
                    FOR EACH impresora:
                         ↓
                    Ricoh Web Client
                         ↓
                    Impresora Ricoh
                         ↓
                    BD (crear asignación)
                         ↓
                    Consola en vivo
```

---

## 🎯 Resultado Final

Después del proceso:

1. **Base de Datos**:
   - Usuario creado en tabla `users`
   - Asignaciones creadas en tabla `user_printer_assignments`

2. **Impresoras Ricoh**:
   - Usuario visible en libreta de direcciones
   - Configuración completa aplicada

3. **Interfaz**:
   - Consola muestra resumen de éxitos/errores
   - Formulario se limpia
   - Selección de impresoras se resetea
