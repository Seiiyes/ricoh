"""
Tests unitarios para el módulo CLI.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

from audit_system.cli import parse_arguments, main


class TestParseArguments:
    """Tests para el parser de argumentos."""
    
    def test_parse_required_project_path(self):
        """Debe parsear el argumento requerido --project-path."""
        with patch('sys.argv', ['cli.py', '-p', '/path/to/project']):
            args = parse_arguments()
            assert args.project_path == '/path/to/project'
    
    def test_parse_output_path(self):
        """Debe parsear el argumento opcional --output."""
        with patch('sys.argv', ['cli.py', '-p', '.', '-o', 'custom/report.md']):
            args = parse_arguments()
            assert args.output == 'custom/report.md'
    
    def test_parse_verbose_flag(self):
        """Debe parsear el flag --verbose."""
        with patch('sys.argv', ['cli.py', '-p', '.', '--verbose']):
            args = parse_arguments()
            assert args.verbose is True
    
    def test_parse_categories(self):
        """Debe parsear el argumento --categories."""
        with patch('sys.argv', ['cli.py', '-p', '.', '-c', 'performance,security']):
            args = parse_arguments()
            assert args.categories == 'performance,security'
    
    def test_default_values(self):
        """Debe usar valores por defecto para argumentos opcionales."""
        with patch('sys.argv', ['cli.py', '-p', '.']):
            args = parse_arguments()
            assert args.output is None
            assert args.verbose is False
            assert args.categories is None


class TestMain:
    """Tests para la función main del CLI."""
    
    @patch('audit_system.cli.AuditOrchestrator')
    @patch('audit_system.cli.Path')
    def test_main_success(self, mock_path, mock_orchestrator):
        """Debe ejecutar auditoría exitosamente."""
        # Mock path validation
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = True
        mock_path_instance.resolve.return_value = Path('/resolved/path')
        mock_path.return_value = mock_path_instance
        
        # Mock orchestrator
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_audit.return_value = ("report", "output.md")
        mock_orchestrator.return_value = mock_orch_instance
        
        # Run with valid arguments
        with patch('sys.argv', ['cli.py', '-p', '.']):
            result = main()
        
        assert result == 0
        mock_orch_instance.run_audit.assert_called_once()
    
    @patch('audit_system.cli.Path')
    def test_main_invalid_path(self, mock_path):
        """Debe fallar si la ruta del proyecto no existe."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        with patch('sys.argv', ['cli.py', '-p', '/invalid/path']):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
    
    @patch('audit_system.cli.Path')
    def test_main_not_directory(self, mock_path):
        """Debe fallar si la ruta no es un directorio."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = False
        mock_path.return_value = mock_path_instance
        
        with patch('sys.argv', ['cli.py', '-p', 'file.txt']):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
    
    @patch('audit_system.cli.AuditOrchestrator')
    @patch('audit_system.cli.Path')
    def test_main_keyboard_interrupt(self, mock_path, mock_orchestrator):
        """Debe manejar interrupción del usuario."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = True
        mock_path_instance.resolve.return_value = Path('.')
        mock_path.return_value = mock_path_instance
        
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_audit.side_effect = KeyboardInterrupt()
        mock_orchestrator.return_value = mock_orch_instance
        
        with patch('sys.argv', ['cli.py', '-p', '.']):
            result = main()
        
        assert result == 130
    
    @patch('audit_system.cli.AuditOrchestrator')
    @patch('audit_system.cli.Path')
    def test_main_exception(self, mock_path, mock_orchestrator):
        """Debe manejar excepciones generales."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = True
        mock_path_instance.resolve.return_value = Path('.')
        mock_path.return_value = mock_path_instance
        
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_audit.side_effect = Exception("Test error")
        mock_orchestrator.return_value = mock_orch_instance
        
        with patch('sys.argv', ['cli.py', '-p', '.']):
            result = main()
        
        assert result == 1
