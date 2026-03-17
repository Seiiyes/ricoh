#!/usr/bin/env python3
"""
Capabilities Detector - Detección automática de capacidades de impresora

Este módulo implementa la detección automática de capacidades de impresoras Ricoh,
incluyendo formato de contadores, soporte de color y campos especiales.
"""
from typing import Optional
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.capabilities import Capabilities


class FormatDetector:
    """
    Detector de formato de contadores de impresora
    
    Detecta el formato de la tabla de contadores por usuario basándose en la
    estructura del HTML y el número de columnas.
    
    Formatos soportados:
    - 'estandar': 18+ columnas con class='listData' (impresoras 250, 251)
    - 'simplificado': 13 columnas sin class='listData' (impresora 252)
    - 'ecologico': Formato especial de contadores ecológicos (impresora 253)
    
    Examples:
        >>> detector = FormatDetector()
        >>> html = open('counter_251.html').read()
        >>> formato = detector.detect_format(html)
        >>> print(formato)
        'estandar'
    """
    
    def detect_format(self, html_content: str) -> str:
        """
        Detecta el formato de contadores basándose en el HTML
        
        Algoritmo de detección:
        1. Buscar tabla con class='adTable' o 'tbl_border'
        2. Analizar primera fila de datos (skip headers)
        3. Contar columnas y verificar class='listData'
        4. Determinar formato:
           - 13 columnas sin class='listData' → 'simplificado'
           - 18+ columnas con class='listData' → 'estandar'
           - URL contiene 'getEcoCounter' → 'ecologico'
        
        Args:
            html_content: Contenido HTML de la página de contadores
            
        Returns:
            str: Formato detectado ('estandar', 'simplificado', 'ecologico')
            
        Examples:
            >>> detector = FormatDetector()
            >>> # HTML de impresora 252 (simplificado)
            >>> html_252 = '''
            ... <table class="tbl_border">
            ...   <tr><td>001</td><td>Usuario 1</td><td>100</td>...</tr>
            ... </table>
            ... '''
            >>> detector.detect_format(html_252)
            'simplificado'
            
            >>> # HTML de impresora 251 (estándar)
            >>> html_251 = '''
            ... <table class="adTable">
            ...   <tr><td class="listData">001</td><td class="listData">Usuario 1</td>...</tr>
            ... </table>
            ... '''
            >>> detector.detect_format(html_251)
            'estandar'
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Detectar formato ecológico por URL o estructura
        if 'getEcoCounter' in html_content or 'eco_' in html_content.lower():
            return 'ecologico'
        
        # Buscar tabla principal
        table = soup.find('table', class_='adTable')
        if not table:
            table = soup.find('table', class_='tbl_border')
        
        if not table:
            # Fallback: si no hay tabla, asumir estándar
            return 'estandar'
        
        # Buscar primera fila de datos (skip headers)
        rows = table.find_all('tr')
        for row in rows:
            # Skip header rows
            if row.find('th'):
                continue
            
            # Analizar primera fila de datos
            cells = row.find_all('td')
            if not cells:
                continue
            
            # Contar columnas con class='listData'
            cells_with_class = row.find_all('td', class_='listData')
            
            # Determinar formato
            if len(cells_with_class) >= 18:
                # Formato estándar: 18+ columnas con class='listData'
                return 'estandar'
            elif len(cells) == 13 and len(cells_with_class) == 0:
                # Formato simplificado: 13 columnas sin class='listData'
                return 'simplificado'
            elif len(cells_with_class) > 0:
                # Tiene class='listData' pero menos de 18 columnas
                # Probablemente estándar con campos opcionales
                return 'estandar'
            else:
                # Sin class='listData' y no es 13 columnas
                # Asumir simplificado
                return 'simplificado'
        
        # Fallback: si no se pudo determinar, asumir estándar
        return 'estandar'


class ColorDetector:
    """
    Detector de soporte de color de impresora
    
    Detecta si la impresora soporta impresión a color analizando los valores
    de los contadores de color.
    
    Examples:
        >>> detector = ColorDetector()
        >>> counters = {
        ...     'copiadora': {'todo_color': 100},
        ...     'impresora': {'color': 50}
        ... }
        >>> detector.detect_color_support(counters)
        True
    """
    
    def detect_color_support(self, counters_data: dict) -> bool:
        """
        Detecta si la impresora soporta color basándose en los contadores
        
        Algoritmo:
        1. Buscar campos de color en copiadora: todo_color, mono_color, dos_colores
        2. Buscar campos de color en impresora: color, mono_color, dos_colores
        3. Si algún valor > 0, la impresora soporta color
        
        Args:
            counters_data: Diccionario con datos de contadores parseados
                          (estructura de parse_user_counter_html)
            
        Returns:
            bool: True si la impresora soporta color, False en caso contrario
            
        Examples:
            >>> detector = ColorDetector()
            >>> # Impresora con color
            >>> counters_color = {
            ...     'copiadora': {'blanco_negro': 100, 'todo_color': 50},
            ...     'impresora': {'blanco_negro': 200, 'color': 30}
            ... }
            >>> detector.detect_color_support(counters_color)
            True
            
            >>> # Impresora B/N
            >>> counters_bn = {
            ...     'copiadora': {'blanco_negro': 100, 'todo_color': 0},
            ...     'impresora': {'blanco_negro': 200, 'color': 0}
            ... }
            >>> detector.detect_color_support(counters_bn)
            False
        """
        # Campos de color a verificar
        color_fields = [
            ('copiadora', 'todo_color'),
            ('copiadora', 'mono_color'),
            ('copiadora', 'dos_colores'),
            ('impresora', 'color'),
            ('impresora', 'mono_color'),
            ('impresora', 'dos_colores'),
        ]
        
        # Verificar si algún campo de color tiene valor > 0
        for section, field in color_fields:
            if section in counters_data:
                value = counters_data[section].get(field, 0)
                if value > 0:
                    return True
        
        return False


class SpecialFieldsDetector:
    """
    Detector de campos especiales de impresora
    
    Detecta campos especiales como hojas a 2 caras, páginas combinadas,
    mono color y dos colores.
    
    Examples:
        >>> detector = SpecialFieldsDetector()
        >>> counters = {
        ...     'copiadora': {'hojas_2_caras': 50, 'paginas_combinadas': 30},
        ...     'impresora': {'hojas_2_caras': 20, 'paginas_combinadas': 10}
        ... }
        >>> fields = detector.detect_special_fields(counters)
        >>> fields['has_hojas_2_caras']
        True
    """
    
    def detect_special_fields(self, counters_data: dict) -> dict:
        """
        Detecta campos especiales basándose en los contadores
        
        Campos detectados:
        - has_hojas_2_caras: Impresión dúplex
        - has_paginas_combinadas: Múltiples páginas en una hoja
        - has_mono_color: Impresión en un solo color
        - has_dos_colores: Impresión en dos colores
        
        Args:
            counters_data: Diccionario con datos de contadores parseados
            
        Returns:
            dict: Diccionario con flags booleanos para cada campo especial
            
        Examples:
            >>> detector = SpecialFieldsDetector()
            >>> counters = {
            ...     'copiadora': {'hojas_2_caras': 50, 'mono_color': 10},
            ...     'impresora': {'hojas_2_caras': 20, 'dos_colores': 5}
            ... }
            >>> fields = detector.detect_special_fields(counters)
            >>> fields
            {'has_hojas_2_caras': True, 'has_paginas_combinadas': False, 'has_mono_color': True, 'has_dos_colores': True}
        """
        result = {
            'has_hojas_2_caras': False,
            'has_paginas_combinadas': False,
            'has_mono_color': False,
            'has_dos_colores': False
        }
        
        # Verificar hojas_2_caras
        for section in ['copiadora', 'impresora']:
            if section in counters_data:
                if counters_data[section].get('hojas_2_caras', 0) > 0:
                    result['has_hojas_2_caras'] = True
                    break
        
        # Verificar paginas_combinadas
        for section in ['copiadora', 'impresora']:
            if section in counters_data:
                if counters_data[section].get('paginas_combinadas', 0) > 0:
                    result['has_paginas_combinadas'] = True
                    break
        
        # Verificar mono_color
        for section in ['copiadora', 'impresora']:
            if section in counters_data:
                if counters_data[section].get('mono_color', 0) > 0:
                    result['has_mono_color'] = True
                    break
        
        # Verificar dos_colores
        for section in ['copiadora', 'impresora']:
            if section in counters_data:
                if counters_data[section].get('dos_colores', 0) > 0:
                    result['has_dos_colores'] = True
                    break
        
        return result


class CapabilitiesDetector:
    """
    Detector completo de capacidades de impresora
    
    Integra todos los detectores individuales para proporcionar una detección
    completa de capacidades.
    
    Examples:
        >>> detector = CapabilitiesDetector()
        >>> html = open('counter_251.html').read()
        >>> counters = [{'copiadora': {'todo_color': 100}, 'impresora': {'color': 50}}]
        >>> caps = detector.detect_capabilities(html, counters)
        >>> caps.formato_contadores
        'estandar'
        >>> caps.has_color
        True
    """
    
    def __init__(self):
        self.format_detector = FormatDetector()
        self.color_detector = ColorDetector()
        self.special_fields_detector = SpecialFieldsDetector()
    
    def detect_capabilities(
        self,
        html_content: str,
        counters_data: list
    ) -> Capabilities:
        """
        Detecta todas las capacidades de la impresora
        
        Integra detección de formato, color y campos especiales para crear
        un objeto Capabilities completo.
        
        Args:
            html_content: Contenido HTML de la página de contadores
            counters_data: Lista de diccionarios con contadores por usuario
                          (resultado de parse_user_counter_html)
            
        Returns:
            Capabilities: Objeto con todas las capacidades detectadas
            
        Examples:
            >>> detector = CapabilitiesDetector()
            >>> html = '<table class="adTable">...</table>'
            >>> counters = [
            ...     {
            ...         'copiadora': {'blanco_negro': 100, 'todo_color': 50},
            ...         'impresora': {'blanco_negro': 200, 'color': 30}
            ...     }
            ... ]
            >>> caps = detector.detect_capabilities(html, counters)
            >>> caps.formato_contadores
            'estandar'
            >>> caps.has_color
            True
        """
        # Detectar formato
        formato = self.format_detector.detect_format(html_content)
        
        # Detectar color y campos especiales
        # Analizar todos los usuarios para detectar capacidades
        has_color = False
        special_fields = {
            'has_hojas_2_caras': False,
            'has_paginas_combinadas': False,
            'has_mono_color': False,
            'has_dos_colores': False
        }
        
        for user_counters in counters_data:
            # Detectar color
            if self.color_detector.detect_color_support(user_counters):
                has_color = True
            
            # Detectar campos especiales
            user_special_fields = self.special_fields_detector.detect_special_fields(user_counters)
            for field, value in user_special_fields.items():
                if value:
                    special_fields[field] = True
        
        # Crear objeto Capabilities
        return Capabilities(
            formato_contadores=formato,
            has_color=has_color,
            has_hojas_2_caras=special_fields['has_hojas_2_caras'],
            has_paginas_combinadas=special_fields['has_paginas_combinadas'],
            has_mono_color=special_fields['has_mono_color'],
            has_dos_colores=special_fields['has_dos_colores'],
            detected_at=datetime.utcnow().isoformat() + 'Z',
            manual_override=False
        )


# Convenience function for direct usage
def detect_printer_capabilities(html_content: str, counters_data: list) -> Capabilities:
    """
    Función de conveniencia para detectar capacidades de impresora
    
    Args:
        html_content: Contenido HTML de la página de contadores
        counters_data: Lista de diccionarios con contadores por usuario
        
    Returns:
        Capabilities: Objeto con todas las capacidades detectadas
        
    Examples:
        >>> from capabilities_detector import detect_printer_capabilities
        >>> html = open('counter_251.html').read()
        >>> counters = [{'copiadora': {'todo_color': 100}}]
        >>> caps = detect_printer_capabilities(html, counters)
        >>> caps.has_color
        True
    """
    detector = CapabilitiesDetector()
    return detector.detect_capabilities(html_content, counters_data)
