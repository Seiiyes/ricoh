# FASE 4: Consolidación de Servicios

**Fecha inicio:** 20 de Marzo de 2026  
**Prioridad:** ALTA  
**Objetivo:** Eliminar duplicación en servicios críticos y reorganizar código

---

## RESUMEN

Esta fase consolida servicios duplicados, reorganiza parsers y centraliza validaciones para reducir la duplicación de código del 5% al 2%.

---

## TAREA 1: Consolidar Servicios de Encriptación

### Problema Actual

Existen 2 servicios de encriptación casi idénticos:

**`backend/services/encryption.py`** (PasswordEncryptionService):
- Clase con `__init__` que acepta encryption_key
- Métodos de instancia: `encrypt()`, `decrypt()`
- Función singleton: `get_encryption_service()`
- Usado principalmente para passwords de red

**`backend/services/encryption_service.py`** (EncryptionService):
- Clase con métodos de clase (`@classmethod`)
- Métodos: `encrypt()`, `decrypt()`, `encrypt_dict()`, `decrypt_dict()`
- Inicialización automática al importar
- Métodos adicionales: `generate_key()`, `derive_key_from_password()`, `is_encrypted()`
- Usado para datos sensibles en BD

### Análisis

Ambos servicios:
- Usan Fernet (AES-128 en modo CBC con HMAC)
- Leen `ENCRYPTION_KEY` del entorno
- Generan clave temporal en desarrollo
- Convierten entre bytes y strings

**Diferencias clave:**
- `encryption_service.py` tiene más funcionalidad (diccionarios, derivación de claves)
- `encryption.py` usa patrón de instancia, `encryption_service.py` usa métodos de clase

### Solución

**Mantener:** `backend/services/encryption_service.py` (más completo)  
**Eliminar:** `backend/services/encryption.py`

**Razones:**
1. `EncryptionService` tiene más funcionalidad
2. Métodos de clase son más simples de usar
3. Ya tiene inicialización automática
4. Incluye métodos para diccionarios (útil para BD)

### Pasos de Implementación

#### 1.1 Identificar usos de `encryption.py`

```bash
# Buscar imports
grep -r "from services.encryption import" backend/
grep -r "from .encryption import" backend/
grep -r "import encryption" backend/
```

**Archivos que probablemente lo usan:**
- `backend/db/models.py` (para passwords de red en Printer)
- `backend/api/printers.py` (al crear/actualizar impresoras)
- Posiblemente otros servicios

#### 1.2 Actualizar imports

**Antes:**
```python
from services.encryption import PasswordEncryptionService, get_encryption_service

# Uso
encryption_service = get_encryption_service()
encrypted = encryption_service.encrypt(password)
```

**Después:**
```python
from services.encryption_service import EncryptionService

# Uso
encrypted = EncryptionService.encrypt(password)
```

#### 1.3 Eliminar archivo

```bash
rm backend/services/encryption.py
```

#### 1.4 Verificar tests

```bash
cd backend
python -m pytest tests/ -v
```

### Archivos a Modificar

- [ ] `backend/db/models.py` - Actualizar imports
- [ ] `backend/api/printers.py` - Actualizar imports
- [ ] Cualquier otro archivo que importe `encryption.py`
- [ ] `backend/services/encryption.py` - ELIMINAR

---

## TAREA 2: Reorganizar Parsers

### Problema Actual

Los parsers están en la raíz de `backend/` en lugar de `backend/services/parsers/`:

```
backend/
├── parsear_contadores.py          # ⚠️ Debe estar en services/parsers/
├── parsear_contadores_usuario.py  # ⚠️ Debe estar en services/parsers/
└── parsear_contador_ecologico.py  # ⚠️ Debe estar en services/parsers/
```

Además, los 3 parsers tienen la función `login_to_printer()` duplicada.

### Solución

**Nueva estructura:**
```
backend/services/parsers/
├── __init__.py
├── ricoh_auth.py              # Autenticación unificada
├── counter_parser.py          # parsear_contadores.py
├── user_counter_parser.py     # parsear_contadores_usuario.py
└── eco_counter_parser.py      # parsear_contador_ecologico.py
```

### Pasos de Implementación

#### 2.1 Crear directorio y estructura

```bash
mkdir -p backend/services/parsers
touch backend/services/parsers/__init__.py
```

#### 2.2 Crear `ricoh_auth.py` con autenticación unificada

**Archivo:** `backend/services/parsers/ricoh_auth.py`

```python
"""
Ricoh Authentication Service
Maneja autenticación unificada para impresoras Ricoh
"""
import requests
import re
import base64
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ADMIN_USER = "admin"
ADMIN_PASS = ""


class RicohAuthService:
    """Servicio de autenticación para impresoras Ricoh"""
    
    @staticmethod
    def login_to_printer(session: requests.Session, printer_ip: str) -> None:
        """
        Login a la impresora - detecta automáticamente el método correcto
        
        Soporta:
        - Método especial para impresoras 252 y 253
        - Método estándar para otras impresoras
        
        Args:
            session: Sesión de requests
            printer_ip: IP de la impresora
            
        Raises:
            Exception: Si el login falla
        """
        # Detectar si es la impresora 252 o 253 (requieren método especial)
        if printer_ip in ["192.168.91.252", "192.168.91.253"]:
            RicohAuthService._login_special_method(session, printer_ip)
        else:
            RicohAuthService._login_standard_method(session, printer_ip)
    
    @staticmethod
    def _login_special_method(session: requests.Session, printer_ip: str) -> None:
        """Método de login especial para impresoras 252 y 253"""
        auth_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi?open=websys/status/getUnificationCounter.cgi"
        auth_resp = session.get(auth_url, timeout=10)
        
        soup = BeautifulSoup(auth_resp.text, 'html.parser')
        wim_token_input = soup.find('input', {'name': 'wimToken'})
        wim_token = wim_token_input.get('value') if wim_token_input else None
        
        login_url = f"http://{printer_ip}/web/guest/es/websys/webArch/login.cgi"
        
        login_data = {
            'userid': base64.b64encode(ADMIN_USER.encode()).decode(),
            'password': base64.b64encode(ADMIN_PASS.encode()).decode(),
            'userid_work': '',
            'password_work': ''
        }
        
        if wim_token:
            login_data['wimToken'] = wim_token
        
        session.post(login_url, data=login_data, timeout=10)
    
    @staticmethod
    def _login_standard_method(session: requests.Session, printer_ip: str) -> None:
        """Método de login estándar para la mayoría de impresoras"""
        login_form_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi"
        form_resp = session.get(login_form_url, timeout=10)
        token_match = re.search(r'name="wimToken"\s+value="(\d+)"', form_resp.text)
        login_token = token_match.group(1) if token_match else ""
        
        userid_b64 = base64.b64encode(ADMIN_USER.encode()).decode()
        login_url = f"http://{printer_ip}/web/guest/es/websys/webArch/login.cgi"
        login_data = {
            'wimToken': login_token,
            'userid_work': '',
            'userid': userid_b64,
            'password_work': '',
            'password': ADMIN_PASS,
            'open': '',
        }
        
        session.post(login_url, data=login_data, timeout=10, allow_redirects=True)
```

#### 2.3 Mover y renombrar parsers

**Mover archivos:**
```bash
# Copiar (no mover aún, por seguridad)
cp backend/parsear_contadores.py backend/services/parsers/counter_parser.py
cp backend/parsear_contadores_usuario.py backend/services/parsers/user_counter_parser.py
cp backend/parsear_contador_ecologico.py backend/services/parsers/eco_counter_parser.py
```

**Actualizar imports en cada parser:**

```python
# Al inicio de cada archivo
from services.parsers.ricoh_auth import RicohAuthService

# Reemplazar función login_to_printer() con:
# RicohAuthService.login_to_printer(session, printer_ip)
```

#### 2.4 Actualizar `__init__.py`

**Archivo:** `backend/services/parsers/__init__.py`

```python
"""
Parsers para impresoras Ricoh
"""
from .counter_parser import get_printer_counters
from .user_counter_parser import get_all_user_counters, get_user_counters
from .eco_counter_parser import get_all_eco_users, get_eco_counter
from .ricoh_auth import RicohAuthService

__all__ = [
    'get_printer_counters',
    'get_all_user_counters',
    'get_user_counters',
    'get_all_eco_users',
    'get_eco_counter',
    'RicohAuthService',
]
```

#### 2.5 Actualizar imports en `counter_service.py`

**Antes:**
```python
from parsear_contadores import get_printer_counters
from parsear_contadores_usuario import get_all_user_counters
from parsear_contador_ecologico import get_all_eco_users
```

**Después:**
```python
from services.parsers import get_printer_counters, get_all_user_counters, get_all_eco_users
```

#### 2.6 Verificar funcionamiento

```bash
# Ejecutar tests
cd backend
python -m pytest tests/ -v

# Probar lectura de contadores
python -c "from services.parsers import get_printer_counters; print('✅ Import OK')"
```

#### 2.7 Eliminar archivos antiguos

```bash
# Solo después de verificar que todo funciona
rm backend/parsear_contadores.py
rm backend/parsear_contadores_usuario.py
rm backend/parsear_contador_ecologico.py
```

### Archivos a Crear/Modificar

- [ ] `backend/services/parsers/__init__.py` - CREAR
- [ ] `backend/services/parsers/ricoh_auth.py` - CREAR
- [ ] `backend/services/parsers/counter_parser.py` - CREAR (copiar y modificar)
- [ ] `backend/services/parsers/user_counter_parser.py` - CREAR (copiar y modificar)
- [ ] `backend/services/parsers/eco_counter_parser.py` - CREAR (copiar y modificar)
- [ ] `backend/services/counter_service.py` - ACTUALIZAR imports
- [ ] `backend/parsear_contadores.py` - ELIMINAR (después de verificar)
- [ ] `backend/parsear_contadores_usuario.py` - ELIMINAR (después de verificar)
- [ ] `backend/parsear_contador_ecologico.py` - ELIMINAR (después de verificar)

---

## TAREA 3: Crear ValidationService Centralizado

### Problema Actual

Validaciones dispersas en múltiples servicios:

```python
# counter_service.py
def validate_counter_data(counters: Dict) -> None:
    if counters is None:
        raise ValueError("Datos de contadores son None")
    if not isinstance(counters, dict):
        raise ValueError(f"Datos de contadores tienen tipo inválido: {type(counters)}")
    # ... más validaciones

def validate_user_counter_data(user: Dict, tipo: str) -> None:
    if user is None:
        raise ValueError("Datos de usuario son None")
    # ... más validaciones
```

### Solución

Crear `ValidationService` centralizado con métodos reutilizables.

### Pasos de Implementación

#### 3.1 Crear `validation_service.py`

**Archivo:** `backend/services/validation_service.py`

```python
"""
Validation Service
Servicio centralizado para validaciones comunes
"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ValidationService:
    """Servicio para validaciones comunes"""
    
    @staticmethod
    def validate_not_none(value: Any, field_name: str) -> None:
        """
        Valida que un valor no sea None
        
        Args:
            value: Valor a validar
            field_name: Nombre del campo (para mensaje de error)
            
        Raises:
            ValueError: Si el valor es None
        """
        if value is None:
            raise ValueError(f"{field_name} no puede ser None")
    
    @staticmethod
    def validate_type(value: Any, expected_type: type, field_name: str) -> None:
        """
        Valida que un valor sea del tipo esperado
        
        Args:
            value: Valor a validar
            expected_type: Tipo esperado
            field_name: Nombre del campo
            
        Raises:
            ValueError: Si el tipo no coincide
        """
        if not isinstance(value, expected_type):
            raise ValueError(
                f"{field_name} debe ser {expected_type.__name__}, "
                f"pero es {type(value).__name__}"
            )
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> None:
        """
        Valida que un diccionario contenga todos los campos requeridos
        
        Args:
            data: Diccionario a validar
            required_fields: Lista de campos requeridos
            
        Raises:
            ValueError: Si falta algún campo
        """
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValueError(
                f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            )
    
    @staticmethod
    def validate_numeric_field(value: Any, field_name: str, 
                               min_value: Optional[int] = None,
                               max_value: Optional[int] = None) -> int:
        """
        Valida y convierte un campo numérico
        
        Args:
            value: Valor a validar
            field_name: Nombre del campo
            min_value: Valor mínimo permitido (opcional)
            max_value: Valor máximo permitido (opcional)
            
        Returns:
            Valor convertido a int
            
        Raises:
            ValueError: Si el valor no es numérico o está fuera de rango
        """
        try:
            numeric_value = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} debe ser un número entero")
        
        if min_value is not None and numeric_value < min_value:
            raise ValueError(f"{field_name} debe ser >= {min_value}")
        
        if max_value is not None and numeric_value > max_value:
            raise ValueError(f"{field_name} debe ser <= {max_value}")
        
        return numeric_value
    
    @staticmethod
    def validate_counter_data(counters: Dict) -> None:
        """
        Valida que los datos de contadores sean consistentes
        
        Args:
            counters: Dict con datos de contadores
            
        Raises:
            ValueError: Si los datos son inconsistentes
        """
        # Validar que no sea None
        ValidationService.validate_not_none(counters, "Datos de contadores")
        
        # Validar tipo
        ValidationService.validate_type(counters, dict, "Datos de contadores")
        
        # Validar campos requeridos
        required_fields = [
            'total', 'copiadora', 'impresora', 'fax', 
            'enviar_total', 'transmision_fax', 'envio_escaner', 'otras_funciones'
        ]
        ValidationService.validate_required_fields(counters, required_fields)
        
        # Validar que total sea numérico
        ValidationService.validate_numeric_field(
            counters['total'], 
            'total', 
            min_value=0
        )
        
        # Validar consistencia: total debe ser >= suma de copiadora + impresora
        suma_minima = (
            counters['copiadora'].get('blanco_negro', 0) +
            counters['copiadora'].get('color', 0) +
            counters['impresora'].get('blanco_negro', 0) +
            counters['impresora'].get('color', 0)
        )
        
        # Permitir total=0 solo si todos los contadores son 0
        if counters['total'] == 0 and suma_minima > 0:
            raise ValueError(
                f"Inconsistencia: total=0 pero suma de contadores={suma_minima}. "
                "Los datos del parser son incorrectos."
            )
        
        # Advertencia si el total es menor que la suma (puede pasar en algunos modelos)
        if counters['total'] > 0 and counters['total'] < suma_minima:
            logger.warning(
                f"Total ({counters['total']}) es menor que suma de contadores ({suma_minima}). "
                "Esto puede ser normal en algunos modelos de impresoras."
            )
    
    @staticmethod
    def validate_user_counter_data(user: Dict, tipo: str) -> None:
        """
        Valida que los datos de contador de usuario sean consistentes
        
        Args:
            user: Dict con datos de usuario
            tipo: "usuario" o "ecologico"
            
        Raises:
            ValueError: Si los datos son inconsistentes
        """
        # Validar que no sea None
        ValidationService.validate_not_none(user, "Datos de usuario")
        
        # Validar tipo
        ValidationService.validate_type(user, dict, "Datos de usuario")
        
        # Validar campos requeridos comunes
        ValidationService.validate_required_fields(
            user, 
            ['codigo_usuario', 'nombre_usuario']
        )
        
        # Validar según tipo
        if tipo == "usuario":
            ValidationService.validate_required_fields(user, ['total_paginas'])
            ValidationService.validate_numeric_field(
                user['total_paginas'],
                'total_paginas',
                min_value=0
            )
        
        elif tipo == "ecologico":
            ValidationService.validate_required_fields(user, ['total_paginas_actual'])
            ValidationService.validate_numeric_field(
                user['total_paginas_actual'],
                'total_paginas_actual',
                min_value=0
            )
        
        else:
            raise ValueError(f"Tipo de contador inválido: {tipo}")
```

#### 3.2 Actualizar `counter_service.py`

**Reemplazar métodos de validación:**

```python
from services.validation_service import ValidationService

class CounterService:
    # Eliminar métodos validate_counter_data y validate_user_counter_data
    # Usar ValidationService en su lugar
    
    @staticmethod
    def read_printer_counters(db: Session, printer_id: int):
        # ...
        counters = get_printer_counters(printer.ip_address)
        
        # Validar datos antes de guardar
        ValidationService.validate_counter_data(counters)
        
        # ...
```

#### 3.3 Verificar tests

```bash
cd backend
python -m pytest tests/ -v
```

### Archivos a Crear/Modificar

- [ ] `backend/services/validation_service.py` - CREAR
- [ ] `backend/services/counter_service.py` - ACTUALIZAR (usar ValidationService)

---

## VERIFICACIÓN FINAL

### Checklist de Completitud

- [ ] Servicio de encriptación consolidado
- [ ] Parsers reorganizados en `services/parsers/`
- [ ] Autenticación Ricoh unificada en `RicohAuthService`
- [ ] `ValidationService` creado y en uso
- [ ] Todos los tests pasando (34/34)
- [ ] Imports actualizados en todos los archivos
- [ ] Archivos antiguos eliminados
- [ ] Documentación actualizada

### Comandos de Verificación

```bash
# 1. Verificar estructura de directorios
ls -la backend/services/parsers/

# 2. Verificar que archivos antiguos fueron eliminados
ls backend/parsear_*.py  # Debe dar error "No such file"

# 3. Ejecutar tests
cd backend
python -m pytest tests/ -v

# 4. Verificar imports
python -c "from services.encryption_service import EncryptionService; print('✅ Encryption OK')"
python -c "from services.parsers import get_printer_counters; print('✅ Parsers OK')"
python -c "from services.validation_service import ValidationService; print('✅ Validation OK')"

# 5. Probar lectura de contadores (requiere impresora disponible)
# python -c "from services.parsers import get_printer_counters; print(get_printer_counters('192.168.91.251'))"
```

### Métricas Esperadas

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Duplicación de código | 5% | 2% | -60% |
| Archivos en raíz backend | 3 parsers | 0 | -100% |
| Servicios de encriptación | 2 | 1 | -50% |
| Funciones login duplicadas | 3 | 1 | -67% |
| Validaciones centralizadas | No | Sí | ✅ |

---

## PRÓXIMOS PASOS

Después de completar esta fase:

1. **Actualizar documentación:**
   - `RESUMEN_PROGRESO_CONSISTENCIA.md`
   - `ANALISIS_ARQUITECTURA_PROYECTO.md`

2. **Iniciar Fase 5:**
   - Centralización de tipos TypeScript
   - Crear estructura `src/types/`

3. **Monitorear:**
   - Verificar que no hay regresiones
   - Revisar logs de producción
   - Confirmar que lecturas de contadores funcionan correctamente

---

**Fecha estimada de completitud:** 20 de Marzo de 2026  
**Tiempo estimado:** 2-3 horas  
**Riesgo:** BAJO (cambios bien definidos, tests existentes)
