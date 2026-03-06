#!/usr/bin/env python3
"""
Guarda el HTML de contadores de una impresora para análisis
"""
import requests
import base64
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_printer_html(printer_ip, output_file):
    """Guarda el HTML de contadores de una impresora"""
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
    counters_url = f"http://{printer_ip}/web/guest/es/websys/status/getUserCounter.cgi"
    resp = session.get(counters_url, timeout=10, verify=False)
    
    # Save HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(resp.text)
    
    print(f"✅ HTML guardado en: {output_file}")
    print(f"   Tamaño: {len(resp.text)} bytes")

if __name__ == '__main__':
    save_printer_html("192.168.91.251", "printer_251_counters.html")
