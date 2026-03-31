"""
Tests unitarios y property-based para ArchitectureAnalyzer.

Valida la detección de patrones arquitectónicos en Backend y Frontend.
"""

import pytest
from hypothesis import given, settings, strategies as st
from audit_system.analyzers.architecture_analyzer import ArchitectureAnalyzer
from audit_system.models import Severity, SourceFile, PythonFile, TypeScriptFile


class TestArchitectureAnalyzerBackend:
    """Tests para análisis de arquitectura en Backend (Python)."""
    
    def test_detect_layer_violation_direct_db_access(self):
        """Verifica detección de acceso directo a DB desde API."""
        code = """
@router.get("/users")
def get_users():
    users = session.query(User).all()
    return users
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_layer_separation(code, "backend/api/users.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "layer_separation"
        assert findings[0].severity == Severity.MEDIO
        assert "separación de capas" in findings[0].title.lower()
    
    def test_no_layer_violation_in_service_file(self):
        """Verifica que no detecte violación en archivos de servicio."""
        code = """
def get_all_users():
    users = session.query(User).all()
    return users
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_layer_separation(code, "backend/services/user_service.py")
        
        assert len(findings) == 0
    
    def test_detect_business_logic_in_api(self):
        """Verifica detección de lógica de negocio en endpoint."""
        code = """
@router.post("/calculate")
def calculate_price(item: Item):
    base_price = item.price
    if item.category == "premium":
        discount = 0.2
    elif item.category == "standard":
        discount = 0.1
    else:
        discount = 0
    
    final_price = base_price * (1 - discount)
    
    for addon in item.addons:
        if addon.type == "extra":
            final_price += addon.price * 1.5
    
    return {"price": final_price}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_business_logic_in_api(code, "backend/api/pricing.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "business_logic_in_api" for f in findings)

    
    def test_no_business_logic_warning_for_simple_endpoint(self):
        """Verifica que no detecte problema en endpoints simples."""
        code = """
@router.get("/users/{user_id}")
def get_user(user_id: int):
    return user_service.get_user_by_id(user_id)
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_business_logic_in_api(code, "backend/api/users.py")
        
        assert len(findings) == 0
    
    def test_detect_missing_commit(self):
        """Verifica detección de operación de escritura sin commit."""
        code = """
def create_user(user_data):
    user = User(**user_data)
    session.add(user)
    return user
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_transaction_handling(code, "backend/services/user_service.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "transaction_handling" for f in findings)
        assert any("commit" in f.title.lower() for f in findings)
    
    def test_transaction_with_commit_and_rollback(self):
        """Verifica que no detecte problema con transacción completa."""
        code = """
def create_user(user_data):
    try:
        user = User(**user_data)
        session.add(user)
        session.commit()
        return user
    except Exception as e:
        session.rollback()
        raise
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_transaction_handling(code, "backend/services/user_service.py")
        
        # No debe reportar problemas con transacción bien manejada
        assert len([f for f in findings if "commit" in f.title.lower()]) == 0
    
    def test_detect_tight_coupling_api_to_db(self):
        """Verifica detección de acoplamiento entre API y DB."""
        code = """
from backend.db.models import User, Post
from backend.db.database import session

@router.get("/users")
def get_users():
    return session.query(User).all()
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_tight_coupling(code, "backend/api/users.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "tight_coupling" for f in findings)
    
    def test_no_coupling_warning_for_service_layer(self):
        """Verifica que no detecte acoplamiento en capa de servicios."""
        code = """
from backend.db.models import User
from backend.db.database import session

def get_all_users():
    return session.query(User).all()
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_tight_coupling(code, "backend/services/user_service.py")
        
        # Servicios pueden importar de DB
        assert len(findings) == 0


class TestArchitectureAnalyzerFrontend:
    """Tests para análisis de arquitectura en Frontend (TypeScript/React)."""
    
    def test_detect_mixed_concerns_in_component(self):
        """Verifica detección de componente con lógica mezclada."""
        code = """
function UserDashboard({ userId }) {
    const [data, setData] = useState(null);
    
    const processedData = data?.items
        .filter(item => item.active)
        .map(item => ({
            ...item,
            score: item.points * 1.5
        }))
        .reduce((acc, item) => acc + item.score, 0);
    
    return <div>{processedData}</div>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_component_separation(code, "src/components/UserDashboard.tsx")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "component_separation" for f in findings)
    
    def test_no_separation_warning_for_presentational_component(self):
        """Verifica que no detecte problema en componentes presentacionales."""
        code = """
function Button({ label, onClick }) {
    return <button onClick={onClick}>{label}</button>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_component_separation(code, "src/components/Button.tsx")
        
        assert len(findings) == 0
    
    def test_detect_api_call_in_component(self):
        """Verifica detección de llamada API directa en componente."""
        code = """
function UserList() {
    const [users, setUsers] = useState([]);
    
    useEffect(() => {
        fetch('/api/users')
            .then(res => res.json())
            .then(data => setUsers(data));
    }, []);
    
    return <div>{users.map(u => <div key={u.id}>{u.name}</div>)}</div>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_api_calls_in_components(code, "src/components/UserList.tsx")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "api_calls_in_components" for f in findings)
        assert any("API" in f.title for f in findings)
    
    def test_detect_axios_call_in_component(self):
        """Verifica detección de llamada axios directa."""
        code = """
function DataFetcher() {
    const loadData = async () => {
        const response = await axios.get('/api/data');
        return response.data;
    };
    
    return <button onClick={loadData}>Load</button>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_api_calls_in_components(code, "src/components/DataFetcher.tsx")
        
        assert len(findings) >= 1
    
    def test_no_api_warning_for_service_usage(self):
        """Verifica que no detecte problema cuando se usa servicio."""
        code = """
import { userService } from '../services/userService';

function UserList() {
    const [users, setUsers] = useState([]);
    
    useEffect(() => {
        userService.getAll().then(setUsers);
    }, []);
    
    return <div>{users.map(u => <div key={u.id}>{u.name}</div>)}</div>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_api_calls_in_components(code, "src/components/UserList.tsx")
        
        assert len(findings) == 0
    
    def test_detect_excessive_local_state(self):
        """Verifica detección de exceso de estado local."""
        code = """
function ComplexForm() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [address, setAddress] = useState('');
    const [city, setCity] = useState('');
    const [country, setCountry] = useState('');
    
    return <form>...</form>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_state_management(code, "src/components/ComplexForm.tsx")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "state_management" for f in findings)
    
    def test_no_state_warning_for_few_usestate(self):
        """Verifica que no detecte problema con pocos useState."""
        code = """
function SimpleForm() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    
    return <form>...</form>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_state_management(code, "src/components/SimpleForm.tsx")
        
        assert len(findings) == 0
    
    def test_detect_simple_context_usage(self):
        """Verifica detección de Context para valor simple."""
        code = """
const ThemeContext = createContext(null);
const UserContext = createContext(undefined);
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_context_usage(code, "src/contexts/AppContext.tsx")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "context_usage" for f in findings)


class TestArchitectureAnalyzerAPIContract:
    """Tests para análisis de contrato API."""
    
    def test_detect_missing_documentation(self):
        """Verifica detección de endpoint sin documentación."""
        code = """
@router.get("/users")
def get_users():
    return []
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_openapi_documentation(code, "backend/api/users.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "openapi_documentation" for f in findings)
    
    def test_no_doc_warning_with_docstring(self):
        """Verifica que no detecte problema con documentación."""
        code = '''
@router.get("/users")
def get_users():
    """
    Obtiene todos los usuarios.
    
    Returns:
        Lista de usuarios
    """
    return []
'''
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_openapi_documentation(code, "backend/api/users.py")
        
        assert len(findings) == 0
    
    def test_detect_wrong_http_verb(self):
        """Verifica detección de verbo HTTP incorrecto."""
        code = """
@router.get("/users/create")
def create_user(user: User):
    session.add(user)
    session.commit()
    return user
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_http_verb_consistency(code, "backend/api/users.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "http_verb_consistency" for f in findings)
    
    def test_no_verb_warning_for_correct_usage(self):
        """Verifica que no detecte problema con verbo correcto."""
        code = """
@router.post("/users")
def create_user(user: User):
    session.add(user)
    session.commit()
    return user
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_http_verb_consistency(code, "backend/api/users.py")
        
        assert len(findings) == 0
    
    def test_detect_inconsistent_error_format(self):
        """Verifica detección de formato inconsistente de errores."""
        code = """
@router.get("/users/{user_id}")
def get_user(user_id: int):
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/posts/{post_id}")
def get_post(post_id: int):
    if not post:
        raise HTTPException(status_code=404)
    return post
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_error_response_format(code, "backend/api/resources.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "error_response_format" for f in findings)
    
    def test_detect_missing_201_status(self):
        """Verifica detección de POST sin status 201."""
        code = """
@router.post("/users")
def create_user(user: User):
    return user_service.create(user)
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_http_status_codes(code, "backend/api/users.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "http_status_codes" for f in findings)
        assert any("201" in f.description for f in findings)
    
    def test_no_status_warning_with_201(self):
        """Verifica que no detecte problema con status 201."""
        code = """
@router.post("/users", status_code=201)
def create_user(user: User):
    return user_service.create(user)
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_http_status_codes(code, "backend/api/users.py")
        
        assert len(findings) == 0


class TestArchitectureAnalyzerIntegration:
    """Tests de integración para el analizador completo."""
    
    def test_analyze_python_file(self):
        """Verifica análisis completo de archivo Python."""
        python_file = PythonFile(
            path="backend/api/users.py",
            language="python",
            lines_of_code=50,
            is_large=False,
            content="""
@router.get("/users")
def get_users():
    users = session.query(User).all()
    for user in users:
        if user.active:
            user.score = calculate_score(user)
    return users
"""
        )
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.analyze([python_file])
        
        # Debe detectar violación de capa y lógica de negocio
        assert len(findings) >= 1
        categories = [f.subcategory for f in findings]
        assert "layer_separation" in categories

    
    def test_analyze_typescript_file(self):
        """Verifica análisis completo de archivo TypeScript."""
        ts_file = TypeScriptFile(
            path="src/components/UserList.tsx",
            language="typescript",
            lines_of_code=40,
            is_large=False,
            is_component=True,
            content="""
function UserList() {
    const [users, setUsers] = useState([]);
    
    useEffect(() => {
        fetch('/api/users')
            .then(res => res.json())
            .then(data => setUsers(data));
    }, []);
    
    return <div>{users.map(u => <div key={u.id}>{u.name}</div>)}</div>;
}
"""
        )
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.analyze([ts_file])
        
        # Debe detectar llamada API directa
        assert len(findings) >= 1
        assert any(f.subcategory == "api_calls_in_components" for f in findings)
    
    def test_analyze_mixed_files(self):
        """Verifica análisis de múltiples archivos de diferentes lenguajes."""
        python_file = PythonFile(
            path="backend/api/test.py",
            language="python",
            lines_of_code=20,
            is_large=False,
            content="@router.get('/test')\ndef test(): pass"
        )
        
        ts_file = TypeScriptFile(
            path="src/Test.tsx",
            language="typescript",
            lines_of_code=10,
            is_large=False,
            is_component=True,
            content="function Test() { return <div>Test</div>; }"
        )
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.analyze([python_file, ts_file])
        
        # Debe analizar ambos archivos sin errores
        assert isinstance(findings, list)
    
    def test_analyze_empty_file_list(self):
        """Verifica que maneje lista vacía de archivos."""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.analyze([])
        
        assert findings == []
    
    def test_finding_structure(self):
        """Verifica que los hallazgos tengan la estructura correcta."""
        code = """
@router.get("/users")
def get_users():
    users = session.query(User).all()
    return users
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_layer_separation(code, "backend/api/users.py")
        
        assert len(findings) > 0
        finding = findings[0]
        
        # Verificar campos requeridos
        assert finding.id
        assert finding.category == "architecture"
        assert finding.subcategory
        assert finding.severity
        assert finding.title
        assert finding.description
        assert finding.file_path == "backend/api/users.py"
        assert finding.line_number is not None
        assert finding.recommendation


class TestArchitectureAnalyzerEdgeCases:
    """Tests para casos límite y edge cases."""
    
    def test_empty_file_content(self):
        """Verifica manejo de archivo vacío."""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_layer_separation("", "empty.py")
        
        assert findings == []
    
    def test_file_with_only_comments(self):
        """Verifica manejo de archivo solo con comentarios."""
        code = """
# This is a comment
# Another comment
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_business_logic_in_api(code, "backend/api/test.py")
        
        assert findings == []
    
    def test_multiline_endpoint_definition(self):
        """Verifica detección en definiciones multilínea."""
        code = """
@router.post(
    "/users",
    response_model=UserResponse,
    status_code=201
)
def create_user(user: UserCreate):
    return user_service.create(user)
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_http_status_codes(code, "backend/api/users.py")
        
        # Debe reconocer status_code=201 en definición multilínea
        assert len(findings) == 0
    
    def test_nested_components(self):
        """Verifica manejo de componentes anidados."""
        code = """
function ParentComponent() {
    function ChildComponent() {
        return <div>Child</div>;
    }
    
    return <div><ChildComponent /></div>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_component_separation(code, "src/components/Parent.tsx")
        
        # Debe manejar componentes anidados sin errores
        assert isinstance(findings, list)
    
    def test_very_long_line(self):
        """Verifica manejo de líneas muy largas."""
        code = "x = " + "1 + " * 1000 + "1"
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_tight_coupling(code, "test.py")
        
        assert isinstance(findings, list)
    
    def test_unicode_content(self):
        """Verifica manejo de contenido Unicode."""
        code = """
@router.get("/usuarios")
def obtener_usuarios():
    # Función con caracteres especiales: ñ, á, é, í, ó, ú
    usuarios = session.query(Usuario).all()
    return usuarios
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_layer_separation(code, "backend/api/usuarios.py")
        
        assert len(findings) >= 1


class TestTransactionHandling:
    """Tests para verificación de manejo de transacciones."""
    
    def test_detect_add_without_commit(self):
        """Verifica detección de add sin commit."""
        code = """
def create_item(item_data):
    item = Item(**item_data)
    session.add(item)
    return item
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_transaction_handling(code, "backend/services/item_service.py")
        
        assert len(findings) >= 1
        assert any("commit" in f.title.lower() for f in findings)
    
    def test_detect_delete_without_commit(self):
        """Verifica detección de delete sin commit."""
        code = """
def remove_item(item_id):
    item = session.query(Item).get(item_id)
    session.delete(item)
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_transaction_handling(code, "backend/services/item_service.py")
        
        assert len(findings) >= 1
    
    def test_commit_without_rollback(self):
        """Verifica detección de commit sin rollback."""
        code = """
def create_item(item_data):
    item = Item(**item_data)
    session.add(item)
    session.commit()
    return item
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_transaction_handling(code, "backend/services/item_service.py")
        
        # Debe detectar falta de manejo de errores
        assert len(findings) >= 1
        assert any("rollback" in f.title.lower() for f in findings)
    
    def test_proper_transaction_handling(self):
        """Verifica que no detecte problema con transacción correcta."""
        code = """
def create_item(item_data):
    try:
        item = Item(**item_data)
        session.add(item)
        session.commit()
        return item
    except Exception as e:
        session.rollback()
        raise
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_transaction_handling(code, "backend/services/item_service.py")
        
        # No debe reportar problemas
        assert len([f for f in findings if "commit" in f.title.lower()]) == 0
    
    def test_multiple_operations_in_transaction(self):
        """Verifica detección en transacciones con múltiples operaciones."""
        code = """
def transfer_items(from_user, to_user, item_ids):
    for item_id in item_ids:
        item = session.query(Item).get(item_id)
        item.owner_id = to_user.id
        session.add(item)
    session.commit()
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_transaction_handling(code, "backend/services/transfer.py")
        
        # Debe detectar falta de rollback
        assert len(findings) >= 1


class TestComponentSeparation:
    """Tests para verificación de separación de componentes."""
    
    def test_detect_complex_data_transformation(self):
        """Verifica detección de transformación compleja en componente."""
        code = """
function DataTable({ data }) {
    const processed = data
        .filter(item => item.active)
        .map(item => ({ ...item, score: item.value * 2 }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 10);
    
    return <table>{processed.map(row => <tr key={row.id}>...</tr>)}</table>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_component_separation(code, "src/components/DataTable.tsx")
        
        assert len(findings) >= 1
        assert any("lógica" in f.description.lower() for f in findings)
    
    def test_detect_complex_validation(self):
        """Verifica detección de validación compleja en componente."""
        code = """
function Form({ data }) {
    const isValid = data.email && data.email.includes('@') && 
                    data.password && data.password.length >= 8 ||
                    data.oauth_token;
    
    return <form>...</form>;
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_component_separation(code, "src/components/Form.tsx")
        
        assert len(findings) >= 1
    
    def test_no_warning_for_simple_component(self):
        """Verifica que no detecte problema en componente simple."""
        code = """
function UserCard({ user }) {
    return (
        <div>
            <h2>{user.name}</h2>
            <p>{user.email}</p>
        </div>
    );
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_component_separation(code, "src/components/UserCard.tsx")
        
        assert len(findings) == 0
    
    def test_arrow_function_component(self):
        """Verifica detección en componentes con arrow function."""
        code = """
const DataProcessor = ({ items }) => {
    const result = items
        .reduce((acc, item) => acc + item.value, 0)
        .map(x => x * 2);
    
    return <div>{result}</div>;
};
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_component_separation(code, "src/components/DataProcessor.tsx")
        
        # Debe detectar lógica compleja
        assert len(findings) >= 1


class TestAPICallsDetection:
    """Tests para detección de llamadas API en componentes."""
    
    def test_detect_fetch_in_useeffect(self):
        """Verifica detección de fetch en useEffect."""
        code = """
function DataLoader() {
    useEffect(() => {
        fetch('/api/data')
            .then(res => res.json())
            .then(setData);
    }, []);
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_api_calls_in_components(code, "src/components/DataLoader.tsx")
        
        assert len(findings) >= 1
    
    def test_detect_axios_post(self):
        """Verifica detección de axios.post."""
        code = """
function FormSubmit() {
    const handleSubmit = async (data) => {
        await axios.post('/api/submit', data);
    };
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_api_calls_in_components(code, "src/components/FormSubmit.tsx")
        
        assert len(findings) >= 1
    
    def test_detect_multiple_api_calls(self):
        """Verifica detección de múltiples llamadas API."""
        code = """
function Dashboard() {
    useEffect(() => {
        fetch('/api/users').then(res => res.json()).then(setUsers);
        axios.get('/api/stats').then(res => setStats(res.data));
    }, []);
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_api_calls_in_components(code, "src/components/Dashboard.tsx")
        
        assert len(findings) >= 2
    
    def test_no_warning_for_service_import(self):
        """Verifica que no detecte problema con import de servicio."""
        code = """
import { apiService } from '../services/api';

function DataLoader() {
    useEffect(() => {
        apiService.getData().then(setData);
    }, []);
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_api_calls_in_components(code, "src/components/DataLoader.tsx")
        
        # No debe detectar llamadas API directas
        assert len(findings) == 0


class TestStateManagement:
    """Tests para verificación de gestión de estado."""
    
    def test_detect_many_usestate(self):
        """Verifica detección de muchos useState."""
        code = """
function LargeForm() {
    const [field1, setField1] = useState('');
    const [field2, setField2] = useState('');
    const [field3, setField3] = useState('');
    const [field4, setField4] = useState('');
    const [field5, setField5] = useState('');
    const [field6, setField6] = useState('');
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_state_management(code, "src/components/LargeForm.tsx")
        
        assert len(findings) >= 1
        assert any("estado local" in f.description.lower() for f in findings)
    
    def test_no_warning_for_reasonable_state(self):
        """Verifica que no detecte problema con estado razonable."""
        code = """
function SimpleComponent() {
    const [count, setCount] = useState(0);
    const [name, setName] = useState('');
    const [isOpen, setIsOpen] = useState(false);
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_state_management(code, "src/components/SimpleComponent.tsx")
        
        assert len(findings) == 0
    
    def test_boundary_case_five_usestate(self):
        """Verifica detección en el límite de 5 useState."""
        code = """
function BoundaryComponent() {
    const [s1, setS1] = useState('');
    const [s2, setS2] = useState('');
    const [s3, setS3] = useState('');
    const [s4, setS4] = useState('');
    const [s5, setS5] = useState('');
}
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_state_management(code, "src/components/BoundaryComponent.tsx")
        
        # Exactamente 5 debe detectarse
        assert len(findings) >= 1


class TestContextUsage:
    """Tests para verificación de uso de Context API."""
    
    def test_detect_simple_context_null(self):
        """Verifica detección de Context con valor null."""
        code = """
const UserContext = createContext(null);
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_context_usage(code, "src/contexts/UserContext.tsx")
        
        assert len(findings) >= 1
        assert any("simple" in f.title.lower() for f in findings)
    
    def test_detect_simple_context_undefined(self):
        """Verifica detección de Context con undefined."""
        code = """
const ThemeContext = createContext(undefined);
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_context_usage(code, "src/contexts/ThemeContext.tsx")
        
        assert len(findings) >= 1
    
    def test_detect_simple_context_boolean(self):
        """Verifica detección de Context con boolean."""
        code = """
const FeatureFlagContext = createContext(false);
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_context_usage(code, "src/contexts/FeatureContext.tsx")
        
        assert len(findings) >= 1
    
    def test_no_warning_for_complex_context(self):
        """Verifica que no detecte problema con Context complejo."""
        code = """
const AppContext = createContext({
    user: null,
    settings: {},
    actions: {}
});
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_context_usage(code, "src/contexts/AppContext.tsx")
        
        # Context complejo es apropiado
        assert len(findings) == 0


class TestOpenAPIDocumentation:
    """Tests para verificación de documentación OpenAPI."""
    
    def test_detect_missing_docstring(self):
        """Verifica detección de endpoint sin docstring."""
        code = """
@router.get("/items")
def get_items():
    return []
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_openapi_documentation(code, "backend/api/items.py")
        
        assert len(findings) >= 1
        assert any("documentación" in f.title.lower() for f in findings)
    
    def test_no_warning_with_docstring(self):
        """Verifica que no detecte problema con docstring."""
        code = '''
@router.get("/items")
def get_items():
    """Get all items."""
    return []
'''
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_openapi_documentation(code, "backend/api/items.py")
        
        assert len(findings) == 0
    
    def test_multiline_docstring(self):
        """Verifica reconocimiento de docstring multilínea."""
        code = '''
@router.get("/items")
def get_items():
    """
    Get all items from the database.
    
    Returns:
        List of items
    """
    return []
'''
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_openapi_documentation(code, "backend/api/items.py")
        
        assert len(findings) == 0
    
    def test_skip_non_api_files(self):
        """Verifica que no analice archivos que no son de API."""
        code = """
def get_items():
    return []
"""
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_openapi_documentation(code, "backend/services/item_service.py")
        
        # No debe analizar archivos de servicios
        assert len(findings) == 0



# ========== Property-Based Tests ==========

class TestArchitectureAnalyzerProperties:
    """Property-based tests usando Hypothesis."""
    
    @given(
        num_queries=st.integers(min_value=1, max_value=10),
        has_commit=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_transaction_detection(self, num_queries, has_commit):
        """
        Property: Para cualquier código con operaciones de escritura,
        si no tiene commit, debe detectarse.
        
        **Validates: Requirements 8.5**
        """
        code_lines = []
        for i in range(num_queries):
            code_lines.append(f"    session.add(item_{i})")
        
        if has_commit:
            code_lines.append("    session.commit()")
        
        code = "def create_items():\n" + "\n".join(code_lines)
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_transaction_handling(code, "test.py")
        
        if has_commit:
            # Si tiene commit, puede o no tener rollback (otro finding)
            assert isinstance(findings, list)
        else:
            # Si no tiene commit, debe detectarse
            assert len(findings) >= 1
            assert any("commit" in f.title.lower() for f in findings)
    
    @given(
        num_usestate=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=100)
    def test_property_excessive_state_detection(self, num_usestate):
        """
        Property: Para cualquier componente con >= 5 useState,
        debe detectarse como exceso de estado local.
        
        **Validates: Requirements 9.3**
        """
        code_lines = ["function TestComponent() {"]
        for i in range(num_usestate):
            code_lines.append(f"    const [state{i}, setState{i}] = useState('');")
        code_lines.append("    return <div>Test</div>;")
        code_lines.append("}")
        
        code = "\n".join(code_lines)
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_state_management(code, "TestComponent.tsx")
        
        if num_usestate >= 5:
            assert len(findings) >= 1
            assert any("estado local" in f.description.lower() for f in findings)
        else:
            assert len(findings) == 0
    
    @given(
        has_fetch=st.booleans(),
        has_axios=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_api_call_detection(self, has_fetch, has_axios):
        """
        Property: Para cualquier componente con fetch o axios,
        debe detectarse llamada API directa.
        
        **Validates: Requirements 9.2**
        """
        code_lines = ["function Component() {"]
        
        if has_fetch:
            code_lines.append("    fetch('/api/data');")
        
        if has_axios:
            code_lines.append("    axios.get('/api/data');")
        
        code_lines.append("    return <div>Test</div>;")
        code_lines.append("}")
        
        code = "\n".join(code_lines)
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_api_calls_in_components(code, "Component.tsx")
        
        expected_findings = (1 if has_fetch else 0) + (1 if has_axios else 0)
        assert len(findings) == expected_findings
    
    @given(
        is_api_file=st.booleans(),
        has_session_query=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_layer_separation(self, is_api_file, has_session_query):
        """
        Property: Para cualquier archivo de API con session.query,
        debe detectarse violación de separación de capas.
        
        **Validates: Requirements 8.1**
        """
        code = """
def get_data():
    data = session.query(Model).all()
    return data
"""
        
        file_path = "backend/api/test.py" if is_api_file else "backend/services/test.py"
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_layer_separation(code if has_session_query else "pass", file_path)
        
        if is_api_file and has_session_query:
            assert len(findings) >= 1
            assert any("separación" in f.title.lower() for f in findings)
        else:
            assert len(findings) == 0
    
    @given(
        num_conditionals=st.integers(min_value=0, max_value=5),
        num_loops=st.integers(min_value=0, max_value=3)
    )
    @settings(max_examples=100)
    def test_property_business_logic_complexity(self, num_conditionals, num_loops):
        """
        Property: Para cualquier endpoint con complejidad >= 3,
        debe detectarse lógica de negocio en API.
        
        **Validates: Requirements 8.2**
        """
        code_lines = ["@router.get('/test')", "def test():"]
        
        for i in range(num_conditionals):
            code_lines.append(f"    if condition_{i}:")
            code_lines.append(f"        result = value_{i}")
        
        for i in range(num_loops):
            code_lines.append(f"    for item in items_{i}:")
            code_lines.append(f"        process(item)")
        
        code_lines.append("    return result")
        
        code = "\n".join(code_lines)
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.detect_business_logic_in_api(code, "backend/api/test.py")
        
        # Complejidad = num_loops + num_conditionals * 0.5
        complexity = num_loops + (num_conditionals * 0.5)
        
        if complexity >= 3:
            assert len(findings) >= 1
        else:
            assert len(findings) == 0
    
    @given(
        http_verb=st.sampled_from(['get', 'post', 'put', 'delete']),
        has_write_operation=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_http_verb_consistency(self, http_verb, has_write_operation):
        """
        Property: Para cualquier endpoint GET con operaciones de escritura,
        debe detectarse uso incorrecto de verbo HTTP.
        
        **Validates: Requirements 10.2**
        """
        code_lines = [f"@router.{http_verb}('/test')", "def test():"]
        
        if has_write_operation:
            code_lines.append("    session.add(item)")
            code_lines.append("    session.commit()")
        
        code_lines.append("    return result")
        
        code = "\n".join(code_lines)
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_http_verb_consistency(code, "backend/api/test.py")
        
        if http_verb == 'get' and has_write_operation:
            assert len(findings) >= 1
            assert any("verbo http" in f.title.lower() for f in findings)
        else:
            assert len(findings) == 0
    
    @given(
        is_post=st.booleans(),
        has_201=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_status_code_consistency(self, is_post, has_201):
        """
        Property: Para cualquier endpoint POST sin status_code=201,
        debe detectarse.
        
        **Validates: Requirements 10.5**
        """
        verb = "post" if is_post else "get"
        status = ", status_code=201" if has_201 else ""
        
        code = f"""
@router.{verb}('/test'{status})
def test():
    return result
"""
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_http_status_codes(code, "backend/api/test.py")
        
        if is_post and not has_201:
            assert len(findings) >= 1
            assert any("201" in f.description for f in findings)
        else:
            assert len(findings) == 0
    
    @given(
        context_value=st.sampled_from(['null', 'undefined', 'false', 'true', '0', '""', '{}'])
    )
    @settings(max_examples=100)
    def test_property_context_usage(self, context_value):
        """
        Property: Para cualquier Context con valor simple (null, undefined, boolean, etc.),
        debe detectarse uso inapropiado.
        
        **Validates: Requirements 9.7**
        """
        code = f"const TestContext = createContext({context_value});"
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_context_usage(code, "TestContext.tsx")
        
        # Valores simples: null, undefined, false, true, 0, ""
        simple_values = ['null', 'undefined', 'false', 'true', '0', '""']
        
        if context_value in simple_values:
            assert len(findings) >= 1
            assert any("simple" in f.title.lower() for f in findings)
        else:
            # {} es un objeto complejo, no debe detectarse
            assert len(findings) == 0
    
    @given(
        has_docstring=st.booleans(),
        is_api_file=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_openapi_documentation(self, has_docstring, is_api_file):
        """
        Property: Para cualquier endpoint en archivo de API sin docstring,
        debe detectarse falta de documentación.
        
        **Validates: Requirements 10.1**
        """
        if has_docstring:
            code = '''
@router.get('/test')
def test():
    """Test endpoint."""
    return result
'''
        else:
            code = """
@router.get('/test')
def test():
    return result
"""
        
        file_path = "backend/api/test.py" if is_api_file else "backend/services/test.py"
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_openapi_documentation(code, file_path)
        
        if is_api_file and not has_docstring:
            assert len(findings) >= 1
            assert any("documentación" in f.title.lower() for f in findings)
        else:
            assert len(findings) == 0
    
    @given(
        num_data_transforms=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_component_separation(self, num_data_transforms):
        """
        Property: Para cualquier componente con múltiples transformaciones
        de datos encadenadas, debe detectarse mezcla de lógica.
        
        **Validates: Requirements 9.1, 9.4**
        """
        code_lines = ["function Component({ data }) {"]
        
        if num_data_transforms >= 2:
            transforms = [".filter(x => x.active)", ".map(x => x.value)", 
                         ".reduce((a, b) => a + b)", ".sort((a, b) => a - b)"]
            transform_chain = "".join(transforms[:num_data_transforms])
            code_lines.append(f"    const result = data{transform_chain};")
        
        code_lines.append("    return <div>{result}</div>;")
        code_lines.append("}")
        
        code = "\n".join(code_lines)
        
        analyzer = ArchitectureAnalyzer()
        findings = analyzer.check_component_separation(code, "Component.tsx")
        
        if num_data_transforms >= 2:
            assert len(findings) >= 1
        else:
            assert len(findings) == 0
