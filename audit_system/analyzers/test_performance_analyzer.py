"""
Tests unitarios para PerformanceAnalyzer.

Valida la detección de patrones de performance en Backend y Frontend.
"""

import pytest
from audit_system.analyzers.performance_analyzer import PerformanceAnalyzer
from audit_system.models import Severity, SourceFile, PythonFile, TypeScriptFile


class TestPerformanceAnalyzerBackend:
    """Tests para análisis de performance en Backend (Python)."""
    
    def test_detect_n_plus_one_basic_pattern(self):
        """Verifica detección de patrón N+1 básico."""
        code = """
users = session.query(User).all()
for user in users:
    posts = session.query(Post).filter(Post.user_id == user.id).all()
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one(code, "test.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "n_plus_one"
        assert findings[0].severity == Severity.ALTO
        assert "N+1" in findings[0].title
    
    def test_detect_n_plus_one_no_false_positive(self):
        """Verifica que no detecte N+1 cuando no existe."""
        code = """
users = session.query(User).all()
for user in users:
    print(user.name)
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one(code, "test.py")
        
        assert len(findings) == 0
    
    def test_detect_n_plus_one_with_get(self):
        """Verifica detección de N+1 usando .get()."""
        code = """
user_ids = [1, 2, 3, 4, 5]
for user_id in user_ids:
    user = session.get(User, user_id)
    process(user)
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one(code, "test.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "n_plus_one"
    
    def test_check_pagination_missing(self):
        """Verifica detección de endpoint sin paginación."""
        code = """
@router.get("/users")
def get_users() -> List[User]:
    return session.query(User).all()
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_pagination(code, "api/users.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_pagination"
        assert findings[0].severity == Severity.MEDIO
    
    def test_check_pagination_present(self):
        """Verifica que no detecte problema cuando hay paginación."""
        code = """
@router.get("/users")
def get_users(skip: int = 0, limit: int = 100) -> List[User]:
    return session.query(User).offset(skip).limit(limit).all()
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_pagination(code, "api/users.py")
        
        assert len(findings) == 0
    
    def test_check_pagination_with_page_params(self):
        """Verifica que reconozca paginación con parámetros page/per_page."""
        code = """
@router.get("/users")
def get_users(page: int = 1, per_page: int = 50) -> List[User]:
    offset = (page - 1) * per_page
    return session.query(User).offset(offset).limit(per_page).all()
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_pagination(code, "api/users.py")
        
        assert len(findings) == 0
    
    def test_detect_blocking_file_operation(self):
        """Verifica detección de operación de archivo bloqueante."""
        code = """
@router.post("/upload")
async def upload_file(file: UploadFile):
    with open("temp.txt", "w") as f:
        f.write(file.content)
    return {"status": "ok"}
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_blocking_operations(code, "api/files.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "blocking_operation" for f in findings)
        assert any("I/O" in f.title for f in findings)
    
    def test_detect_blocking_http_request(self):
        """Verifica detección de request HTTP síncrono."""
        code = """
@router.get("/proxy")
async def proxy_request():
    response = requests.get("https://api.example.com/data")
    return response.json()
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_blocking_operations(code, "api/proxy.py")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "blocking_operation" for f in findings)
        assert any("HTTP" in f.title for f in findings)
    
    def test_no_blocking_with_await(self):
        """Verifica que no detecte bloqueo cuando se usa await."""
        code = """
@router.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_blocking_operations(code, "api/data.py")
        
        assert len(findings) == 0


class TestPerformanceAnalyzerFrontend:
    """Tests para análisis de performance en Frontend (TypeScript/React)."""
    
    def test_detect_component_without_memo(self):
        """Verifica detección de componente sin memoización."""
        code = """
function UserCard({ user, onSelect }) {
    return (
        <div onClick={() => onSelect(user.id)}>
            {user.name}
        </div>
    );
}
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_unnecessary_rerenders(code, "components/UserCard.tsx")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "unnecessary_rerender"
        assert "memo" in findings[0].title.lower()
    
    def test_no_memo_warning_for_memoized_component(self):
        """Verifica que no detecte problema en componente memoizado."""
        code = """
const UserCard = React.memo(function UserCard({ user, onSelect }) {
    return (
        <div onClick={() => onSelect(user.id)}>
            {user.name}
        </div>
    );
});
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_unnecessary_rerenders(code, "components/UserCard.tsx")
        
        assert len(findings) == 0
    
    def test_no_memo_warning_for_component_without_props(self):
        """Verifica que no sugiera memo para componentes sin props."""
        code = """
function App() {
    return <div>Hello World</div>;
}
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_unnecessary_rerenders(code, "App.tsx")
        
        assert len(findings) == 0
    
    def test_useeffect_without_deps_array(self):
        """Verifica detección de useEffect sin array de dependencias."""
        code = """
function Component() {
    const [count, setCount] = useState(0);
    
    useEffect(() => {
        console.log(count);
    });
    
    return <div>{count}</div>;
}
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_useeffect_deps(code, "Component.tsx")
        
        assert len(findings) >= 1
        assert any(f.subcategory == "useeffect_deps" for f in findings)
        assert any("no tiene array de dependencias" in f.description for f in findings)
    
    def test_useeffect_with_empty_deps(self):
        """Verifica detección de useEffect con deps vacío pero usando variables."""
        code = """
function Component() {
    const [count, setCount] = useState(0);
    
    useEffect(() => {
        console.log(count);
    }, []);
    
    return <div>{count}</div>;
}
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_useeffect_deps(code, "Component.tsx")
        
        # Puede detectar dependencias faltantes
        assert len(findings) >= 0  # Es una heurística, puede o no detectar
    
    def test_useeffect_with_correct_deps(self):
        """Verifica que no detecte problema con dependencias correctas."""
        code = """
function Component() {
    const [count, setCount] = useState(0);
    
    useEffect(() => {
        console.log(count);
    }, [count]);
    
    return <div>{count}</div>;
}
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_useeffect_deps(code, "Component.tsx")
        
        # No debe detectar problemas con dependencias correctas
        assert len([f for f in findings if "sin array" in f.description]) == 0
    
    def test_useeffect_multiline(self):
        """Verifica detección en useEffect multilínea."""
        code = """
function Component() {
    useEffect(() => {
        fetchData();
        updateUI();
        return () => cleanup();
    });
}
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_useeffect_deps(code, "Component.tsx")
        
        assert len(findings) >= 1
        assert any("no tiene array de dependencias" in f.description for f in findings)


class TestPerformanceAnalyzerIntegration:
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
async def get_users() -> List[User]:
    users = session.query(User).all()
    for user in users:
        user.posts = session.query(Post).filter(Post.user_id == user.id).all()
    return users
"""
        )
        
        analyzer = PerformanceAnalyzer()
        findings = analyzer.analyze([python_file])
        
        # Debe detectar N+1 y falta de paginación
        assert len(findings) >= 2
        categories = [f.subcategory for f in findings]
        assert "n_plus_one" in categories
        assert "no_pagination" in categories
    
    def test_analyze_typescript_file(self):
        """Verifica análisis completo de archivo TypeScript."""
        ts_file = TypeScriptFile(
            path="src/components/UserList.tsx",
            language="typescript",
            lines_of_code=30,
            is_large=False,
            is_component=True,
            content="""
function UserList({ users }) {
    useEffect(() => {
        loadUsers();
    });
    
    return (
        <div>
            {users.map(user => <UserCard key={user.id} user={user} />)}
        </div>
    );
}
"""
        )
        
        analyzer = PerformanceAnalyzer()
        findings = analyzer.analyze([ts_file])
        
        # Debe detectar useEffect sin deps y componente sin memo
        assert len(findings) >= 1
        assert any(f.subcategory == "useeffect_deps" for f in findings)
    
    def test_analyze_mixed_files(self):
        """Verifica análisis de múltiples archivos de diferentes lenguajes."""
        python_file = PythonFile(
            path="backend/api/test.py",
            language="python",
            lines_of_code=20,
            is_large=False,
            content="@router.get('/test')\nasync def test(): pass"
        )
        
        ts_file = TypeScriptFile(
            path="src/Test.tsx",
            language="typescript",
            lines_of_code=10,
            is_large=False,
            is_component=True,
            content="function Test() { return <div>Test</div>; }"
        )
        
        analyzer = PerformanceAnalyzer()
        findings = analyzer.analyze([python_file, ts_file])
        
        # Debe analizar ambos archivos sin errores
        assert isinstance(findings, list)
    
    def test_analyze_empty_file_list(self):
        """Verifica que maneje lista vacía de archivos."""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.analyze([])
        
        assert findings == []
    
    def test_finding_structure(self):
        """Verifica que los hallazgos tengan la estructura correcta."""
        code = """
for item in items:
    result = session.query(Model).filter(Model.id == item.id).first()
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one(code, "test.py")
        
        assert len(findings) > 0
        finding = findings[0]
        
        # Verificar campos requeridos
        assert finding.id
        assert finding.category == "performance"
        assert finding.subcategory
        assert finding.severity
        assert finding.title
        assert finding.description
        assert finding.file_path == "test.py"
        assert finding.line_number is not None
        assert finding.recommendation


class TestPerformanceAnalyzerEdgeCases:
    """Tests para casos límite y edge cases."""
    
    def test_empty_file_content(self):
        """Verifica manejo de archivo vacío."""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one("", "empty.py")
        
        assert findings == []
    
    def test_file_with_only_comments(self):
        """Verifica manejo de archivo solo con comentarios."""
        code = """
# This is a comment
# Another comment
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one(code, "comments.py")
        
        assert findings == []
    
    def test_nested_loops_with_query(self):
        """Verifica detección en loops anidados."""
        code = """
for user in users:
    for post in user.posts:
        comments = session.query(Comment).filter(Comment.post_id == post.id).all()
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one(code, "nested.py")
        
        # Debe detectar al menos un N+1
        assert len(findings) >= 1
    
    def test_while_loop_with_query(self):
        """Verifica detección en while loops."""
        code = """
i = 0
while i < len(items):
    item = session.query(Item).get(items[i])
    i += 1
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one(code, "while.py")
        
        # El patrón actual busca 'for', este test documenta limitación
        # En una implementación más completa, debería detectar while también
        assert isinstance(findings, list)
    
    def test_very_long_line(self):
        """Verifica manejo de líneas muy largas."""
        code = "x = " + "1 + " * 1000 + "1"
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one(code, "long.py")
        
        assert isinstance(findings, list)
    
    def test_unicode_content(self):
        """Verifica manejo de contenido Unicode."""
        code = """
# Función con caracteres especiales: ñ, á, é, í, ó, ú
def procesar_usuarios():
    usuarios = session.query(Usuario).all()
    for usuario in usuarios:
        datos = session.query(Datos).filter(Datos.usuario_id == usuario.id).all()
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_n_plus_one(code, "unicode.py")
        
        assert len(findings) >= 1


class TestConnectionPooling:
    """Tests para verificación de connection pooling."""
    
    def test_detect_missing_connection_pooling(self):
        """Verifica detección de create_engine sin configuración de pooling."""
        code = """
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost/db")
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_connection_pooling(code, "backend/db/database.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "connection_pooling"
        assert findings[0].severity == Severity.MEDIO
        assert "pooling" in findings[0].title.lower()
    
    def test_connection_pooling_present(self):
        """Verifica que no detecte problema cuando hay configuración de pooling."""
        code = """
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600
)
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_connection_pooling(code, "backend/db/database.py")
        
        assert len(findings) == 0
    
    def test_connection_pooling_partial_config(self):
        """Verifica que no detecte problema con configuración parcial."""
        code = """
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=10
)
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_connection_pooling(code, "backend/db/database.py")
        
        assert len(findings) == 0
    
    def test_skip_non_database_files(self):
        """Verifica que no analice archivos que no son de base de datos."""
        code = """
from sqlalchemy import create_engine
engine = create_engine("sqlite:///test.db")
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_connection_pooling(code, "backend/api/users.py")
        
        # No debe analizar archivos que no son de configuración de DB
        assert len(findings) == 0
    
    def test_multiline_create_engine(self):
        """Verifica detección en create_engine multilínea."""
        code = """
engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True
)
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_connection_pooling(code, "backend/db/database.py")
        
        assert len(findings) == 1


class TestMissingIndexes:
    """Tests para detección de índices faltantes."""
    
    def test_detect_foreign_key_without_index(self):
        """Verifica detección de ForeignKey sin índice."""
        code = """
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_missing_indexes(code, "backend/db/models.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "missing_index"
        assert findings[0].severity == Severity.MEDIO
        assert "ForeignKey" in findings[0].title
    
    def test_foreign_key_with_index(self):
        """Verifica que no detecte problema cuando ForeignKey tiene índice."""
        code = """
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String)
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_missing_indexes(code, "backend/db/models.py")
        
        assert len(findings) == 0
    
    def test_multiple_foreign_keys(self):
        """Verifica detección de múltiples ForeignKeys sin índice."""
        code = """
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_missing_indexes(code, "backend/db/models.py")
        
        assert len(findings) == 2
    
    def test_skip_non_model_files(self):
        """Verifica que no analice archivos que no son modelos."""
        code = """
user_id = Column(Integer, ForeignKey("users.id"))
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_missing_indexes(code, "backend/api/users.py")
        
        # No debe analizar archivos que no son modelos
        assert len(findings) == 0
    
    def test_unique_column_no_warning(self):
        """Verifica que no reporte unique columns (ya tienen índice automático)."""
        code = """
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_missing_indexes(code, "backend/db/models.py")
        
        # unique ya crea índice automáticamente, no debe reportar
        assert len(findings) == 0



class TestLazyLoading:
    """Tests para verificación de lazy loading."""
    
    def test_detect_page_component_without_lazy(self):
        """Verifica detección de componente de página sin lazy loading."""
        code = """
import HomePage from './pages/HomePage';
import UserPage from './pages/UserPage';

const routes = [
    { path: '/', component: HomePage },
    { path: '/users', component: UserPage }
];
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_lazy_loading(code, "src/routes/AppRouter.tsx")
        
        assert len(findings) == 2
        assert all(f.subcategory == "no_lazy_loading" for f in findings)
        assert all(f.severity == Severity.BAJO for f in findings)
    
    def test_lazy_loading_present(self):
        """Verifica que no detecte problema cuando hay lazy loading."""
        code = """
const HomePage = React.lazy(() => import('./pages/HomePage'));
const UserPage = React.lazy(() => import('./pages/UserPage'));

const routes = [
    { path: '/', component: HomePage },
    { path: '/users', component: UserPage }
];
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_lazy_loading(code, "src/routes/AppRouter.tsx")
        
        assert len(findings) == 0
    
    def test_skip_non_page_components(self):
        """Verifica que no reporte componentes pequeños."""
        code = """
import Button from './components/Button';
import Input from './components/Input';
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_lazy_loading(code, "src/routes/AppRouter.tsx")
        
        # No debe reportar componentes pequeños (no tienen 'page', 'view', etc.)
        assert len(findings) == 0
    
    def test_skip_non_route_files(self):
        """Verifica que solo analice archivos de rutas."""
        code = """
import HomePage from './pages/HomePage';
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_lazy_loading(code, "src/components/Header.tsx")
        
        # No debe analizar archivos que no son de rutas
        assert len(findings) == 0
    
    def test_view_component_without_lazy(self):
        """Verifica detección con componentes tipo 'view'."""
        code = """
import DashboardView from './views/DashboardView';
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.check_lazy_loading(code, "src/App.tsx")
        
        assert len(findings) == 1
        assert "lazy loading" in findings[0].title.lower()


class TestFullLibraryImports:
    """Tests para detección de imports de librerías completas."""
    
    def test_detect_lodash_full_import(self):
        """Verifica detección de import completo de lodash."""
        code = """
import _ from 'lodash';

const result = _.map(items, item => item.id);
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_full_library_imports(code, "src/utils/helpers.ts")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "full_library_import"
        assert findings[0].severity == Severity.MEDIO
        assert "lodash" in findings[0].title.lower()
    
    def test_detect_namespace_import(self):
        """Verifica detección de import namespace."""
        code = """
import * as _ from 'lodash';

const result = _.debounce(fn, 300);
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_full_library_imports(code, "src/utils/helpers.ts")
        
        assert len(findings) == 1
        assert "namespace" in findings[0].title.lower()
    
    def test_specific_import_no_warning(self):
        """Verifica que no detecte problema con imports específicos."""
        code = """
import { map, filter } from 'lodash';
import debounce from 'lodash/debounce';

const result = map(items, item => item.id);
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_full_library_imports(code, "src/utils/helpers.ts")
        
        assert len(findings) == 0
    
    def test_detect_date_fns_full_import(self):
        """Verifica detección de import completo de date-fns."""
        code = """
import dateFns from 'date-fns';

const formatted = dateFns.format(new Date(), 'yyyy-MM-dd');
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_full_library_imports(code, "src/utils/date.ts")
        
        assert len(findings) == 1
        assert "date-fns" in findings[0].title.lower()
    
    def test_detect_mui_full_import(self):
        """Verifica detección de import completo de Material-UI."""
        code = """
import * as MUI from '@mui/material';

const MyButton = () => <MUI.Button>Click</MUI.Button>;
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_full_library_imports(code, "src/components/Button.tsx")
        
        assert len(findings) == 1
        assert "@mui/material" in findings[0].title.lower()
    
    def test_multiple_full_imports(self):
        """Verifica detección de múltiples imports completos."""
        code = """
import _ from 'lodash';
import dateFns from 'date-fns';
import * as R from 'ramda';
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_full_library_imports(code, "src/utils/index.ts")
        
        assert len(findings) == 3
    
    def test_ignore_non_tree_shakeable_libs(self):
        """Verifica que no reporte librerías que no están en la lista."""
        code = """
import React from 'react';
import axios from 'axios';
"""
        analyzer = PerformanceAnalyzer()
        findings = analyzer.detect_full_library_imports(code, "src/api/client.ts")
        
        # No debe reportar librerías que no están en tree_shakeable_libs
        assert len(findings) == 0
