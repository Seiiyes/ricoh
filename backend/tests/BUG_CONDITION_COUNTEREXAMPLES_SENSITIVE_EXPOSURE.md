# Bug Condition Counterexamples - Sensitive Information Exposure

**Fecha**: 2024
**Spec**: correccion-vulnerabilidades-seguridad-auditoria
**Tarea**: 2. Escribir tests de exploración para exposición de información sensible

## Resumen

Los tests de exploración han confirmado que el código sin corregir expone información sensible en logs. Se documentan a continuación los contraejemplos específicos encontrados.

## Contraejemplos Encontrados

### 1. Exposición de Tokens JWT en auth_middleware.py

**Ubicación**: `backend/middleware/auth_middleware.py`, líneas 60-61

**Bug Condition**: El middleware de autenticación expone los primeros 20 caracteres del token JWT en logs.

**Código Vulnerable**:
```python
print(f"[AUTH] Autenticación iniciada - Token: {token[:20] if token else 'NONE'}...")
logger.info(f"🔐 Autenticación iniciada - Token: {token[:20] if token else 'NONE'}...")
```

**Contraejemplo**:
```
Token completo: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

Log expuesto: "Token: eyJhbGciOiJIUzI1NiIsI..."

Caracteres expuestos: 20 (esperado: ≤ 8)
```

**Impacto**: Los primeros 20 caracteres del token JWT incluyen el algoritmo de firma y el tipo de token, información que puede facilitar ataques criptográficos.

**Comportamiento Esperado**: Enmascarar el token mostrando solo los primeros 4 y últimos 4 caracteres:
```python
token_preview = f"{token[:4]}...{token[-4:]}" if token and len(token) > 8 else "NONE"
print(f"[AUTH] Autenticación iniciada - Token: {token_preview}")
logger.info(f"🔐 Autenticación iniciada - Token: {token_preview}")
```

**Resultado Esperado**: `"Token: eyJh...w5c"` (8 caracteres totales)

---

### 2. Exposición de Contraseñas en init_superadmin.py

**Ubicación**: `backend/scripts/init_superadmin.py`, línea ~150

**Bug Condition**: El script de inicialización imprime la contraseña temporal del superadmin en texto plano.

**Código Vulnerable**:
```python
print(f"   Password: {temp_password}")
```

**Contraejemplo**:
```
Contraseña generada: "kdXHhl5WcI+^(2L^"

Output en consola:
   Password: kdXHhl5WcI+^(2L^
```

**Impacto**: La contraseña queda visible en:
- Output de consola
- Logs del sistema
- Historial del terminal
- Capturas de pantalla

Esto compromete la seguridad de la cuenta de superadmin.

**Comportamiento Esperado**: Mostrar solo la longitud de la contraseña y guardarla en un archivo seguro:
```python
print(f"   Password: [Saved to secure file: .superadmin_password]")
print(f"   Password length: {len(temp_password)} characters")

# Guardar en archivo con permisos restrictivos
password_file = backend_dir / '.superadmin_password'
password_file.write_text(temp_password)
os.chmod(password_file, 0o600)  # Solo lectura para el propietario
```

---

### 3. Exposición de wimTokens en ricoh_web_client.py

**Ubicación**: `backend/services/ricoh_web_client.py`, múltiples ubicaciones

**Bug Condition**: El cliente web de Ricoh registra wimTokens completos sin enmascarar en múltiples lugares.

#### 3.1 En _refresh_wim_token() - Línea 94

**Código Vulnerable**:
```python
logger.debug(f"✅ Nuevo wimToken obtenido: {token}")
```

**Contraejemplo**:
```
wimToken: "1234567890123456"

Log expuesto: "✅ Nuevo wimToken obtenido: 1234567890123456"

Caracteres expuestos: 16 (esperado: ≤ 8)
```

#### 3.2 En _authenticate() - Línea 171

**Código Vulnerable**:
```python
logger.debug(f"Login wimToken obtenido: {login_token}")
```

**Contraejemplo**:
```
wimToken: "9876543210987654"

Log expuesto: "Login wimToken obtenido: 9876543210987654"

Caracteres expuestos: 16 (esperado: ≤ 8)
```

#### 3.3 En provision_user() - Líneas 262 y 294

**Código Vulnerable**:
```python
logger.info(f"✅ wimToken de lista obtenido: {list_wim_token}")
logger.info(f"✅ wimToken FRESCO del formulario obtenido: {wim_token}")
```

**Contraejemplo**:
```
wimToken 1: "1111222233334444"
wimToken 2: "5555666677778888"

Logs expuestos:
"✅ wimToken de lista obtenido: 1111222233334444"
"✅ wimToken FRESCO del formulario obtenido: 5555666677778888"

Caracteres expuestos: 16 cada uno (esperado: ≤ 8)
```

**Impacto**: Los wimTokens son identificadores de sesión para impresoras Ricoh. Exponerlos en logs permite:
- Secuestro de sesión (session hijacking)
- Acceso no autorizado a funciones de la impresora
- Manipulación de configuraciones de usuarios

**Comportamiento Esperado**: Enmascarar todos los wimTokens usando el formato estándar:
```python
token_preview = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else token
logger.debug(f"✅ Nuevo wimToken obtenido: {token_preview}")
```

**Resultado Esperado**: `"✅ Nuevo wimToken obtenido: 1234...6789"` (8 caracteres totales)

#### 3.4 Ubicaciones Adicionales

El análisis del código identifica aproximadamente **15+ ubicaciones** adicionales donde wimTokens se registran sin enmascarar:

- `_get_user_details()` - múltiples ubicaciones
- `set_user_functions()` - múltiples ubicaciones
- `update_user_in_printer()` - múltiples ubicaciones
- Otros métodos que manejan wimTokens

**Todas estas ubicaciones requieren aplicar el mismo enmascaramiento.**

---

## Resultados de Tests

### Tests Ejecutados: 11
- **Fallidos (esperado)**: 7
- **Pasados**: 4 (tests de documentación)

### Tests Fallidos (Confirman Bugs)

1. ✗ `test_bug_condition_jwt_token_exposure_in_auth_middleware` - Confirma exposición de 20 caracteres de JWT
2. ✗ `test_bug_condition_jwt_token_exposure_print_statement` - Confirma exposición en print statements
3. ✗ `test_bug_condition_password_exposure_in_init_superadmin` - Confirma exposición de contraseña en texto plano
4. ✗ `test_bug_condition_wimtoken_exposure_in_ricoh_client` - Confirma exposición de wimTokens completos
5. ✗ `test_bug_condition_wimtoken_in_refresh_method` - Confirma exposición en _refresh_wim_token()
6. ✗ `test_bug_condition_wimtoken_in_authenticate_method` - Confirma exposición en _authenticate()
7. ✗ `test_bug_condition_wimtoken_in_provision_user_method` - Confirma exposición en provision_user()

### Tests Pasados (Documentación)

1. ✓ `test_document_jwt_token_20_chars_exposure` - Documenta el bug de JWT
2. ✓ `test_document_password_plaintext_exposure` - Documenta el bug de contraseñas
3. ✓ `test_document_wimtoken_full_exposure` - Documenta el bug de wimTokens
4. ✓ `test_document_multiple_wimtoken_locations` - Documenta ubicaciones múltiples

---

## Property-Based Testing

Se utilizó Hypothesis para generar casos de prueba con diferentes longitudes de tokens:

```python
@given(token_length=st.integers(min_value=10, max_value=50))
@settings(max_examples=10, deadline=None)
def test_bug_condition_wimtoken_exposure_in_ricoh_client(self, token_length):
    # Genera tokens de 10-50 caracteres y verifica enmascaramiento
```

**Contraejemplo encontrado por Hypothesis**:
```
Falsifying example: token_length=10
Token: "0123456789"
Exposición: 10 caracteres (esperado: ≤ 8)
```

Hypothesis generó **70+ casos de prueba** con diferentes longitudes de token, todos confirmando el bug.

---

## Validación de Requirements

### Requirement 2.5 - Enmascaramiento de Tokens JWT
**Estado**: ❌ FALLA en código sin corregir
- Expone 20 caracteres en lugar de 8
- Presente en 2 ubicaciones (print y logger)

### Requirement 2.6 - Ocultación de Contraseñas Temporales
**Estado**: ❌ FALLA en código sin corregir
- Imprime contraseña completa en texto plano
- Ejemplo: "kdXHhl5WcI+^(2L^"

### Requirement 2.7 - Enmascaramiento de wimTokens
**Estado**: ❌ FALLA en código sin corregir
- Expone tokens completos (16 caracteres)
- Presente en 15+ ubicaciones en ricoh_web_client.py

---

## Próximos Pasos

1. **Implementar correcciones** según el diseño especificado
2. **Re-ejecutar tests** para verificar que ahora pasan
3. **Ejecutar tests de preservación** para asegurar que no hay regresiones
4. **Actualizar documentación** con resultados de tests corregidos

---

## Notas Técnicas

### Formato de Enmascaramiento Estándar

Para todos los tokens (JWT, wimToken, etc.):
```python
def mask_token(token: str) -> str:
    """Mask token showing only first 4 and last 4 characters"""
    if not token or len(token) <= 8:
        return "****"
    return f"{token[:4]}...{token[-4:]}"
```

### Manejo de Contraseñas

Para contraseñas temporales:
```python
# NO hacer esto:
print(f"Password: {password}")

# Hacer esto:
print(f"Password length: {len(password)} characters")
print(f"Password saved to: {secure_file_path}")
```

### Consideraciones de Seguridad

1. **Logs de producción**: Nunca deben contener información sensible sin enmascarar
2. **Logs de desarrollo**: Aplicar el mismo estándar para evitar fugas accidentales
3. **Auditoría**: Los logs enmascarados aún permiten correlación (primeros y últimos 4 caracteres)
4. **Compliance**: El enmascaramiento cumple con estándares de seguridad (OWASP, PCI-DSS)

---

**Conclusión**: Los tests de exploración han confirmado exitosamente la existencia de las 3 vulnerabilidades de exposición de información sensible especificadas en el documento de requisitos. Los contraejemplos documentados proporcionan evidencia clara para proceder con las correcciones.
