import pytest
from fastapi import status
from datetime import date
from db.models import CierreMensual, CierreMensualUsuario, Printer, User, Empresa
from db.repository import UserRepository

def test_delete_monthly_close_success(client, db_session, admin_user, admin_token):
    # Setup: Create printer in the admin's company
    printer = Printer(
        hostname="printer-test-delete",
        ip_address="192.168.1.100",
        empresa_id=admin_user.empresa_id,
        status="ONLINE"
    )
    db_session.add(printer)
    db_session.commit()

    # Create a normal end-user
    normal_user = UserRepository.create(
        db=db_session,
        name="User Test Deletion",
        codigo_de_usuario="1234",
        network_username="reliteltda\\scaner",
        network_password_encrypted="encryptedpassword",
        smb_server="server",
        smb_port=21,
        smb_path="path"
    )
    normal_user.empresa_id = admin_user.empresa_id
    db_session.commit()

    cierre = CierreMensual(
        printer_id=printer.id,
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 30),
        anio=2026,
        mes=6,
        total_paginas=1000,
        cerrado_por="test_admin"
    )
    db_session.add(cierre)
    db_session.commit()

    cierre_usuario = CierreMensualUsuario(
        cierre_mensual_id=cierre.id,
        user_id=normal_user.id,
        total_paginas=500,
        total_bn=400,
        total_color=100,
        copiadora_bn=0,
        copiadora_color=0,
        impresora_bn=0,
        impresora_color=0,
        escaner_bn=0,
        escaner_color=0,
        fax_bn=0,
        consumo_total=500,
        consumo_copiadora=0,
        consumo_impresora=0,
        consumo_escaner=0,
        consumo_fax=0
    )
    db_session.add(cierre_usuario)
    db_session.commit()

    closure_id = cierre.id

    # Verify records exist before delete
    assert db_session.query(CierreMensual).filter(CierreMensual.id == closure_id).first() is not None
    assert db_session.query(CierreMensualUsuario).filter(CierreMensualUsuario.cierre_mensual_id == closure_id).first() is not None

    # Perform DELETE
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/api/counters/monthly/{closure_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Cierre de contadores eliminado correctamente"

    # Verify records are deleted (cascade works)
    db_session.expire_all()
    assert db_session.query(CierreMensual).filter(CierreMensual.id == closure_id).first() is None
    assert db_session.query(CierreMensualUsuario).filter(CierreMensualUsuario.cierre_mensual_id == closure_id).first() is None


def test_delete_monthly_close_not_found(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete("/api/counters/monthly/99999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "El cierre no fue encontrado"


def test_delete_monthly_close_forbidden(client, db_session, admin_token):
    # Setup: Create another company
    other_empresa = Empresa(
        razon_social="Other Company S.A.S.",
        nombre_comercial="other-company",
        nit="900888999-1",
        email="other@company.com",
        is_active=True
    )
    db_session.add(other_empresa)
    db_session.commit()

    printer = Printer(
        hostname="printer-other-company",
        ip_address="192.168.2.100",
        empresa_id=other_empresa.id,
        status="ONLINE"
    )
    db_session.add(printer)
    db_session.commit()

    cierre = CierreMensual(
        printer_id=printer.id,
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 30),
        anio=2026,
        mes=6,
        total_paginas=1000,
        cerrado_por="test_user"
    )
    db_session.add(cierre)
    db_session.commit()

    # Admin user of the first company tries to delete closure of second company's printer
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/api/counters/monthly/{cierre.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
