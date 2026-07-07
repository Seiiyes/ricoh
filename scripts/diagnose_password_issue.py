#!/usr/bin/env python3
"""
Script de diagnóstico para probar el flujo de configuración de contraseña
de escáner SMB en la impresora real 192.168.91.251.
(ASCII safe version to prevent encoding issues on Windows)
"""
import sys
import os
import io
import requests
from pathlib import Path

# Configurar encoding a UTF-8 para consola de Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Añadir el backend al path para poder importar los servicios
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.ricoh_web_client import RicohWebClient
from services.ricoh_password_flow import RicohPasswordFlow


def main():
    print("="*60)
    print(" DIAGNOSTICANDO CONFIGURACION DE CONTRASEÑA EN 192.168.91.251")
    print("="*60)
    
    # 1. Crear sesión autenticada
    client = RicohWebClient(admin_password="admin")
    
    printer_ip = "192.168.91.251"
    print(f"1. Autenticando con la impresora {printer_ip}...")
    auth_success = client._authenticate(printer_ip)
    if not auth_success:
        print("[ERROR] Fallo la autenticacion inicial. ¿Contrasena incorrecta?")
        return
        
    print("[OK] Autenticado con exito en WIM.")
    
    # 2. Buscar un usuario de prueba en la libreta de direcciones
    print("\n2. Buscando un usuario existente o creando uno de prueba...")
    user_code = "7104" # Código real del usuario
    existing_user = client.find_specific_user(printer_ip, user_code, logout=False)
    
    if existing_user:
        entry_index = existing_user.get('entry_index')
        print(f"[OK] Usuario JUAN LIZARAZO encontrado en el indice: {entry_index}")
    else:
        print("[INFO] El usuario JUAN LIZARAZO no existe. Creando...")
        user_config = {
            "nombre": "JUAN LIZARAZO",
            "codigo_de_usuario": user_code,
            "nombre_usuario_inicio_sesion": "reliteltda\\scaner",
            "contrasena_inicio_sesion": "Temporal2021",
            "funciones_disponibles": {
                "copiadora": True,
                "impresora": True,
                "escaner": True
            },
            "carpeta_smb": {
                "protocolo": "SMB",
                "servidor": "TIC0264",
                "ruta": "\\\\TIC0264\\Escaner"
            }
        }
        res = client.provision_user(printer_ip, user_config, logout=False)
        if isinstance(res, tuple) and res[0]:
            entry_index = res[1]
            print(f"[OK] Usuario de prueba creado en el indice: {entry_index}")
        else:
            print(f"[ERROR] Fallo la creacion del usuario. Resultado: {res}")
            return

    # 3. Ejecutar el flujo de contraseña detallado y capturar las respuestas HTML en cada paso
    print("\n3. Ejecutando flujo de contrasena de carpeta...")
    flow = RicohPasswordFlow(client.session, timeout=30)
    
    # Ejecutamos a mano los pasos de set_folder_password para poder volcar las respuestas
    try:
        # Paso 1: adrsList.cgi
        list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
        list_resp = client.session.get(list_url, timeout=30)
        with open("step1_list.html", "w", encoding="utf-8") as f:
            f.write(list_resp.text)
            
        import re
        match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
        if not match:
            print("[ERROR] No se pudo extraer wimToken en el paso 1.")
            return
        wim_token = match.group(1)
        print(f" - Paso 1 OK. wimToken: {wim_token}")
        
        # Paso 2: MODUSER
        get_user_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
        get_user_data = {
            'wimToken': wim_token,
            'mode': 'MODUSER',
            'outputSpecifyModeIn': 'PROGRAMMED',
            'entryIndexIn': entry_index.zfill(5)
        }
        user_resp = client.session.post(get_user_url, data=get_user_data, timeout=30)
        with open("step2_user_form.html", "w", encoding="utf-8") as f:
            f.write(user_resp.text)
            
        match = re.search(r'name="wimToken"\s+value="(\d+)"', user_resp.text)
        if not match:
            print("[ERROR] No se pudo extraer wimToken en el paso 2.")
            return
        wim_token = match.group(1)
        print(f" - Paso 2 OK. Nuevo wimToken: {wim_token}")
        
        # Paso 3: adrsEditPassword.cgi
        edit_password_url = f"http://{printer_ip}/web/entry/es/address/adrsEditPassword.cgi"
        edit_password_open_data = {
            'wimToken': wim_token,
            'mode': 'MODUSER',
            'wayFrom': 'adrsGetUser.cgi#AUTH_INFO_C?outputSpecifyModeIn=SETTINGS',
            'wayTo': 'adrsEditPassword.cgi?inputSpecifyMode=NONE&kind=FOLDER',
            'pageSpecifiedIn': '',
            'pageNumberIn': '',
            'outputSpecifyModeIn': '',
            'kind': 'FOLDER',
            'inputSpecifyMode': 'NONE'
        }
        pwd_form_resp = client.session.post(edit_password_url, data=edit_password_open_data, timeout=30)
        with open("step3_pwd_form.html", "w", encoding="utf-8") as f:
            f.write(pwd_form_resp.text)
            
        match = re.search(r'name="wimToken"\s+value="(\d+)"', pwd_form_resp.text)
        if not match:
            print("[ERROR] No se pudo extraer wimToken en el paso 3.")
            return
        wim_token = match.group(1)
        print(f" - Paso 3 OK. Nuevo wimToken: {wim_token}")
        
        # Paso 4: Enviar contraseña codificada
        import base64
        password_b64 = base64.b64encode("Temporal2021".encode()).decode()
        edit_password_submit_data = {
            'wimToken': wim_token,
            'mode': 'MODUSER',
            'kind': 'FOLDER',
            'inputSpecifyMode': 'FIX',
            'wayFrom': 'adrsEditPassword.cgi?inputSpecifyMode=NONE&kind=FOLDER',
            'wayTo': 'adrsGetUser.cgi#AUTH_INFO_C?outputSpecifyModeIn=SETTINGS',
            'pageSpecifiedIn': '',
            'pageNumberIn': '',
            'outputSpecifyModeIn': '',
            'passwordIn': '',
            'wkpasswordIn': password_b64,
            'passwordConfirmIn': '',
            'wkpasswordConfirmIn': password_b64
        }
        pwd_submit_resp = client.session.post(edit_password_url, data=edit_password_submit_data, timeout=30)
        with open("step4_pwd_submitted.html", "w", encoding="utf-8") as f:
            f.write(pwd_submit_resp.text)
            
        match = re.search(r'name="wimToken"\s+value="(\d+)"', pwd_submit_resp.text)
        if not match:
            print("[ERROR] No se pudo extraer wimToken en el paso 4.")
            return
        wim_token = match.group(1)
        print(f" - Paso 4 OK. Nuevo wimToken: {wim_token}")
        
        # Paso 5: Volver a MODUSER
        get_user_confirm_data = {
            'wimToken': wim_token,
            'mode': 'MODUSER',
            'kind': 'FOLDER',
            'inputSpecifyMode': 'FIX',
            'wayFrom': 'adrsEditPassword.cgi?inputSpecifyMode=NONE&kind=FOLDER',
            'wayTo': 'adrsGetUser.cgi#AUTH_INFO_C?outputSpecifyModeIn=SETTINGS',
            'pageSpecifiedIn': '',
            'pageNumberIn': '',
            'outputSpecifyModeIn': 'SETTINGS'
        }
        confirm_resp = client.session.post(get_user_url, data=get_user_confirm_data, timeout=30)
        with open("step5_confirm_user_form.html", "w", encoding="utf-8") as f:
            f.write(confirm_resp.text)
            
        match = re.search(r'name="wimToken"\s+value="(\d+)"', confirm_resp.text)
        if not match:
            print("[ERROR] No se pudo extraer wimToken en el paso 5.")
            return
        wim_token = match.group(1)
        print(f" - Paso 5 OK. Nuevo wimToken: {wim_token}")
        
        # Paso 6: Guardar
        set_user_url = f"http://{printer_ip}/web/entry/es/address/adrsSetUser.cgi"
        set_user_data = [
            ('inputSpecifyModeIn', 'WRITE'),
            ('listUpdateIn', 'UPDATE'),
            ('wimToken', wim_token),
            ('mode', 'MODUSER'),
            ('pageSpecifiedIn', ''),
            ('pageNumberIn', ''),
            ('outputSpecifyModeIn', ''),
            ('inputSpecifyModeIn', ''),
            ('wayFrom', 'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS'),
            ('wayTo', 'adrsList.cgi'),
            ('isSelfPasswordEditMode', 'false'),
            ('isLocalAuthPasswordUpdated', 'false'),
            ('isFolderAuthPasswordUpdated', 'true'),
            ('entryIndexIn', entry_index.zfill(5)),
            ('entryNameIn', "JUAN LIZARAZO"),
            ('entryDisplayNameIn', "JUAN LIZARAZO"),
            ('priorityIn', '5'),
            ('entryTagInfoIn', '1'),
            ('entryTagInfoIn', '1'),
            ('entryTagInfoIn', '1'),
            ('entryTagInfoIn', '1'),
            ('userCodeIn', user_code),
            ('smtpAuthAccountIn', 'AUTH_SYSTEM_O'),
            ('folderAuthAccountIn', 'AUTH_ASSIGNMENT_O'),
            ('folderAuthUserNameIn', "reliteltda\\scaner"),
            ('ldapAuthAccountIn', 'AUTH_SYSTEM_O'),
            ('entryUseIn', 'ENTRYUSE_TO_O'),
            ('entryUseIn', 'ENTRYUSE_FROM_O'),
            ('mailAddressIn', ''),
            ('isCertificateExist', 'false'),
            ('isEncryptAlways', 'false'),
            ('folderProtocolIn', 'SMB_O'),
            ('folderPathNameIn', "\\\\TIC0264\\Escaner"),
        ]
        final_resp = client.session.post(set_user_url, data=set_user_data, timeout=30)
        with open("step6_final_save.html", "w", encoding="utf-8") as f:
            f.write(final_resp.text)
            
        print(" - Paso 6 OK. Guardado completado.")
        print("\nAnalisis del resultado:")
        if "BADFLOW" in final_resp.text:
            print("[ERROR] BADFLOW detectado al guardar en paso 6.")
        elif "está siendo utilizado" in final_resp.text:
            print("[ERROR] La impresora esta ocupada.")
        elif "error" in final_resp.text.lower() or "se ha producido un error" in final_resp.text.lower():
            print("[ERROR] La impresora reporto un error en la interfaz.")
        else:
            print("[SUCCESS] ¡Aparentemente el flujo se completo de forma exitosa!")
            
    except Exception as e:
        print(f"[ERROR] Excepcion durante el flujo de prueba: {e}")
        
    client.logout(printer_ip)


if __name__ == "__main__":
    main()
