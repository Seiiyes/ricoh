import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = "192.168.91.131"
USERNAME = "odootic"
PASSWORD = "Zuly152325*"

python_code = """
import requests
import re
import base64
import logging
from bs4 import BeautifulSoup
from db.database import SessionLocal
from db.models import User, Printer
from services.ricoh_web_client import get_ricoh_web_client

logging.basicConfig(level=logging.DEBUG)

db = SessionLocal()
try:
    user = db.query(User).filter(User.codigo_de_usuario == "7104").first()
    printer = db.query(Printer).filter(Printer.ip_address == "192.168.91.251").first()
    
    print(f"User: {user.name}, Printer: {printer.ip_address}")
    
    client = get_ricoh_web_client()
    client.reset_session()
    
    # 1. Authenticate
    print("Authenticating...")
    auth_success = client._authenticate(printer.ip_address, admin_password=printer.admin_password)
    print(f"Auth result: {auth_success}")
    
    session = client.session
    
    # 2. Get entry index dynamically
    print("Finding user on printer...")
    existing_user = client.find_specific_user(printer.ip_address, user.codigo_de_usuario, admin_password=printer.admin_password)
    if not existing_user:
        print("❌ User not found on printer!")
        sys.exit(1)
        
    entry_index = existing_user.get('entry_index')
    print(f"User slot index: {entry_index}")
    
    # 3. Get list page and token
    list_url = f"http://{printer.ip_address}/web/entry/es/address/adrsList.cgi"
    resp = session.get(list_url)
    match = re.search(r'name="wimToken"[ \\t]+value="([0-9]+)"', resp.text)
    if not match:
        print("❌ Could not match initial token!")
        # Save HTML
        with open("debug_list_page.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        sys.exit(1)
        
    wim_token = match.group(1)
    print(f"Initial token: {wim_token}")
    
    # 4. Load batch (Ajax)
    batch = (int(entry_index) // 50) + 1
    ajax_url = f"http://{printer.ip_address}/web/entry/es/address/adrsListLoadEntry.cgi"
    ajax_data = {
        'wimToken': wim_token,
        'listCountIn': '50',
        'getCountIn': str(batch)
    }
    ajax_headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': list_url,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    print(f"Loading batch {batch}...")
    ajax_resp = session.post(ajax_url, data=ajax_data, headers=ajax_headers)
    print(f"Batch loaded status: {ajax_resp.status_code}")
    
    # 5. Get User form with Referer
    get_user_url = f"http://{printer.ip_address}/web/entry/es/address/adrsGetUser.cgi"
    get_user_data = {
        'wimToken': wim_token,
        'mode': 'MODUSER',
        'outputSpecifyModeIn': 'PROGRAMMED', # Changed from SETTINGS
        'entryIndexIn': entry_index
    }
    get_user_headers = {
        'Referer': list_url,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    print(f"Is login form in list response? {'authForm.cgi' in resp.text}")
    print("Getting User form (Step 2)...")
    user_form_response = session.post(get_user_url, data=get_user_data, headers=get_user_headers)
    print(f"User form status: {user_form_response.status_code}")
    if "Tiempo de sesión agotado" in user_form_response.text or "TIMEOUT" in user_form_response.text:
        print("❌ TIMEOUT detected in Step 2!")
        with open("debug_step2_fail.html", "w", encoding="utf-8") as f:
            f.write(user_form_response.text)
    else:
        print("✅ Step 2 Succeeded!")
        match = re.search(r'name="wimToken"[ \\t]+value="([0-9]+)"', user_form_response.text)
        wim_token = match.group(1)
        print(f"Next token: {wim_token}")
        
        # 5. Open password form (Step 3)
        edit_password_url = f"http://{printer.ip_address}/web/entry/es/address/adrsEditPassword.cgi"
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
        edit_password_headers = {
            'Referer': get_user_url,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        print("Opening password form (Step 3)...")
        password_form_response = session.post(edit_password_url, data=edit_password_open_data, headers=edit_password_headers)
        print(f"Password form status: {password_form_response.status_code}")
        
        if "TIMEOUT" in password_form_response.text:
            print("❌ TIMEOUT in Step 3!")
        else:
            print("✅ Step 3 Succeeded!")
            
finally:
    db.close()
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
    sftp = client.open_sftp()
    with sftp.open('/home/odootic/ricoh-app/backend/test_single_debug.py', 'w') as f:
        f.write(python_code)
    sftp.close()
    
    stdin, stdout, stderr = client.exec_command("echo 'Zuly152325*' | sudo -S docker exec ricoh-backend python test_single_debug.py")
    print(stdout.read().decode('utf-8', errors='replace').strip())
    print(stderr.read().decode('utf-8', errors='replace').strip())
    
    client.exec_command("rm /home/odootic/ricoh-app/backend/test_single_debug.py")
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
