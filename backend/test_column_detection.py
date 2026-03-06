#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para detectar cuántas columnas tiene cada impresora
"""
import parsear_contadores_usuario as parser
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def test_printer(printer_ip, printer_name):
    """Prueba una impresora y muestra cuántas columnas detecta"""
    print(f"\n{'='*80}")
    print(f"PROBANDO: {printer_name} ({printer_ip})")
    print(f"{'='*80}")
    
    try:
        # Get HTML
        session = parser.requests.Session()
        parser.login_to_printer(session, printer_ip)
        
        counters_url = f"http://{printer_ip}/web/guest/es/websys/status/getUserCounter.cgi"
        resp = session.get(counters_url, timeout=10, verify=False)
        
        # Parse
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        table = soup.find('table', class_='adTable')
        if not table:
            table = soup.find('table', class_='tbl_border')
        
        if not table:
            print("ERROR: No se encontro tabla")
            return
        
        # Find first data row
        rows = table.find_all('tr')
        for row in rows:
            if row.find('th'):
                continue
            
            cells = row.find_all('td')
            cells_with_class = row.find_all('td', class_='listData')
            
            if cells:
                print(f"\nOK: Formato detectado:")
                print(f"   Total celdas <td>: {len(cells)}")
                print(f"   Celdas con class='listData': {len(cells_with_class)}")
                
                if len(cells) == 13:
                    print(f"   -> Formato 252 (13 columnas)")
                elif len(cells_with_class) >= 22:
                    print(f"   -> Formato EXTENDIDO (22+ columnas con hojas_2_caras)")
                elif len(cells_with_class) >= 18:
                    print(f"   -> Formato ESTANDAR (18 columnas sin hojas_2_caras)")
                
                # Show first user data
                if cells_with_class and len(cells_with_class) >= 2:
                    print(f"\n   Primer usuario:")
                    print(f"   Codigo: {cells_with_class[0].get_text(strip=True)}")
                    print(f"   Nombre: {cells_with_class[1].get_text(strip=True)}")
                
                break
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    printers = [
        ("192.168.91.250", "Impresora 250"),
        ("192.168.91.251", "Impresora 251"),
        ("192.168.91.252", "Impresora 252"),
        ("192.168.91.253", "Impresora 253"),
        ("192.168.110.250", "Impresora 110.250"),
    ]
    
    for ip, name in printers:
        test_printer(ip, name)
    
    print(f"\n{'='*80}")
    print("TEST COMPLETADO")
    print(f"{'='*80}\n")
