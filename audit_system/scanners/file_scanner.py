"""
FileScanner: Componente para mapear la estructura del proyecto.

Responsable de:
- Escanear directorios recursivamente
- Identificar archivos Python y TypeScript
- Clasificar archivos por tamaño
- Construir la estructura del proyecto
"""

import os
from pathlib import Path
from typing import List

from audit_system.config import get_config
from audit_system.models import ProjectStructure, PythonFile, TypeScriptFile
from audit_system.logger import get_logger

logger = get_logger(__name__)


class FileScanner:
    """Escáner de archivos para mapeo de estructura del proyecto."""
    
    def __init__(self):
        """Inicializa el FileScanner con configuración."""
        self.config = get_config()
    
    def scan_project(self, root_path: str) -> ProjectStructure:
        """
        Escanea el proyecto completo y retorna estructura mapeada.
        
        Args:
            root_path: Ruta raíz del proyecto
            
        Returns:
            ProjectStructure con todos los archivos identificados
            
        Validates: Requirements 1.1, 1.2, 1.3, 1.6, 1.7
        """
        logger.info(f"Iniciando escaneo del proyecto: {root_path}")
        
        # Identificar archivos Python en backend
        backend_path = os.path.join(root_path, "backend")
        python_files = self.find_python_files(backend_path) if os.path.exists(backend_path) else []
        
        # Identificar archivos TypeScript en frontend
        frontend_path = os.path.join(root_path, "src")
        typescript_files = self.find_typescript_files(frontend_path) if os.path.exists(frontend_path) else []
        
        logger.info(f"Archivos Python encontrados: {len(python_files)}")
        logger.info(f"Archivos TypeScript encontrados: {len(typescript_files)}")
        
        # Construir estructura del proyecto
        structure = ProjectStructure(
            root_path=root_path,
            backend_files=python_files,
            frontend_files=typescript_files
        )
        
        return structure
    
    def find_python_files(self, backend_path: str) -> List[PythonFile]:
        """
        Identifica todos los archivos .py en el directorio backend.
        
        Recorre recursivamente el directorio backend excluyendo directorios
        configurados (node_modules, __pycache__, .git, etc.).
        
        Args:
            backend_path: Ruta al directorio backend
            
        Returns:
            Lista de PythonFile con información de cada archivo
            
        Validates: Requirements 1.1, 1.3
        """
        logger.info(f"Buscando archivos Python en: {backend_path}")
        
        python_files = []
        
        if not os.path.exists(backend_path):
            logger.warning(f"Directorio backend no existe: {backend_path}")
            return python_files
        
        # Recorrer directorios recursivamente
        for root, dirs, files in os.walk(backend_path):
            # Excluir directorios configurados
            dirs[:] = [d for d in dirs if d not in self.config.EXCLUDE_DIRS]
            
            for file in files:
                # Verificar extensión Python
                if any(file.endswith(ext) for ext in self.config.PYTHON_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, start=os.path.dirname(backend_path))
                    
                    try:
                        # Leer contenido del archivo
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Contar líneas de código
                        lines_of_code = len(content.splitlines())
                        
                        # Clasificar tamaño
                        is_large = self.classify_file_size(lines_of_code)
                        
                        # Crear objeto PythonFile
                        python_file = PythonFile(
                            path=relative_path,
                            language='python',
                            lines_of_code=lines_of_code,
                            is_large=is_large,
                            content=content
                        )
                        
                        python_files.append(python_file)
                        
                    except (IOError, PermissionError, UnicodeDecodeError) as e:
                        logger.error(f"No se pudo leer archivo {file_path}: {e}")
                        continue
        
        logger.info(f"Total archivos Python encontrados: {len(python_files)}")
        return python_files
    
    def find_typescript_files(self, frontend_path: str) -> List[TypeScriptFile]:
        """
        Identifica todos los archivos .ts y .tsx en el directorio frontend.
        
        Recorre recursivamente el directorio frontend excluyendo directorios
        configurados (node_modules, dist, build, etc.).
        
        Args:
            frontend_path: Ruta al directorio frontend (src)
            
        Returns:
            Lista de TypeScriptFile con información de cada archivo
            
        Validates: Requirements 1.2, 1.3
        """
        logger.info(f"Buscando archivos TypeScript en: {frontend_path}")
        
        typescript_files = []
        
        if not os.path.exists(frontend_path):
            logger.warning(f"Directorio frontend no existe: {frontend_path}")
            return typescript_files
        
        # Recorrer directorios recursivamente
        for root, dirs, files in os.walk(frontend_path):
            # Excluir directorios configurados
            dirs[:] = [d for d in dirs if d not in self.config.EXCLUDE_DIRS]
            
            for file in files:
                # Verificar extensión TypeScript
                if any(file.endswith(ext) for ext in self.config.TYPESCRIPT_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, start=os.path.dirname(frontend_path))
                    
                    try:
                        # Leer contenido del archivo
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Contar líneas de código
                        lines_of_code = len(content.splitlines())
                        
                        # Clasificar tamaño
                        is_large = self.classify_file_size(lines_of_code)
                        
                        # Determinar si es componente React (heurística: .tsx o contiene JSX)
                        is_component = file.endswith('.tsx') or 'return (' in content or 'return<' in content
                        
                        # Crear objeto TypeScriptFile
                        typescript_file = TypeScriptFile(
                            path=relative_path,
                            language='typescript',
                            lines_of_code=lines_of_code,
                            is_large=is_large,
                            content=content,
                            is_component=is_component
                        )
                        
                        typescript_files.append(typescript_file)
                        
                    except (IOError, PermissionError, UnicodeDecodeError) as e:
                        logger.error(f"No se pudo leer archivo {file_path}: {e}")
                        continue
        
        logger.info(f"Total archivos TypeScript encontrados: {len(typescript_files)}")
        return typescript_files
    
    def classify_file_size(self, lines_of_code: int) -> bool:
        """
        Clasifica un archivo como grande si excede el umbral configurado.
        
        Args:
            lines_of_code: Número de líneas del archivo
            
        Returns:
            True si el archivo es grande (>300 líneas), False en caso contrario
            
        Validates: Requirements 1.3
        """
        return lines_of_code > self.config.LARGE_FILE_THRESHOLD
