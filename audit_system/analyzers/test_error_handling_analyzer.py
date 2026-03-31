"""
Tests para ErrorHandlingAnalyzer.

Valida la detección de problemas en el manejo de errores en código Backend.
"""

import pytest
from audit_system.analyzers.error_handling_analyzer import ErrorHandlingAnalyzer
from audit_system.models import SourceFile, Severity


@pytest.fixture
def analyzer():
    """Fixture que retorna una instancia de ErrorHandlingAnalyzer."""
    return ErrorHandlingAnalyzer()


class TestCheckTryExceptLogging:
    """Tests para check_try_except_logging."""
    
    def test_detects_except_without_logging(self, analyzer):
        """Detecta except sin logging."""
        code = """
        try:
            risky_operation()
        except ValueError as e:
            return None
        """
        findings = analyzer.check_try_except_logging(code, "module.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_logging"
        assert findings[0].severity == Severity.MEDIO
    
    def test_no_finding_with_logger(self, analyzer):
        """No reporta cuando usa logger."""
        code = """
        try:
            risky_operation()
        except ValueError as e:
            logger.error(f'Error: {e}', exc_info=True)
        """
        findings = analyzer.check_try_except_logging(code, "module.py")
        
        assert len(findings) == 0
    
    def test_no_finding_with_logging_module(self, analyzer):
        """No reporta cuando usa logging."""
        code = """
        try:
            risky_operation()
        except ValueError as e:
            logging.exception('Error occurred')
        """
        findings = analyzer.check_try_except_logging(code, "module.py")
        
        assert len(findings) == 0
    
    def test_no_finding_with_print(self, analyzer):
        """No reporta cuando usa print (aunque no es ideal)."""
        code = """
        try:
            risky_operation()
        except ValueError as e:
            print(f'Error: {e}')
        """
        findings = analyzer.check_try_except_logging(code, "module.py")
        
        assert len(findings) == 0
    
    def test_no_finding_with_pass(self, analyzer):
        """No reporta pass vacío aquí (se maneja en detect_silenced_errors)."""
        code = """
        try:
            risky_operation()
        except ValueError:
            pass
        """
        findings = analyzer.check_try_except_logging(code, "module.py")
        
        assert len(findings) == 0


class TestDetectGenericExceptions:
    """Tests para detect_generic_exceptions."""
    
    def test_detects_bare_except(self, analyzer):
        """Detecta except: sin tipo."""
        code = """
        try:
            risky_operation()
        except:
            handle_error()
        """
        findings = analyzer.detect_generic_exceptions(code, "module.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "generic_exception"
        assert findings[0].severity == Severity.MEDIO
    
    def test_detects_except_exception(self, analyzer):
        """Detecta except Exception."""
        code = "try:\n    risky_operation()\nexcept Exception as e:\n    handle_error(e)"
        findings = analyzer.detect_generic_exceptions(code, "module.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "generic_exception"
        assert findings[0].severity == Severity.BAJO
    
    def test_no_finding_with_specific_exception(self, analyzer):
        """No reporta cuando usa excepción específica."""
        code = """
        try:
            risky_operation()
        except ValueError as e:
            handle_error(e)
        """
        findings = analyzer.detect_generic_exceptions(code, "module.py")
        
        assert len(findings) == 0
    
    def test_no_finding_with_multiple_specific_exceptions(self, analyzer):
        """No reporta cuando usa múltiples excepciones específicas."""
        code = """
        try:
            risky_operation()
        except (ValueError, TypeError) as e:
            handle_error(e)
        """
        findings = analyzer.detect_generic_exceptions(code, "module.py")
        
        assert len(findings) == 0
    
    def test_detects_multiple_bare_excepts(self, analyzer):
        """Detecta múltiples except: en el mismo archivo."""
        code = """
        try:
            operation1()
        except:
            pass
        
        try:
            operation2()
        except:
            pass
        """
        findings = analyzer.detect_generic_exceptions(code, "module.py")
        
        assert len(findings) == 2


class TestCheckApiErrorCodes:
    """Tests para check_api_error_codes."""
    
    def test_detects_http_exception_without_status_code(self, analyzer):
        """Detecta HTTPException sin status_code."""
        code = """
        if not user:
            raise HTTPException(detail="User not found")
        """
        findings = analyzer.check_api_error_codes(code, "api/users.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "api_error_code"
        assert findings[0].severity == Severity.MEDIO
    
    def test_no_finding_with_status_code(self, analyzer):
        """No reporta cuando especifica status_code."""
        code = """
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        """
        findings = analyzer.check_api_error_codes(code, "api/users.py")
        
        assert len(findings) == 0
    
    def test_detects_200_in_except_block(self, analyzer):
        """Detecta status_code 200 en bloque except."""
        code = """
        try:
            process_data()
        except ValueError:
            return JSONResponse(status_code=200, content={"error": "Invalid"})
        """
        findings = analyzer.check_api_error_codes(code, "api/data.py")
        
        assert len(findings) == 1
        assert findings[0].severity == Severity.ALTO
    
    def test_no_finding_for_200_outside_except(self, analyzer):
        """No reporta 200 fuera de bloques except."""
        code = """
        def get_user():
            user = fetch_user()
            return JSONResponse(status_code=200, content=user)
        """
        findings = analyzer.check_api_error_codes(code, "api/users.py")
        
        assert len(findings) == 0
    
    def test_ignores_non_api_files(self, analyzer):
        """Ignora archivos que no son de API."""
        code = """
        raise HTTPException(detail="Error")
        """
        findings = analyzer.check_api_error_codes(code, "utils/helper.py")
        
        assert len(findings) == 0


class TestDetectSilencedErrors:
    """Tests para detect_silenced_errors."""
    
    def test_detects_except_with_pass(self, analyzer):
        """Detecta except con pass vacío."""
        code = """
        try:
            risky_operation()
        except ValueError:
            pass
        """
        findings = analyzer.detect_silenced_errors(code, "module.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "silenced_error"
        assert findings[0].severity == Severity.ALTO
    
    def test_detects_bare_except_with_pass(self, analyzer):
        """Detecta except: con pass."""
        code = """
        try:
            risky_operation()
        except:
            pass
        """
        findings = analyzer.detect_silenced_errors(code, "module.py")
        
        assert len(findings) == 1
    
    def test_no_finding_with_actual_handling(self, analyzer):
        """No reporta cuando hay manejo real del error."""
        code = """
        try:
            risky_operation()
        except ValueError as e:
            logger.error(f'Error: {e}')
            return None
        """
        findings = analyzer.detect_silenced_errors(code, "module.py")
        
        assert len(findings) == 0
    
    def test_no_finding_with_pass_and_comment(self, analyzer):
        """Detecta pass incluso con comentario."""
        code = "try:\n    risky_operation()\nexcept ValueError:\n    # Intentional: this error is expected and can be ignored\n    pass"
        findings = analyzer.detect_silenced_errors(code, "module.py")
        
        # Aún detecta el pass (el comentario no lo hace válido, solo lo justifica)
        assert len(findings) == 1
    
    def test_detects_multiple_silenced_errors(self, analyzer):
        """Detecta múltiples errores silenciados."""
        code = """
        try:
            operation1()
        except ValueError:
            pass
        
        try:
            operation2()
        except TypeError:
            pass
        """
        findings = analyzer.detect_silenced_errors(code, "module.py")
        
        assert len(findings) == 2


class TestAnalyze:
    """Tests para el método analyze principal."""
    
    def test_analyzes_python_files(self, analyzer):
        """Analiza archivos Python."""
        file = SourceFile(
            path="module.py",
            language="python",
            lines_of_code=50,
            is_large=False,
            content="""
            try:
                risky_operation()
            except:
                pass
            """
        )
        
        findings = analyzer.analyze([file])
        
        assert len(findings) > 0
        assert all(f.category == "error_handling" for f in findings)
    
    def test_ignores_non_python_files(self, analyzer):
        """Ignora archivos que no son Python."""
        file = SourceFile(
            path="Component.tsx",
            language="typescript",
            lines_of_code=50,
            is_large=False,
            content="try { } catch (e) { }"
        )
        
        findings = analyzer.analyze([file])
        
        assert len(findings) == 0
    
    def test_analyzes_multiple_files(self, analyzer):
        """Analiza múltiples archivos."""
        files = [
            SourceFile(
                path="module1.py",
                language="python",
                lines_of_code=30,
                is_large=False,
                content="try:\n    pass\nexcept:\n    pass"
            ),
            SourceFile(
                path="module2.py",
                language="python",
                lines_of_code=40,
                is_large=False,
                content="try:\n    pass\nexcept Exception:\n    return None"
            )
        ]
        
        findings = analyzer.analyze(files)
        
        assert len(findings) >= 2
    
    def test_comprehensive_error_detection(self, analyzer):
        """Detecta múltiples tipos de problemas en un archivo."""
        file = SourceFile(
            path="api/users.py",
            language="python",
            lines_of_code=100,
            is_large=False,
            content="""
            try:
                user = get_user()
            except:
                pass
            
            try:
                data = process()
            except Exception as e:
                return {"status": "ok"}
            
            if not found:
                raise HTTPException(detail="Not found")
            """
        )
        
        findings = analyzer.analyze([file])
        
        # Debería detectar: bare except, pass, Exception genérico, HTTPException sin status_code
        assert len(findings) >= 3
