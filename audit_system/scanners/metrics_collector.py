"""
MetricsCollector: Componente para recolectar métricas del código.

Responsable de:
- Contar líneas de código por lenguaje
- Contar archivos por tipo
- Identificar archivos grandes (>300 líneas)
- Identificar funciones largas (>50 líneas en Python)
- Identificar componentes grandes (>200 líneas en TypeScript)
"""

import ast
from typing import List

from audit_system.config import get_config
from audit_system.models import ProjectStructure, CodeMetrics, PythonFile, TypeScriptFile
from audit_system.logger import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Recolector de métricas del código."""
    
    def __init__(self):
        """Inicializa el MetricsCollector con configuración."""
        self.config = get_config()
    
    def collect_metrics(self, structure: ProjectStructure) -> CodeMetrics:
        """
        Recolecta todas las métricas del proyecto.
        
        Args:
            structure: ProjectStructure con archivos identificados
            
        Returns:
            CodeMetrics con todas las métricas calculadas
            
        Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8
        """
        logger.info("Iniciando recolección de métricas")
        
        # Métricas de Backend
        backend_total_lines = self.count_total_lines(structure.backend_files)
        backend_total_files = len(structure.backend_files)
        backend_large_files = self.count_large_files(structure.backend_files)
        backend_long_functions = self.count_long_functions(structure.backend_files)
        backend_dependencies_count = len(structure.backend_dependencies)
        
        # Métricas de Frontend
        frontend_total_lines = self.count_total_lines(structure.frontend_files)
        frontend_total_files = len(structure.frontend_files)
        frontend_large_components = self.count_large_components(structure.frontend_files)
        frontend_dependencies_count = len(structure.frontend_dependencies)
        
        # Métricas de dependencias
        total_outdated_dependencies = self.count_outdated_dependencies(
            structure.backend_dependencies + structure.frontend_dependencies
        )
        total_vulnerabilities = self.count_vulnerabilities(
            structure.backend_dependencies + structure.frontend_dependencies
        )
        
        metrics = CodeMetrics(
            backend_total_lines=backend_total_lines,
            backend_total_files=backend_total_files,
            backend_large_files=backend_large_files,
            backend_long_functions=backend_long_functions,
            backend_dependencies_count=backend_dependencies_count,
            frontend_total_lines=frontend_total_lines,
            frontend_total_files=frontend_total_files,
            frontend_large_components=frontend_large_components,
            frontend_dependencies_count=frontend_dependencies_count,
            total_outdated_dependencies=total_outdated_dependencies,
            total_vulnerabilities=total_vulnerabilities
        )
        
        logger.info(f"Métricas recolectadas: Backend {backend_total_files} archivos, "
                   f"Frontend {frontend_total_files} archivos")
        
        return metrics
    
    def count_total_lines(self, files: List) -> int:
        """
        Cuenta el total de líneas de código en una lista de archivos.
        
        Args:
            files: Lista de SourceFile (PythonFile o TypeScriptFile)
            
        Returns:
            Total de líneas de código
            
        Validates: Requirements 12.1, 12.2
        """
        return sum(file.lines_of_code for file in files)
    
    def count_large_files(self, files: List) -> int:
        """
        Cuenta archivos que exceden el umbral de tamaño (>300 líneas).
        
        Args:
            files: Lista de SourceFile
            
        Returns:
            Número de archivos grandes
            
        Validates: Requirements 12.4
        """
        return sum(1 for file in files if file.is_large)
    
    def count_long_functions(self, python_files: List[PythonFile]) -> int:
        """
        Cuenta funciones que exceden el umbral de líneas (>50 líneas).
        
        Parsea el AST de archivos Python para identificar funciones y
        contar sus líneas de código.
        
        Args:
            python_files: Lista de PythonFile
            
        Returns:
            Número de funciones largas
            
        Validates: Requirements 12.5
        """
        long_functions_count = 0
        
        for py_file in python_files:
            try:
                # Parsear AST del archivo
                tree = ast.parse(py_file.content)
                
                # Recorrer todos los nodos del AST
                for node in ast.walk(tree):
                    # Verificar si es una definición de función
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Calcular líneas de la función
                        function_lines = self._count_function_lines(node)
                        
                        # Verificar si excede el umbral
                        if function_lines > self.config.LONG_FUNCTION_THRESHOLD:
                            long_functions_count += 1
                            logger.debug(f"Función larga detectada: {node.name} "
                                       f"({function_lines} líneas) en {py_file.path}")
            
            except SyntaxError as e:
                logger.warning(f"No se pudo parsear {py_file.path}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error procesando {py_file.path}: {e}")
                continue
        
        logger.info(f"Funciones largas encontradas: {long_functions_count}")
        return long_functions_count
    
    def _count_function_lines(self, node: ast.FunctionDef) -> int:
        """
        Cuenta las líneas de código de una función.
        
        Args:
            node: Nodo AST de la función
            
        Returns:
            Número de líneas de la función
        """
        # Obtener línea de inicio y fin
        if hasattr(node, 'end_lineno') and node.end_lineno is not None:
            # Python 3.8+ tiene end_lineno
            return node.end_lineno - node.lineno + 1
        else:
            # Fallback: contar líneas del cuerpo
            if node.body:
                last_stmt = node.body[-1]
                if hasattr(last_stmt, 'lineno'):
                    return last_stmt.lineno - node.lineno + 1
            return 1
    
    def count_large_components(self, typescript_files: List[TypeScriptFile]) -> int:
        """
        Cuenta componentes TypeScript que exceden el umbral (>200 líneas).
        
        Args:
            typescript_files: Lista de TypeScriptFile
            
        Returns:
            Número de componentes grandes
            
        Validates: Requirements 12.6
        """
        large_components_count = 0
        
        for ts_file in typescript_files:
            # Verificar si es un componente
            if ts_file.is_component:
                # Verificar si excede el umbral de componentes grandes
                if ts_file.lines_of_code > self.config.LARGE_COMPONENT_THRESHOLD:
                    large_components_count += 1
                    logger.debug(f"Componente grande detectado: {ts_file.path} "
                               f"({ts_file.lines_of_code} líneas)")
        
        logger.info(f"Componentes grandes encontrados: {large_components_count}")
        return large_components_count
    
    def count_outdated_dependencies(self, dependencies: List) -> int:
        """
        Cuenta dependencias desactualizadas.
        
        Args:
            dependencies: Lista de Dependency
            
        Returns:
            Número de dependencias desactualizadas
            
        Validates: Requirements 12.8
        """
        return sum(1 for dep in dependencies if dep.is_outdated)
    
    def count_vulnerabilities(self, dependencies: List) -> int:
        """
        Cuenta el total de vulnerabilidades en dependencias.
        
        Args:
            dependencies: Lista de Dependency
            
        Returns:
            Número total de vulnerabilidades
            
        Validates: Requirements 12.8
        """
        return sum(len(dep.vulnerabilities) for dep in dependencies)
