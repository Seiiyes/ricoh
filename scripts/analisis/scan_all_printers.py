"""
Query all 5 printers in the network to inspect their WIM address book AJAX formats.
"""
import sys
sys.path.insert(0, '/app')

import re
import ast
import json
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
    print(f"Authenticating...")
    if not client._authenticate(ip, admin_password):
        print(f"Failed to authenticate with {ip}")
        continue
    
    # Get wimToken
    try:
        list_url = f"http://{ip}/web/entry/es/address/adrsList.cgi"
        list_resp = client.session.get(list_url, timeout=15)
        match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
        if not match:
            print(f"Failed to get wimToken from {ip}")
            continue
        wim_token = match.group(1)
        
        # Load batch 1
        ajax_url = f"http://{ip}/web/entry/es/address/adrsListLoadEntry.cgi"
        payload = {
            'wimToken': wim_token,
            'listCountIn': '50',
            'getCountIn': '1'
        }
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': list_url
        }
        resp = client.session.post(ajax_url, data=payload, headers=headers, timeout=15)
        
        try:
            data = ast.literal_eval(resp.text.strip())
        except:
            data = json.loads(resp.text.strip().replace("'", '"'))
            
        print(f"Response status: {resp.status_code}")
        print(f"Total entries in batch 1: {len(data)}")
        if data:
            print(f"First entry length: {len(data[0])}")
            print(f"First entry: {data[0]}")
        else:
            print("No entries in address book")
    except Exception as e:
        print(f"Error querying {ip}: {e}")

db.close()
print("\n=== Scan Complete ===")
