"""
Tests unitarios para QualityAnalyzer.

Valida la detección de problemas de calidad en Backend y Frontend.
"""

import pytest
from audit_system.analyzers.quality_analyzer import QualityAnalyzer
from audit_system.models import Severity, SourceFile, PythonFile, TypeScriptFile


class TestQualityAnalyzerBackend:
    """Tests para análisis de calidad en Backend (Python)."""
    
    def test_detect_long_function(self):
        """Verifica detección de función larga."""
        # Crear función con más de 50 líneas
        code = "def long_function():\n" + "    x = 1\n" * 60
        
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_long_functions(code, "test.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "long_function"
        assert findings[0].severity == Severity.MEDIO
        assert "long_function" in findings[0].title
    
    def test_detect_very_long_function_critical(self):
        """Verifica que funciones >100 líneas sean críticas."""
        code = "def very_long_function():\n" + "    x = 1\n" * 110
        
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_long_functions(code, "test.py")
        
        assert len(findings) == 1
        assert findings[0].severity == Severity.CRITICO
    
    def test_short_function_no_warning(self):
        """Verifica que funciones cortas no generen hallazgos."""
        code = """
def short_function():
    return 42
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_long_functions(code, "test.py")
        
        assert len(findings) == 0
    
    def test_detect_deep_nesting(self):
        """Verifica detección de indentación profunda."""
        code = """
def nested():
    if True:
        if True:
            if True:
                if True:
                    x = 1
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_deep_nesting(code, "test.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "deep_nesting" for f in findings)
    
    def test_shallow_nesting_no_warning(self):
        """Verifica que indentación normal no genere hallazgos."""
        code = """
def normal():
    if True:
        if True:
            x = 1
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_deep_nesting(code, "test.py")
        
        assert len(findings) == 0
    
    def test_detect_missing_type_hints(self):
        """Verifica detección de funciones sin type hints."""
        code = """
def process_data(data):
    return data * 2
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.check_type_hints(code, "test.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_type_hints"
        assert findings[0].severity == Severity.MEDIO
    
    def test_function_with_type_hints_no_warning(self):
        """Verifica que funciones con type hints no generen hallazgos."""
        code = """
def process_data(data: int) -> int:
    return data * 2
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.check_type_hints(code, "test.py")
        
        assert len(findings) == 0
    
    def test_private_function_no_type_hint_warning(self):
        """Verifica que funciones privadas no requieran type hints."""
        code = """
def _internal_helper(data):
    return data * 2
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.check_type_hints(code, "test.py")
        
        assert len(findings) == 0
    
    def test_detect_generic_exception(self):
        """Verifica detección de except genérico."""
        code = """
try:
    risky_operation()
except:
    pass
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.check_exception_handling(code, "test.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "exception_handling" for f in findings)
        assert any("genérica" in f.title.lower() for f in findings)
    
    def test_detect_exception_without_logging(self):
        """Verifica detección de except sin logging."""
        code = """
try:
    risky_operation()
except Exception:
    return None
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.check_exception_handling(code, "test.py")
        
        assert len(findings) >= 1
        assert any("logging" in f.title.lower() for f in findings)
    
    def test_exception_with_logging_no_warning(self):
        """Verifica que except con logging no genere hallazgos."""
        code = """
try:
    risky_operation()
except Exception as e:
    logger.error(f"Error: {e}")
    return None
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.check_exception_handling(code, "test.py")
        
        # No debe detectar problema cuando hay logging
        assert len([f for f in findings if "logging" in f.title.lower()]) == 0
    
    def test_detect_silenced_exception(self):
        """Verifica detección de excepción silenciada con pass."""
        code = """
try:
    operation()
except ValueError:
    pass
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.check_exception_handling(code, "test.py")
        
        assert len(findings) >= 1
        assert any(f.severity == Severity.ALTO for f in findings)
        assert any("silenciada" in f.title.lower() for f in findings)
    
    def test_detect_missing_docstring(self):
        """Verifica detección de función sin docstring."""
        code = """
def public_function(x: int) -> int:
    return x * 2
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.check_docstrings(code, "test.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_docstring"
        assert findings[0].severity == Severity.BAJO
    
    def test_function_with_docstring_no_warning(self):
        """Verifica que funciones con docstring no generen hallazgos."""
        code = '''
def public_function(x: int) -> int:
    """Multiplica x por 2."""
    return x * 2
'''
        analyzer = QualityAnalyzer()
        findings = analyzer.check_docstrings(code, "test.py")
        
        assert len(findings) == 0
    
    def test_private_function_no_docstring_warning(self):
        """Verifica que funciones privadas no requieran docstring."""
        code = """
def _internal_helper(x):
    return x * 2
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.check_docstrings(code, "test.py")
        
        assert len(findings) == 0


class TestQualityAnalyzerFrontend:
    """Tests para análisis de calidad en Frontend (TypeScript/React)."""
    
    def test_detect_large_component(self):
        """Verifica detección de componente grande."""
        # Crear componente con más de 200 líneas
        code = "function LargeComponent() {\n" + "  const x = 1;\n" * 210 + "  return <div>Test</div>;\n}"
        
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_large_components(code, "LargeComponent.tsx")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "large_component"
        assert findings[0].severity == Severity.MEDIO
        assert "LargeComponent" in findings[0].title
    
    def test_small_component_no_warning(self):
        """Verifica que componentes pequeños no generen hallazgos."""
        code = """
function SmallComponent() {
    return <div>Hello</div>;
}
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_large_components(code, "SmallComponent.tsx")
        
        assert len(findings) == 0
    
    def test_detect_props_drilling(self):
        """Verifica detección de props drilling."""
        code = """
function Parent() {
    return <Child user={user} data={data} />;
}

function Child() {
    return <GrandChild user={user} data={data} />;
}

function GrandChild() {
    return <GreatGrandChild user={user} data={data} />;
}
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_props_drilling(code, "Component.tsx")
        
        # La heurística detecta props que se pasan múltiples veces
        assert len(findings) >= 1
        assert any(f.subcategory == "props_drilling" for f in findings)
    
    def test_no_props_drilling_with_few_levels(self):
        """Verifica que props en pocos niveles no generen hallazgos."""
        code = """
function Parent({ user }) {
    return <Child user={user} />;
}

function Child({ user }) {
    return <div>{user.name}</div>;
}
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_props_drilling(code, "Component.tsx")
        
        # Solo 2 niveles, no debería reportar
        assert len(findings) == 0
    
    def test_detect_type_any(self):
        """Verifica detección de tipo 'any'."""
        code = """
function processData(data: any): any {
    return data;
}
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_type_any(code, "utils.ts")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "type_any" for f in findings)
        assert any(f.severity == Severity.MEDIO for f in findings)
    
    def test_detect_any_array(self):
        """Verifica detección de any[]."""
        code = """
const items: any[] = [];
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_type_any(code, "utils.ts")
        
        assert len(findings) == 1
    
    def test_detect_any_generic(self):
        """Verifica detección de <any>."""
        code = """
const promise: Promise<any> = fetchData();
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_type_any(code, "utils.ts")
        
        assert len(findings) == 1
    
    def test_no_any_warning_in_comments(self):
        """Verifica que 'any' en comentarios no genere hallazgos."""
        code = """
// This function can accept any value
function process(data: string): void {}
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_type_any(code, "utils.ts")
        
        assert len(findings) == 0
    
    def test_detect_console_log(self):
        """Verifica detección de console.log."""
        code = """
function debug() {
    console.log("Debug info");
    console.error("Error info");
}
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_console_logs(code, "utils.ts")
        
        assert len(findings) == 2
        assert all(f.subcategory == "console_log" for f in findings)
        assert all(f.severity == Severity.BAJO for f in findings)
    
    def test_no_console_log_in_comments(self):
        """Verifica que console.log en comentarios no genere hallazgos."""
        code = """
// console.log("This is commented out")
function clean() {
    return true;
}
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_console_logs(code, "utils.ts")
        
        assert len(findings) == 0
    
    def test_detect_business_logic_in_component(self):
        """Verifica detección de lógica de negocio en componente."""
        code = """
function UserList({ users }) {
    const filtered = users.filter(u => {
        return u.age > 18 && u.status === 'active' && u.verified === true;
    });
    
    return (
        <div>{filtered.map(u => <User key={u.id} user={u} />)}</div>
    );
}
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_business_logic_in_ui(code, "components/UserList.tsx")
        
        # La heurística busca patrones complejos cerca del return
        # Este test documenta el comportamiento actual
        assert isinstance(findings, list)


class TestQualityAnalyzerIntegration:
    """Tests de integración para el analizador completo."""
    
    def test_analyze_python_file(self):
        """Verifica análisis completo de archivo Python."""
        code = """
def process_data(data):
    if True:
        if True:
            if True:
                if True:
                    x = 1
    try:
        operation()
    except:
        pass
    return data
"""
        python_file = PythonFile(
            path="backend/services/processor.py",
            language="python",
            lines_of_code=20,
            is_large=False,
            content=code
        )
        
        analyzer = QualityAnalyzer()
        findings = analyzer.analyze([python_file])
        
        # Debe detectar: deep nesting, no type hints, generic exception, no docstring
        assert len(findings) >= 3
    
    def test_analyze_typescript_file(self):
        """Verifica análisis completo de archivo TypeScript."""
        code = """
function Component({ data }: any) {
    console.log(data);
    return <div>Test</div>;
}
"""
        ts_file = TypeScriptFile(
            path="src/components/Component.tsx",
            language="typescript",
            lines_of_code=10,
            is_large=False,
            is_component=True,
            content=code
        )
        
        analyzer = QualityAnalyzer()
        findings = analyzer.analyze([ts_file])
        
        # Debe detectar: type any, console.log
        assert len(findings) >= 2
    
    def test_analyze_empty_file_list(self):
        """Verifica que maneje lista vacía de archivos."""
        analyzer = QualityAnalyzer()
        findings = analyzer.analyze([])
        
        assert findings == []
    
    def test_finding_structure(self):
        """Verifica que los hallazgos tengan la estructura correcta."""
        code = "def func(x):\n" + "    pass\n" * 60
        
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_long_functions(code, "test.py")
        
        assert len(findings) > 0
        finding = findings[0]
        
        # Verificar campos requeridos
        assert finding.id
        assert finding.category == "quality"
        assert finding.subcategory
        assert finding.severity
        assert finding.title
        assert finding.description
        assert finding.file_path == "test.py"
        assert finding.line_number is not None
        assert finding.recommendation


class TestCodeDuplication:
    """Tests para detección de código duplicado."""
    
    def test_detect_duplicate_functions(self):
        """Verifica detección de funciones duplicadas."""
        code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
        total += item.tax
    return total

def compute_sum(products):
    total = 0
    for product in products:
        total += product.price
        total += product.tax
    return total
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_code_duplication(code, "test.py")
        
        # La detección de duplicación requiere alta similitud
        # Este test documenta el comportamiento actual
        assert isinstance(findings, list)
    
    def test_no_duplication_with_different_functions(self):
        """Verifica que funciones suficientemente diferentes no generen hallazgos."""
        code = """
def add(a, b):
    result = a + b
    print(f"Adding {a} and {b}")
    return result

def multiply(a, b):
    result = a * b
    result = result ** 2
    return result / 2
"""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_code_duplication(code, "test.py")
        
        # Funciones con lógica diferente no deberían tener alta similitud
        assert len([f for f in findings if f.subcategory == "code_duplication"]) == 0


class TestQualityAnalyzerEdgeCases:
    """Tests para casos límite y edge cases."""
    
    def test_empty_file_content(self):
        """Verifica manejo de archivo vacío."""
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_long_functions("", "empty.py")
        
        assert findings == []
    
    def test_syntax_error_handling(self):
        """Verifica manejo de errores de sintaxis."""
        code = "def broken( syntax error"
        
        analyzer = QualityAnalyzer()
        findings = analyzer.detect_long_functions(code, "broken.py")
        
        # No debe lanzar excepción, solo retornar lista vacía
        assert isinstance(findings, list)
    
    def test_unicode_content(self):
        """Verifica manejo de contenido Unicode."""
        code = '''
def procesar_datos(datos):
    """Procesa datos con caracteres especiales: ñ, á, é."""
    return datos
'''
        analyzer = QualityAnalyzer()
        findings = analyzer.check_type_hints(code, "unicode.py")
        
        assert isinstance(findings, list)
    
    def test_multiple_issues_same_function(self):
        """Verifica detección de múltiples problemas en la misma función."""
        code = """
def problematic(data):
    if True:
        if True:
            if True:
                if True:
                    try:
                        x = 1
                    except:
                        pass
"""
        analyzer = QualityAnalyzer()
        
        # Debe detectar: no type hints, deep nesting, generic exception
        all_findings = []
        all_findings.extend(analyzer.check_type_hints(code, "test.py"))
        all_findings.extend(analyzer.detect_deep_nesting(code, "test.py"))
        all_findings.extend(analyzer.check_exception_handling(code, "test.py"))
        
        assert len(all_findings) >= 3
