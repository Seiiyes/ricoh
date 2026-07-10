import pytest
import os
from unittest.mock import patch, MagicMock
from db.models import Printer
from fastapi.testclient import TestClient

@pytest.mark.integration
@patch.dict(os.environ, {"RICOH_ADMIN_PASSWORD": "test-env-password"})
class TestStoredJobsDeletion:
    """Test suite for stored job deletion backend logic and endpoints"""

    def test_delete_job_not_found_printer(self, client, db_session, superadmin_token):
        """Test DELETE /printers/{printer_id}/jobs/{job_id} returns 404 when printer does not exist"""
        response = client.delete(
            "/printers/99999/jobs/job123",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_job_forbidden_access(self, client, db_session, test_empresa, admin_token):
        """Test DELETE /printers/{printer_id}/jobs/{job_id} returns 403 when user does not have access"""
        # Create a printer belonging to a different company
        # We will create a printer with empresa_id = 99999
        printer = Printer(
            hostname="DiffPrinter",
            ip_address="192.168.1.55",
            status="ONLINE",
            empresa_id=99999,
            serial_number="DIFFSERIAL"
        )
        db_session.add(printer)
        db_session.commit()

        response = client.delete(
            f"/printers/{printer.id}/jobs/job123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower()

    @patch("services.ricoh_web_client.RicohWebClient.delete_stored_job")
    def test_delete_job_success(self, mock_delete_stored_job, client, db_session, test_empresa, superadmin_token):
        """Test DELETE /printers/{printer_id}/jobs/{job_id} deletes stored job successfully"""
        mock_delete_stored_job.return_value = True

        printer = Printer(
            hostname="TestPrinter",
            ip_address="192.168.91.250",
            status="ONLINE",
            empresa_id=test_empresa.id,
            serial_number="TESTSERIAL",
            admin_password="test-password"
        )
        db_session.add(printer)
        db_session.commit()

        response = client.delete(
            f"/printers/{printer.id}/jobs/job123",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]
        
        # Verify the client method was called with correct parameters
        mock_delete_stored_job.assert_called_once_with(
            printer.ip_address,
            "job123",
            admin_password="test-password",
            job_type="stored"
        )


    @patch("services.ricoh_web_client.RicohWebClient.delete_stored_job")
    def test_delete_job_failure_in_client(self, mock_delete_stored_job, client, db_session, test_empresa, superadmin_token):
        """Test DELETE /printers/{printer_id}/jobs/{job_id} returns 500 when client delete fails"""
        mock_delete_stored_job.return_value = False

        printer = Printer(
            hostname="TestPrinter",
            ip_address="192.168.91.250",
            status="ONLINE",
            empresa_id=test_empresa.id,
            serial_number="TESTSERIAL"
        )
        db_session.add(printer)
        db_session.commit()

        response = client.delete(
            f"/printers/{printer.id}/jobs/job123",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )

        assert response.status_code == 500
        assert "failed to delete job" in response.json()["detail"].lower()
