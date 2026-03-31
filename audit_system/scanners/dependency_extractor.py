"""
DependencyExtractor: Componente para extraer y analizar dependencias del proyecto.

Responsable de:
- Parsear requirements.txt para dependencias Python
- Parsear package.json para dependencias npm
- Verificar vulnerabilidades conocidas (CVE)
- Clasificar dependencias desactualizadas
"""

import json
import os
import re
from typing import List, Optional

from audit_system.config import get_config
from audit_system.models import Dependency, Vulnerability
from audit_system.logger import get_logger

logger = get_logger(__name__)


class DependencyExtractor:
    """Extractor de dependencias para análisis de seguridad."""
    
    def __init__(self):
        """Inicializa el DependencyExtractor con configuración."""
        self.config = get_config()
    
    def extract_python_deps(self, requirements_path: str) -> List[Dependency]:
        """
        Extrae dependencias de requirements.txt.
        
        Parsea el archivo requirements.txt línea por línea, soportando formatos:
        - package==version (versión exacta)
        - package>=version (versión mínima)
        - package~=version (versión compatible)
        - package (sin versión especificada)
        
        Args:
            requirements_path: Ruta al archivo requirements.txt
            
        Returns:
            Lista de Dependency con información de cada paquete Python
            
        Validates: Requirements 1.4, 14.1
        """
        logger.info(f"Extrayendo dependencias Python de: {requirements_path}")
        
        dependencies = []
        
        if not os.path.exists(requirements_path):
            logger.warning(f"Archivo requirements.txt no existe: {requirements_path}")
            return dependencies
        
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, start=1):
                # Limpiar línea
                line = line.strip()
                
                # Ignorar líneas vacías y comentarios
                if not line or line.startswith('#'):
                    continue
                
                # Parsear dependencia
                dependency = self._parse_python_dependency(line, line_num)
                if dependency:
                    dependencies.append(dependency)
        
        except (IOError, PermissionError, UnicodeDecodeError) as e:
            logger.error(f"No se pudo leer requirements.txt: {e}")
            return dependencies
        
        logger.info(f"Total dependencias Python extraídas: {len(dependencies)}")
        return dependencies
    
    def _parse_python_dependency(self, line: str, line_num: int) -> Optional[Dependency]:
        """
        Parsea una línea de requirements.txt.
        
        Soporta formatos:
        - package==1.0.0
        - package>=1.0.0
        - package~=1.0.0
        - package[extra]==1.0.0
        - package
        
        Args:
            line: Línea del archivo requirements.txt
            line_num: Número de línea (para logging)
            
        Returns:
            Dependency si se pudo parsear, None en caso contrario
        """
        # Patrón regex para parsear dependencias Python
        # Captura: nombre[extras] operador versión
        pattern = r'^([a-zA-Z0-9_-]+)(?:\[([a-zA-Z0-9_,-]+)\])?\s*([=><~!]+)?\s*([0-9.]+.*)?$'
        
        match = re.match(pattern, line)
        
        if not match:
            logger.warning(f"No se pudo parsear línea {line_num}: {line}")
            return None
        
        name = match.group(1)
        extras = match.group(2)  # Opcional: [standard], [email], etc.
        operator = match.group(3)  # ==, >=, ~=, etc.
        version = match.group(4)  # 1.0.0
        
        # Si tiene extras, incluirlos en el nombre para referencia
        if extras:
            display_name = f"{name}[{extras}]"
        else:
            display_name = name
        
        # Si no tiene versión especificada
        if not version:
            version = "unspecified"
            logger.debug(f"Dependencia sin versión: {display_name}")
        
        # Crear objeto Dependency
        dependency = Dependency(
            name=display_name,
            current_version=version,
            latest_version="unknown",  # Se actualizaría con API externa
            is_outdated=False,  # Se actualizaría con verificación
            vulnerabilities=[],  # Se llenaría con check_vulnerabilities()
            ecosystem="python"
        )
        
        return dependency
    
    def extract_npm_deps(self, package_json_path: str) -> List[Dependency]:
        """
        Extrae dependencias de package.json.
        
        Parsea el archivo package.json extrayendo tanto dependencies como
        devDependencies. Soporta formatos de versión:
        - ^1.0.0 (compatible)
        - ~1.0.0 (patch)
        - 1.0.0 (exacta)
        - >=1.0.0 (rango)
        
        Args:
            package_json_path: Ruta al archivo package.json
            
        Returns:
            Lista de Dependency con información de cada paquete npm
            
        Validates: Requirements 1.5, 14.2
        """
        logger.info(f"Extrayendo dependencias npm de: {package_json_path}")
        
        dependencies = []
        
        if not os.path.exists(package_json_path):
            logger.warning(f"Archivo package.json no existe: {package_json_path}")
            return dependencies
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # Extraer dependencies
            deps = package_data.get('dependencies', {})
            for name, version in deps.items():
                dependency = self._create_npm_dependency(name, version, is_dev=False)
                dependencies.append(dependency)
            
            # Extraer devDependencies
            dev_deps = package_data.get('devDependencies', {})
            for name, version in dev_deps.items():
                dependency = self._create_npm_dependency(name, version, is_dev=True)
                dependencies.append(dependency)
        
        except (IOError, PermissionError) as e:
            logger.error(f"No se pudo leer package.json: {e}")
            return dependencies
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando package.json: {e}")
            return dependencies
        
        logger.info(f"Total dependencias npm extraídas: {len(dependencies)}")
        return dependencies
    
    def _create_npm_dependency(self, name: str, version: str, is_dev: bool) -> Dependency:
        """
        Crea un objeto Dependency para una dependencia npm.
        
        Args:
            name: Nombre del paquete
            version: Versión especificada (puede incluir ^, ~, etc.)
            is_dev: True si es devDependency
            
        Returns:
            Dependency con información del paquete
        """
        # Limpiar versión de prefijos (^, ~, >=, etc.)
        clean_version = re.sub(r'^[\^~>=<]+', '', version)
        
        # Agregar sufijo si es dev dependency
        display_name = f"{name} (dev)" if is_dev else name
        
        dependency = Dependency(
            name=display_name,
            current_version=clean_version,
            latest_version="unknown",  # Se actualizaría con API externa
            is_outdated=False,  # Se actualizaría con verificación
            vulnerabilities=[],  # Se llenaría con check_vulnerabilities()
            ecosystem="npm"
        )
        
        return dependency
    
    def check_vulnerabilities(self, dependency: Dependency) -> List[Vulnerability]:
        """
        Verifica vulnerabilidades conocidas (CVE) para una dependencia.
        
        Implementación simple que marca como "not_verified" si no hay API disponible.
        En una implementación completa, esto consultaría:
        - Para Python: PyPI Advisory Database o OSV.dev
        - Para npm: npm audit API o Snyk
        
        Args:
            dependency: Dependencia a verificar
            
        Returns:
            Lista de Vulnerability encontradas (vacía si no hay API)
            
        Validates: Requirements 14.3
        """
        logger.debug(f"Verificando vulnerabilidades para: {dependency.name}")
        
        # Implementación simple: marcar como no verificado
        # En producción, aquí se haría una llamada a API externa
        
        # Ejemplo de cómo se vería con una API real:
        # try:
        #     if dependency.ecosystem == "python":
        #         vulnerabilities = self._check_pypi_vulnerabilities(dependency)
        #     elif dependency.ecosystem == "npm":
        #         vulnerabilities = self._check_npm_vulnerabilities(dependency)
        #     else:
        #         vulnerabilities = []
        # except APIError as e:
        #     logger.warning(f"No se pudo verificar vulnerabilidades: {e}")
        #     vulnerabilities = []
        
        # Por ahora, retornar lista vacía (no bloquear el análisis)
        logger.debug(f"Verificación de vulnerabilidades no implementada (API no disponible)")
        return []
    
    def extract_all_dependencies(self, root_path: str) -> tuple[List[Dependency], List[Dependency]]:
        """
        Extrae todas las dependencias del proyecto (Python y npm).
        
        Args:
            root_path: Ruta raíz del proyecto
            
        Returns:
            Tupla (python_dependencies, npm_dependencies)
        """
        logger.info(f"Extrayendo todas las dependencias del proyecto: {root_path}")
        
        # Extraer dependencias Python
        requirements_path = os.path.join(root_path, "backend", "requirements.txt")
        python_deps = self.extract_python_deps(requirements_path)
        
        # Extraer dependencias npm
        package_json_path = os.path.join(root_path, "package.json")
        npm_deps = self.extract_npm_deps(package_json_path)
        
        # Verificar vulnerabilidades para todas las dependencias
        all_deps = python_deps + npm_deps
        for dep in all_deps:
            vulnerabilities = self.check_vulnerabilities(dep)
            dep.vulnerabilities = vulnerabilities
        
        logger.info(f"Total dependencias extraídas: {len(all_deps)} "
                   f"(Python: {len(python_deps)}, npm: {len(npm_deps)})")
        
        return python_deps, npm_deps
