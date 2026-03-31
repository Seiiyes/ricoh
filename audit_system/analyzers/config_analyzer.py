"""
Analizador de configuración para Backend.

Este módulo contiene la clase ConfigAnalyzer que identifica problemas
en la configuración y manejo de variables de entorno en código Python (Backend).
"""

import re
from typing import List
from audit_system.models import Finding, Severity, SourceFile
from audit_system.config import get_config


class ConfigAnalyzer:
    """
    Analizador de configuración para Backend.
    
    Identifica problemas en la configuración:
    - Falta de documentación de variables de entorno (.env.example)
    - Valores por defecto inseguros
    - Configuraciones hardcodeadas
    - Falta de validación de variables requeridas
    """
    
    def __init__(self):
        """Inicializa el analizador con configuración."""
        self.config = get_config()
    
    def analyze(self, files: List[SourceFile]) -> List[Finding]:
        """
        Analiza una lista de archivos y retorna hallazgos de configuración.
        
        Args:
            files: Lista de archivos de código fuente a analizar
            
        Returns:
            Lista de hallazgos de configuración detectados
        """
        findings = []
        
        for file in files:
            if file.language == "python":
                findings.extend(self._analyze_backend_file(file))
        
        return findings
    
    def _analyze_backend_file(self, file: SourceFile) -> List[Finding]:
        """
        Analiza un archivo Python para problemas de configuración.
        
        Args:
            file: Archivo Python a analizar
            
        Returns:
            Lista de hallazgos de configuración en el archivo
        """
        findings = []
        
        # Verificar documentación de variables de entorno
        findings.extend(self.check_env_documentation(file.content, file.path))
        
        # Detectar valores por defecto inseguros
        findings.extend(self.detect_insecure_defaults(file.content, file.path))
        
        # Detectar configuraciones hardcodeadas
        findings.extend(self.detect_hardcoded_config(file.content, file.path))
        
        # Verificar validación de variables requeridas
        findings.extend(self.check_env_validation(file.content, file.path))
        
        return findings
    
    def check_env_documentation(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que las variables de entorno estén documentadas en .env.example.
        
        Identifica uso de os.getenv() sin documentación correspondiente.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de variables sin documentar
        """
        findings = []
        
        # Solo analizar archivos de configuración
        if 'config' not in file_path.lower() and 'settings' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar uso de os.getenv o os.environ.get
            env_match = re.search(r'(?:os\.getenv|os\.environ\.get|getenv)\s*\(\s*["\']([^"\']+)["\']', line)
            
            if env_match:
                env_var = env_match.group(1)
                
                # Verificar si tiene comentario explicativo cerca
                has_comment = False
                for j in range(max(0, i - 3), min(i + 2, len(lines))):
                    if '#' in lines[j] and env_var in lines[j]:
                        has_comment = True
                        break
                
                if not has_comment:
                    findings.append(Finding(
                        id=f"config_undocumented_env_{file_path}_{i}",
                        category="configuration",
                        subcategory="undocumented_env",
                        severity=Severity.BAJO,
                        title=f"Variable de entorno {env_var} sin documentar",
                        description=f"La variable de entorno {env_var} en la línea {i} no tiene "
                                  f"comentario explicativo. Las variables de entorno deberían estar "
                                  f"documentadas para facilitar la configuración.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation=f"Agregar comentario explicando el propósito de {env_var} y "
                                     f"asegurar que esté en .env.example con valor de ejemplo."
                    ))
        
        return findings
    
    def detect_insecure_defaults(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta valores por defecto inseguros en configuración.
        
        Identifica valores por defecto que no deberían usarse en producción
        como DEBUG=True, SECRET_KEY con valor hardcodeado, etc.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de valores por defecto inseguros
        """
        findings = []
        
        # Solo analizar archivos de configuración
        if 'config' not in file_path.lower() and 'settings' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        # Patrones de configuraciones inseguras
        insecure_patterns = [
            (r'DEBUG\s*=\s*True', "DEBUG=True en producción es inseguro"),
            (r'getenv\s*\(["\']SECRET_KEY["\']\s*,\s*["\'][^"\']+["\']', "SECRET_KEY con valor por defecto hardcodeado"),
            (r'getenv\s*\(["\']PASSWORD["\']\s*,\s*["\'][^"\']+["\']', "PASSWORD con valor por defecto"),
            (r'ALLOWED_HOSTS\s*=\s*\[\s*["\']?\*["\']?\s*\]', "ALLOWED_HOSTS con wildcard (*)"),
            (r'CORS_ALLOW_ALL_ORIGINS\s*=\s*True', "CORS permitiendo todos los orígenes"),
        ]
        
        for i, line in enumerate(lines, start=1):
            for pattern, description in insecure_patterns:
                if re.search(pattern, line):
                    findings.append(Finding(
                        id=f"config_insecure_default_{file_path}_{i}",
                        category="configuration",
                        subcategory="insecure_default",
                        severity=Severity.ALTO,
                        title="Valor por defecto inseguro en configuración",
                        description=f"La línea {i} contiene una configuración insegura: {description}. "
                                  f"Esto puede exponer la aplicación a riesgos de seguridad.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Usar valores seguros por defecto y requerir configuración explícita "
                                     "para valores sensibles. Nunca usar valores inseguros en producción."
                    ))
        
        return findings
    
    def detect_hardcoded_config(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta configuraciones hardcodeadas que deberían ser variables de entorno.
        
        Identifica URLs, hosts, puertos y otros valores de configuración
        hardcodeados en el código.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de configuraciones hardcodeadas
        """
        findings = []
        
        lines = file_content.split('\n')
        
        # Patrones de configuraciones que deberían ser variables de entorno
        config_patterns = [
            (r'["\']https?://[^"\']+["\']', "URL hardcodeada"),
            (r'["\'](?:localhost|127\.0\.0\.1|0\.0\.0\.0):\d+["\']', "Host/puerto hardcodeado"),
            (r'DATABASE_URL\s*=\s*["\'][^"\']+["\']', "DATABASE_URL hardcodeada"),
            (r'REDIS_URL\s*=\s*["\'][^"\']+["\']', "REDIS_URL hardcodeada"),
        ]
        
        for i, line in enumerate(lines, start=1):
            # Ignorar comentarios
            if line.strip().startswith('#'):
                continue
            
            # Ignorar si ya usa getenv
            if 'getenv' in line or 'environ' in line:
                continue
            
            for pattern, description in config_patterns:
                if re.search(pattern, line):
                    findings.append(Finding(
                        id=f"config_hardcoded_{file_path}_{i}",
                        category="configuration",
                        subcategory="hardcoded_config",
                        severity=Severity.MEDIO,
                        title=f"{description} en código",
                        description=f"La línea {i} contiene {description.lower()}. "
                                  f"Las configuraciones deberían ser variables de entorno "
                                  f"para facilitar el despliegue en diferentes ambientes.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        recommendation="Mover la configuración a una variable de entorno: "
                                     "os.getenv('CONFIG_NAME', 'default_value')"
                    ))
                    break  # Solo reportar una vez por línea
        
        return findings
    
    def check_env_validation(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que las variables de entorno requeridas sean validadas.
        
        Identifica uso de os.getenv() sin valor por defecto para variables críticas,
        lo que puede causar errores en runtime.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de validación faltante
        """
        findings = []
        
        # Solo analizar archivos de configuración
        if 'config' not in file_path.lower() and 'settings' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        # Variables críticas que deberían ser validadas
        critical_vars = ['SECRET_KEY', 'DATABASE_URL', 'API_KEY', 'PRIVATE_KEY']
        
        for i, line in enumerate(lines, start=1):
            # Buscar getenv de variables críticas
            for var in critical_vars:
                # Patrón: getenv('VAR') sin segundo parámetro (sin default)
                pattern = rf'(?:os\.getenv|getenv)\s*\(\s*["\']({var})["\']\s*\)'
                match = re.search(pattern, line)
                
                if match:
                    # Verificar si hay validación después (raise, assert, if not)
                    has_validation = False
                    for j in range(i, min(i + 5, len(lines))):
                        if re.search(r'(raise|assert|if\s+not)', lines[j]):
                            has_validation = True
                            break
                    
                    if not has_validation:
                        findings.append(Finding(
                            id=f"config_no_validation_{file_path}_{i}",
                            category="configuration",
                            subcategory="no_env_validation",
                            severity=Severity.ALTO,
                            title=f"Variable crítica {var} sin validación",
                            description=f"La variable de entorno {var} en la línea {i} no tiene "
                                      f"valor por defecto ni validación. Si no está configurada, "
                                      f"la aplicación fallará en runtime.",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            recommendation=f"Agregar validación: {var} = os.getenv('{var}') or "
                                         f"raise ValueError('{var} is required')"
                        ))
        
        return findings
