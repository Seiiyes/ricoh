"""
Tests para UXAnalyzer.

Valida la detección de problemas de UX en código Frontend.
"""

import pytest
from audit_system.analyzers.ux_analyzer import UXAnalyzer
from audit_system.models import SourceFile, Severity


@pytest.fixture
def analyzer():
    """Fixture que retorna una instancia de UXAnalyzer."""
    return UXAnalyzer()


class TestCheckLoadingStates:
    """Tests para check_loading_states."""
    
    def test_detects_fetch_without_loading_state(self, analyzer):
        """Detecta fetch sin estado de carga."""
        code = """
        const fetchData = async () => {
            const response = await fetch('/api/data');
            const data = await response.json();
            setData(data);
        };
        """
        findings = analyzer.check_loading_states(code, "Component.tsx")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_loading_state"
        assert findings[0].severity == Severity.MEDIO
    
    def test_detects_axios_without_loading_state(self, analyzer):
        """Detecta axios sin estado de carga."""
        code = """
        const fetchData = async () => {
            const response = await axios.get('/api/data');
            setData(response.data);
        };
        """
        findings = analyzer.check_loading_states(code, "Component.tsx")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_loading_state"
    
    def test_no_finding_when_loading_state_exists(self, analyzer):
        """No reporta cuando existe estado de carga."""
        code = """
        const [isLoading, setIsLoading] = useState(false);
        
        const fetchData = async () => {
            setIsLoading(true);
            const response = await fetch('/api/data');
            setIsLoading(false);
        };
        """
        findings = analyzer.check_loading_states(code, "Component.tsx")
        
        assert len(findings) == 0
    
    def test_no_finding_without_api_calls(self, analyzer):
        """No reporta cuando no hay llamadas a API."""
        code = """
        const handleClick = () => {
            setCount(count + 1);
        };
        """
        findings = analyzer.check_loading_states(code, "Component.tsx")
        
        assert len(findings) == 0
    
    def test_detects_api_call_without_loading(self, analyzer):
        """Detecta llamada a api. sin estado de carga."""
        code = """
        const fetchData = async () => {
            const data = await api.getData();
            setData(data);
        };
        """
        findings = analyzer.check_loading_states(code, "Component.tsx")
        
        assert len(findings) == 1


class TestCheckErrorStates:
    """Tests para check_error_states."""
    
    def test_detects_catch_without_error_display(self, analyzer):
        """Detecta catch sin mostrar error al usuario."""
        code = """
        fetchData().catch((error) => {
            console.log(error);
        });
        """
        findings = analyzer.check_error_states(code, "Component.tsx")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_error_display"
        assert findings[0].severity == Severity.MEDIO
    
    def test_detects_try_catch_without_error_display(self, analyzer):
        """Detecta try-catch sin mostrar error."""
        code = """
        try {
            await fetchData();
        } catch (error) {
            console.log(error);
        }
        """
        findings = analyzer.check_error_states(code, "Component.tsx")
        
        assert len(findings) == 1
    
    def test_no_finding_when_error_is_displayed(self, analyzer):
        """No reporta cuando el error se muestra al usuario."""
        code = """
        fetchData().catch((error) => {
            setError(error.message);
            toast.error('Failed to load data');
        });
        """
        findings = analyzer.check_error_states(code, "Component.tsx")
        
        assert len(findings) == 0
    
    def test_no_finding_with_toast_notification(self, analyzer):
        """No reporta cuando usa toast para notificar."""
        code = """
        try {
            await fetchData();
        } catch (error) {
            toast.error('Something went wrong');
        }
        """
        findings = analyzer.check_error_states(code, "Component.tsx")
        
        assert len(findings) == 0
    
    def test_no_finding_with_alert(self, analyzer):
        """No reporta cuando usa alert."""
        code = """
        fetchData().catch((error) => {
            alert('Error: ' + error.message);
        });
        """
        findings = analyzer.check_error_states(code, "Component.tsx")
        
        assert len(findings) == 0


class TestCheckEmptyStates:
    """Tests para check_empty_states."""
    
    def test_detects_map_without_empty_check(self, analyzer):
        """Detecta .map() sin verificación de lista vacía."""
        code = """
        return (
            <div>
                {items.map(item => <Item key={item.id} {...item} />)}
            </div>
        );
        """
        findings = analyzer.check_empty_states(code, "Component.tsx")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_empty_state"
        assert findings[0].severity == Severity.BAJO
    
    def test_no_finding_with_length_check(self, analyzer):
        """No reporta cuando verifica length === 0."""
        code = """
        return (
            <div>
                {items.length === 0 ? (
                    <EmptyState />
                ) : (
                    items.map(item => <Item key={item.id} {...item} />)
                )}
            </div>
        );
        """
        findings = analyzer.check_empty_states(code, "Component.tsx")
        
        assert len(findings) == 0
    
    def test_no_finding_with_isEmpty_check(self, analyzer):
        """No reporta cuando usa isEmpty."""
        code = """
        if (isEmpty(items)) {
            return <EmptyState />;
        }
        return items.map(item => <Item key={item.id} {...item} />);
        """
        findings = analyzer.check_empty_states(code, "Component.tsx")
        
        assert len(findings) == 0
    
    def test_no_finding_with_negated_length(self, analyzer):
        """No reporta cuando verifica !items.length."""
        code = """
        if (!items.length) return <EmptyState />;
        return items.map(item => <Item key={item.id} {...item} />);
        """
        findings = analyzer.check_empty_states(code, "Component.tsx")
        
        assert len(findings) == 0


class TestCheckFormValidation:
    """Tests para check_form_validation."""
    
    def test_detects_form_without_validation(self, analyzer):
        """Detecta formulario sin validación."""
        code = """
        <form onSubmit={handleSubmit}>
            <input name="email" />
            <button type="submit">Submit</button>
        </form>
        """
        findings = analyzer.check_form_validation(code, "Form.tsx")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_form_validation"
        assert findings[0].severity == Severity.MEDIO
    
    def test_no_finding_with_react_hook_form(self, analyzer):
        """No reporta cuando usa react-hook-form."""
        code = """
        const { register, handleSubmit } = useForm();
        
        <form onSubmit={handleSubmit(onSubmit)}>
            <input {...register('email')} />
            <button type="submit">Submit</button>
        </form>
        """
        findings = analyzer.check_form_validation(code, "Form.tsx")
        
        assert len(findings) == 0
    
    def test_no_finding_with_formik(self, analyzer):
        """No reporta cuando usa Formik."""
        code = """
        <Formik initialValues={{}} onSubmit={handleSubmit}>
            <Form>
                <Field name="email" />
                <button type="submit">Submit</button>
            </Form>
        </Formik>
        """
        findings = analyzer.check_form_validation(code, "Form.tsx")
        
        assert len(findings) == 0
    
    def test_no_finding_with_yup_validation(self, analyzer):
        """No reporta cuando usa yup."""
        code = """
        const schema = yup.object().shape({
            email: yup.string().email().required()
        });
        
        <form onSubmit={handleSubmit}>
            <input name="email" />
        </form>
        """
        findings = analyzer.check_form_validation(code, "Form.tsx")
        
        assert len(findings) == 0
    
    def test_no_finding_with_zod_validation(self, analyzer):
        """No reporta cuando usa zod."""
        code = """
        const schema = z.object({
            email: z.string().email()
        });
        
        <form onSubmit={handleSubmit}>
            <input name="email" />
        </form>
        """
        findings = analyzer.check_form_validation(code, "Form.tsx")
        
        assert len(findings) == 0


class TestAnalyze:
    """Tests para el método analyze principal."""
    
    def test_analyzes_typescript_files(self, analyzer):
        """Analiza archivos TypeScript."""
        file = SourceFile(
            path="Component.tsx",
            language="typescript",
            lines_of_code=50,
            is_large=False,
            content="""
            const fetchData = async () => {
                const response = await fetch('/api/data');
            };
            """
        )
        
        findings = analyzer.analyze([file])
        
        assert len(findings) > 0
        assert all(f.category == "ux" for f in findings)
    
    def test_ignores_non_typescript_files(self, analyzer):
        """Ignora archivos que no son TypeScript."""
        file = SourceFile(
            path="module.py",
            language="python",
            lines_of_code=50,
            is_large=False,
            content="def fetch_data(): pass"
        )
        
        findings = analyzer.analyze([file])
        
        assert len(findings) == 0
    
    def test_analyzes_multiple_files(self, analyzer):
        """Analiza múltiples archivos."""
        files = [
            SourceFile(
                path="Component1.tsx",
                language="typescript",
                lines_of_code=30,
                is_large=False,
                content="fetch('/api/data')"
            ),
            SourceFile(
                path="Component2.tsx",
                language="typescript",
                lines_of_code=40,
                is_large=False,
                content="<form onSubmit={handleSubmit}></form>"
            )
        ]
        
        findings = analyzer.analyze(files)
        
        assert len(findings) >= 2
