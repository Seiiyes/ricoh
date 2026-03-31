"""
Analizador de manejo de errores para Backend.

Este módulo contiene la clase ErrorHandlingAnalyzer que identifica problemas
en el manejo de errores en código Python (Backend).
"""

import re
from typing import List
from audit_system.models import Finding, Severity, SourceFile
from audit_system.config import get_config


class ErrorHandlingAnalyzer:
    """
    Analizador de manejo de errores para Backend.
    
    Identifica patrones problemáticos en el manejo de errores:
    - Excepciones sin logging
    - Excepciones genéricas sin tipo específico
    - Códigos HTTP inapropiados en APIs
    - Errores silenciados con pass vacío
    """
    
    def __init__(self):
        """Inicializa el analizador con configuración."""
        self.config = get_config()
    
    def analyze(self, files: List[SourceFile]) -> List[Finding]:
        """
        Analiza una lista de archivos y retorna hallazgos de manejo de errores.
        
        Args:
            files: Lista de archivos de código fuente a analizar
            
        Returns:
            Lista de hallazgos de manejo de errores detectados
        """
        findings = []
        
        for file in files:
            if file.language == "python":
                findings.extend(self._analyze_backend_file(file))
        
        return findings
    
    def _analyze_backend_file(self, file: SourceFile) -> List[Finding]:
        """
        Analiza un archivo Python para problemas de manejo de errores.
        
        Args:
            file: Archivo Python a analizar
            
        Returns:
            Lista de hallazgos de manejo de errores en el archivo
        """
        findings = []
        
        # Verificar logging en excepciones
        findings.extend(self.check_try_except_logging(file.content, file.path))
        
        # Detectar excepciones genéricas
        findings.extend(self.detect_generic_exceptions(file.content, file.path))
        
        # Verificar códigos HTTP apropiados
        findings.extend(self.check_api_error_codes(file.content, file.path))
        
        # Detectar errores silenciados
        findings.extend(self.detect_silenced_errors(file.content, file.path))
        
        return findings
    
    def check_try_except_logging(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que los bloques try-except registren las excepciones.
        
        Identifica bloques except que capturan excepciones sin registrarlas
        en logs, lo que dificulta el debugging y monitoreo.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de excepciones sin logging
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar bloques except
            if re.search(r'^\s*except\s+\w+', line):
                # Recolectar el bloque except
                indent = len(line) - len(line.lstrip())
                except_lines = []
                
                j = i
                while j < len(lines):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # Si la indentación es menor o igual y no es la línea del except, salimos
                    if next_indent <= indent and j > i - 1 and next_line.strip():
                        break
                    
                    except_lines.append(next_line)
                    j += 1
                
                except_text = '\n'.join(except_lines)
                
                # Verificar si tiene logging
                has_logging = bool(re.search(r'(logger\.|log\.|logging\.|print\()', except_text))
                
                # Verificar si es un pass vacío
                is_pass = bool(re.search(r'^\s*pass\s*$', except_text, re.MULTILINE))
                
                if not has_logging and not is_pass:
                    findings.append(Finding(
                        id=f"error_no_logging_{file_path}_{i}",
                        category="error_handling",
                        subcategory="no_logging",
                        severity=Severity.MEDIO,
                        title="Excepción capturada sin logging",
                        description=f"El bloque except en la línea {i} captura una excepción pero no la registra. "
                                  f"Esto dificulta el debugging y monitoreo de errores en producción.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar logging de la excepción: logger.error(f'Error: {e}', exc_info=True) "
                                     "o logger.exception('Error message')"
                    ))
        
        return findings
    
    def detect_generic_exceptions(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta uso de excepciones genéricas sin tipo específico.
        
        Identifica except: o except Exception: que capturan todas las excepciones,
        lo que puede ocultar errores inesperados.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de excepciones genéricas
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Detectar except sin tipo
            if re.search(r'^\s*except\s*:', line):
                findings.append(Finding(
                    id=f"error_generic_except_{file_path}_{i}",
                    category="error_handling",
                    subcategory="generic_exception",
                    severity=Severity.MEDIO,
                    title="Excepción genérica sin tipo específico",
                    description=f"El except en la línea {i} captura todas las excepciones sin especificar "
                              f"el tipo. Esto puede ocultar errores inesperados como KeyboardInterrupt "
                              f"o SystemExit, y dificulta el debugging.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Especificar el tipo de excepción esperada: except ValueError: "
                                 "o except (TypeError, KeyError): para múltiples tipos."
                ))
            
            # Detectar except Exception genérico
            elif re.search(r'^\s*except\s+Exception(\s+as\s+\w+)?\s*:', line):
                findings.append(Finding(
                    id=f"error_exception_base_{file_path}_{i}",
                    category="error_handling",
                    subcategory="generic_exception",
                    severity=Severity.BAJO,
                    title="Uso de Exception base en lugar de tipo específico",
                    description=f"El except Exception en la línea {i} captura todas las excepciones. "
                              f"Es mejor capturar tipos específicos de excepciones esperadas.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Usar tipos específicos como ValueError, TypeError, HTTPException, etc. "
                                 "Solo usar Exception si realmente necesitas capturar cualquier error."
                ))
        
        return findings
    
    def check_api_error_codes(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que los endpoints de API retornen códigos HTTP apropiados.
        
        Identifica endpoints que retornan 200 OK para errores o no especifican
        códigos de estado apropiados.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de códigos HTTP inapropiados
        """
        findings = []
        
        # Solo analizar archivos de API
        if 'api' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar raise HTTPException
            if re.search(r'raise\s+HTTPException', line):
                # Verificar si especifica status_code
                has_status_code = bool(re.search(r'status_code\s*=', line))
                
                if not has_status_code:
                    findings.append(Finding(
                        id=f"error_no_status_code_{file_path}_{i}",
                        category="error_handling",
                        subcategory="api_error_code",
                        severity=Severity.MEDIO,
                        title="HTTPException sin código de estado",
                        description=f"El HTTPException en la línea {i} no especifica un status_code. "
                                  f"Esto puede resultar en códigos de error genéricos poco informativos.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Especificar status_code apropiado: 400 (Bad Request), "
                                     "404 (Not Found), 403 (Forbidden), 500 (Internal Server Error), etc."
                    ))
            
            # Buscar return con status_code 200 en bloques except
            if re.search(r'status_code\s*=\s*200', line):
                # Verificar si está dentro de un bloque except
                in_except_block = False
                for j in range(max(0, i - 10), i):
                    if re.search(r'^\s*except', lines[j]):
                        in_except_block = True
                        break
                
                if in_except_block:
                    findings.append(Finding(
                        id=f"error_200_in_except_{file_path}_{i}",
                        category="error_handling",
                        subcategory="api_error_code",
                        severity=Severity.ALTO,
                        title="Código 200 OK retornado en bloque de error",
                        description=f"La línea {i} retorna status_code 200 dentro de un bloque except. "
                                  f"Los errores no deberían retornar 200 OK.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Usar códigos de error apropiados: 400 para errores de cliente, "
                                     "500 para errores de servidor."
                    ))
        
        return findings
    
    def detect_silenced_errors(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta errores silenciados con pass vacío.
        
        Identifica bloques except que solo contienen pass, lo que oculta
        completamente los errores.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de errores silenciados
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar bloques except
            if re.search(r'^\s*except', line):
                # Verificar si la siguiente línea no vacía es solo 'pass'
                indent = len(line) - len(line.lstrip())
                found_pass = False
                
                for j in range(i, min(i + 10, len(lines))):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # Ignorar líneas vacías y comentarios
                    if not next_line.strip() or next_line.strip().startswith('#'):
                        continue
                    
                    # Si la indentación es menor o igual al except, salimos
                    if next_indent <= indent and j > i:
                        break
                    
                    # Si encontramos pass
                    if next_line.strip() == 'pass':
                        found_pass = True
                        break
                    
                    # Si hay otra instrucción (no pass), no es pass vacío
                    if next_indent > indent and next_line.strip() != 'pass':
                        break
                
                if found_pass:
                    findings.append(Finding(
                        id=f"error_silenced_{file_path}_{i}",
                        category="error_handling",
                        subcategory="silenced_error",
                        severity=Severity.ALTO,
                        title="Error silenciado con pass vacío",
                        description=f"El bloque except en la línea {i} silencia completamente la excepción "
                                  f"con pass. Esto oculta errores y dificulta enormemente el debugging.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Registrar la excepción con logger.exception() o manejarla apropiadamente. "
                                     "Si es intencional, agregar comentario explicando por qué se ignora."
                    ))
        
        return findings
