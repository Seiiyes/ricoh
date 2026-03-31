"""
Analizador de arquitectura para Backend y Frontend.

Este módulo contiene la clase ArchitectureAnalyzer que evalúa la separación
de responsabilidades y organización del código en Python (Backend) y TypeScript/React (Frontend).
"""

import re
from typing import List, Optional
from audit_system.models import Finding, Severity, SourceFile
from audit_system.config import get_config


class ArchitectureAnalyzer:
    """
    Analizador de arquitectura para Backend y Frontend.
    
    Evalúa:
    - Backend: Separación de capas, lógica de negocio en API, transacciones, acoplamiento
    - Frontend: Separación UI/lógica, llamadas API dispersas, gestión de estado
    - API: Documentación OpenAPI, consistencia de verbos HTTP, formato de errores
    """
    
    def __init__(self):
        """Inicializa el analizador con configuración."""
        self.config = get_config()
    
    def analyze(self, files: List[SourceFile]) -> List[Finding]:
        """
        Analiza una lista de archivos y retorna hallazgos de arquitectura.
        
        Args:
            files: Lista de archivos de código fuente a analizar
            
        Returns:
            Lista de hallazgos de arquitectura detectados
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
        Analiza un archivo Python para problemas de arquitectura.
        
        Args:
            file: Archivo Python a analizar
            
        Returns:
            Lista de hallazgos de arquitectura en el archivo
        """
        findings = []
        
        # Verificar separación de capas
        findings.extend(self.check_layer_separation(file.content, file.path))
        
        # Detectar lógica de negocio en endpoints API
        findings.extend(self.detect_business_logic_in_api(file.content, file.path))
        
        # Verificar manejo de transacciones
        findings.extend(self.check_transaction_handling(file.content, file.path))
        
        # Detectar acoplamiento fuerte
        findings.extend(self.detect_tight_coupling(file.content, file.path))
        
        # Verificar documentación OpenAPI
        findings.extend(self.check_openapi_documentation(file.content, file.path))
        
        # Verificar consistencia de verbos HTTP
        findings.extend(self.check_http_verb_consistency(file.content, file.path))
        
        # Verificar formato de respuestas de error
        findings.extend(self.check_error_response_format(file.content, file.path))
        
        # Verificar códigos de estado HTTP
        findings.extend(self.check_http_status_codes(file.content, file.path))
        
        return findings
    
    def _analyze_frontend_file(self, file: SourceFile) -> List[Finding]:
        """
        Analiza un archivo TypeScript/React para problemas de arquitectura.
        
        Args:
            file: Archivo TypeScript a analizar
            
        Returns:
            Lista de hallazgos de arquitectura en el archivo
        """
        findings = []
        
        # Verificar separación de componentes
        findings.extend(self.check_component_separation(file.content, file.path))
        
        # Detectar llamadas API en componentes
        findings.extend(self.detect_api_calls_in_components(file.content, file.path))
        
        # Verificar gestión de estado
        findings.extend(self.check_state_management(file.content, file.path))
        
        # Verificar uso de Context API
        findings.extend(self.check_context_usage(file.content, file.path))
        
        return findings
    
    # ========== Métodos de análisis de Backend ==========
    
    def check_layer_separation(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica la separación entre capas API, servicios y repositorio.
        
        Identifica violaciones de separación de capas donde archivos de API
        acceden directamente a la base de datos sin pasar por servicios.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de violación de separación de capas
        """
        findings = []
        
        # Solo analizar archivos de API
        if '/api/' not in file_path and '\\api\\' not in file_path:
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar acceso directo a session/query en archivos de API
            if re.search(r'session\.(query|execute|add|delete|commit)', line):
                findings.append(Finding(
                    id=f"arch_layer_violation_{file_path}_{i}",
                    category="architecture",
                    subcategory="layer_separation",
                    severity=Severity.MEDIO,
                    title="Violación de separación de capas",
                    description=f"El archivo de API en la línea {i} accede directamente a la base de datos. "
                              f"Los endpoints deben delegar operaciones de datos a la capa de servicios o repositorio.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Mover la lógica de acceso a datos a un servicio o repositorio, "
                                 "y llamar ese servicio desde el endpoint."
                ))
        
        return findings
    
    def detect_business_logic_in_api(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta lógica de negocio implementada directamente en endpoints.
        
        Identifica endpoints con lógica compleja (loops, condicionales múltiples,
        cálculos) que debería estar en servicios.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de lógica de negocio en API
        """
        findings = []
        
        # Solo analizar archivos de API
        if '/api/' not in file_path and '\\api\\' not in file_path:
            return findings
        
        lines = file_content.split('\n')
        in_endpoint = False
        endpoint_start = 0
        endpoint_complexity = 0
        
        for i, line in enumerate(lines, start=1):
            # Detectar inicio de endpoint
            if re.search(r'@\w+\.(get|post|put|delete|patch)\(', line):
                in_endpoint = True
                endpoint_start = i
                endpoint_complexity = 0
                continue
            
            # Detectar fin de endpoint (nueva función o decorador)
            if in_endpoint and (re.search(r'^(async\s+)?def\s+', line) or re.search(r'^@\w+\.\w+\(', line)) and i > endpoint_start + 1:
                # Evaluar complejidad acumulada
                if endpoint_complexity >= 3:
                    findings.append(Finding(
                        id=f"arch_business_logic_api_{file_path}_{endpoint_start}",
                        category="architecture",
                        subcategory="business_logic_in_api",
                        severity=Severity.MEDIO,
                        title="Lógica de negocio en endpoint de API",
                        description=f"El endpoint en la línea {endpoint_start} contiene lógica de negocio compleja. "
                                  f"Los endpoints deben ser delgados y delegar la lógica a servicios.",
                        file_path=file_path,
                        line_number=endpoint_start,
                        recommendation="Extraer la lógica de negocio a un servicio dedicado y "
                                     "llamar ese servicio desde el endpoint."
                    ))
                in_endpoint = False
                endpoint_complexity = 0
            
            # Contar indicadores de complejidad dentro del endpoint
            if in_endpoint:
                # Loops
                if re.search(r'^\s*(for|while)\s+', line):
                    endpoint_complexity += 1
                
                # Condicionales múltiples
                if re.search(r'^\s*if\s+.*(and|or)', line):
                    endpoint_complexity += 1
                elif re.search(r'^\s*(if|elif)\s+', line):
                    endpoint_complexity += 0.5
                
                # Cálculos complejos
                if re.search(r'[+\-*/].*[+\-*/]', line):
                    endpoint_complexity += 0.5
        
        # Evaluar último endpoint si el archivo termina
        if in_endpoint and endpoint_complexity >= 3:
            findings.append(Finding(
                id=f"arch_business_logic_api_{file_path}_{endpoint_start}",
                category="architecture",
                subcategory="business_logic_in_api",
                severity=Severity.MEDIO,
                title="Lógica de negocio en endpoint de API",
                description=f"El endpoint en la línea {endpoint_start} contiene lógica de negocio compleja. "
                          f"Los endpoints deben ser delgados y delegar la lógica a servicios.",
                file_path=file_path,
                line_number=endpoint_start,
                recommendation="Extraer la lógica de negocio a un servicio dedicado y "
                             "llamar ese servicio desde el endpoint."
            ))
        
        return findings
    
    def check_transaction_handling(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica la consistencia en el manejo de transacciones de base de datos.
        
        Identifica operaciones de escritura sin commit explícito o sin manejo
        de rollback en caso de error.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de manejo inconsistente de transacciones
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar operaciones de escritura
            if re.search(r'session\.(add|delete|update|merge)\(', line):
                # Buscar commit en las siguientes líneas
                has_commit = False
                has_rollback = False
                has_try_except = False
                
                # Revisar contexto (20 líneas hacia adelante)
                for j in range(i, min(i + 20, len(lines))):
                    if 'commit' in lines[j]:
                        has_commit = True
                    if 'rollback' in lines[j]:
                        has_rollback = True
                    if re.search(r'^\s*try:', lines[j]) or re.search(r'^\s*except', lines[j]):
                        has_try_except = True
                
                # Reportar si falta commit
                if not has_commit:
                    findings.append(Finding(
                        id=f"arch_missing_commit_{file_path}_{i}",
                        category="architecture",
                        subcategory="transaction_handling",
                        severity=Severity.MEDIO,
                        title="Operación de escritura sin commit explícito",
                        description=f"La operación de escritura en la línea {i} no tiene un commit explícito. "
                                  f"Esto puede causar que los cambios no se persistan.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar session.commit() después de las operaciones de escritura, "
                                     "preferiblemente dentro de un bloque try-except con rollback."
                    ))
                
                # Reportar si falta manejo de errores
                elif not has_try_except or not has_rollback:
                    findings.append(Finding(
                        id=f"arch_missing_rollback_{file_path}_{i}",
                        category="architecture",
                        subcategory="transaction_handling",
                        severity=Severity.BAJO,
                        title="Transacción sin manejo de rollback",
                        description=f"La transacción en la línea {i} no tiene manejo de rollback en caso de error. "
                                  f"Esto puede dejar la base de datos en estado inconsistente.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Envolver las operaciones de transacción en try-except con "
                                     "session.rollback() en el bloque except."
                    ))
        
        return findings
    
    def detect_tight_coupling(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta acoplamiento fuerte entre módulos.
        
        Identifica imports directos de implementaciones concretas en lugar de
        interfaces o abstracciones, y dependencias circulares.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de acoplamiento fuerte
        """
        findings = []
        
        lines = file_content.split('\n')
        imports = []
        
        for i, line in enumerate(lines, start=1):
            # Recolectar imports
            import_match = re.search(r'from\s+([\w.]+)\s+import', line)
            if import_match:
                module = import_match.group(1)
                imports.append((module, i))
        
        # Detectar imports cruzados entre capas
        is_api_file = '/api/' in file_path or '\\api\\' in file_path
        is_db_file = '/db/' in file_path or '\\db\\' in file_path
        
        for module, line_num in imports:
            # API importando directamente de DB (debería usar servicios)
            if is_api_file and '.db.' in module:
                findings.append(Finding(
                    id=f"arch_tight_coupling_{file_path}_{line_num}",
                    category="architecture",
                    subcategory="tight_coupling",
                    severity=Severity.MEDIO,
                    title="Acoplamiento fuerte entre capas",
                    description=f"El archivo de API en la línea {line_num} importa directamente de la capa de datos. "
                              f"Esto crea acoplamiento fuerte y dificulta el testing y mantenimiento.",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=f"from {module} import ...",
                    recommendation="Usar una capa de servicios intermedia para desacoplar API de la base de datos."
                ))
        
        return findings
    
    # ========== Métodos de análisis de Frontend ==========
    
    def check_component_separation(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica la separación entre componentes de UI y lógica de negocio.
        
        Identifica componentes que mezclan presentación con lógica de datos
        o cálculos complejos.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de falta de separación en componentes
        """
        findings = []
        
        # Solo analizar componentes
        if not re.search(r'(function|const)\s+[A-Z]\w+', file_content):
            return findings
        
        lines = file_content.split('\n')
        in_component = False
        component_start = 0
        component_name = ""
        has_business_logic = False
        
        for i, line in enumerate(lines, start=1):
            # Detectar inicio de componente (function o const con arrow function)
            component_match = re.search(r'(?:function|const)\s+([A-Z]\w+)', line)
            if component_match:
                in_component = True
                component_start = i
                component_name = component_match.group(1)
                has_business_logic = False
                continue
            
            # Detectar fin de componente (nueva función/const o cierre de función)
            if in_component and (re.search(r'^(?:function|const)\s+[A-Z]', line) or re.search(r'^\}', line)) and i > component_start + 1:
                # Evaluar si tiene lógica de negocio
                if has_business_logic:
                    findings.append(Finding(
                        id=f"arch_mixed_concerns_{file_path}_{component_start}",
                        category="architecture",
                        subcategory="component_separation",
                        severity=Severity.MEDIO,
                        title=f"Componente {component_name} mezcla UI y lógica de negocio",
                        description=f"El componente {component_name} en la línea {component_start} contiene "
                                  f"lógica de negocio mezclada con presentación. Esto dificulta el testing "
                                  f"y reutilización.",
                        file_path=file_path,
                        line_number=component_start,
                        recommendation="Extraer la lógica de negocio a hooks personalizados o servicios, "
                                     "dejando el componente enfocado solo en presentación."
                    ))
                in_component = False
            
            # Detectar lógica de negocio dentro del componente
            if in_component:
                # Cálculos complejos - múltiples operaciones encadenadas (misma línea)
                if re.search(r'\.(reduce|map|filter).*\.(reduce|map|filter)', line):
                    has_business_logic = True
                
                # Operaciones encadenadas en líneas separadas
                if re.search(r'\.(reduce|map|filter|sort|slice)\(', line):
                    # Contar cuántas operaciones hay en las siguientes líneas
                    chain_count = 1
                    for j in range(i, min(i + 10, len(lines))):
                        if re.search(r'\.(reduce|map|filter|sort|slice)\(', lines[j]):
                            chain_count += 1
                    if chain_count >= 2:
                        has_business_logic = True
                
                # Validaciones complejas (if con && y ||, o const con && y ||)
                if re.search(r'(if\s*\(|const\s+\w+\s*=).*&&.*\|\|', line):
                    has_business_logic = True
                
                # Validaciones complejas multilínea (const con && en una línea y || en siguiente)
                if re.search(r'const\s+\w+\s*=.*&&', line):
                    # Buscar || en las siguientes líneas
                    for j in range(i, min(i + 5, len(lines))):
                        if '||' in lines[j]:
                            has_business_logic = True
                            break
        
        # Evaluar último componente si el archivo termina
        if in_component and has_business_logic:
            findings.append(Finding(
                id=f"arch_mixed_concerns_{file_path}_{component_start}",
                category="architecture",
                subcategory="component_separation",
                severity=Severity.MEDIO,
                title=f"Componente {component_name} mezcla UI y lógica de negocio",
                description=f"El componente {component_name} en la línea {component_start} contiene "
                          f"lógica de negocio mezclada con presentación. Esto dificulta el testing "
                          f"y reutilización.",
                file_path=file_path,
                line_number=component_start,
                recommendation="Extraer la lógica de negocio a hooks personalizados o servicios, "
                             "dejando el componente enfocado solo en presentación."
            ))
        
        return findings
    
    def detect_api_calls_in_components(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Identifica llamadas API dispersas en componentes.
        
        Detecta componentes que realizan llamadas HTTP directamente en lugar
        de usar servicios centralizados.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de llamadas API dispersas
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar llamadas fetch directas
            if re.search(r'\bfetch\s*\(', line):
                findings.append(Finding(
                    id=f"arch_dispersed_api_call_{file_path}_{i}",
                    category="architecture",
                    subcategory="api_calls_in_components",
                    severity=Severity.MEDIO,
                    title="Llamada API directa en componente",
                    description=f"El componente en la línea {i} realiza una llamada API directa. "
                              f"Las llamadas API deben estar centralizadas en servicios para "
                              f"facilitar mantenimiento, testing y manejo de errores.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Crear un servicio API centralizado (ej: api/userService.ts) "
                                 "y usar ese servicio desde los componentes."
                ))
            
            # Buscar llamadas axios directas
            if re.search(r'axios\.(get|post|put|delete|patch)\(', line):
                findings.append(Finding(
                    id=f"arch_dispersed_api_call_{file_path}_{i}",
                    category="architecture",
                    subcategory="api_calls_in_components",
                    severity=Severity.MEDIO,
                    title="Llamada API directa en componente",
                    description=f"El componente en la línea {i} realiza una llamada API directa. "
                              f"Las llamadas API deben estar centralizadas en servicios para "
                              f"facilitar mantenimiento, testing y manejo de errores.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Crear un servicio API centralizado (ej: api/userService.ts) "
                                 "y usar ese servicio desde los componentes."
                ))
        
        return findings
    
    def check_state_management(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica el uso apropiado de Zustand para gestión de estado global.
        
        Identifica estado que debería ser global pero se maneja localmente,
        o viceversa.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de gestión de estado inapropiada
        """
        findings = []
        
        lines = file_content.split('\n')
        
        # Buscar múltiples useState con datos relacionados
        usestate_count = 0
        usestate_lines = []
        
        for i, line in enumerate(lines, start=1):
            if re.search(r'useState\s*\(', line):
                usestate_count += 1
                usestate_lines.append(i)
        
        # Si hay muchos useState en un componente, podría necesitar Zustand
        if usestate_count >= 5:
            findings.append(Finding(
                id=f"arch_excessive_local_state_{file_path}_{usestate_lines[0]}",
                category="architecture",
                subcategory="state_management",
                severity=Severity.BAJO,
                title="Exceso de estado local en componente",
                description=f"El componente tiene {usestate_count} llamadas a useState. "
                          f"Considerar si parte de este estado local debería ser global usando Zustand.",
                file_path=file_path,
                line_number=usestate_lines[0],
                recommendation="Evaluar si el estado es compartido entre componentes. "
                             "Si es así, moverlo a un store de Zustand."
            ))
        
        return findings
    
    def check_context_usage(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica el uso apropiado de Context API vs estado local.
        
        Identifica uso excesivo de Context para estado que debería ser local,
        o falta de Context para estado compartido.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de uso inapropiado de Context
        """
        findings = []
        
        lines = file_content.split('\n')
        
        # Buscar createContext con valores simples
        for i, line in enumerate(lines, start=1):
            if re.search(r'createContext\s*\(', line):
                # Verificar si el contexto es para un valor simple
                if re.search(r'createContext\s*\(\s*(?:null|undefined|false|true|0|"")\s*\)', line):
                    findings.append(Finding(
                        id=f"arch_simple_context_{file_path}_{i}",
                        category="architecture",
                        subcategory="context_usage",
                        severity=Severity.BAJO,
                        title="Context API para valor simple",
                        description=f"El Context en la línea {i} se usa para un valor simple. "
                                  f"Context API es mejor para estado complejo compartido. "
                                  f"Para valores simples, considerar props o estado local.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Evaluar si el valor realmente necesita Context. "
                                     "Para estado simple, usar props drilling o Zustand."
                    ))
        
        return findings
    
    # ========== Métodos de análisis de API Contract ==========
    
    def check_openapi_documentation(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica la existencia de documentación OpenAPI para endpoints.
        
        Identifica endpoints sin docstrings o sin schemas de respuesta definidos.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de falta de documentación
        """
        findings = []
        
        # Solo analizar archivos de API
        if '/api/' not in file_path and '\\api\\' not in file_path:
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar definiciones de endpoints
            if re.search(r'@\w+\.(get|post|put|delete|patch)\(', line):
                # Verificar si tiene docstring en las siguientes líneas
                has_docstring = False
                has_response_model = False
                
                # Revisar las siguientes 10 líneas
                for j in range(i, min(i + 10, len(lines))):
                    if '"""' in lines[j] or "'''" in lines[j]:
                        has_docstring = True
                    if 'response_model' in lines[j]:
                        has_response_model = True
                
                if not has_docstring:
                    findings.append(Finding(
                        id=f"arch_missing_docs_{file_path}_{i}",
                        category="architecture",
                        subcategory="openapi_documentation",
                        severity=Severity.BAJO,
                        title="Endpoint sin documentación",
                        description=f"El endpoint en la línea {i} no tiene docstring. "
                                  f"La documentación es esencial para generar OpenAPI correctamente.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar docstring al endpoint describiendo su propósito, "
                                     "parámetros y respuestas."
                    ))
        
        return findings
    
    def check_http_verb_consistency(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica el uso consistente de verbos HTTP.
        
        Identifica endpoints que usan verbos HTTP incorrectos para su operación
        (ej: GET para operaciones que modifican datos).
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de uso inconsistente de verbos HTTP
        """
        findings = []
        
        # Solo analizar archivos de API
        if '/api/' not in file_path and '\\api\\' not in file_path:
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar GET endpoints que modifican datos
            if re.search(r'@\w+\.get\(', line):
                # Revisar el cuerpo de la función (siguientes 30 líneas)
                # i es 1-indexed, pero lines es 0-indexed, así que usamos i-1
                for j in range(i - 1, min(i - 1 + 30, len(lines))):
                    # Si hace operaciones de escritura, es incorrecto
                    if re.search(r'session\.(add|delete|update|commit)', lines[j]):
                        findings.append(Finding(
                            id=f"arch_wrong_http_verb_{file_path}_{i}",
                            category="architecture",
                            subcategory="http_verb_consistency",
                            severity=Severity.MEDIO,
                            title="Verbo HTTP incorrecto para operación",
                            description=f"El endpoint GET en la línea {i} realiza operaciones de escritura. "
                                      f"GET debe ser idempotente y solo para lectura.",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            recommendation="Usar POST para crear, PUT/PATCH para actualizar, DELETE para eliminar. "
                                         "GET solo para operaciones de lectura."
                        ))
                        break
        
        return findings
    
    def check_error_response_format(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica el formato consistente de respuestas de error.
        
        Identifica endpoints que retornan errores en formatos inconsistentes.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de formato inconsistente de errores
        """
        findings = []
        
        # Solo analizar archivos de API
        if '/api/' not in file_path and '\\api\\' not in file_path:
            return findings
        
        lines = file_content.split('\n')
        error_formats = []
        
        for i, line in enumerate(lines, start=1):
            # Buscar raises de HTTPException
            if re.search(r'raise\s+HTTPException\(', line):
                # Extraer el formato del error
                error_formats.append((i, line.strip()))
        
        # Si hay múltiples formatos diferentes, reportar
        if len(error_formats) > 1:
            # Verificar si todos tienen 'detail'
            all_have_detail = all('detail=' in fmt[1] for fmt in error_formats)
            
            if not all_have_detail:
                findings.append(Finding(
                    id=f"arch_inconsistent_error_format_{file_path}",
                    category="architecture",
                    subcategory="error_response_format",
                    severity=Severity.BAJO,
                    title="Formato inconsistente de respuestas de error",
                    description=f"El archivo tiene múltiples formatos de error. "
                              f"Todas las respuestas de error deben seguir el mismo formato.",
                    file_path=file_path,
                    line_number=error_formats[0][0],
                    recommendation="Estandarizar el formato de error usando siempre 'detail' "
                                 "y opcionalmente 'code' para errores específicos."
                ))
        
        return findings
    
    def check_http_status_codes(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica el uso consistente de códigos de estado HTTP.
        
        Identifica endpoints que usan códigos de estado incorrectos o inconsistentes.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de uso inconsistente de códigos HTTP
        """
        findings = []
        
        # Solo analizar archivos de API
        if '/api/' not in file_path and '\\api\\' not in file_path:
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar POST endpoints
            if re.search(r'@\w+\.post\(', line):
                # Verificar si tiene status_code=201 en la misma línea o siguientes
                has_201 = False
                
                # Revisar la línea actual y las siguientes 5 líneas
                for j in range(i - 1, min(i + 5, len(lines))):
                    if j >= 0 and j < len(lines):
                        if re.search(r'status_code\s*=\s*201', lines[j]):
                            has_201 = True
                            break
                
                if not has_201:
                    findings.append(Finding(
                        id=f"arch_missing_201_status_{file_path}_{i}",
                        category="architecture",
                        subcategory="http_status_codes",
                        severity=Severity.BAJO,
                        title="Endpoint POST sin status code 201",
                        description=f"El endpoint POST en la línea {i} no especifica status_code=201. "
                                  f"Los endpoints de creación deben retornar 201 Created.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar status_code=201 al decorador del endpoint POST."
                    ))
        
        return findings
