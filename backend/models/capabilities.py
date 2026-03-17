#!/usr/bin/env python3
"""
Capabilities Model - Estructura de datos de capacidades de impresora

Este módulo define el modelo de datos para las capacidades detectadas de cada impresora,
incluyendo formato de contadores, soporte de color y campos especiales.
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Capabilities(BaseModel):
    """
    Estructura de datos de capacidades de impresora
    
    Almacena las características técnicas detectadas de una impresora Ricoh,
    incluyendo el formato de contadores, soporte de color y campos especiales.
    
    Attributes:
        formato_contadores: Formato de contadores ('estandar', 'simplificado', 'ecologico')
        has_color: Si la impresora soporta impresión a color
        has_hojas_2_caras: Si soporta impresión dúplex (hojas a 2 caras)
        has_paginas_combinadas: Si soporta múltiples páginas en una hoja
        has_mono_color: Si soporta impresión en un solo color
        has_dos_colores: Si soporta impresión en dos colores
        detected_at: Timestamp ISO 8601 de cuándo se detectaron las capacidades
        manual_override: Si las capacidades fueron configuradas manualmente
    
    Examples:
        >>> caps = Capabilities(
        ...     formato_contadores='estandar',
        ...     has_color=True,
        ...     has_hojas_2_caras=True,
        ...     has_paginas_combinadas=True,
        ...     has_mono_color=True,
        ...     has_dos_colores=True,
        ...     detected_at='2024-03-15T10:30:00Z',
        ...     manual_override=False
        ... )
        >>> caps.formato_contadores
        'estandar'
    """
    
    formato_contadores: str = Field(
        ...,
        description="Formato de contadores: 'estandar' (18+ cols), 'simplificado' (13 cols), 'ecologico'"
    )
    has_color: bool = Field(
        ...,
        description="Si la impresora soporta impresión a color"
    )
    has_hojas_2_caras: bool = Field(
        ...,
        description="Si soporta impresión dúplex (hojas a 2 caras)"
    )
    has_paginas_combinadas: bool = Field(
        ...,
        description="Si soporta múltiples páginas en una hoja"
    )
    has_mono_color: bool = Field(
        ...,
        description="Si soporta impresión en un solo color"
    )
    has_dos_colores: bool = Field(
        ...,
        description="Si soporta impresión en dos colores"
    )
    detected_at: str = Field(
        ...,
        description="Timestamp ISO 8601 de cuándo se detectaron las capacidades"
    )
    manual_override: bool = Field(
        default=False,
        description="Si las capacidades fueron configuradas manualmente"
    )
    
    def to_json(self) -> dict:
        """
        Serializa el objeto Capabilities a un diccionario JSON
        
        Este método se usa para almacenar las capacidades en el campo
        capabilities_json (JSONB) de la tabla printers.
        
        Returns:
            dict: Diccionario con todos los campos de capacidades
            
        Examples:
            >>> caps = Capabilities(
            ...     formato_contadores='estandar',
            ...     has_color=True,
            ...     has_hojas_2_caras=True,
            ...     has_paginas_combinadas=True,
            ...     has_mono_color=True,
            ...     has_dos_colores=True,
            ...     detected_at='2024-03-15T10:30:00Z'
            ... )
            >>> json_data = caps.to_json()
            >>> json_data['formato_contadores']
            'estandar'
        """
        return self.model_dump()
    
    @classmethod
    def from_json(cls, data: dict) -> 'Capabilities':
        """
        Deserializa un diccionario JSON a un objeto Capabilities
        
        Este método se usa para cargar las capacidades desde el campo
        capabilities_json (JSONB) de la tabla printers.
        
        Args:
            data: Diccionario con los campos de capacidades
            
        Returns:
            Capabilities: Objeto Capabilities deserializado
            
        Examples:
            >>> json_data = {
            ...     'formato_contadores': 'estandar',
            ...     'has_color': True,
            ...     'has_hojas_2_caras': True,
            ...     'has_paginas_combinadas': True,
            ...     'has_mono_color': True,
            ...     'has_dos_colores': True,
            ...     'detected_at': '2024-03-15T10:30:00Z',
            ...     'manual_override': False
            ... }
            >>> caps = Capabilities.from_json(json_data)
            >>> caps.has_color
            True
        """
        return cls(**data)
    
    def merge(self, other: 'Capabilities') -> 'Capabilities':
        """
        Merge con otra instancia de Capabilities preservando capacidades detectadas
        
        Regla de merge: Si un campo booleano es True en el objeto existente (self),
        permanece True en el resultado. Esto asegura que una vez detectada una
        capacidad, nunca se "desactiva" automáticamente.
        
        El formato_contadores y detected_at se toman del objeto nuevo (other).
        El manual_override se preserva del objeto existente (self).
        
        Args:
            other: Nuevas capacidades detectadas
            
        Returns:
            Capabilities: Objeto con capacidades merged
            
        Examples:
            >>> existing = Capabilities(
            ...     formato_contadores='estandar',
            ...     has_color=True,
            ...     has_hojas_2_caras=False,
            ...     has_paginas_combinadas=False,
            ...     has_mono_color=False,
            ...     has_dos_colores=False,
            ...     detected_at='2024-03-15T10:00:00Z'
            ... )
            >>> new = Capabilities(
            ...     formato_contadores='estandar',
            ...     has_color=False,
            ...     has_hojas_2_caras=True,
            ...     has_paginas_combinadas=False,
            ...     has_mono_color=False,
            ...     has_dos_colores=False,
            ...     detected_at='2024-03-15T11:00:00Z'
            ... )
            >>> merged = existing.merge(new)
            >>> merged.has_color  # Se preserva True del existing
            True
            >>> merged.has_hojas_2_caras  # Se toma True del new
            True
            >>> merged.detected_at  # Se actualiza con el timestamp nuevo
            '2024-03-15T11:00:00Z'
        """
        return Capabilities(
            formato_contadores=other.formato_contadores,
            has_color=self.has_color or other.has_color,
            has_hojas_2_caras=self.has_hojas_2_caras or other.has_hojas_2_caras,
            has_paginas_combinadas=self.has_paginas_combinadas or other.has_paginas_combinadas,
            has_mono_color=self.has_mono_color or other.has_mono_color,
            has_dos_colores=self.has_dos_colores or other.has_dos_colores,
            detected_at=other.detected_at,
            manual_override=self.manual_override
        )
    
    @classmethod
    def create_default(cls, formato: str = 'estandar') -> 'Capabilities':
        """
        Crea un objeto Capabilities con valores por defecto seguros
        
        Los valores por defecto asumen que la impresora tiene todas las capacidades,
        lo que garantiza que el frontend muestre todas las columnas (retrocompatibilidad).
        
        Args:
            formato: Formato de contadores ('estandar', 'simplificado', 'ecologico')
            
        Returns:
            Capabilities: Objeto con valores por defecto
            
        Examples:
            >>> caps = Capabilities.create_default()
            >>> caps.has_color
            True
            >>> caps.formato_contadores
            'estandar'
        """
        return cls(
            formato_contadores=formato,
            has_color=True,
            has_hojas_2_caras=True,
            has_paginas_combinadas=True,
            has_mono_color=True,
            has_dos_colores=True,
            detected_at=datetime.utcnow().isoformat() + 'Z',
            manual_override=False
        )


# Constantes para validación
VALID_FORMATS = ['estandar', 'simplificado', 'ecologico']


def validate_formato(formato: str) -> bool:
    """
    Valida que el formato de contadores sea uno de los valores permitidos
    
    Args:
        formato: Formato a validar
        
    Returns:
        bool: True si el formato es válido, False en caso contrario
        
    Examples:
        >>> validate_formato('estandar')
        True
        >>> validate_formato('invalido')
        False
    """
    return formato in VALID_FORMATS
