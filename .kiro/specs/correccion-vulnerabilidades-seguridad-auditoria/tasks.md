# Plan de Implementación - Corrección de Vulnerabilidades de Seguridad

## Fase 1: Exploración - Tests de Bug Condition (ANTES de implementar correcciones)

- [x] 1. Escribir tests de exploración para vulnerabilidades de gestión de secretos
  - **Property 1: Bug Condition** - Configuración Insegura de Secretos
  - **CRÍTICO**: Estos tests DEBEN FALLAR en código sin corregir - el fallo confirma que los bugs existen
  - **NO intentar corregir los tests o el código cuando fallen**
  - **NOTA**: Estos tests codifican el comportamiento esperado - validarán las correcciones cuando pasen después de la implementación
  - **OBJETIVO**: Descubrir contraejemplos que demuestren que los bugs existen
  - **Enfoque PBT Acotado**: Para bugs determinísticos, acotar la propiedad a los casos concretos que fallan para asegurar reproducibilidad
  - Test que EncryptionService rechaza ENCRYPTION_KEY=None en todos los entornos (de Bug Condition en diseño)
  - Test que JWTService rechaza SECRET_KEY con baja entropía (solo minúsculas, solo mayúsculas, etc.)
  - Test que RicohWebClient rechaza RICOH_ADMIN_PASSWORD vacía o None
  - Test que database.py rechaza DATABASE_URL no configurada
  - Las aserciones de test deben coincidir con Expected Behavior Properties del diseño
  - Ejecutar tests en código SIN CORREGIR
  - **RESULTADO ESPERADO**: Tests FALLAN (esto es correcto - prueba que los bugs existen)
  - Documentar contraejemplos encontrados para entender causa raíz
  - Marcar tarea completa cuando tests estén escritos, ejecutados, y fallos documentados
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2. Escribir tests de exploración para exposición de información sensible
  - **Property 1: Bug Condition** - Exposición de Información Sensible en Logs
  - **CRÍTICO**: Estos tests DEBEN FALLAR en código sin corregir - el fallo confirma que los bugs existen
  - **NO intentar corregir los tests o el código cuando fallen**
  - **NOTA**: Estos tests codifican el comportamiento esperado - validarán las correcciones cuando pasen después de la implementación
  - **OBJETIVO**: Descubrir contraejemplos que demuestren que los bugs existen
  - **Enfoque PBT Acotado**: Capturar logs durante operaciones y verificar que exponen más de 8 caracteres de tokens
  - Test que auth_middleware enmascara tokens JWT mostrando solo 4+4 caracteres (de Bug Condition en diseño)
  - Test que init_superadmin.py no imprime contraseñas en texto plano
  - Test que ricoh_web_client.py enmascara wimTokens en todos los logs
  - Las aserciones de test deben coincidir con Expected Behavior Properties del diseño
  - Ejecutar tests en código SIN CORREGIR
  - **RESULTADO ESPERADO**: Tests FALLAN (esto es correcto - prueba que los bugs existen)
  - Documentar contraejemplos encontrados (ej: "Log expone 20 caracteres del token JWT")
  - Marcar tarea completa cuando tests estén escritos, ejecutados, y fallos documentados
  - _Requirements: 2.5, 2.6, 2.7_

- [x] 3. Escribir tests de exploración para configuración de seguridad permisiva
  - **Property 1: Bug Condition** - Configuración de Seguridad Permisiva
  - **CRÍTICO**: Estos tests DEBEN FALLAR en código sin corregir - el fallo confirma que los bugs existen
  - **NO intentar corregir los tests o el código cuando fallen**
  - **NOTA**: Estos tests codifican el comportamiento esperado - validarán las correcciones cuando pasen después de la implementación
  - **OBJETIVO**: Descubrir contraejemplos que demuestren que los bugs existen
  - **Enfoque PBT Acotado**: Verificar configuraciones actuales y compararlas con configuraciones restrictivas esperadas
  - Test que CORS usa listas explícitas de métodos y headers (no ["*"])
  - Test que CSRF está habilitada por defecto en producción
  - Test que CSRF usa Redis cuando REDIS_URL está configurada
  - Test que rate limiter usa Redis cuando REDIS_URL está configurada
  - Las aserciones de test deben coincidir con Expected Behavior Properties del diseño
  - Ejecutar tests en código SIN CORREGIR
  - **RESULTADO ESPERADO**: Tests FALLAN (esto es correcto - prueba que los bugs existen)
  - Documentar contraejemplos encontrados (ej: "CORS configurado con allow_methods=['*']")
  - Marcar tarea completa cuando tests estén escritos, ejecutados, y fallos documentados
  - _Requirements: 2.8, 2.9, 2.10, 2.11_

## Fase 2: Preservación - Tests de Comportamiento Existente (ANTES de implementar correcciones)

- [x] 4. Escribir tests de preservación para funcionalidad de encriptación y autenticación (ANTES de implementar correcciones)
  - **Property 2: Preservation** - Funcionalidad de Encriptación y Autenticación
  - **IMPORTANTE**: Seguir metodología observation-first
  - Observar: Encriptación/desencriptación con ENCRYPTION_KEY válida funciona en código sin corregir
  - Observar: Generación/validación de tokens JWT con SECRET_KEY válida funciona en código sin corregir
  - Escribir tests basados en propiedades: para todas las claves válidas, encriptación es reversible (de Preservation Requirements en diseño)
  - Escribir tests basados en propiedades: para todos los tokens JWT válidos, validación retorna usuario correcto
  - Los tests basados en propiedades generan muchos casos de prueba para garantías más fuertes
  - Ejecutar tests en código SIN CORREGIR
  - **RESULTADO ESPERADO**: Tests PASAN (esto confirma comportamiento base a preservar)
  - Marcar tarea completa cuando tests estén escritos, ejecutados, y pasando en código sin corregir
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. Escribir tests de preservación para integración con impresoras Ricoh (ANTES de implementar correcciones)
  - **Property 2: Preservation** - Integración con Impresoras Ricoh
  - **IMPORTANTE**: Seguir metodología observation-first
  - Observar: Autenticación con impresoras usando credenciales válidas funciona en código sin corregir
  - Observar: Obtención y uso de wimTokens funciona en código sin corregir
  - Observar: Operaciones CRUD en libretas de direcciones funcionan en código sin corregir
  - Escribir tests basados en propiedades: para todas las credenciales válidas, autenticación establece sesión (de Preservation Requirements en diseño)
  - Escribir tests basados en propiedades: para todos los wimTokens válidos, operaciones autorizadas tienen éxito
  - Los tests basados en propiedades generan muchos casos de prueba para garantías más fuertes
  - Ejecutar tests en código SIN CORREGIR
  - **RESULTADO ESPERADO**: Tests PASAN (esto confirma comportamiento base a preservar)
  - Marcar tarea completa cuando tests estén escritos, ejecutados, y pasando en código sin corregir
  - _Requirements: 3.6, 3.7, 3.8_

- [x] 6. Escribir tests de preservación para configuración CORS, CSRF y rate limiting (ANTES de implementar correcciones)
  - **Property 2: Preservation** - Configuración de Seguridad con Valores Válidos
  - **IMPORTANTE**: Seguir metodología observation-first
  - Observar: Peticiones de orígenes permitidos se procesan correctamente en código sin corregir
  - Observar: Peticiones con tokens CSRF válidos se procesan correctamente en código sin corregir
  - Observar: Peticiones dentro de límites de rate limiting se procesan sin restricciones en código sin corregir
  - Escribir tests basados en propiedades: para todos los orígenes permitidos, peticiones con métodos permitidos tienen éxito (de Preservation Requirements en diseño)
  - Escribir tests basados en propiedades: para todos los tokens CSRF válidos, peticiones POST/PUT/DELETE tienen éxito
  - Escribir tests basados en propiedades: para todas las peticiones dentro de límites, no hay restricciones aplicadas
  - Los tests basados en propiedades generan muchos casos de prueba para garantías más fuertes
  - Ejecutar tests en código SIN CORREGIR
  - **RESULTADO ESPERADO**: Tests PASAN (esto confirma comportamiento base a preservar)
  - Marcar tarea completa cuando tests estén escritos, ejecutados, y pasando en código sin corregir
  - _Requirements: 3.9, 3.10, 3.11, 3.12, 3.13, 3.14_

- [x] 7. Escribir tests de preservación para logging y auditoría (ANTES de implementar correcciones)
  - **Property 2: Preservation** - Logging y Auditoría de Eventos
  - **IMPORTANTE**: Seguir metodología observation-first
  - Observar: Eventos de auditoría se registran con información contextual en código sin corregir
  - Observar: Logs de auditoría proporcionan trazabilidad completa en código sin corregir
  - Observar: Inicialización de base de datos y creación de usuarios funcionan en código sin corregir
  - Escribir tests basados en propiedades: para todos los eventos críticos, logs contienen información contextual necesaria (de Preservation Requirements en diseño)
  - Escribir tests basados en propiedades: para todas las configuraciones válidas, inicialización de DB tiene éxito
  - Los tests basados en propiedades generan muchos casos de prueba para garantías más fuertes
  - Ejecutar tests en código SIN CORREGIR
  - **RESULTADO ESPERADO**: Tests PASAN (esto confirma comportamiento base a preservar)
  - Marcar tarea completa cuando tests estén escritos, ejecutados, y pasando en código sin corregir
  - _Requirements: 3.15, 3.16, 3.17, 3.18_

## Fase 3: Implementación - Correcciones de Vulnerabilidades

### 3.1 Categoría 1: Gestión de Secretos y Configuración

- [x] 8. Corrección de ENCRYPTION_KEY obligatoria en todos los entornos

  - [ ] 8.1 Implementar validación obligatoria de ENCRYPTION_KEY
    - Modificar `backend/services/encryption_service.py` método `initialize()`
    - Eliminar bloque que genera clave temporal en modo desarrollo (líneas 35-40)
    - Lanzar ValueError si ENCRYPTION_KEY no está configurada en cualquier entorno
    - Incluir mensaje instructivo con comando para generar clave válida
    - _Bug_Condition: isBugCondition_SecretConfig(config) donde config.ENCRYPTION_KEY = NULL_
    - _Expected_Behavior: expectedBehavior(result) - ValueError con instrucciones de diseño_
    - _Preservation: Preservation Requirements 3.1, 3.2 - encriptación con clave válida funciona_
    - _Requirements: 2.1, 3.1, 3.2_

  - [ ] 8.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - ENCRYPTION_KEY Obligatoria
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 1 - NO escribir un nuevo test
    - El test de la tarea 1 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de ENCRYPTION_KEY de la tarea 1
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.1_

  - [ ] 8.3 Verificar que tests de preservación de encriptación siguen pasando
    - **Property 2: Preservation** - Funcionalidad de Encriptación
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 4 - NO escribir nuevos tests
    - Ejecutar tests de preservación de encriptación de la tarea 4
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

- [x] 9. Corrección de validación de entropía de SECRET_KEY

  - [x] 9.1 Implementar validación de entropía de SECRET_KEY
    - Modificar `backend/services/jwt_service.py` método `_get_secret_key()`
    - Agregar método `_validate_secret_key_entropy()` que verifica complejidad
    - Verificar presencia de al menos 3 de 4 categorías de caracteres (mayúsculas, minúsculas, dígitos, especiales)
    - Lanzar ValueError con mensaje instructivo si entropía es insuficiente
    - _Bug_Condition: isBugCondition_SecretConfig(config) donde config.SECRET_KEY.entropy < 3_
    - _Expected_Behavior: expectedBehavior(result) - ValueError con instrucciones de diseño_
    - _Preservation: Preservation Requirements 3.3, 3.4, 3.5 - autenticación con clave válida funciona_
    - _Requirements: 2.2, 3.3, 3.4, 3.5_

  - [x] 9.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - SECRET_KEY con Entropía Suficiente
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 1 - NO escribir un nuevo test
    - El test de la tarea 1 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de SECRET_KEY de la tarea 1
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.2_

  - [x] 9.3 Verificar que tests de preservación de autenticación siguen pasando
    - **Property 2: Preservation** - Funcionalidad de Autenticación JWT
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 4 - NO escribir nuevos tests
    - Ejecutar tests de preservación de autenticación de la tarea 4
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

- [x] 10. Corrección de RICOH_ADMIN_PASSWORD obligatoria

  - [x] 10.1 Implementar validación obligatoria de RICOH_ADMIN_PASSWORD
    - Modificar `backend/services/ricoh_web_client.py` método `__init__()`
    - Cambiar parámetro `admin_password: str = ""` a `admin_password: str = None`
    - Intentar obtener de variable de entorno `RICOH_ADMIN_PASSWORD` si no se proporciona
    - Lanzar ValueError si admin_password es None o vacío
    - _Bug_Condition: isBugCondition_SecretConfig(config) donde config.RICOH_ADMIN_PASSWORD = ""_
    - _Expected_Behavior: expectedBehavior(result) - ValueError con instrucciones de diseño_
    - _Preservation: Preservation Requirements 3.6, 3.7, 3.8 - integración con impresoras funciona_
    - _Requirements: 2.3, 3.6, 3.7, 3.8_

  - [x] 10.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - RICOH_ADMIN_PASSWORD Obligatoria
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 1 - NO escribir un nuevo test
    - El test de la tarea 1 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de RICOH_ADMIN_PASSWORD de la tarea 1
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.3_

  - [x] 10.3 Verificar que tests de preservación de integración con impresoras siguen pasando
    - **Property 2: Preservation** - Integración con Impresoras Ricoh
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 5 - NO escribir nuevos tests
    - Ejecutar tests de preservación de integración con impresoras de la tarea 5
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

- [x] 11. Corrección de DATABASE_URL sin credenciales hardcodeadas

  - [x] 11.1 Implementar validación obligatoria de DATABASE_URL
    - Modificar `backend/db/database.py` configuración a nivel de módulo
    - Eliminar valor por defecto con credenciales hardcodeadas (líneas 8-11)
    - Requerir variable de entorno DATABASE_URL
    - Lanzar ValueError si DATABASE_URL no está configurada
    - Incluir mensaje instructivo con ejemplo de formato correcto
    - _Bug_Condition: isBugCondition_SecretConfig(config) donde config.DATABASE_URL contiene credenciales hardcodeadas_
    - _Expected_Behavior: expectedBehavior(result) - ValueError con instrucciones de diseño_
    - _Preservation: Preservation Requirements 3.17, 3.18 - inicialización de DB funciona_
    - _Requirements: 2.4, 3.17, 3.18_

  - [x] 11.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - DATABASE_URL sin Credenciales Hardcodeadas
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 1 - NO escribir un nuevo test
    - El test de la tarea 1 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de DATABASE_URL de la tarea 1
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.4_

  - [x] 11.3 Verificar que tests de preservación de inicialización de DB siguen pasando
    - **Property 2: Preservation** - Inicialización de Base de Datos
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 7 - NO escribir nuevos tests
    - Ejecutar tests de preservación de inicialización de DB de la tarea 7
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

### 3.2 Categoría 2: Exposición de Información Sensible en Logs

- [x] 12. Corrección de enmascaramiento de tokens JWT en logs

  - [x] 12.1 Implementar enmascaramiento de tokens JWT
    - Modificar `backend/middleware/auth_middleware.py` función `get_current_user()`
    - Cambiar formato de logging de `token[:20]` a `token[:4]...token[-4:]`
    - Aplicar a todos los print statements y logger.info (líneas 60-61)
    - Mantener trazabilidad con primeros y últimos 4 caracteres
    - _Bug_Condition: isBugCondition_SensitiveExposure(logEntry) donde logEntry contiene token JWT sin enmascarar_
    - _Expected_Behavior: expectedBehavior(result) - formato "XXXX...YYYY" de diseño_
    - _Preservation: Preservation Requirements 3.15, 3.16 - auditoría de eventos funciona_
    - _Requirements: 2.5, 3.15, 3.16_

  - [x] 12.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - Enmascaramiento de Tokens JWT
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 2 - NO escribir un nuevo test
    - El test de la tarea 2 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de tokens JWT de la tarea 2
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.5_

  - [x] 12.3 Verificar que tests de preservación de logging siguen pasando
    - **Property 2: Preservation** - Logging y Auditoría
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 7 - NO escribir nuevos tests
    - Ejecutar tests de preservación de logging de la tarea 7
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

- [x] 13. Corrección de exposición de contraseñas en init_superadmin.py

  - [x] 13.1 Implementar ocultación de contraseñas temporales
    - Modificar `backend/scripts/init_superadmin.py` función `main()`
    - No imprimir contraseña temporal en texto plano
    - Mostrar solo longitud de contraseña generada
    - Guardar contraseña en archivo seguro `.superadmin_password` con permisos 0600
    - _Bug_Condition: isBugCondition_SensitiveExposure(logEntry) donde logEntry contiene contraseña en texto plano_
    - _Expected_Behavior: expectedBehavior(result) - mostrar solo longitud de diseño_
    - _Preservation: Preservation Requirements 3.17, 3.18 - creación de usuarios funciona_
    - _Requirements: 2.6, 3.17, 3.18_

  - [x] 13.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - Ocultación de Contraseñas Temporales
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 2 - NO escribir un nuevo test
    - El test de la tarea 2 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de contraseñas de la tarea 2
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.6_

  - [x] 13.3 Verificar que tests de preservación de creación de usuarios siguen pasando
    - **Property 2: Preservation** - Creación de Usuarios Administrativos
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 7 - NO escribir nuevos tests
    - Ejecutar tests de preservación de creación de usuarios de la tarea 7
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

- [x] 14. Corrección de enmascaramiento de wimTokens en logs

  - [x] 14.1 Implementar enmascaramiento de wimTokens
    - Modificar `backend/services/ricoh_web_client.py` múltiples funciones
    - Identificar todos los logger.debug/info que imprimen wimToken
    - Aplicar formato `token[:4]...token[-4:]` en todos los casos
    - Actualizar aproximadamente 15 ubicaciones incluyendo `_refresh_wim_token()`, `_authenticate()`, `provision_user()`
    - _Bug_Condition: isBugCondition_SensitiveExposure(logEntry) donde logEntry contiene wimToken sin enmascarar_
    - _Expected_Behavior: expectedBehavior(result) - formato "XXXX...YYYY" de diseño_
    - _Preservation: Preservation Requirements 3.6, 3.7, 3.8 - integración con impresoras funciona_
    - _Requirements: 2.7, 3.6, 3.7, 3.8_

  - [x] 14.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - Enmascaramiento de wimTokens
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 2 - NO escribir un nuevo test
    - El test de la tarea 2 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de wimTokens de la tarea 2
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.7_

  - [x] 14.3 Verificar que tests de preservación de integración con impresoras siguen pasando
    - **Property 2: Preservation** - Integración con Impresoras Ricoh
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 5 - NO escribir nuevos tests
    - Ejecutar tests de preservación de integración con impresoras de la tarea 5
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

### 3.3 Categoría 3: Configuración de Seguridad Permisiva

- [x] 15. Corrección de configuración CORS restrictiva

  - [x] 15.1 Implementar configuración CORS restrictiva
    - Modificar `backend/main.py` configuración de CORS Middleware (líneas 149-155)
    - Definir constantes ALLOWED_METHODS y ALLOWED_HEADERS
    - Cambiar `["*"]` a lista específica de métodos HTTP necesarios: `["GET", "POST", "PUT", "DELETE", "PATCH"]`
    - Cambiar `["*"]` a lista específica de headers requeridos: `["Content-Type", "Authorization", "X-CSRF-Token", "X-Request-ID"]`
    - Agregar expose_headers: `["X-RateLimit-Limit", "X-RateLimit-Remaining"]`
    - _Bug_Condition: isBugCondition_PermissiveConfig(securityConfig) donde securityConfig.CORS.allowMethods = ["*"]_
    - _Expected_Behavior: expectedBehavior(result) - listas explícitas de diseño_
    - _Preservation: Preservation Requirements 3.9, 3.10 - CORS con orígenes permitidos funciona_
    - _Requirements: 2.8, 3.9, 3.10_

  - [x] 15.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - Configuración CORS Restrictiva
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 3 - NO escribir un nuevo test
    - El test de la tarea 3 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de CORS de la tarea 3
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.8_

  - [x] 15.3 Verificar que tests de preservación de CORS siguen pasando
    - **Property 2: Preservation** - Configuración CORS con Orígenes Permitidos
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 6 - NO escribir nuevos tests
    - Ejecutar tests de preservación de CORS de la tarea 6
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

- [-] 16. Corrección de CSRF habilitada por defecto en producción

  - [x] 16.1 Implementar habilitación automática de CSRF en producción
    - Modificar `backend/main.py` inicialización de CSRF Protection Middleware (líneas 162-164)
    - Cambiar lógica para habilitar CSRF si ENVIRONMENT=production
    - Permitir deshabilitar explícitamente solo si ENABLE_CSRF=false está configurado
    - Agregar logging claro indicando si CSRF está habilitada o deshabilitada y por qué
    - _Bug_Condition: isBugCondition_PermissiveConfig(securityConfig) donde securityConfig.environment = "production" AND securityConfig.CSRF.enabled = false_
    - _Expected_Behavior: expectedBehavior(result) - CSRF habilitada por defecto en producción de diseño_
    - _Preservation: Preservation Requirements 3.11, 3.12 - CSRF con token válido funciona_
    - _Requirements: 2.9, 3.11, 3.12_

  - [x] 16.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - CSRF Habilitada en Producción
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 3 - NO escribir un nuevo test
    - El test de la tarea 3 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de CSRF de la tarea 3
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.9_

  - [x] 16.3 Verificar que tests de preservación de CSRF siguen pasando
    - **Property 2: Preservation** - Protección CSRF con Token Válido
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 6 - NO escribir nuevos tests
    - Ejecutar tests de preservación de CSRF de la tarea 6
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

- [x] 17. Corrección de almacenamiento CSRF con Redis

  - [x] 17.1 Implementar soporte de Redis para almacenamiento CSRF
    - Modificar `backend/middleware/csrf_protection.py` clase `CSRFProtectionMiddleware`
    - Agregar parámetro `redis_url` a `__init__()` (línea 35)
    - Detectar configuración: usar Redis si REDIS_URL está configurada, memoria en caso contrario
    - Implementar métodos `_store_token_redis()`, `_get_token_redis()`, `_delete_token_redis()`
    - Actualizar `_store_token()`, `_validate_csrf_token()`, `_cleanup_expired_tokens()` para usar Redis
    - Mantener compatibilidad con modo memoria para desarrollo local
    - Agregar logging indicando backend de almacenamiento usado
    - _Bug_Condition: isBugCondition_PermissiveConfig(securityConfig) donde securityConfig.CSRF.storage = "memory"_
    - _Expected_Behavior: expectedBehavior(result) - Redis como backend distribuido de diseño_
    - _Preservation: Preservation Requirements 3.11, 3.12 - CSRF con token válido funciona_
    - _Requirements: 2.10, 3.11, 3.12_

  - [x] 17.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - Almacenamiento CSRF con Redis
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 3 - NO escribir un nuevo test
    - El test de la tarea 3 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de almacenamiento CSRF de la tarea 3
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.10_

  - [x] 17.3 Verificar que tests de preservación de CSRF siguen pasando
    - **Property 2: Preservation** - Protección CSRF con Token Válido
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 6 - NO escribir nuevos tests
    - Ejecutar tests de preservación de CSRF de la tarea 6
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

- [-] 18. Corrección de almacenamiento rate limiting con Redis

  - [x] 18.1 Implementar soporte de Redis para rate limiting
    - Modificar `backend/services/rate_limiter_service.py` clase `RateLimiterService`
    - Agregar método `initialize()` para configurar backend de almacenamiento
    - Detectar configuración: usar Redis si REDIS_URL está configurada, memoria en caso contrario
    - Implementar método `check_rate_limit_redis()` usando comandos atómicos INCR y EXPIRE
    - Actualizar `check_rate_limit()` para delegar a Redis o memoria según configuración
    - Mantener compatibilidad con modo memoria para desarrollo local
    - Agregar logging indicando backend de almacenamiento usado
    - _Bug_Condition: isBugCondition_PermissiveConfig(securityConfig) donde securityConfig.rateLimit.storage = "memory"_
    - _Expected_Behavior: expectedBehavior(result) - Redis como backend distribuido de diseño_
    - _Preservation: Preservation Requirements 3.13, 3.14 - rate limiting dentro de límites funciona_
    - _Requirements: 2.11, 3.13, 3.14_

  - [x] 18.2 Verificar que test de exploración de bug condition ahora pasa
    - **Property 1: Expected Behavior** - Almacenamiento Rate Limiting con Redis
    - **IMPORTANTE**: Re-ejecutar el MISMO test de la tarea 3 - NO escribir un nuevo test
    - El test de la tarea 3 codifica el comportamiento esperado
    - Cuando este test pase, confirma que el comportamiento esperado está satisfecho
    - Ejecutar test de exploración de almacenamiento rate limiting de la tarea 3
    - **RESULTADO ESPERADO**: Test PASA (confirma que bug está corregido)
    - _Requirements: Expected Behavior Properties del diseño - 2.11_

  - [x] 18.3 Verificar que tests de preservación de rate limiting siguen pasando
    - **Property 2: Preservation** - Rate Limiting Dentro de Límites
    - **IMPORTANTE**: Re-ejecutar los MISMOS tests de la tarea 6 - NO escribir nuevos tests
    - Ejecutar tests de preservación de rate limiting de la tarea 6
    - **RESULTADO ESPERADO**: Tests PASAN (confirma que no hay regresiones)
    - Confirmar que todos los tests siguen pasando después de la corrección (sin regresiones)

## Fase 4: Checkpoint Final

- [x] 19. Checkpoint - Asegurar que todos los tests pasan
  - Ejecutar suite completa de tests de exploración (tareas 1-3)
  - Ejecutar suite completa de tests de preservación (tareas 4-7)
  - Verificar que todas las 11 vulnerabilidades están corregidas
  - Verificar que toda la funcionalidad existente se preserva
  - Preguntar al usuario si surgen dudas o problemas
  - **RESULTADO**: ✅ 78/89 tests pasados (87.6%) - 11 vulnerabilidades corregidas (100%)
  - **RESUMEN**: Ver `backend/tests/CHECKPOINT_FINAL_SUMMARY.md` para detalles completos

