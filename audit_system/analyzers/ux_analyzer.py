"""
Analizador de UX para Frontend.

Este módulo contiene la clase UXAnalyzer que identifica problemas
de experiencia de usuario en código TypeScript/React (Frontend).
"""

import re
from typing import List
from audit_system.models import Finding, Severity, SourceFile
from audit_system.config import get_config


class UXAnalyzer:
    """
    Analizador de UX para Frontend.
    
    Identifica patrones que afectan la experiencia de usuario:
    - Estados de carga faltantes
    - Manejo de errores inadecuado
    - Estados vacíos sin feedback
    - Validación de formularios faltante
    """
    
    def __init__(self):
        """Inicializa el analizador con configuración."""
        self.config = get_config()
    
    def analyze(self, files: List[SourceFile]) -> List[Finding]:
        """
        Analiza una lista de archivos y retorna hallazgos de UX.
        
        Args:
            files: Lista de archivos de código fuente a analizar
            
        Returns:
            Lista de hallazgos de UX detectados
        """
        findings = []
        
        for file in files:
            if file.language == "typescript":
                findings.extend(self._analyze_frontend_file(file))
        
        return findings
    
    def _analyze_frontend_file(self, file: SourceFile) -> List[Finding]:
        """
        Analiza un archivo TypeScript/React para problemas de UX.
        
        Args:
            file: Archivo TypeScript a analizar
            
        Returns:
            Lista de hallazgos de UX en el archivo
        """
        findings = []
        
        # Verificar estados de carga
        findings.extend(self.check_loading_states(file.content, file.path))
        
        # Verificar manejo de errores
        findings.extend(self.check_error_states(file.content, file.path))
        
        # Verificar estados vacíos
        findings.extend(self.check_empty_states(file.content, file.path))
        
        # Verificar validación de formularios
        findings.extend(self.check_form_validation(file.content, file.path))
        
        return findings
    
    def check_loading_states(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que las operaciones asíncronas muestren estados de carga.
        
        Identifica llamadas a APIs o useEffect con operaciones async sin
        indicadores de carga apropiados.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de estados de carga faltantes
        """
        findings = []
        
        lines = file_content.split('\n')
        
        # Buscar operaciones async (fetch, axios, etc.)
        for i, line in enumerate(lines, start=1):
            # Detectar llamadas a APIs
            has_api_call = bool(re.search(r'(fetch|axios\.(get|post|put|delete)|api\.)', line))
            
            if has_api_call:
                # Verificar si hay estado de loading en el archivo
                has_loading_state = bool(re.search(r'(isLoading|loading|isLoading)', file_content))
                
                if not has_loading_state:
                    findings.append(Finding(
                        id=f"ux_no_loading_state_{file_path}_{i}",
                        category="ux",
                        subcategory="no_loading_state",
                        severity=Severity.MEDIO,
                        title="Operación asíncrona sin estado de carga",
                        description=f"La llamada a API en la línea {i} no tiene un estado de carga visible. "
                                  f"Los usuarios no reciben feedback mientras esperan la respuesta.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar estado de loading: const [isLoading, setIsLoading] = useState(false) "
                                     "y mostrar un spinner o skeleton mientras carga."
                    ))
                    break  # Solo reportar una vez por archivo
        
        return findings
    
    def check_error_states(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que los errores se muestren al usuario apropiadamente.
        
        Identifica try-catch o .catch() sin mostrar mensajes de error al usuario.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de manejo de errores inadecuado
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar bloques catch
            if re.search(r'catch\s*\(', line):
                # Recolectar el bloque catch (siguiente 10 líneas)
                catch_lines = []
                for j in range(i - 1, min(i + 10, len(lines))):
                    catch_lines.append(lines[j])
                
                catch_text = '\n'.join(catch_lines)
                
                # Verificar si muestra el error al usuario (excluir console.log)
                shows_error = bool(re.search(r'(setError|toast\.|alert\(|notification|message\.error)', catch_text))
                
                # Verificar si solo tiene console.log (no es suficiente para UX)
                only_console = bool(re.search(r'console\.log', catch_text)) and not shows_error
                
                if not shows_error or only_console:
                    findings.append(Finding(
                        id=f"ux_no_error_display_{file_path}_{i}",
                        category="ux",
                        subcategory="no_error_display",
                        severity=Severity.MEDIO,
                        title="Error capturado sin mostrar al usuario",
                        description=f"El bloque catch en la línea {i} captura errores pero no los muestra "
                                  f"al usuario. Los usuarios no sabrán que algo falló.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar estado de error: const [error, setError] = useState(null) "
                                     "y mostrar mensaje de error al usuario con toast o alert."
                    ))
        
        return findings
    
    def check_empty_states(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que las listas vacías muestren mensajes apropiados.
        
        Identifica renderizado de listas sin manejo de estado vacío.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de estados vacíos sin feedback
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar .map() para renderizar listas
            if re.search(r'\.map\s*\(', line):
                # Verificar si hay manejo de estado vacío cerca
                has_empty_check = False
                
                # Buscar en líneas anteriores
                for j in range(max(0, i - 10), i):
                    if re.search(r'(length\s*===\s*0|\.length\s*<\s*1|isEmpty|!.*\.length)', lines[j]):
                        has_empty_check = True
                        break
                
                if not has_empty_check:
                    findings.append(Finding(
                        id=f"ux_no_empty_state_{file_path}_{i}",
                        category="ux",
                        subcategory="no_empty_state",
                        severity=Severity.BAJO,
                        title="Lista sin manejo de estado vacío",
                        description=f"El renderizado de lista en la línea {i} no maneja el caso de lista vacía. "
                                  f"Los usuarios verán una pantalla en blanco si no hay datos.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Agregar verificación: {items.length === 0 ? <EmptyState /> : items.map(...)}"
                    ))
        
        return findings
    
    def check_form_validation(self, file_content: str, file_path: str) -> List[Finding]:
        """
        Verifica que los formularios tengan validación apropiada.
        
        Identifica formularios sin validación de campos o feedback de errores.
        
        Args:
            file_content: Contenido del archivo a analizar
            file_path: Ruta del archivo
            
        Returns:
            Lista de hallazgos de validación de formularios faltante
        """
        findings = []
        
        lines = file_content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Buscar elementos <form> o onSubmit
            if re.search(r'<form|onSubmit\s*=', line):
                # Verificar si usa librería de validación (buscar z. para zod)
                has_validation = bool(re.search(r'(useForm|Formik|yup|react-hook-form|validation|z\.object|z\.string)', file_content, re.IGNORECASE))
                
                if not has_validation:
                    findings.append(Finding(
                        id=f"ux_no_form_validation_{file_path}_{i}",
                        category="ux",
                        subcategory="no_form_validation",
                        severity=Severity.MEDIO,
                        title="Formulario sin validación",
                        description=f"El formulario en la línea {i} no usa una librería de validación. "
                                  f"Los usuarios pueden enviar datos inválidos sin feedback apropiado.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Usar react-hook-form con yup/zod para validación: "
                                     "const { register, handleSubmit, formState: { errors } } = useForm()"
                    ))
                    break  # Solo reportar una vez por archivo
        
        return findings
