#!/usr/bin/env python3
"""
Guarda el HTML de la impresora 253 para análisis
"""
import sys
sys.path.insert(0, '/app')

import requests
import base64
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_253_html():
    """Guarda el HTML de contadores de la impresora 253"""
    printer_ip = "192.168.91.253"
    session = requests.Session()
    
    # Login
    login_form_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi"
    form_resp = session.get(login_form_url, timeout=10, verify=False)
    
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
    counters_url = f"http://{printer_ip}/web/entry/es/websys/status/getUserCounter.cgi"
    resp = session.get(counters_url, timeout=10, verify=False)
    
    # Save HTML
    output_file = "/app/printer_253_counters.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(resp.text)
    
    print(f"HTML guardado en: {output_file}")
    print(f"Tamaño: {len(resp.text)} bytes")
    
    # Quick analysis
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    table = soup.find('table', class_='adTable')
    if not table:
        table = soup.find('table', class_='tbl_border')
    
    if table:
        rows = table.find_all('tr')
        print(f"\nTabla encontrada con {len(rows)} filas")
        
        # Check first data row
        for row in rows:
            if row.find('th'):
                continue
            cells = row.find_all('td')
            cells_with_class = row.find_all('td', class_='listData')
            if cells:
                print(f"Primera fila de datos: {len(cells)} celdas totales, {len(cells_with_class)} con class='listData'")
                break
    else:
        print("\nNo se encontró tabla")

if __name__ == '__main__':
    save_253_html()
