"""
Scan the edit user form checkboxes for user index '00001' on all 5 printers to map color permissions correctly.
"""
import sys
sys.path.insert(0, '/app')

import re
from bs4 import BeautifulSoup
from services.ricoh_web_client import get_ricoh_web_client
from db.database import SessionLocal
from db.repository import PrinterRepository

printers = [
    "192.168.110.250",
    "192.168.91.250",
    "192.168.91.251",
    "192.168.91.252",
    "192.168.91.253"
]

db = SessionLocal()
client = get_ricoh_web_client()

for ip in printers:
    print(f"\n=== Printer {ip} ===")
    printer = PrinterRepository.get_by_ip(db, ip)
    admin_password = printer.admin_password if printer else None
    
    client.reset_session()
    if not client._authenticate(ip, admin_password):
        print("Auth failed")
        continue
        
    try:
        # Get wimToken
        list_url = f"http://{ip}/web/entry/es/address/adrsList.cgi"
        list_resp = client.session.get(list_url, timeout=15)
        wim_token = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text).group(1)
        
        # Load batch 1
        ajax_url = f"http://{ip}/web/entry/es/address/adrsListLoadEntry.cgi"
        client.session.post(ajax_url, data={'wimToken': wim_token, 'listCountIn': '50', 'getCountIn': '1'}, headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': list_url
        }, timeout=15)
        
        # Request edit user form for index '00001'
        edit_url = f"http://{ip}/web/entry/es/address/adrsGetUser.cgi"
        form_data = {
            'wimToken': wim_token,
            'mode': 'MODUSER',
            'outputSpecifyModeIn': 'PROGRAMMED',
            'inputSpecifyModeIn': 'READ',
            'entryIndexIn': '00001'
        }
        headers = {
            'Referer': list_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        resp = client.session.post(edit_url, data=form_data, headers=headers, timeout=15)
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        inputs = soup.find_all('input')
        cbs = [inp for inp in inputs if inp.get('type') == 'checkbox' and inp.get('name') == 'availableFuncIn']
        
        print(f"availableFuncIn checkboxes ({len(cbs)}):")
        for cb in cbs:
            is_checked = cb.has_attr('checked') or cb.get('checked') == 'checked'
            print(f"  value='{cb.get('value')}', checked={is_checked}")
    except Exception as e:
        print(f"Error: {e}")

db.close()
