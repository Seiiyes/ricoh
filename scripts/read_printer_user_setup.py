#!/usr/bin/env python3
"""
Lee y muestra la configuración actual de libreta de direcciones para el usuario 00256
en la impresora 192.168.91.251.
"""
import sys
import io
from pathlib import Path
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.append(str(Path(__file__).parent.parent / "backend"))
from services.ricoh_web_client import RicohWebClient


def main():
    client = RicohWebClient(admin_password="admin")
    printer_ip = "192.168.91.253"
    
    if not client._authenticate(printer_ip):
        print("[ERROR] No se pudo autenticar")
        return
        
    print("[OK] Autenticado en la impresora.")
    
    # Obtener el formulario del usuario 00195
    list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
    list_resp = client.session.get(list_url, timeout=30)
    
    import re
    match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
    if not match:
        print("[ERROR] No se pudo extraer wimToken en el paso 1.")
        return
    wim_token = match.group(1)
    
    get_user_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
    get_user_data = {
        'wimToken': wim_token,
        'mode': 'MODUSER',
        'outputSpecifyModeIn': 'PROGRAMMED',
        'entryIndexIn': '00195'
    }
    user_resp = client.session.post(get_user_url, data=get_user_data, timeout=30)
    
    # Parsear con BeautifulSoup
    soup = BeautifulSoup(user_resp.text, 'html.parser')
    
    print("\n--- DETALLES ACTUALES EN LA LIBRETA DE DIRECCIONES (IMPRESORA) ---")
    print(f"Nombre en libreta: {soup.find('input', {'name': 'entryNameIn'}).get('value', '') if soup.find('input', {'name': 'entryNameIn'}) else 'None'}")
    print(f"Nombre a mostrar: {soup.find('input', {'name': 'entryDisplayNameIn'}).get('value', '') if soup.find('input', {'name': 'entryDisplayNameIn'}) else 'None'}")
    print(f"Codigo de Usuario (PIN): {soup.find('input', {'name': 'userCodeIn'}).get('value', '') if soup.find('input', {'name': 'userCodeIn'}) else 'None'}")
    
    # Detalles de Autenticación de Carpeta
    print(f"Ruta de carpeta (SMB): {soup.find('input', {'name': 'folderPathNameIn'}).get('value', '') if soup.find('input', {'name': 'folderPathNameIn'}) else 'None'}")
    print(f"Usuario de Autenticacion: {soup.find('input', {'name': 'folderAuthUserNameIn'}).get('value', '') if soup.find('input', {'name': 'folderAuthUserNameIn'}) else 'None'}")
    
    # Verificar si está configurada la autenticación
    auth_account_o = soup.find('input', {'name': 'folderAuthAccountIn', 'value': 'AUTH_ASSIGNMENT_O'})
    auth_checked = "SI (AUTH_ASSIGNMENT_O)" if auth_account_o and auth_account_o.has_attr('checked') else "NO (AUTH_SYSTEM_O)"
    print(f"¿Autenticacion SMB activa?: {auth_checked}")
    
    client.logout(printer_ip)


if __name__ == "__main__":
    main()
