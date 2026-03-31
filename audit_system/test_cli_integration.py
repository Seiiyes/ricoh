"""
Tests de integración para el CLI.

Verifica que el CLI se integra correctamente con el AuditOrchestrator.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from audit_system.cli import main


class TestCLIIntegration:
    """Tests de integración del CLI con el sistema de auditoría."""
    
    @patch('audit_system.cli.AuditOrchestrator')
    def test_cli_calls_orchestrator_with_correct_params(self, mock_orchestrator):
        """Debe llamar al orquestador con los parámetros correctos."""
        # Setup
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_audit.return_value = ("report", "output.md")
        mock_orchestrator.return_value = mock_orch_instance
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_report.md")
            
            # Execute
            with patch('sys.argv', ['cli.py', '-p', tmpdir, '-o', output_path]):
                result = main()
            
            # Verify
            assert result == 0
            mock_orch_instance.run_audit.assert_called_once()
            call_args = mock_orch_instance.run_audit.call_args
            assert call_args[1]['output_path'] == output_path
    
    @patch('audit_system.cli.AuditOrchestrator')
    def test_cli_uses_default_output_path(self, mock_orchestrator):
        """Debe usar la ruta de salida por defecto si no se especifica."""
        # Setup
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_audit.return_value = ("report", "docs/OPTIMIZACION_HALLAZGOS.md")
        mock_orchestrator.return_value = mock_orch_instance
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Execute
            with patch('sys.argv', ['cli.py', '-p', tmpdir]):
                result = main()
            
            # Verify
            assert result == 0
            mock_orch_instance.run_audit.assert_called_once()
            call_args = mock_orch_instance.run_audit.call_args
            # Should use None, letting orchestrator use default
            assert call_args[1]['output_path'] is None
    
    @patch('audit_system.cli.AuditOrchestrator')
    @patch('audit_system.cli.update_config')
    def test_cli_enables_verbose_logging(self, mock_update_config, mock_orchestrator):
        """Debe habilitar logging verbose cuando se especifica."""
        # Setup
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_audit.return_value = ("report", "output.md")
        mock_orchestrator.return_value = mock_orch_instance
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Execute
            with patch('sys.argv', ['cli.py', '-p', tmpdir, '--verbose']):
                result = main()
            
            # Verify
            assert result == 0
            mock_update_config.assert_called_once_with(LOG_LEVEL="DEBUG")
    
    @patch('audit_system.cli.AuditOrchestrator')
    def test_cli_handles_orchestrator_exception(self, mock_orchestrator):
        """Debe manejar excepciones del orquestador."""
        # Setup
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_audit.side_effect = Exception("Orchestrator error")
        mock_orchestrator.return_value = mock_orch_instance
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Execute
            with patch('sys.argv', ['cli.py', '-p', tmpdir]):
                result = main()
            
            # Verify
            assert result == 1
