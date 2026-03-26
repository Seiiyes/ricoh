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
