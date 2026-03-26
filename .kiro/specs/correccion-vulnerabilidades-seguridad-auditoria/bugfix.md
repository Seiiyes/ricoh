# Documento de Requisitos de Bugfix

## Introducción

Este documento especifica los requisitos para corregir 11 vulnerabilidades de seguridad identificadas en la auditoría del 26 de marzo de 2026 del sistema Ricoh Equipment Management. Las vulnerabilidades incluyen 3 hallazgos críticos, 4 de alto riesgo de la auditoría original, y 4 hallazgos adicionales encontrados en la revisión posterior.

El objetivo es corregir sistemáticamente todas estas vulnerabilidades sin romper la funcionalidad existente del sistema, aplicando el principio de correcciones incrementales que preserven el comportamiento correcto actual.

## Análisis del Bug

### Comportamiento Actual (Defecto)

#### 1. Gestión de Secretos y Configuración

1.1 CUANDO `ENCRYPTION_KEY` no está configurada en modo desarrollo ENTONCES el sistema genera una clave temporal que causa pérdida de datos al reiniciar

1.2 CUANDO `SECRET_KEY` tiene longitud mínima pero baja entropía ENTONCES el sistema acepta la clave débil que puede ser crackeada por fuerza bruta

1.3 CUANDO `RICOH_ADMIN_PASSWORD` no está configurada ENTONCES el sistema usa una cadena vacía como valor por defecto en `ricoh_web_client.py`

1.4 CUANDO se configura `DATABASE_URL` ENTONCES el sistema usa credenciales hardcodeadas por defecto `postgresql://ricoh_admin:ricoh_secure_2024@localhost:5432/ricoh_fleet` en `backend/db/database.py`

#### 2. Exposición de Información Sensible en Logs

1.5 CUANDO se realiza autenticación ENTONCES el sistema registra los primeros 20 caracteres del token JWT en logs de debugging en `backend/middleware/auth_middleware.py`

1.6 CUANDO se inicializa el superadmin ENTONCES el script `init_superadmin.py` imprime la contraseña temporal en texto plano en la consola

1.7 CUANDO se procesan tokens de sesión web (wimToken) ENTONCES el sistema registra los tokens completos en logs de debugging en múltiples archivos

#### 3. Configuración de Seguridad Permisiva

1.8 CUANDO se configura CORS en producción ENTONCES el sistema permite todos los métodos (`["*"]`) y todos los headers (`["*"]`) sin restricciones

1.9 CUANDO se inicia la aplicación ENTONCES la protección CSRF está deshabilitada por defecto y requiere configuración manual con `ENABLE_CSRF=true`

1.10 CUANDO se almacenan tokens CSRF ENTONCES el sistema usa memoria del proceso (`self._token_cache = {}`) que no funciona en despliegues multi-instancia

1.11 CUANDO se aplica rate limiting ENTONCES el sistema usa almacenamiento en memoria que no funciona correctamente con load balancers

### Comportamiento Esperado (Correcto)

#### 1. Gestión de Secretos y Configuración

2.1 CUANDO `ENCRYPTION_KEY` no está configurada en cualquier entorno ENTONCES el sistema DEBERÁ lanzar un error de configuración con instrucciones para generar una clave válida

2.2 CUANDO se valida `SECRET_KEY` ENTONCES el sistema DEBERÁ verificar longitud mínima de 32 caracteres Y entropía mínima (al menos 3 de 4: mayúsculas, minúsculas, dígitos, caracteres especiales)

2.3 CUANDO `RICOH_ADMIN_PASSWORD` no está configurada ENTONCES el sistema DEBERÁ lanzar un error de configuración requiriendo que se establezca explícitamente

2.4 CUANDO se configura `DATABASE_URL` ENTONCES el sistema DEBERÁ requerir la variable de entorno sin proporcionar valores por defecto con credenciales

#### 2. Exposición de Información Sensible en Logs

2.5 CUANDO se registran tokens en logs ENTONCES el sistema DEBERÁ enmascarar completamente los tokens mostrando solo los primeros 4 y últimos 4 caracteres (formato: `XXXX...YYYY`)

2.6 CUANDO se inicializa el superadmin ENTONCES el script DEBERÁ mostrar solo la longitud de la contraseña generada, no la contraseña en texto plano

2.7 CUANDO se procesan tokens de sesión web (wimToken) ENTONCES el sistema DEBERÁ enmascarar los tokens en todos los logs usando el mismo formato de enmascaramiento

#### 3. Configuración de Seguridad Restrictiva

2.8 CUANDO se configura CORS ENTONCES el sistema DEBERÁ usar listas explícitas de métodos permitidos (`["GET", "POST", "PUT", "DELETE", "PATCH"]`) y headers permitidos específicos

2.9 CUANDO se inicia la aplicación en producción ENTONCES la protección CSRF DEBERÁ estar habilitada por defecto

2.10 CUANDO se almacenan tokens CSRF ENTONCES el sistema DEBERÁ usar Redis como backend de almacenamiento distribuido con expiración configurada

2.11 CUANDO se aplica rate limiting ENTONCES el sistema DEBERÁ usar Redis como backend de almacenamiento distribuido para funcionar correctamente con load balancers

### Comportamiento Sin Cambios (Prevención de Regresiones)

#### 1. Funcionalidad de Encriptación

3.1 CUANDO `ENCRYPTION_KEY` está correctamente configurada ENTONCES el sistema DEBERÁ CONTINUAR encriptando y desencriptando datos sensibles correctamente

3.2 CUANDO se usan claves existentes válidas ENTONCES el sistema DEBERÁ CONTINUAR desencriptando datos previamente encriptados sin pérdida de información

#### 2. Autenticación y Autorización

3.3 CUANDO se realiza login con credenciales válidas ENTONCES el sistema DEBERÁ CONTINUAR generando tokens JWT válidos y funcionales

3.4 CUANDO se valida un token JWT válido ENTONCES el sistema DEBERÁ CONTINUAR autenticando correctamente al usuario

3.5 CUANDO se accede a endpoints protegidos con token válido ENTONCES el sistema DEBERÁ CONTINUAR permitiendo el acceso según los permisos del usuario

#### 3. Integración con Impresoras Ricoh

3.6 CUANDO se autentica con una impresora Ricoh usando credenciales válidas ENTONCES el sistema DEBERÁ CONTINUAR estableciendo sesiones autenticadas correctamente

3.7 CUANDO se obtienen wimTokens de impresoras ENTONCES el sistema DEBERÁ CONTINUAR usando los tokens para operaciones autorizadas

3.8 CUANDO se realizan operaciones CRUD en libretas de direcciones ENTONCES el sistema DEBERÁ CONTINUAR ejecutando las operaciones correctamente

#### 4. Configuración CORS

3.9 CUANDO se reciben peticiones de orígenes permitidos ENTONCES el sistema DEBERÁ CONTINUAR procesando las peticiones correctamente

3.10 CUANDO se usan métodos HTTP permitidos ENTONCES el sistema DEBERÁ CONTINUAR aceptando y procesando las peticiones

#### 5. Protección CSRF

3.11 CUANDO la protección CSRF está habilitada y se envía un token válido ENTONCES el sistema DEBERÁ CONTINUAR procesando la petición correctamente

3.12 CUANDO se generan tokens CSRF para sesiones válidas ENTONCES el sistema DEBERÁ CONTINUAR generando tokens únicos y válidos

#### 6. Rate Limiting

3.13 CUANDO se realizan peticiones dentro de los límites configurados ENTONCES el sistema DEBERÁ CONTINUAR procesando las peticiones sin restricciones

3.14 CUANDO se detectan patrones de uso legítimos ENTONCES el sistema DEBERÁ CONTINUAR permitiendo el acceso normal

#### 7. Logging y Auditoría

3.15 CUANDO se registran eventos de auditoría ENTONCES el sistema DEBERÁ CONTINUAR registrando todos los eventos críticos con la información contextual necesaria

3.16 CUANDO se consultan logs de auditoría ENTONCES el sistema DEBERÁ CONTINUAR proporcionando trazabilidad completa de acciones

#### 8. Inicialización de Base de Datos

3.17 CUANDO se ejecutan scripts de inicialización con configuración válida ENTONCES el sistema DEBERÁ CONTINUAR creando y configurando correctamente la base de datos

3.18 CUANDO se crean usuarios administrativos ENTONCES el sistema DEBERÁ CONTINUAR generando credenciales seguras y almacenándolas correctamente

## Condición del Bug y Propiedades

### Funciones de Condición del Bug

#### C1: Configuración de Secretos Insegura
```pascal
FUNCTION isBugCondition_SecretConfig(config)
  INPUT: config de tipo SystemConfiguration
  OUTPUT: boolean
  
  RETURN (
    config.ENCRYPTION_KEY = NULL OR
    config.SECRET_KEY.length < 32 OR
    config.SECRET_KEY.entropy < 3 OR
    config.RICOH_ADMIN_PASSWORD = "" OR
    config.DATABASE_URL contiene credenciales hardcodeadas
  )
END FUNCTION
```

#### C2: Exposición de Información Sensible
```pascal
FUNCTION isBugCondition_SensitiveExposure(logEntry)
  INPUT: logEntry de tipo LogEntry
  OUTPUT: boolean
  
  RETURN (
    logEntry contiene token JWT sin enmascarar OR
    logEntry contiene contraseña en texto plano OR
    logEntry contiene wimToken sin enmascarar
  )
END FUNCTION
```

#### C3: Configuración de Seguridad Permisiva
```pascal
FUNCTION isBugCondition_PermissiveConfig(securityConfig)
  INPUT: securityConfig de tipo SecurityConfiguration
  OUTPUT: boolean
  
  RETURN (
    securityConfig.CORS.allowMethods = ["*"] OR
    securityConfig.CORS.allowHeaders = ["*"] OR
    (securityConfig.environment = "production" AND securityConfig.CSRF.enabled = false) OR
    securityConfig.CSRF.storage = "memory" OR
    securityConfig.rateLimit.storage = "memory"
  )
END FUNCTION
```

### Propiedades de Corrección

#### Propiedad 1: Verificación de Corrección de Secretos
```pascal
// Property: Fix Checking - Configuración Segura de Secretos
FOR ALL config WHERE isBugCondition_SecretConfig(config) DO
  result ← validateConfiguration'(config)
  ASSERT (
    result.raises_error = true AND
    result.error_message contiene instrucciones de configuración
  )
END FOR
```

#### Propiedad 2: Verificación de Enmascaramiento
```pascal
// Property: Fix Checking - Enmascaramiento de Información Sensible
FOR ALL logEntry WHERE isBugCondition_SensitiveExposure(logEntry) DO
  result ← logSensitiveData'(logEntry)
  ASSERT (
    result.masked = true AND
    result.format = "XXXX...YYYY" AND
    result.exposes_full_value = false
  )
END FOR
```

#### Propiedad 3: Verificación de Configuración Restrictiva
```pascal
// Property: Fix Checking - Configuración de Seguridad Restrictiva
FOR ALL securityConfig WHERE isBugCondition_PermissiveConfig(securityConfig) DO
  result ← applySecurityConfig'(securityConfig)
  ASSERT (
    result.CORS.allowMethods es lista explícita AND
    result.CORS.allowHeaders es lista explícita AND
    (result.environment = "production" IMPLIES result.CSRF.enabled = true) AND
    result.CSRF.storage = "redis" AND
    result.rateLimit.storage = "redis"
  )
END FOR
```

### Propiedad de Preservación

```pascal
// Property: Preservation Checking
FOR ALL input WHERE NOT (
  isBugCondition_SecretConfig(input) OR
  isBugCondition_SensitiveExposure(input) OR
  isBugCondition_PermissiveConfig(input)
) DO
  ASSERT F(input) = F'(input)
END FOR
```

Donde:
- **F**: Código original (sin corregir)
- **F'**: Código corregido

Esta propiedad asegura que para todas las configuraciones válidas, datos no sensibles, y configuraciones de seguridad apropiadas, el sistema corregido se comporta idénticamente al sistema original.

### Ejemplos Concretos (Contraejemplos)

#### Ejemplo 1: ENCRYPTION_KEY no configurada
```python
# Input que dispara el bug
os.environ["ENVIRONMENT"] = "development"
os.environ.pop("ENCRYPTION_KEY", None)

# Comportamiento actual (F)
# Genera clave temporal, datos se pierden al reiniciar

# Comportamiento esperado (F')
# Lanza ValueError con mensaje instructivo
```

#### Ejemplo 2: Token JWT en logs
```python
# Input que dispara el bug
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"

# Comportamiento actual (F)
logger.info(f"Token: {token[:20]}...")  # Expone "eyJhbGciOiJIUzI1NiIsI..."

# Comportamiento esperado (F')
logger.info(f"Token: {token[:4]}...{token[-4:]}")  # Muestra "eyJh...R8U"
```

#### Ejemplo 3: CORS permisivo
```python
# Input que dispara el bug
config = {
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}

# Comportamiento actual (F)
# Acepta cualquier método y header

# Comportamiento esperado (F')
config = {
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
    "allow_headers": ["Content-Type", "Authorization", "X-CSRF-Token", "X-Request-ID"]
}
```
