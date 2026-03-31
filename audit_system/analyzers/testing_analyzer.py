"""
Analizador de cobertura de testing para Backend y Frontend.

Este módulo contiene la clase TestingAnalyzer que identifica código
sin tests apropiados en Python (Backend) y TypeScript/React (Frontend).
"""

import re
import ast
from typing import List
from audit_system.models import Finding, Severity, SourceFile
from audit_system.config import get_config


class TestingAnalyzer:
    """
    Analizador de cobertura de testing para Backend y Frontend.
    
    Identifica código sin tests:
    - Archivos Python sin tests correspondientes
    - Componentes React sin tests
    - Endpoints críticos sin tests de integración
    - Funciones complejas sin tests
    """
    
    def __init__(self):
        """Inicializa el analizador con configuración."""
        self.config = get_config()
    
    def analyze(self, files: List[SourceFile]) -> List[Finding]:
        """
        Analiza una lista de archivos y retorna hallazgos de testing.
        
        Args:
            files: Lista de archivos de código fuente a analizar
            
        Returns:
            Lista de hallazgos de testing detectados
        """
        findings = []
        
        # Separar archivos por lenguaje
        python_files = [f for f in files if f.language == "python"]
        typescript_files = [f for f in files if f.language == "typescript"]
        
        # Analizar archivos Python
        findings.extend(self.identify_files_without_tests(python_files))
        findings.extend(self.identify_complex_functions_without_tests(python_files))
        findings.extend(self.check_integration_tests(python_files))
        
        # Analizar archivos TypeScript
        findings.extend(self.identify_components_without_tests(typescript_files))
        
        return findings
    
    def identify_files_without_tests(self, files: List[SourceFile]) -> List[Finding]:
        """
        Identifica archivos Python sin archivos de test correspondientes.
        
        Verifica que cada módulo Python tenga un archivo test_*.py correspondiente.
        
        Args:
            files: Lista de archivos Python a analizar
            
        Returns:
            Lista de hallazgos de archivos sin tests
        """
        findings = []
        
        # Filtrar archivos de test
        test_files = {f.path for f in files if 'test_' in f.path or '_test.py' in f.path}
        
        # Verificar cada archivo no-test
        for file in files:
            # Ignorar archivos de test, __init__.py, y archivos de configuración
            if 'test_' in file.path or file.path.endswith('__init__.py'):
                continue
            
            if 'config' in file.path.lower() or 'settings' in file.path.lower():
                continue
            
            # Construir nombre esperado del archivo de test
            # Ejemplo: api/users.py -> api/test_users.py o tests/test_users.py
            path_parts = file.path.split('/')
            filename = path_parts[-1]
            test_filename = f"test_{filename}"
            
            # Buscar archivo de test en varias ubicaciones posibles
            possible_test_paths = [
                '/'.join(path_parts[:-1] + [test_filename]),  # Mismo directorio
                f"tests/{test_filename}",  # Directorio tests/
                f"test/{test_filename}",  # Directorio test/
            ]
            
            has_test = any(test_path in test_files for test_path in possible_test_paths)
            
            if not has_test:
                findings.append(Finding(
                    id=f"testing_no_test_file_{file.path}",
                    category="testing",
                    subcategory="no_test_file",
                    severity=Severity.MEDIO,
                    title=f"Archivo {filename} sin tests",
                    description=f"El archivo {file.path} no tiene un archivo de test correspondiente. "
                              f"Todo código de producción debería tener tests.",
                    file_path=file.path,
                    line_number=1,
                    code_snippet=filename,
                    recommendation=f"Crear archivo de test: {test_filename} con tests unitarios "
                                 f"para las funciones y clases en este módulo."
                ))
        
        return findings
    
    def identify_components_without_tests(self, files: List[SourceFile]) -> List[Finding]:
        """
        Identifica componentes React sin archivos de test correspondientes.
        
        Verifica que cada componente React tenga un archivo .test.tsx o .spec.tsx.
        
        Args:
            files: Lista de archivos TypeScript a analizar
            
        Returns:
            Lista de hallazgos de componentes sin tests
        """
        findings = []
        
        # Filtrar archivos de test
        test_files = {f.path for f in files if '.test.' in f.path or '.spec.' in f.path}
        
        # Verificar cada componente
        for file in files:
            # Ignorar archivos de test y archivos que no son componentes
            if '.test.' in file.path or '.spec.' in file.path:
                continue
            
            # Solo verificar archivos en directorios de componentes
            if 'component' not in file.path.lower() and 'page' not in file.path.lower():
                continue
            
            # Verificar si es un componente React (heurística simple)
            is_component = bool(re.search(r'(export\s+(default\s+)?function\s+[A-Z]|const\s+[A-Z]\w+.*=.*React)', file.content))
            
            if not is_component:
                continue
            
            # Construir nombres esperados de archivos de test
            base_path = file.path.replace('.tsx', '').replace('.ts', '')
            possible_test_paths = [
                f"{base_path}.test.tsx",
                f"{base_path}.test.ts",
                f"{base_path}.spec.tsx",
                f"{base_path}.spec.ts",
            ]
            
            has_test = any(test_path in test_files for test_path in possible_test_paths)
            
            if not has_test:
                filename = file.path.split('/')[-1]
                findings.append(Finding(
                    id=f"testing_no_component_test_{file.path}",
                    category="testing",
                    subcategory="no_component_test",
                    severity=Severity.MEDIO,
                    title=f"Componente {filename} sin tests",
                    description=f"El componente React en {file.path} no tiene tests. "
                              f"Los componentes deberían tener tests para verificar su renderizado y comportamiento.",
                    file_path=file.path,
                    line_number=1,
                    code_snippet=filename,
                    recommendation=f"Crear archivo de test: {base_path}.test.tsx con tests usando "
                                 f"React Testing Library o similar."
                ))
        
        return findings
    
    def check_integration_tests(self, files: List[SourceFile]) -> List[Finding]:
        """
        Verifica que los endpoints críticos tengan tests de integración.
        
        Identifica endpoints de API sin tests de integración correspondientes.
        
        Args:
            files: Lista de archivos Python a analizar
            
        Returns:
            Lista de hallazgos de endpoints sin tests de integración
        """
        findings = []
        
        # Buscar archivos de API
        api_files = [f for f in files if 'api' in f.path.lower() and 'test_' not in f.path]
        
        # Buscar archivos de test de integración
        integration_test_files = [f for f in files if 'test_' in f.path and 'integration' in f.path.lower()]
        
        for api_file in api_files:
            # Buscar endpoints en el archivo
            endpoints = []
            lines = api_file.content.split('\n')
            
            for i, line in enumerate(lines, start=1):
                # Buscar decoradores de rutas
                if re.search(r'@\w+\.(get|post|put|delete|patch)\(', line):
                    # Extraer el método HTTP
                    method_match = re.search(r'@\w+\.(get|post|put|delete|patch)', line)
                    if method_match:
                        method = method_match.group(1).upper()
                        endpoints.append((i, method))
            
            # Si hay endpoints, verificar si hay tests de integración
            if endpoints and not integration_test_files:
                findings.append(Finding(
                    id=f"testing_no_integration_tests_{api_file.path}",
                    category="testing",
                    subcategory="no_integration_test",
                    severity=Severity.ALTO,
                    title=f"Endpoints en {api_file.path.split('/')[-1]} sin tests de integración",
                    description=f"El archivo {api_file.path} contiene {len(endpoints)} endpoint(s) "
                              f"pero no se encontraron tests de integración. Los endpoints críticos "
                              f"deberían tener tests end-to-end.",
                    file_path=api_file.path,
                    line_number=endpoints[0][0],
                    code_snippet=f"{len(endpoints)} endpoints encontrados",
                    recommendation="Crear tests de integración que verifiquen los endpoints completos "
                                 "incluyendo autenticación, validación, y respuestas."
                ))
        
        return findings
    
    def identify_complex_functions_without_tests(self, files: List[SourceFile]) -> List[Finding]:
        """
        Identifica funciones complejas (>50 líneas o alta complejidad) sin tests.
        
        Funciones complejas son más propensas a bugs y requieren tests exhaustivos.
        
        Args:
            files: Lista de archivos Python a analizar
            
        Returns:
            Lista de hallazgos de funciones complejas sin tests
        """
        findings = []
        
        # Filtrar archivos que no son de test
        source_files = [f for f in files if 'test_' not in f.path]
        
        for file in source_files:
            try:
                tree = ast.parse(file.content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Ignorar funciones privadas y métodos especiales
                        if node.name.startswith('_'):
                            continue
                        
                        # Calcular líneas de la función
                        func_start = node.lineno
                        func_end = node.end_lineno if hasattr(node, 'end_lineno') else func_start
                        func_lines = func_end - func_start + 1
                        
                        # Verificar si es compleja (>50 líneas)
                        if func_lines > self.config.LONG_FUNCTION_THRESHOLD:
                            # Buscar tests para esta función
                            # Heurística: buscar test_<function_name> en archivos de test
                            test_name = f"test_{node.name}"
                            
                            has_test = False
                            for test_file in files:
                                if 'test_' in test_file.path and test_name in test_file.content:
                                    has_test = True
                                    break
                            
                            if not has_test:
                                findings.append(Finding(
                                    id=f"testing_complex_function_no_test_{file.path}_{func_start}",
                                    category="testing",
                                    subcategory="complex_function_no_test",
                                    severity=Severity.ALTO,
                                    title=f"Función compleja {node.name} sin tests",
                                    description=f"La función {node.name} en la línea {func_start} tiene "
                                              f"{func_lines} líneas pero no parece tener tests. "
                                              f"Funciones complejas son más propensas a bugs y requieren "
                                              f"tests exhaustivos.",
                                    file_path=file.path,
                                    line_number=func_start,
                                    code_snippet=f"def {node.name}(...)",
                                    recommendation=f"Crear tests unitarios para {node.name} que cubran "
                                                 f"casos normales, edge cases, y manejo de errores."
                                ))
            except SyntaxError:
                # Si hay error de sintaxis, no podemos analizar
                pass
        
        return findings
