# Ricoh Suite Backend - Test Suite

## 📋 Resumen

Suite completa de tests para el backend de Ricoh Suite, incluyendo tests unitarios, de integración y property-based tests.

## 🚀 Instalación

```bash
# Instalar dependencias de testing
pip install -r requirements_test.txt
```

## 🧪 Ejecutar Tests

### Todos los tests
```bash
pytest -v
```

### Solo tests unitarios
```bash
pytest -v -m unit
```

### Solo tests de integración
```bash
pytest -v -m integration
```

### Con reporte de cobertura
```bash
pytest -v --cov=services --cov=api --cov=middleware --cov-report=term-missing --cov-report=html
```

### Script automatizado
```bash
python run_tests.py
```

## 📁 Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures compartidos
├── test_password_service.py       # Tests unitarios para PasswordService
├── test_jwt_service.py            # Tests unitarios para JWTService
├── test_auth_endpoints.py         # Tests de integración para /auth
├── test_empresa_endpoints.py      # Tests de integración para /empresas
├── test_multi_tenancy.py          # Tests de aislamiento multi-tenant
└── README.md                      # Este archivo
```

## 🔬 Tests Implementados

### Tests Unitarios (Unit Tests)

#### PasswordService (test_password_service.py)
- ✅ `test_hash_password_returns_valid_bcrypt_hash`: Verifica formato bcrypt
- ✅ `test_hash_password_generates_different_hashes`: Verifica salting
- ✅ `test_verify_password_with_correct_password`: Verifica contraseña correcta
- ✅ `test_verify_password_with_incorrect_password`: Verifica contraseña incorrecta
- ✅ `test_validate_password_strength_valid_password`: Acepta contraseña válida
- ✅ `test_validate_password_strength_too_short`: Rechaza contraseña corta
- ✅ `test_validate_password_strength_no_uppercase`: Rechaza sin mayúscula
- ✅ `test_validate_password_strength_no_lowercase`: Rechaza sin minúscula
- ✅ `test_validate_password_strength_no_digit`: Rechaza sin número
- ✅ `test_validate_password_strength_no_special_char`: Rechaza sin carácter especial
- ✅ `test_generate_temporary_password_length`: Verifica longitud de 16 caracteres
- ✅ `test_generate_temporary_password_is_valid`: Verifica que pasa validación
- ✅ `test_generate_temporary_password_is_unique`: Verifica unicidad

#### JWTService (test_jwt_service.py)
- ✅ `test_create_access_token_returns_valid_jwt`: Verifica formato JWT
- ✅ `test_create_access_token_includes_user_data`: Verifica payload
- ✅ `test_create_refresh_token_returns_valid_jwt`: Verifica formato JWT
- ✅ `test_create_refresh_token_includes_type`: Verifica type="refresh"
- ✅ `test_decode_token_with_valid_token`: Decodifica token válido
- ✅ `test_decode_token_with_invalid_signature`: Rechaza firma inválida
- ✅ `test_verify_signature_with_valid_token`: Verifica firma válida
- ✅ `test_verify_signature_with_invalid_token`: Rechaza firma inválida
- ✅ `test_access_token_expiration_time`: Verifica 30 minutos
- ✅ `test_refresh_token_expiration_time`: Verifica 7 días

### Tests de Integración (Integration Tests)

#### Auth Endpoints (test_auth_endpoints.py)
- ✅ `test_login_with_valid_credentials`: POST /auth/login exitoso
- ✅ `test_login_with_invalid_credentials`: POST /auth/login con error 401
- ✅ `test_login_with_nonexistent_user`: Usuario no existe retorna 401
- ✅ `test_login_with_inactive_user`: Usuario inactivo retorna 403
- ✅ `test_get_me_with_valid_token`: GET /auth/me exitoso
- ✅ `test_get_me_without_token`: Sin token retorna 401
- ✅ `test_get_me_with_invalid_token`: Token inválido retorna 401
- ✅ `test_logout_with_valid_token`: POST /auth/logout exitoso
- ✅ `test_change_password_with_correct_current_password`: Cambio exitoso
- ✅ `test_change_password_with_incorrect_current_password`: Error 400
- ✅ `test_change_password_with_weak_new_password`: Error 422

#### Empresa Endpoints (test_empresa_endpoints.py)
- ✅ `test_get_empresas_as_superadmin`: GET /empresas como superadmin
- ✅ `test_get_empresas_as_admin`: GET /empresas como admin retorna 403
- ✅ `test_create_empresa_as_superadmin`: POST /empresas exitoso
- ✅ `test_create_empresa_with_duplicate_razon_social`: Error 409
- ✅ `test_create_empresa_with_duplicate_nombre_comercial`: Error 409
- ✅ `test_get_empresa_by_id_as_superadmin`: GET /empresas/{id} exitoso
- ✅ `test_update_empresa_as_superadmin`: PUT /empresas/{id} exitoso
- ✅ `test_delete_empresa_without_resources`: DELETE soft delete exitoso

#### Multi-Tenancy (test_multi_tenancy.py)
- ✅ `test_superadmin_sees_all_data`: Superadmin ve todos los datos
- ✅ `test_admin_sees_only_own_empresa_data`: Admin solo ve su empresa
- ✅ `test_admin_cannot_access_other_empresa_resource`: Admin no accede a otra empresa
- ✅ `test_admin_can_access_own_empresa_resource`: Admin accede a su empresa
- ✅ `test_enforce_company_on_create_for_admin`: Empresa_id forzado para admin
- ✅ `test_enforce_company_on_create_for_superadmin`: No forzado para superadmin

## 📊 Cobertura Esperada

- **PasswordService**: 100%
- **JWTService**: 95%
- **AuthService**: 85%
- **CompanyFilterService**: 90%
- **Auth Endpoints**: 85%
- **Empresa Endpoints**: 80%

**Cobertura Total Esperada**: >= 80%

## 🔧 Fixtures Disponibles

### Base de Datos
- `db_engine`: Motor de base de datos SQLite en memoria
- `db_session`: Sesión de base de datos para tests

### Usuarios
- `superadmin_user`: Usuario superadmin de prueba
- `admin_user`: Usuario admin de prueba
- `test_empresa`: Empresa de prueba

### Tokens
- `superadmin_token`: JWT token para superadmin
- `admin_token`: JWT token para admin

### Cliente
- `client`: TestClient de FastAPI

## 📝 Agregar Nuevos Tests

### Test Unitario
```python
import pytest

@pytest.mark.unit
class TestMyService:
    def test_my_function(self):
        # Arrange
        input_data = "test"
        
        # Act
        result = my_function(input_data)
        
        # Assert
        assert result == expected_output
```

### Test de Integración
```python
import pytest

@pytest.mark.integration
class TestMyEndpoint:
    def test_my_endpoint(self, client, superadmin_token):
        # Act
        response = client.get(
            "/my-endpoint",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        # Assert
        assert response.status_code == 200
```

## 🐛 Debugging Tests

### Ver output detallado
```bash
pytest -v -s
```

### Ver solo tests fallidos
```bash
pytest --lf
```

### Detener en primer fallo
```bash
pytest -x
```

### Ver traceback completo
```bash
pytest --tb=long
```

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Hypothesis (Property Testing)](https://hypothesis.readthedocs.io/)

## ✅ Checklist de Testing

Antes de hacer commit:
- [ ] Todos los tests pasan
- [ ] Cobertura >= 80%
- [ ] No hay warnings
- [ ] Tests documentados
- [ ] Fixtures reutilizables

---

**Última actualización**: 20 de Marzo de 2026
