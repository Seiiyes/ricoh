"""
Analizador de seguridad para Backend.

Este módulo contiene la clase SecurityAnalyzer que identifica vulnerabilidades
y problemas de seguridad en código Python (Backend).
"""

import re
from typing import List
from audit_system.models import Finding, Severity, SourceFile
from audit_system.config import get_config


class SecurityAnalyzer:
    """
    Analizador de seguridad para Backend.
    
    Identifica vulnerabilidades y problemas de seguridad:
    - Secrets hardcodeados
    - SQL injection
    - Validación de inputs
    - Autenticación faltante
    - Configuración HTTPS/CORS
    - Rate limiting
    """
    
    def __init__(self):
        """Inicializa el analizador con configuración."""
        self.config = get_config()
    
    def analyze(self, files: List[SourceFile]) -> List[Finding]:
        """
        Analiza una lista de archivos y retorna hallazgos de seguridad.
        
        Args:
            files: Lista de archivos de código fuente a analizar
            
        Returns:
            Lista de hallazgos de seguridad detectados
        """
        findings = []
        
        for file in files:
            if file.language == "python":
                findings.extend(self._analyze_backend_file(file))
        
        return findings
    
    def _analyze_backend_file(self, file: SourceFile) -> List[Finding]:
        """
        Analiza un archivo Python para problemas de seguridad.
        
        Args:
            file: Archivo Python a analizar
            
        Returns:
            Lista de hallazgos de seguridad en el archivo
        """
        findings = []
        
        # Detectar secrets hardcodeados
        findings.extend(self.detect_hardcoded_secrets(file.content, file.path))
        
        # Verificar SQL injection
        findings.extend(self.check_sql_injection(file.content, file.path))
        
        # Verificar validación de inputs
        findings.extend(self.check_input_validation(file.content, file.path))
        
        # Verificar autenticación en endpoints
        findings.extend(self.check_authentication(file.content, file.path))
        
        # Verificar configuración HTTPS/CORS
        findings.extend(self.check_https_cors(file.content, file.path))
        
        # Verificar rate limiting
        findings.extend(self.check_rate_limiting(file.content, file.path))
        
        return findings
    
    def detect_hardcoded_secrets(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta secrets hardcodeados en el código.
        
        Identifica passwords, API keys, tokens y otros secrets que no deberían
        estar en el código fuente.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de secrets hardcodeados
        """
        findings = []
        
        # Obtener patrones de secrets de la configuración
        secret_patterns = self.config.SECRET_PATTERNS
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Ignorar comentarios
            if line.strip().startswith('#'):
                continue
            
            # Buscar cada patrón de secret
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Verificar que no sea una variable de entorno
                    if 'os.environ' in line or 'os.getenv' in line or 'getenv' in line:
                        continue
                    
                    # Verificar que no sea un placeholder
                    if re.search(r'(your|example|test|dummy|placeholder|xxx)', line, re.IGNORECASE):
                        continue
                    
                    findings.append(Finding(
                        id=f"security_hardcoded_secret_{file_path}_{i}",
                        category="security",
                        subcategory="hardcoded_secret",
                        severity=Severity.CRITICO,
                        title="Secret hardcodeado detectado",
                        description=f"Se detectó un posible secret hardcodeado en la línea {i}. "
                                  f"Secrets en el código fuente son un riesgo de seguridad crítico.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet="[REDACTED]",  # No mostrar el secret
                        recommendation="Mover el secret a variables de entorno (.env) y usar os.getenv(). "
                                     "Nunca commitear secrets al repositorio."
                    ))
                    break  # Solo reportar una vez por línea
        
        return findings
    
    def check_sql_injection(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta posibles vulnerabilidades de SQL injection.
        
        Identifica concatenación de strings en queries SQL, lo que puede permitir
        ataques de SQL injection.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de SQL injection
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar concatenación de strings en queries
            # Patrón: query con f-string o concatenación +
            if re.search(r'(SELECT|INSERT|UPDATE|DELETE|WHERE)', line, re.IGNORECASE):
                # Verificar si usa f-string o concatenación
                has_fstring = bool(re.search(r'f["\'].*\{.*\}', line))
                has_concat = bool(re.search(r'["\'].*\+.*["\']', line))
                
                if has_fstring or has_concat:
                    findings.append(Finding(
                        id=f"security_sql_injection_{file_path}_{i}",
                        category="security",
                        subcategory="sql_injection",
                        severity=Severity.CRITICO,
                        title="Posible vulnerabilidad de SQL injection",
                        description=f"La línea {i} construye una query SQL usando concatenación de strings "
                                  f"o f-strings. Esto puede permitir ataques de SQL injection.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        recommendation="Usar queries parametrizadas con placeholders (?) o el ORM de SQLAlchemy. "
                                     "Nunca concatenar input del usuario directamente en queries."
                    ))
        
        return findings
    
    def check_input_validation(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica validación de inputs en endpoints.
        
        Identifica endpoints que reciben datos sin validación apropiada usando
        schemas Pydantic.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de validación de inputs faltante
        """
        findings = []
        
        # Solo analizar archivos de API
        if 'api' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar endpoints POST/PUT/PATCH que reciben datos
            if re.search(r'@\w+\.(post|put|patch)\(', line):
                # Buscar la función correspondiente
                func_content = []
                for j in range(i, min(i + 20, len(lines))):
                    func_content.append(lines[j])
                    if j > i and re.search(r'^@\w+\.\w+\(', lines[j]):
                        break
                
                func_text = '\n'.join(func_content)
                
                # Verificar si usa Pydantic schema
                has_schema = bool(re.search(r':\s*\w+Schema|:\s*BaseModel', func_text))
                
                # Verificar si accede a request.json o request.form directamente
                has_direct_access = bool(re.search(r'request\.(json|form|body)', func_text))
                
                if has_direct_access and not has_schema:
                    findings.append(Finding(
                        id=f"security_no_input_validation_{file_path}_{i}",
                        category="security",
                        subcategory="no_input_validation",
                        severity=Severity.ALTO,
                        title="Endpoint sin validación de input",
                        description=f"El endpoint en la línea {i} accede a datos del request sin "
                                  f"validación usando schemas Pydantic. Esto puede permitir datos "
                                  f"maliciosos o malformados.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Definir un schema Pydantic (BaseModel) y usarlo como tipo del parámetro. "
                                     "Pydantic validará automáticamente los datos."
                    ))
        
        return findings
    
    def check_authentication(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que los endpoints tengan autenticación apropiada.
        
        Identifica endpoints que deberían estar protegidos pero no tienen
        decoradores de autenticación.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de autenticación faltante
        """
        findings = []
        
        # Solo analizar archivos de API
        if 'api' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar endpoints que modifican datos (POST, PUT, DELETE, PATCH)
            if re.search(r'@\w+\.(post|put|delete|patch)\(', line):
                # Verificar si tiene autenticación en las líneas anteriores
                has_auth = False
                for j in range(max(0, i - 5), i):
                    if re.search(r'@require|@auth|Depends\(.*auth|get_current_user', lines[j]):
                        has_auth = True
                        break
                
                if not has_auth:
                    findings.append(Finding(
                        id=f"security_no_authentication_{file_path}_{i}",
                        category="security",
                        subcategory="no_authentication",
                        severity=Severity.ALTO,
                        title="Endpoint sin autenticación",
                        description=f"El endpoint en la línea {i} modifica datos pero no tiene "
                                  f"autenticación. Esto puede permitir acceso no autorizado.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar decorador de autenticación o usar Depends(get_current_user) "
                                     "en los parámetros de la función."
                    ))
        
        return findings
    
    def check_https_cors(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica configuración segura de HTTPS y CORS.
        
        Identifica configuraciones inseguras de CORS o falta de HTTPS.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de configuración insegura
        """
        findings = []
        
        # Solo analizar archivos de configuración principal
        if 'main.py' not in file_path.lower() and 'config' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar configuración de CORS permisiva
            if re.search(r'allow_origins\s*=\s*\[\s*["\']?\*["\']?\s*\]', line):
                findings.append(Finding(
                    id=f"security_cors_wildcard_{file_path}_{i}",
                    category="security",
                    subcategory="insecure_cors",
                    severity=Severity.ALTO,
                    title="CORS configurado con wildcard (*)",
                    description=f"La configuración de CORS en la línea {i} permite cualquier origen (*). "
                              f"Esto puede permitir ataques CSRF desde cualquier dominio.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Especificar orígenes permitidos explícitamente: "
                                 "allow_origins=['https://yourdomain.com']"
                ))
            
            # Buscar allow_credentials con wildcard origins
            if re.search(r'allow_credentials\s*=\s*True', line):
                # Verificar si hay wildcard en las líneas cercanas
                for j in range(max(0, i - 5), min(i + 5, len(lines))):
                    if re.search(r'allow_origins\s*=\s*\[\s*["\']?\*["\']?\s*\]', lines[j]):
                        findings.append(Finding(
                            id=f"security_cors_credentials_wildcard_{file_path}_{i}",
                            category="security",
                            subcategory="insecure_cors",
                            severity=Severity.CRITICO,
                            title="CORS con credentials y wildcard origin",
                            description=f"La configuración en la línea {i} permite credentials con wildcard origin. "
                                      f"Esto es una vulnerabilidad crítica de seguridad.",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            recommendation="Nunca usar allow_credentials=True con allow_origins=['*']. "
                                         "Especificar orígenes explícitamente."
                        ))
                        break
        
        return findings
    
    def check_rate_limiting(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica protección contra DDoS con rate limiting.
        
        Identifica endpoints públicos sin rate limiting.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de rate limiting faltante
        """
        findings = []
        
        # Solo analizar archivos de API
        if 'api' not in file_path.lower():
            return findings
        
        # Verificar si el archivo tiene rate limiting configurado
        has_rate_limit = bool(re.search(r'@limiter|RateLimiter|rate_limit', file_content))
        
        if not has_rate_limit:
            lines = file_content.split('\n')
            
            # Buscar endpoints públicos (sin autenticación)
            for i, line in enumerate(lines, start=1):
                if re.search(r'@\w+\.(get|post)\(', line):
                    # Verificar si tiene autenticación
                    has_auth = False
                    for j in range(max(0, i - 5), i):
                        if re.search(r'@require|@auth|Depends\(.*auth', lines[j]):
                            has_auth = True
                            break
                    
                    # Si es público (sin auth), debería tener rate limiting
                    if not has_auth:
                        findings.append(Finding(
                            id=f"security_no_rate_limiting_{file_path}_{i}",
                            category="security",
                            subcategory="no_rate_limiting",
                            severity=Severity.MEDIO,
                            title="Endpoint público sin rate limiting",
                            description=f"El endpoint público en la línea {i} no tiene rate limiting. "
                                      f"Esto puede permitir ataques de DDoS o abuso del API.",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            recommendation="Implementar rate limiting usando slowapi o similar: "
                                         "@limiter.limit('10/minute')"
                        ))
                        break  # Solo reportar una vez por archivo
        
        return findings
