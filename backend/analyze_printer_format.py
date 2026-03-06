#!/usr/bin/env python3
"""
Analiza el formato HTML de una impresora para determinar la estructura de columnas
"""
import requests
import base64
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def analyze_printer(printer_ip):
    """Analiza el formato de tabla de una impresora"""
    print(f"\n{'='*80}")
    print(f"ANALIZANDO IMPRESORA: {printer_ip}")
    print(f"{'='*80}\n")
    
    session = requests.Session()
    
    # Login
    login_form_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi"
    form_resp = session.get(login_form_url, timeout=10, verify=False)
    
    import re
    token_match = re.search(r'name="wimToken"\s+value="(\d+)"', form_resp.text)
    login_token = token_match.group(1) if token_match else ""
    
    userid_b64 = base64.b64encode('admin'.encode()).decode()
    login_url = f"http://{printer_ip}/web/guest/es/websys/webArch/login.cgi"
    login_data = {
        'wimToken': login_token,
        'userid_work': '',
        'userid': userid_b64,
        'password_work': '',
        'password': '',
        'open': '',
    }
    
    session.post(login_url, data=login_data, timeout=10, allow_redirects=True, verify=False)
    
    # Get user counters page
    counters_url = f"http://{printer_ip}/web/guest/es/websys/status/getUserCounter.cgi"
    resp = session.get(counters_url, timeout=10, verify=False)
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Find table
    table = soup.find('table', class_='adTable')
    if not table:
        table = soup.find('table', class_='tbl_border')
    
    if not table:
        print("❌ No se encontró tabla")
        return
    
    # Analyze headers
    print("ENCABEZADOS DE TABLA:")
    print("-" * 80)
    header_rows = table.find_all('tr')
    for i, row in enumerate(header_rows[:3]):  # First 3 rows
        headers = row.find_all('th')
        if headers:
            print(f"\nFila {i+1} ({len(headers)} columnas):")
            for j, th in enumerate(headers):
                colspan = th.get('colspan', '1')
                rowspan = th.get('rowspan', '1')
                text = th.get_text(strip=True)
                print(f"  [{j}] {text} (colspan={colspan}, rowspan={rowspan})")
    
    # Analyze first data row
    print("\n" + "="*80)
    print("PRIMERA FILA DE DATOS:")
    print("-" * 80)
    
    for row in header_rows:
        if row.find('th'):
            continue
        
        # Try both formats
        cells = row.find_all('td')
        cells_with_class = row.find_all('td', class_='listData')
        
        if cells:
            print(f"\nTotal celdas <td>: {len(cells)}")
            print(f"Celdas con class='listData': {len(cells_with_class)}")
            
            print("\nContenido de las primeras 20 celdas:")
            for i, cell in enumerate(cells[:20]):
                text = cell.get_text(strip=True)
                has_class = 'listData' in cell.get('class', [])
                print(f"  [{i:2d}] {text:30s} {'(listData)' if has_class else ''}")
            
            if len(cells) > 20:
                print(f"\n  ... y {len(cells) - 20} celdas más")
            
            break
    
    print("\n" + "="*80)

if __name__ == '__main__':
    # Analizar las 4 impresoras que no son 252
    printers = [
        "192.168.91.251",  # Impresora 1
        "192.168.91.253",  # Impresora 2
        "192.168.91.254",  # Impresora 3
        "192.168.91.255",  # Impresora 4
    ]
    
    for printer_ip in printers:
        try:
            analyze_printer(printer_ip)
        except Exception as e:
            print(f"❌ Error analizando {printer_ip}: {e}")
