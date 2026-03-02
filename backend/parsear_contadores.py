#!/usr/bin/env python3
"""
Parser de Contadores Ricoh
Extrae datos estructurados del HTML de contadores
"""
import requests
import re
import base64
from bs4 import BeautifulSoup
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PRINTER_IP = "192.168.91.251"
ADMIN_USER = "admin"
ADMIN_PASS = ""

def login_to_printer(session):
    """Login a la impresora"""
    login_form_url = f"http://{PRINTER_IP}/web/guest/es/websys/webArch/authForm.cgi"
    form_resp = session.get(login_form_url, timeout=10)
    token_match = re.search(r'name="wimToken"\s+value="(\d+)"', form_resp.text)
    login_token = token_match.group(1) if token_match else ""
    
    userid_b64 = base64.b64encode(ADMIN_USER.encode()).decode()
    login_url = f"http://{PRINTER_IP}/web/guest/es/websys/webArch/login.cgi"
    login_data = {
        'wimToken': login_token,
        'userid_work': '',
        'userid': userid_b64,
        'password_work': '',
        'password': ADMIN_PASS,
        'open': '',
    }
    
    session.post(login_url, data=login_data, timeout=10, allow_redirects=True)

def parse_counter_html(html_content):
    """
    Parsea el HTML de contadores y extrae datos estructurados
    
    Returns:
        dict con estructura de contadores
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    counters = {
        'total': 0,
        'copiadora': {
            'blanco_negro': 0,
            'color': 0,
            'color_personalizado': 0,
            'dos_colores': 0
        },
        'impresora': {
            'blanco_negro': 0,
            'color': 0,
            'color_personalizado': 0,
            'dos_colores': 0
        },
        'fax': {
            'blanco_negro': 0
        },
        'enviar_total': {
            'blanco_negro': 0,
            'color': 0
        },
        'transmision_fax': {
            'total': 0
        },
        'envio_escaner': {
            'blanco_negro': 0,
            'color': 0
        },
        'otras_funciones': {
            'a3_dlt': 0,
            'duplex': 0
        }
    }
    
    # Buscar todas las filas de la tabla
    rows = soup.find_all('tr', class_='staticProp')
    
    current_section = None
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 3:
            continue
        
        # Extraer texto de las celdas
        label_cell = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        value_cell = cells[3].get_text(strip=True) if len(cells) > 3 else ""
        
        # Identificar sección actual
        if "Total" in label_cell and ":" in row.get_text():
            # Total general
            try:
                counters['total'] = int(value_cell)
            except:
                pass
        
        # Copiadora
        elif label_cell == "Blanco y Negro" and current_section == 'copiadora':
            try:
                counters['copiadora']['blanco_negro'] = int(value_cell)
            except:
                pass
        elif label_cell == "A todo color" and current_section == 'copiadora':
            try:
                counters['copiadora']['color'] = int(value_cell)
            except:
                pass
        elif label_cell == "Color personalizado" and current_section == 'copiadora':
            try:
                counters['copiadora']['color_personalizado'] = int(value_cell)
            except:
                pass
        elif label_cell == "Dos colores" and current_section == 'copiadora':
            try:
                counters['copiadora']['dos_colores'] = int(value_cell)
            except:
                pass
        
        # Impresora
        elif label_cell == "Blanco y Negro" and current_section == 'impresora':
            try:
                counters['impresora']['blanco_negro'] = int(value_cell)
            except:
                pass
        elif label_cell == "A todo color" and current_section == 'impresora':
            try:
                counters['impresora']['color'] = int(value_cell)
            except:
                pass
        elif label_cell == "Color personalizado" and current_section == 'impresora':
            try:
                counters['impresora']['color_personalizado'] = int(value_cell)
            except:
                pass
        elif label_cell == "Dos colores" and current_section == 'impresora':
            try:
                counters['impresora']['dos_colores'] = int(value_cell)
            except:
                pass
        
        # Fax
        elif label_cell == "Blanco y Negro" and current_section == 'fax':
            try:
                counters['fax']['blanco_negro'] = int(value_cell)
            except:
                pass
        
        # Enviar/TX Total
        elif label_cell == "Blanco y Negro" and current_section == 'enviar_total':
            try:
                counters['enviar_total']['blanco_negro'] = int(value_cell)
            except:
                pass
        elif label_cell == "Color" and current_section == 'enviar_total':
            try:
                counters['enviar_total']['color'] = int(value_cell)
            except:
                pass
        
        # Transmisión por fax
        elif label_cell == "Total" and current_section == 'transmision_fax':
            try:
                counters['transmision_fax']['total'] = int(value_cell)
            except:
                pass
        
        # Envío por escáner
        elif label_cell == "Blanco y Negro" and current_section == 'envio_escaner':
            try:
                counters['envio_escaner']['blanco_negro'] = int(value_cell)
            except:
                pass
        elif label_cell == "Color" and current_section == 'envio_escaner':
            try:
                counters['envio_escaner']['color'] = int(value_cell)
            except:
                pass
        
        # Otras funciones
        elif label_cell == "A3/DLT":
            try:
                counters['otras_funciones']['a3_dlt'] = int(value_cell)
            except:
                pass
        elif label_cell == "Dúplex":
            try:
                counters['otras_funciones']['duplex'] = int(value_cell)
            except:
                pass
    
    # Detectar secciones por encabezados
    headers = soup.find_all('div', class_='standard', style=lambda x: x and 'font-weight:bold' in x)
    sections_text = [h.get_text(strip=True) for h in headers]
    
    # Parsear de forma más robusta usando el texto completo
    text = soup.get_text()
    
    # Total
    match = re.search(r'Total\s*:\s*(\d+)', text)
    if match:
        counters['total'] = int(match.group(1))
    
    # Copiadora
    copiadora_section = re.search(r'Copiadora.*?Blanco y Negro\s*:\s*(\d+).*?A todo color\s*:\s*(\d+).*?Color personalizado\s*:\s*(\d+).*?Dos colores\s*:\s*(\d+)', text, re.DOTALL)
    if copiadora_section:
        counters['copiadora']['blanco_negro'] = int(copiadora_section.group(1))
        counters['copiadora']['color'] = int(copiadora_section.group(2))
        counters['copiadora']['color_personalizado'] = int(copiadora_section.group(3))
        counters['copiadora']['dos_colores'] = int(copiadora_section.group(4))
    
    # Impresora
    impresora_section = re.search(r'Impresora.*?Blanco y Negro\s*:\s*(\d+).*?A todo color\s*:\s*(\d+).*?Color personalizado\s*:\s*(\d+).*?Dos colores\s*:\s*(\d+)', text, re.DOTALL)
    if impresora_section:
        counters['impresora']['blanco_negro'] = int(impresora_section.group(1))
        counters['impresora']['color'] = int(impresora_section.group(2))
        counters['impresora']['color_personalizado'] = int(impresora_section.group(3))
        counters['impresora']['dos_colores'] = int(impresora_section.group(4))
    
    # Fax
    fax_section = re.search(r'Fax.*?Blanco y Negro\s*:\s*(\d+)', text, re.DOTALL)
    if fax_section:
        counters['fax']['blanco_negro'] = int(fax_section.group(1))
    
    # Enviar/TX Total
    enviar_section = re.search(r'Enviar/TX Total.*?Blanco y Negro\s*:\s*(\d+).*?Color\s*:\s*(\d+)', text, re.DOTALL)
    if enviar_section:
        counters['enviar_total']['blanco_negro'] = int(enviar_section.group(1))
        counters['enviar_total']['color'] = int(enviar_section.group(2))
    
    # Transmisión por fax
    trans_fax_section = re.search(r'Transmisión por fax.*?Total\s*:\s*(\d+)', text, re.DOTALL)
    if trans_fax_section:
        counters['transmision_fax']['total'] = int(trans_fax_section.group(1))
    
    # Envío por escáner
    escaner_section = re.search(r'Envío por escáner.*?Blanco y Negro\s*:\s*(\d+).*?Color\s*:\s*(\d+)', text, re.DOTALL)
    if escaner_section:
        counters['envio_escaner']['blanco_negro'] = int(escaner_section.group(1))
        counters['envio_escaner']['color'] = int(escaner_section.group(2))
    
    # Otras funciones
    otras_section = re.search(r'A3/DLT\s*:\s*(\d+).*?Dúplex\s*:\s*(\d+)', text, re.DOTALL)
    if otras_section:
        counters['otras_funciones']['a3_dlt'] = int(otras_section.group(1))
        counters['otras_funciones']['duplex'] = int(otras_section.group(2))
    
    return counters

def get_printer_counters(printer_ip=PRINTER_IP):
    """
    Obtiene los contadores de la impresora
    
    Returns:
        dict con contadores estructurados
    """
    session = requests.Session()
    session.verify = False
    
    # Login
    login_to_printer(session)
    
    # Obtener contadores
    counter_url = f"http://{printer_ip}/web/entry/es/websys/status/getUnificationCounter.cgi"
    resp = session.get(counter_url, timeout=10)
    
    if resp.status_code != 200:
        raise Exception(f"Error al obtener contadores: {resp.status_code}")
    
    # Parsear HTML
    counters = parse_counter_html(resp.text)
    
    return counters

if __name__ == "__main__":
    print("=" * 80)
    print("📊 PARSER DE CONTADORES RICOH")
    print("=" * 80)
    print(f"\nImpresora: {PRINTER_IP}")
    print()
    
    try:
        counters = get_printer_counters()
        
        print("✅ Contadores obtenidos exitosamente!")
        print("\n" + "=" * 80)
        print("DATOS ESTRUCTURADOS")
        print("=" * 80)
        print(json.dumps(counters, indent=2, ensure_ascii=False))
        
        # Guardar en archivo JSON
        with open('contadores_estructurados.json', 'w', encoding='utf-8') as f:
            json.dump(counters, f, indent=2, ensure_ascii=False)
        print("\n💾 Datos guardados en: contadores_estructurados.json")
        
        # Resumen
        print("\n" + "=" * 80)
        print("RESUMEN")
        print("=" * 80)
        print(f"\n📊 Total General: {counters['total']:,} páginas")
        print(f"\n📋 Copiadora:")
        print(f"   - B/N: {counters['copiadora']['blanco_negro']:,}")
        print(f"   - Color: {counters['copiadora']['color']:,}")
        print(f"   - Total: {counters['copiadora']['blanco_negro'] + counters['copiadora']['color']:,}")
        print(f"\n🖨️  Impresora:")
        print(f"   - B/N: {counters['impresora']['blanco_negro']:,}")
        print(f"   - Color: {counters['impresora']['color']:,}")
        print(f"   - Total: {counters['impresora']['blanco_negro'] + counters['impresora']['color']:,}")
        print(f"\n📠 Fax: {counters['fax']['blanco_negro']:,}")
        print(f"\n📤 Escáner:")
        print(f"   - B/N: {counters['envio_escaner']['blanco_negro']:,}")
        print(f"   - Color: {counters['envio_escaner']['color']:,}")
        print(f"   - Total: {counters['envio_escaner']['blanco_negro'] + counters['envio_escaner']['color']:,}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
