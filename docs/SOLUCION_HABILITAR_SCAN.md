# Solución: Habilitar/Deshabilitar Funciones en Usuarios Ricoh

## Resumen

Se logró implementar exitosamente la funcionalidad para habilitar y deshabilitar funciones (como SCAN) en usuarios de impresoras Ricoh de forma programática, sin usar Selenium, logrando un rendimiento 5-10x más rápido.

## Problema Original

- Necesidad de habilitar/deshabilitar funciones de usuarios (SCAN, COPY, PRINT, etc.)
- Intentos iniciales resultaban en error 500 o BADFLOW
- Selenium era muy lento (10-15 minutos para 200+ usuarios)

## Solución Encontrada

### Flujo Correcto para ESCRIBIR Funciones

1. **Login** con credenciales admin
2. **Obtener wimToken** desde `adrsList.cgi`
3. **Cargar batch AJAX** del usuario (crítico para evitar BADFLOW)
4. **Obtener formulario** con `mode=MODUSER` + `outputSpecifyModeIn=PROGRAMMED` + `inputSpecifyModeIn=READ`
5. **Construir payload** con TODOS los campos obligatorios
6. **Enviar actualización** a `adrsSetUser.cgi`

### Campos Obligatorios Clave

```python
payload = [
    ('wimToken', wim_token),
    ('mode', 'MODUSER'),
    ('inputSpecifyModeIn', 'WRITE'),
    ('listUpdateIn', 'UPDATE'),
    ('entryIndexIn', entry_index),
    ('entryNameIn', user_name),
    ('entryDisplayNameIn', user_name),
    ('userCodeIn', user_code),
    ('priorityIn', '5'),
    ('outputSpecifyModeIn', ''),
    ('pageSpecifiedIn', ''),
    ('pageNumberIn', ''),
    ('wayFrom', 'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS'),
    ('wayTo', 'adrsList.cgi'),
    ('isSelfPasswordEditMode', 'false'),
    ('isLocalAuthPasswordUpdated', 'false'),
    ('isFolderAuthPasswordUpdated', 'false'),
    ('entryTagInfoIn', '1'),  # Repetir 4 veces
    ('entryTagInfoIn', '1'),
    ('entryTagInfoIn', '1'),
    ('entryTagInfoIn', '1'),
    ('smtpAuthAccountIn', 'AUTH_SYSTEM_O'),
    ('folderAuthAccountIn', 'AUTH_ASSIGNMENT_O'),
    ('folderAuthUserNameIn', ''),
    ('ldapAuthAccountIn', 'AUTH_SYSTEM_O'),
    ('entryUseIn', 'ENTRYUSE_TO_O'),
    ('entryUseIn', 'ENTRYUSE_FROM_O'),
    ('isCertificateExist', 'false'),
    ('isEncryptAlways', 'false'),
    ('folderProtocolIn', 'SMB_O'),
    ('folderPathNameIn', '\\\\TIC-0122\\Escaner'),
]

# Agregar funciones seleccionadas
for func in active_funcs:
    payload.append(('availableFuncIn', func))
```

## Archivos Implementados

### Scripts de Prueba

1. **`habilitar_scan_final.py`** ✅ FUNCIONA
   - Script standalone que habilita SCAN para usuario 7104
   - Incluye verificación de cambios
   - Tiempo de ejecución: ~3-5 segundos

### Servicio Actualizado

2. **`services/ricoh_web_client.py`** ✅ ACTUALIZADO
   - Método `set_user_functions()` implementado con el flujo correcto
   - Incluye fallback a Selenium si hay BADFLOW
   - Mapeo automático de permisos a valores de hardware Ricoh

## Mapeo de Funciones

| Permiso DB | Valor Ricoh Hardware |
|------------|---------------------|
| copiadora | COPY_BW, COPY_TC, COPY_MC |
| copiadora_color | COPY_FC |
| impresora | PRT_BW |
| impresora_color | PRT_FC |
| escaner | SCAN |
| document_server | DBX |
| fax | FAX |
| navegador | MFPBROWSER |

## Resultados de Pruebas

### Usuario 7104 (JUAN LIZARAZO)

```
Funciones antes:
   [X] COPY_BW
   [X] PRT_BW
   [ ] SCAN

Funciones después:
   [X] COPY_BW
   [X] PRT_BW
   [X] SCAN  ← HABILITADO EXITOSAMENTE
```

### Rendimiento

- **Lectura de funciones**: 2-3 minutos para 200+ usuarios (sin Selenium)
- **Escritura de funciones**: 3-5 segundos por usuario
- **Mejora vs Selenium**: 5-10x más rápido

## Uso desde Frontend

### Endpoint API

```http
PUT /api/printers/{ip}/users/{code}/functions
Content-Type: application/json

{
  "copiadora": true,
  "copiadora_color": false,
  "impresora": true,
  "impresora_color": false,
  "escaner": true,
  "document_server": false,
  "fax": false,
  "navegador": false
}
```

### Sincronización Completa

```http
POST /api/printers/{ip}/sync
```

Este endpoint:
1. Lee TODOS los usuarios de la impresora
2. Obtiene sus funciones REALES del hardware
3. Actualiza la base de datos con persistencia

## Notas Técnicas

### Por qué funciona ahora

1. **Cargar batch AJAX**: Ricoh requiere que el usuario esté en el cache de sesión
2. **Campos obligatorios completos**: La impresora valida que TODOS los campos estén presentes
3. **wimToken fresco**: Debe obtenerse del formulario, no reutilizar el de la lista
4. **mode=MODUSER**: Permite modificar usuarios existentes (vs ADDUSER o EDIT)

### Errores Comunes Evitados

- ❌ `mode=EDIT` → Causa BADFLOW
- ❌ `outputSpecifyModeIn=SETTINGS` al leer → No devuelve checkboxes
- ❌ No cargar batch AJAX → Causa BADFLOW
- ❌ Faltan campos obligatorios → Error 500
- ✅ `mode=MODUSER` + `PROGRAMMED` + batch AJAX + campos completos → FUNCIONA

## Próximos Pasos

1. ✅ Script standalone funciona
2. ✅ Servicio actualizado
3. ⏳ Integrar con API endpoints
4. ⏳ Probar con frontend
5. ⏳ Documentar para equipo

## Conclusión

La solución permite habilitar/deshabilitar funciones de usuarios Ricoh de forma programática, rápida y confiable, sin depender de Selenium para operaciones normales. El flujo correcto fue descubierto mediante reverse engineering del JavaScript de la impresora y pruebas exhaustivas.
