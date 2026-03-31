"""
Analizador de performance para Backend y Frontend.

Este módulo contiene la clase base PerformanceAnalyzer que identifica problemas
de rendimiento en código Python (Backend) y TypeScript/React (Frontend).
"""

import re
from typing import List, Optional
from audit_system.models import Finding, Severity, SourceFile
from audit_system.config import get_config


class PerformanceAnalyzer:
    """
    Analizador de performance para Backend y Frontend.
    
    Identifica patrones que afectan el rendimiento:
    - Backend: N+1 queries, falta de paginación, operaciones bloqueantes
    - Frontend: re-renders innecesarios, useEffect sin dependencias
    """
    
    def __init__(self):
        """Inicializa el analizador con configuración."""
        self.config = get_config()
    
    def analyze(self, files: List[SourceFile]) -> List[Finding]:
        """
        Analiza una lista de archivos y retorna hallazgos de performance.
        
        Args:
            files: Lista de archivos de código fuente a analizar
            
        Returns:
            Lista de hallazgos de performance detectados
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
        Analiza un archivo Python para problemas de performance.
        
        Args:
            file: Archivo Python a analizar
            
        Returns:
            Lista de hallazgos de performance en el archivo
        """
        findings = []
        
        # Detectar patrones N+1
        findings.extend(self.detect_n_plus_one(file.content, file.path))
        
        # Verificar paginación en endpoints
        findings.extend(self.check_pagination(file.content, file.path))
        
        # Detectar operaciones bloqueantes en rutas async
        findings.extend(self.detect_blocking_operations(file.content, file.path))
        
        # Verificar configuración de connection pooling
        findings.extend(self.check_connection_pooling(file.content, file.path))
        
        # Detectar índices faltantes en modelos
        findings.extend(self.detect_missing_indexes(file.content, file.path))
        
        return findings
    
    def _analyze_frontend_file(self, file: SourceFile) -> List[Finding]:
        """
        Analiza un archivo TypeScript/React para problemas de performance.
        
        Args:
            file: Archivo TypeScript a analizar
            
        Returns:
            Lista de hallazgos de performance en el archivo
        """
        findings = []
        
        # Detectar re-renders innecesarios
        findings.extend(self.detect_unnecessary_rerenders(file.content, file.path))
        
        # Verificar dependencias de useEffect
        findings.extend(self.check_useeffect_deps(file.content, file.path))
        
        # Verificar lazy loading de rutas
        findings.extend(self.check_lazy_loading(file.content, file.path))
        
        # Detectar imports de librerías completas
        findings.extend(self.detect_full_library_imports(file.content, file.path))
        
        return findings
    
    # ========== Métodos de análisis de Backend ==========
    
    def detect_n_plus_one(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta patrones N+1 en queries de base de datos.
        
        Identifica código donde se ejecuta una query dentro de un loop,
        lo que resulta en N+1 queries en lugar de una sola query optimizada.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de patrones N+1 detectados
        """
        findings = []
        
        # Patrón: loop seguido de query dentro del loop
        # Buscar: for/while + query/filter dentro
        pattern = r'for\s+\w+\s+in\s+.*?:\s*\n.*?(?:query|filter|get)\('
        
        lines = file_content.split('\n')
        for i, line in enumerate(lines, start=1):
            # Buscar loops
            if re.search(r'^\s*for\s+\w+\s+in\s+', line):
                # Verificar si hay queries en las siguientes líneas (dentro del loop)
                indent = len(line) - len(line.lstrip())
                for j in range(i, min(i + 10, len(lines))):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # Si la indentación es menor o igual, salimos del loop
                    if next_indent <= indent and j > i:
                        break
                    
                    # Buscar queries dentro del loop
                    if re.search(r'\.(?:query|filter|get)\(', next_line):
                        findings.append(Finding(
                            id=f"perf_n_plus_one_{file_path}_{i}",
                            category="performance",
                            subcategory="n_plus_one",
                            severity=Severity.ALTO,
                            title="Patrón N+1 detectado en query de base de datos",
                            description=f"Se detectó una query dentro de un loop en la línea {i}, "
                                      f"lo que puede resultar en múltiples queries a la base de datos. "
                                      f"Esto afecta significativamente el rendimiento.",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            recommendation="Usar eager loading (joinedload, selectinload) o una sola "
                                         "query con JOIN para obtener todos los datos necesarios."
                        ))
                        break
        
        return findings
    
    def check_pagination(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica la existencia de paginación en endpoints que retornan colecciones.
        
        Identifica endpoints que retornan listas sin implementar paginación,
        lo que puede causar problemas de rendimiento con grandes volúmenes de datos.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de falta de paginación
        """
        findings = []
        
        # Buscar endpoints que retornan listas sin paginación
        # Patrón: @router.get + return List[...] sin limit/offset
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar definiciones de endpoints GET
            if re.search(r'@\w+\.get\(', line):
                # Buscar la función correspondiente
                func_start = i
                func_content = []
                
                # Recolectar contenido de la función
                for j in range(i, min(i + 50, len(lines))):
                    func_content.append(lines[j])
                    
                    # Si encontramos otra definición de función, terminamos
                    if j > i and re.search(r'^@\w+\.\w+\(', lines[j]):
                        break
                
                func_text = '\n'.join(func_content)
                
                # Verificar si retorna una lista/colección
                returns_list = bool(re.search(r'List\[|list\[', func_text))
                
                # Verificar si tiene paginación
                has_pagination = bool(re.search(r'limit|offset|skip|page|per_page', func_text, re.IGNORECASE))
                
                if returns_list and not has_pagination:
                    findings.append(Finding(
                        id=f"perf_no_pagination_{file_path}_{func_start}",
                        category="performance",
                        subcategory="no_pagination",
                        severity=Severity.MEDIO,
                        title="Endpoint sin paginación retorna colección",
                        description=f"El endpoint en la línea {func_start} retorna una colección "
                                  f"sin implementar paginación. Esto puede causar problemas de "
                                  f"rendimiento con grandes volúmenes de datos.",
                        file_path=file_path,
                        line_number=func_start,
                        code_snippet=line.strip(),
                        recommendation="Implementar paginación usando parámetros limit y offset, "
                                     "o usar skip y limit de SQLAlchemy."
                    ))
        
        return findings
    
    def detect_blocking_operations(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Identifica operaciones bloqueantes síncronas en rutas async de FastAPI.
        
        Detecta operaciones de I/O síncronas (lectura de archivos, requests HTTP)
        dentro de funciones async, lo que bloquea el event loop.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de operaciones bloqueantes
        """
        findings = []
        
        lines = file_content.split('\n')
        in_async_function = False
        async_func_line = 0
        
        for i, line in enumerate(lines, start=1):
            # Detectar inicio de función async
            if re.search(r'^\s*async\s+def\s+', line):
                in_async_function = True
                async_func_line = i
                continue
            
            # Detectar fin de función (nueva definición o des-indentación)
            if in_async_function and re.search(r'^(async\s+)?def\s+', line):
                in_async_function = False
                continue
            
            # Buscar operaciones bloqueantes dentro de funciones async
            if in_async_function:
                # Operaciones de archivo síncronas
                if re.search(r'\bopen\(|\.read\(|\.write\(', line) and not re.search(r'await', line):
                    findings.append(Finding(
                        id=f"perf_blocking_io_{file_path}_{i}",
                        category="performance",
                        subcategory="blocking_operation",
                        severity=Severity.MEDIO,
                        title="Operación de I/O bloqueante en función async",
                        description=f"Se detectó una operación de I/O síncrona en la línea {i} "
                                  f"dentro de una función async (definida en línea {async_func_line}). "
                                  f"Esto bloquea el event loop y afecta el rendimiento.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Usar operaciones async (aiofiles para archivos, httpx para HTTP) "
                                     "o ejecutar operaciones bloqueantes en un thread pool con run_in_executor."
                    ))
                
                # Requests HTTP síncronos
                if re.search(r'requests\.(get|post|put|delete|patch)', line) and not re.search(r'await', line):
                    findings.append(Finding(
                        id=f"perf_blocking_http_{file_path}_{i}",
                        category="performance",
                        subcategory="blocking_operation",
                        severity=Severity.MEDIO,
                        title="Request HTTP síncrono en función async",
                        description=f"Se detectó un request HTTP síncrono (requests library) en la línea {i} "
                                  f"dentro de una función async. Esto bloquea el event loop.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Usar httpx.AsyncClient o aiohttp para requests HTTP asíncronos."
                    ))
        
        return findings
    
    def check_connection_pooling(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que las conexiones a base de datos usen connection pooling.
        
        Identifica configuraciones de base de datos sin pool_size o pool_recycle,
        lo que puede causar problemas de rendimiento con múltiples conexiones.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de configuración de connection pooling
        """
        findings = []
        
        # Solo analizar archivos de configuración de DB
        if 'database' not in file_path.lower() and 'db' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar creación de engine de SQLAlchemy
            if re.search(r'create_engine\s*\(', line):
                # Recolectar la llamada completa (puede ser multilínea)
                engine_lines = [line]
                paren_count = line.count('(') - line.count(')')
                
                j = i
                while j < len(lines) and paren_count > 0:
                    j += 1
                    if j < len(lines):
                        next_line = lines[j]
                        engine_lines.append(next_line)
                        paren_count += next_line.count('(') - next_line.count(')')
                
                engine_text = '\n'.join(engine_lines)
                
                # Verificar si tiene configuración de pooling
                has_pool_size = bool(re.search(r'pool_size\s*=', engine_text))
                has_pool_recycle = bool(re.search(r'pool_recycle\s*=', engine_text))
                has_max_overflow = bool(re.search(r'max_overflow\s*=', engine_text))
                
                if not (has_pool_size or has_pool_recycle or has_max_overflow):
                    findings.append(Finding(
                        id=f"perf_no_connection_pool_{file_path}_{i}",
                        category="performance",
                        subcategory="connection_pooling",
                        severity=Severity.MEDIO,
                        title="Configuración de connection pooling faltante",
                        description=f"El create_engine en la línea {i} no especifica configuración "
                                  f"de connection pooling (pool_size, pool_recycle, max_overflow). "
                                  f"Esto puede causar problemas de rendimiento con múltiples conexiones.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar configuración de pooling: pool_size=20, "
                                     "max_overflow=10, pool_recycle=3600"
                    ))
        
        return findings
    
    def detect_missing_indexes(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta columnas que deberían tener índices pero no los tienen.
        
        Identifica columnas usadas en foreign keys o queries frecuentes sin índices,
        lo que puede causar queries lentas.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de índices faltantes
        """
        findings = []
        
        # Solo analizar archivos de modelos
        if 'models' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar ForeignKey sin index
            if re.search(r'ForeignKey\s*\(', line):
                # Verificar si la columna tiene index=True
                has_index = bool(re.search(r'index\s*=\s*True', line))
                
                if not has_index:
                    findings.append(Finding(
                        id=f"perf_missing_fk_index_{file_path}_{i}",
                        category="performance",
                        subcategory="missing_index",
                        severity=Severity.MEDIO,
                        title="ForeignKey sin índice",
                        description=f"La columna ForeignKey en la línea {i} no tiene índice. "
                                  f"Las foreign keys son usadas frecuentemente en JOINs y "
                                  f"deberían tener índices para mejorar el rendimiento.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar index=True a la definición de la columna ForeignKey."
                    ))
            
            # Buscar columnas con unique=True sin index explícito
            # (unique ya crea un índice, pero es bueno ser explícito)
            if re.search(r'unique\s*=\s*True', line) and 'Column' in line:
                has_index = bool(re.search(r'index\s*=\s*True', line))
                
                # Esto es informativo, no crítico (unique ya crea índice)
                if not has_index:
                    # No reportar como finding, unique ya crea índice automáticamente
                    pass
        
        return findings
    
    # ========== Métodos de análisis de Frontend ==========
    
    def detect_unnecessary_rerenders(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Identifica componentes React sin memoización apropiada.
        
        Detecta componentes que podrían beneficiarse de React.memo, useMemo o useCallback
        para evitar re-renders innecesarios.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de re-renders innecesarios
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar definiciones de componentes funcionales
            component_match = re.search(r'(?:function|const)\s+([A-Z]\w+)\s*(?:=\s*)?(?:\([^)]*\))?\s*(?:=>)?\s*\{', line)
            
            if component_match:
                component_name = component_match.group(1)
                
                # Verificar si el componente usa React.memo
                has_memo = False
                for j in range(max(0, i - 5), min(i + 5, len(lines))):
                    if re.search(r'React\.memo|memo\(', lines[j]):
                        has_memo = True
                        break
                
                # Verificar si el componente tiene props
                has_props = bool(re.search(r'\([^)]*\w+[^)]*\)', line))
                
                # Si tiene props y no usa memo, podría beneficiarse
                if has_props and not has_memo:
                    findings.append(Finding(
                        id=f"perf_no_memo_{file_path}_{i}",
                        category="performance",
                        subcategory="unnecessary_rerender",
                        severity=Severity.BAJO,
                        title=f"Componente {component_name} sin memoización",
                        description=f"El componente {component_name} en la línea {i} recibe props "
                                  f"pero no usa React.memo. Esto puede causar re-renders innecesarios "
                                  f"cuando el componente padre se re-renderiza.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation=f"Envolver el componente con React.memo: "
                                     f"export default React.memo({component_name})"
                    ))
        
        return findings
    
    def check_useeffect_deps(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica arrays de dependencias en useEffect hooks.
        
        Identifica useEffect hooks sin array de dependencias o con dependencias
        incorrectas, lo que puede causar loops infinitos o efectos que no se ejecutan.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de useEffect con dependencias incorrectas
        """
        findings = []
        
        lines = file_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Buscar useEffect
            if re.search(r'useEffect\s*\(', line):
                # Recolectar el useEffect completo (puede ser multilínea)
                effect_lines = [line]
                paren_count = line.count('(') - line.count(')')
                brace_count = line.count('{') - line.count('}')
                
                j = i + 1
                # Continuar hasta cerrar todos los paréntesis y llaves
                while j < len(lines) and (paren_count > 0 or brace_count > 0):
                    next_line = lines[j]
                    effect_lines.append(next_line)
                    paren_count += next_line.count('(') - next_line.count(')')
                    brace_count += next_line.count('{') - next_line.count('}')
                    j += 1
                
                effect_text = '\n'.join(effect_lines)
                
                # Verificar si tiene array de dependencias
                # Buscar patrón: }, [...]); o });
                has_deps_array = bool(re.search(r'\}\s*,\s*\[', effect_text))
                
                # Verificar si el array está vacío
                empty_deps = bool(re.search(r'\}\s*,\s*\[\s*\]\s*\)', effect_text))
                
                if not has_deps_array:
                    findings.append(Finding(
                        id=f"perf_useeffect_no_deps_{file_path}_{i+1}",
                        category="performance",
                        subcategory="useeffect_deps",
                        severity=Severity.MEDIO,
                        title="useEffect sin array de dependencias",
                        description=f"El useEffect en la línea {i+1} no tiene array de dependencias. "
                                  f"Esto causa que el efecto se ejecute después de cada render, "
                                  f"lo que puede afectar el rendimiento.",
                        file_path=file_path,
                        line_number=i+1,
                        code_snippet=line.strip(),
                        recommendation="Agregar array de dependencias al useEffect. Si el efecto debe "
                                     "ejecutarse solo una vez, usar array vacío []."
                    ))
                elif empty_deps:
                    # Verificar si usa variables externas (posible dependencia faltante)
                    # Esto es una heurística simple
                    if re.search(r'(?:state|props|\w+\.\w+)', effect_text):
                        findings.append(Finding(
                            id=f"perf_useeffect_missing_deps_{file_path}_{i+1}",
                            category="performance",
                            subcategory="useeffect_deps",
                            severity=Severity.BAJO,
                            title="useEffect con posibles dependencias faltantes",
                            description=f"El useEffect en la línea {i+1} tiene array de dependencias vacío "
                                      f"pero parece usar variables externas. Esto puede causar bugs "
                                      f"donde el efecto no se actualiza cuando debería.",
                            file_path=file_path,
                            line_number=i+1,
                            code_snippet=line.strip(),
                            recommendation="Revisar si todas las variables usadas en el efecto están "
                                         "incluidas en el array de dependencias."
                        ))
            
            i += 1
        
        return findings

    
    def check_lazy_loading(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica el uso de lazy loading para rutas y componentes grandes.
        
        Identifica rutas o componentes que deberían usar React.lazy() para
        code splitting y mejorar el tiempo de carga inicial.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de falta de lazy loading
        """
        findings = []
        
        # Solo analizar archivos de rutas/routing
        if 'route' not in file_path.lower() and 'router' not in file_path.lower() and 'app' not in file_path.lower():
            return findings
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar imports directos de componentes en archivos de rutas
            # Patrón: import Component from './path'
            import_match = re.search(r'import\s+([A-Z]\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', line)
            
            if import_match:
                component_name = import_match.group(1)
                import_path = import_match.group(2)
                
                # Verificar si es un componente de página/vista (no un componente pequeño)
                is_page_component = any(keyword in import_path.lower() for keyword in ['page', 'view', 'screen', 'container'])
                
                # Verificar si ya usa lazy loading
                has_lazy = False
                for j in range(max(0, i - 3), min(i + 3, len(lines))):
                    if re.search(r'React\.lazy|lazy\(', lines[j]):
                        has_lazy = True
                        break
                
                # Si es un componente de página y no usa lazy, reportar
                if is_page_component and not has_lazy:
                    findings.append(Finding(
                        id=f"perf_no_lazy_loading_{file_path}_{i}",
                        category="performance",
                        subcategory="no_lazy_loading",
                        severity=Severity.BAJO,
                        title=f"Componente {component_name} sin lazy loading",
                        description=f"El componente de página {component_name} en la línea {i} "
                                  f"se importa directamente sin lazy loading. Esto aumenta el "
                                  f"tamaño del bundle inicial y afecta el tiempo de carga.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation=f"Usar React.lazy para cargar el componente bajo demanda: "
                                     f"const {component_name} = React.lazy(() => import('{import_path}'))"
                    ))
        
        return findings
    
    def detect_full_library_imports(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Detecta imports de librerías completas sin tree-shaking.
        
        Identifica imports que cargan librerías completas en lugar de
        importar solo las funciones necesarias, aumentando el bundle size.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de imports ineficientes
        """
        findings = []
        
        # Librerías conocidas que soportan tree-shaking
        tree_shakeable_libs = {
            'lodash': 'lodash/[function]',
            'date-fns': 'date-fns/[function]',
            'ramda': 'ramda/src/[function]',
            'rxjs': 'rxjs/operators',
            '@mui/material': '@mui/material/[Component]',
            '@mui/icons-material': '@mui/icons-material/[Icon]'
        }
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar imports de librerías completas
            # Patrón: import _ from 'lodash' o import * as _ from 'lodash'
            for lib, recommendation in tree_shakeable_libs.items():
                # Import default de librería completa
                if re.search(rf'import\s+\w+\s+from\s+[\'\"]{lib}[\'\"]', line):
                    findings.append(Finding(
                        id=f"perf_full_lib_import_{file_path}_{i}",
                        category="performance",
                        subcategory="full_library_import",
                        severity=Severity.MEDIO,
                        title=f"Import completo de {lib} sin tree-shaking",
                        description=f"El import en la línea {i} carga toda la librería {lib}, "
                                  f"lo que aumenta significativamente el tamaño del bundle. "
                                  f"Solo se deberían importar las funciones necesarias.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation=f"Importar funciones específicas: import {{ function }} from '{recommendation}'"
                    ))
                
                # Import namespace de librería completa
                elif re.search(rf'import\s+\*\s+as\s+\w+\s+from\s+[\'\"]{lib}[\'\"]', line):
                    findings.append(Finding(
                        id=f"perf_namespace_import_{file_path}_{i}",
                        category="performance",
                        subcategory="full_library_import",
                        severity=Severity.MEDIO,
                        title=f"Import namespace de {lib} sin tree-shaking",
                        description=f"El import namespace en la línea {i} puede incluir toda la librería {lib}. "
                                  f"Es mejor importar solo las funciones necesarias.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation=f"Importar funciones específicas: import {{ function }} from '{recommendation}'"
                    ))
        
        return findings
