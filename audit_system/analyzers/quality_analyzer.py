"""
Analizador de calidad de código para Backend y Frontend.

Este módulo contiene la clase QualityAnalyzer que identifica problemas
de calidad en código Python (Backend) y TypeScript/React (Frontend).
"""

import ast
import re
from typing import List, Set, Tuple
from difflib import SequenceMatcher
from audit_system.models import Finding, Severity, SourceFile
from audit_system.config import get_config


class QualityAnalyzer:
    """
    Analizador de calidad de código para Backend y Frontend.
    
    Identifica patrones que afectan la calidad y mantenibilidad:
    - Backend: funciones largas, indentación profunda, código duplicado, type hints
    - Frontend: componentes grandes, props drilling, uso de 'any', console.log
    """
    
    def __init__(self):
        """Inicializa el analizador con configuración."""
        self.config = get_config()
    
    def analyze(self, files: List[SourceFile]) -> List[Finding]:
        """
        Analiza una lista de archivos y retorna hallazgos de calidad.
        
        Args:
            files: Lista de archivos de código fuente a analizar
            
        Returns:
            Lista de hallazgos de calidad detectados
        """
        findings = []
        
        for file in files:
            if file.language == "python":
                findings.extend(self._analyze_backend_file(file))
            elif file.language == "typescript":
                findings.extend(self._analyze_frontend_file(file))
        
        return findings
    
    def _analyze_backend_file(self, file: SourceFile) -> List[Finding]:
        """
        Analiza un archivo Python para problemas de calidad.
        
        Args:
            file: Archivo Python a analizar
            
        Returns:
            Lista de hallazgos de calidad en el archivo
        """
        findings = []
        
        # Detectar funciones largas
        findings.extend(self.detect_long_functions(file.content, file.path))
        
        # Detectar indentación profunda
        findings.extend(self.detect_deep_nesting(file.content, file.path))
        
        # Verificar type hints
        findings.extend(self.check_type_hints(file.content, file.path))
        
        # Verificar manejo de excepciones
        findings.extend(self.check_exception_handling(file.content, file.path))
        
        # Verificar docstrings
        findings.extend(self.check_docstrings(file.content, file.path))
        
        return findings
    
    def _analyze_frontend_file(self, file: SourceFile) -> List[Finding]:
        """
        Analiza un archivo TypeScript/React para problemas de calidad.
        
        Args:
            file: Archivo TypeScript a analizar
            
        Returns:
            Lista de hallazgos de calidad en el archivo
        """
        findings = []
        
        # Detectar componentes grandes
        findings.extend(self.detect_large_components(file.content, file.path))
        
        # Detectar props drilling
        findings.extend(self.detect_props_drilling(file.content, file.path))
        
        # Detectar uso de 'any'
        findings.extend(self.detect_type_any(file.content, file.path))
        
        # Detectar console.log
        findings.extend(self.detect_console_logs(file.content, file.path))
        
        # Detectar lógica de negocio en UI
        findings.extend(self.detect_business_logic_in_ui(file.content, file.path))
        
        return findings
    
    # ========== Métodos de análisis de Backend ==========
    
    def detect_long_functions(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta funciones que exceden el límite de líneas configurado.
        
        Funciones muy largas son difíciles de entender, probar y mantener.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de funciones largas
        """
        findings = []
        threshold = self.config.LONG_FUNCTION_THRESHOLD
        
        try:
            tree = ast.parse(file_content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Calcular líneas de la función
                    func_start = node.lineno
                    func_end = node.end_lineno if hasattr(node, 'end_lineno') else func_start
                    func_lines = func_end - func_start + 1
                    
                    if func_lines > threshold:
                        severity = Severity.CRITICO if func_lines > 100 else Severity.MEDIO
                        
                        findings.append(Finding(
                            id=f"quality_long_function_{file_path}_{func_start}",
                            category="quality",
                            subcategory="long_function",
                            severity=severity,
                            title=f"Función {node.name} demasiado larga ({func_lines} líneas)",
                            description=f"La función {node.name} en la línea {func_start} tiene {func_lines} líneas, "
                                      f"excediendo el límite de {threshold} líneas. Funciones largas son difíciles "
                                      f"de entender, probar y mantener.",
                            file_path=file_path,
                            line_number=func_start,
                            code_snippet=f"def {node.name}(...)",
                            recommendation="Dividir la función en funciones más pequeñas con responsabilidades claras. "
                                         "Extraer lógica a funciones auxiliares."
                        ))
        except SyntaxError:
            # Si hay error de sintaxis, no podemos analizar
            pass
        
        return findings
    
    def detect_deep_nesting(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta código con indentación profunda (>3 niveles).
        
        Indentación profunda indica complejidad ciclomática alta y dificulta la lectura.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de indentación profunda
        """
        findings = []
        threshold = self.config.DEEP_NESTING_THRESHOLD
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            if line.strip():  # Ignorar líneas vacías
                # Contar espacios de indentación
                indent = len(line) - len(line.lstrip())
                # Asumir 4 espacios por nivel
                indent_level = indent // 4
                
                if indent_level > threshold:
                    findings.append(Finding(
                        id=f"quality_deep_nesting_{file_path}_{i}",
                        category="quality",
                        subcategory="deep_nesting",
                        severity=Severity.MEDIO,
                        title=f"Indentación profunda detectada ({indent_level} niveles)",
                        description=f"La línea {i} tiene {indent_level} niveles de indentación, "
                                  f"excediendo el límite de {threshold}. Esto indica alta complejidad "
                                  f"ciclomática y dificulta la lectura del código.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        recommendation="Refactorizar para reducir anidamiento: extraer funciones auxiliares, "
                                     "usar early returns, o simplificar la lógica condicional."
                    ))
        
        return findings
    
    def detect_code_duplication(self, file_content: str, file_path: str, all_files: List[SourceFile] = None) -> List[Finding]:
        """
        Detecta código duplicado con similitud >80%.
        
        Código duplicado aumenta el esfuerzo de mantenimiento y la probabilidad de bugs.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            all_files: Lista de todos los archivos para comparación (opcional)
            
        Returns:
            Lista de hallazgos de código duplicado
        """
        findings = []
        threshold = self.config.CODE_DUPLICATION_THRESHOLD
        
        # Por ahora, implementación simplificada que detecta funciones duplicadas dentro del mismo archivo
        # Una implementación completa compararía con otros archivos
        
        try:
            tree = ast.parse(file_content)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            # Comparar cada par de funciones
            for i, func1 in enumerate(functions):
                for func2 in functions[i+1:]:
                    # Obtener código de las funciones
                    lines = file_content.split('\n')
                    func1_code = '\n'.join(lines[func1.lineno-1:func1.end_lineno])
                    func2_code = '\n'.join(lines[func2.lineno-1:func2.end_lineno])
                    
                    # Calcular similitud
                    similarity = SequenceMatcher(None, func1_code, func2_code).ratio()
                    
                    if similarity > threshold:
                        findings.append(Finding(
                            id=f"quality_code_duplication_{file_path}_{func1.lineno}_{func2.lineno}",
                            category="quality",
                            subcategory="code_duplication",
                            severity=Severity.MEDIO,
                            title=f"Código duplicado entre {func1.name} y {func2.name}",
                            description=f"Las funciones {func1.name} (línea {func1.lineno}) y {func2.name} "
                                      f"(línea {func2.lineno}) tienen {similarity*100:.1f}% de similitud. "
                                      f"Código duplicado aumenta el esfuerzo de mantenimiento.",
                            file_path=file_path,
                            line_number=func1.lineno,
                            code_snippet=f"def {func1.name}(...) vs def {func2.name}(...)",
                            recommendation="Extraer la lógica común a una función auxiliar reutilizable."
                        ))
        except SyntaxError:
            pass
        
        return findings
    
    def check_type_hints(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que las funciones públicas tengan type hints.
        
        Type hints mejoran la documentación, detección de errores y autocompletado.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de type hints faltantes
        """
        findings = []
        
        try:
            tree = ast.parse(file_content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Ignorar funciones privadas (empiezan con _)
                    if node.name.startswith('_'):
                        continue
                    
                    # Verificar si tiene type hints en parámetros
                    has_param_hints = all(arg.annotation is not None for arg in node.args.args if arg.arg != 'self')
                    
                    # Verificar si tiene type hint de retorno
                    has_return_hint = node.returns is not None
                    
                    if not has_param_hints or not has_return_hint:
                        findings.append(Finding(
                            id=f"quality_no_type_hints_{file_path}_{node.lineno}",
                            category="quality",
                            subcategory="no_type_hints",
                            severity=Severity.MEDIO,
                            title=f"Función {node.name} sin type hints completos",
                            description=f"La función pública {node.name} en la línea {node.lineno} no tiene "
                                      f"type hints completos. Type hints mejoran la documentación y "
                                      f"permiten detección temprana de errores.",
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet=f"def {node.name}(...)",
                            recommendation="Agregar type hints a todos los parámetros y al valor de retorno."
                        ))
        except SyntaxError:
            pass
        
        return findings
    
    def check_exception_handling(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica el manejo apropiado de excepciones.
        
        Detecta excepciones genéricas sin logging o excepciones silenciadas.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de manejo de excepciones inadecuado
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Detectar except genérico sin tipo
            if re.search(r'^\s*except\s*:', line):
                findings.append(Finding(
                    id=f"quality_generic_exception_{file_path}_{i}",
                    category="quality",
                    subcategory="exception_handling",
                    severity=Severity.MEDIO,
                    title="Excepción genérica sin tipo específico",
                    description=f"El except en la línea {i} captura todas las excepciones sin especificar "
                                f"el tipo. Esto puede ocultar errores inesperados y dificultar el debugging.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Especificar el tipo de excepción: except ValueError: o except (TypeError, KeyError):"
                ))
            
            # Detectar except Exception genérico
            elif re.search(r'^\s*except\s+Exception\s*:', line):
                # Verificar si hay logging en el bloque except
                has_logging = False
                indent = len(line) - len(line.lstrip())
                
                for j in range(i, min(i + 10, len(lines))):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    if next_indent <= indent and j > i:
                        break
                    
                    if re.search(r'log\.|logger\.|print\(', next_line):
                        has_logging = True
                        break
                
                if not has_logging:
                    findings.append(Finding(
                        id=f"quality_exception_no_logging_{file_path}_{i}",
                        category="quality",
                        subcategory="exception_handling",
                        severity=Severity.MEDIO,
                        title="Excepción capturada sin logging",
                        description=f"El except Exception en la línea {i} no registra la excepción. "
                                  f"Esto dificulta el debugging y monitoreo de errores.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar logging de la excepción: logger.error(f'Error: {e}', exc_info=True)"
                    ))
            
            # Detectar excepciones silenciadas (pass vacío)
            elif re.search(r'^\s*except.*:\s*$', line):
                # Verificar si la siguiente línea es solo 'pass'
                if i < len(lines):
                    next_line = lines[i].strip()
                    if next_line == 'pass':
                        findings.append(Finding(
                            id=f"quality_silenced_exception_{file_path}_{i}",
                            category="quality",
                            subcategory="exception_handling",
                            severity=Severity.ALTO,
                            title="Excepción silenciada con pass",
                            description=f"El except en la línea {i} silencia la excepción con pass. "
                                      f"Esto oculta errores y dificulta el debugging.",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            recommendation="Registrar la excepción o manejarla apropiadamente. "
                                         "Si es intencional, agregar comentario explicando por qué."
                        ))
        
        return findings
    
    def check_docstrings(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que las funciones públicas tengan docstrings.
        
        Docstrings mejoran la documentación y facilitan el mantenimiento.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de docstrings faltantes
        """
        findings = []
        
        try:
            tree = ast.parse(file_content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Ignorar funciones privadas
                    if node.name.startswith('_'):
                        continue
                    
                    # Verificar si tiene docstring
                    has_docstring = (
                        ast.get_docstring(node) is not None
                    )
                    
                    if not has_docstring:
                        findings.append(Finding(
                            id=f"quality_no_docstring_{file_path}_{node.lineno}",
                            category="quality",
                            subcategory="no_docstring",
                            severity=Severity.BAJO,
                            title=f"Función {node.name} sin docstring",
                            description=f"La función pública {node.name} en la línea {node.lineno} no tiene "
                                      f"docstring. La documentación facilita el mantenimiento y uso de la función.",
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet=f"def {node.name}(...)",
                            recommendation='Agregar docstring con formato: """Descripción breve.\\n\\nArgs:\\n    param: descripción\\n\\nReturns:\\n    descripción"""'
                        ))
        except SyntaxError:
            pass
        
        return findings
    
    # ========== Métodos de análisis de Frontend ==========
    
    def detect_large_components(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta componentes React que exceden el límite de líneas.
        
        Componentes grandes son difíciles de entender y mantener.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de componentes grandes
        """
        findings = []
        threshold = self.config.LARGE_COMPONENT_THRESHOLD
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar definiciones de componentes
            component_match = re.search(r'(?:function|const)\s+([A-Z]\w+)\s*(?:=\s*)?(?:\([^)]*\))?\s*(?:=>)?\s*\{', line)
            
            if component_match:
                component_name = component_match.group(1)
                
                # Contar líneas del componente (hasta el cierre de la función)
                brace_count = line.count('{') - line.count('}')
                component_lines = 1
                
                j = i
                while j < len(lines) and brace_count > 0:
                    j += 1
                    if j < len(lines):
                        next_line = lines[j]
                        brace_count += next_line.count('{') - next_line.count('}')
                        component_lines += 1
                
                if component_lines > threshold:
                    findings.append(Finding(
                        id=f"quality_large_component_{file_path}_{i}",
                        category="quality",
                        subcategory="large_component",
                        severity=Severity.MEDIO,
                        title=f"Componente {component_name} demasiado grande ({component_lines} líneas)",
                        description=f"El componente {component_name} en la línea {i} tiene {component_lines} líneas, "
                                  f"excediendo el límite de {threshold} líneas. Componentes grandes son "
                                  f"difíciles de entender y mantener.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=f"function {component_name}(...)",
                        recommendation="Dividir el componente en componentes más pequeños. Extraer lógica "
                                     "a custom hooks. Separar secciones en sub-componentes."
                    ))
        
        return findings
    
    def detect_props_drilling(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta props drilling de más de 2 niveles.
        
        Props drilling excesivo indica que se debería usar Context o estado global.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de props drilling
        """
        findings = []
        
        # Buscar props que se pasan a través de múltiples componentes
        # Patrón: prop={prop} repetido en componentes anidados
        lines = file_content.split('\n')
        
        # Heurística: buscar el mismo nombre de prop usado múltiples veces
        prop_usage = {}
        
        for i, line in enumerate(lines, start=1):
            # Buscar props pasados a componentes: <Component prop={value} />
            prop_matches = re.findall(r'(\w+)=\{(\w+)\}', line)
            
            for prop_name, prop_value in prop_matches:
                if prop_value not in prop_usage:
                    prop_usage[prop_value] = []
                prop_usage[prop_value].append(i)
        
        # Si un prop se usa más de 2 veces, puede ser drilling
        for prop_name, line_numbers in prop_usage.items():
            if len(line_numbers) > 2:
                findings.append(Finding(
                    id=f"quality_props_drilling_{file_path}_{line_numbers[0]}",
                    category="quality",
                    subcategory="props_drilling",
                    severity=Severity.MEDIO,
                    title=f"Props drilling detectado: {prop_name}",
                    description=f"La prop {prop_name} se pasa a través de {len(line_numbers)} niveles "
                              f"de componentes (líneas {', '.join(map(str, line_numbers[:3]))}). "
                              f"Props drilling excesivo dificulta el mantenimiento.",
                    file_path=file_path,
                    line_number=line_numbers[0],
                    code_snippet=f"{prop_name}={{...}}",
                    recommendation="Considerar usar React Context, Zustand, o composición de componentes "
                                 "para evitar pasar props a través de múltiples niveles."
                ))
        
        return findings
    
    def detect_type_any(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta uso de 'any' en TypeScript.
        
        El tipo 'any' elimina los beneficios de type safety de TypeScript.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de uso de 'any'
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar declaraciones con tipo 'any'
            # Patrón: : any o <any> o any[]
            if re.search(r':\s*any\b|<any>|any\[\]', line):
                # Ignorar comentarios
                if line.strip().startswith('//'):
                    continue
                
                findings.append(Finding(
                    id=f"quality_type_any_{file_path}_{i}",
                    category="quality",
                    subcategory="type_any",
                    severity=Severity.MEDIO,
                    title="Uso de tipo 'any' en TypeScript",
                    description=f"La línea {i} usa el tipo 'any', lo que elimina los beneficios "
                              f"de type safety de TypeScript. Esto puede ocultar errores de tipos.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Definir un tipo específico o usar 'unknown' si el tipo es realmente desconocido."
                ))
        
        return findings
    
    def detect_console_logs(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta console.log/error en código de producción.
        
        Console logs deberían removerse antes de producción.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de console.log
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar console.log, console.error, console.warn
            if re.search(r'\bconsole\.(log|error|warn|info|debug)\s*\(', line):
                # Ignorar comentarios
                if line.strip().startswith('//'):
                    continue
                
                findings.append(Finding(
                    id=f"quality_console_log_{file_path}_{i}",
                    category="quality",
                    subcategory="console_log",
                    severity=Severity.BAJO,
                    title="Console.log en código de producción",
                    description=f"La línea {i} contiene console.log/error. Los console logs "
                              f"deberían removerse antes de producción o reemplazarse con "
                              f"un sistema de logging apropiado.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Remover console.log o usar un logger apropiado (winston, pino). "
                                 "Considerar usar un linter para detectar esto automáticamente."
                ))
        
        return findings
    
    def detect_business_logic_in_ui(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta lógica de negocio dentro de componentes UI.
        
        La lógica de negocio debería estar en hooks o servicios, no en componentes.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de lógica de negocio en UI
        """
        findings = []
        
        # Solo analizar archivos de componentes
        if 'component' not in file_path.lower() and 'page' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        # Buscar patrones de lógica de negocio
        business_logic_patterns = [
            (r'\.map\(.*=>\s*\{[^}]{50,}', "Transformación compleja de datos"),
            (r'\.filter\(.*=>\s*\{[^}]{30,}', "Filtrado complejo de datos"),
            (r'\.reduce\(', "Reducción de datos"),
            (r'if\s*\([^)]{50,}\)', "Condicional complejo"),
            (r'switch\s*\([^)]+\)\s*\{', "Switch statement")
        ]
        
        for i, line in enumerate(lines, start=1):
            # Verificar si estamos dentro de un componente (heurística simple)
            if re.search(r'return\s*\(?\s*<', line):
                # Buscar patrones de lógica de negocio cerca del return
                for j in range(max(0, i - 20), i):
                    check_line = lines[j]
                    
                    for pattern, description in business_logic_patterns:
                        if re.search(pattern, check_line):
                            findings.append(Finding(
                                id=f"quality_business_logic_in_ui_{file_path}_{j+1}",
                                category="quality",
                                subcategory="business_logic_in_ui",
                                severity=Severity.MEDIO,
                                title=f"{description} en componente UI",
                                description=f"La línea {j+1} contiene lógica de negocio ({description.lower()}) "
                                          f"dentro de un componente UI. Esto dificulta el testing y reutilización.",
                                file_path=file_path,
                                line_number=j+1,
                                code_snippet=check_line.strip()[:80],
                                recommendation="Extraer la lógica a un custom hook o servicio. "
                                             "Los componentes deberían enfocarse en renderizado."
                            ))
                            break
        
        return findings
