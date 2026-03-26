#!/usr/bin/env python3
"""
Parser de Contadores Ricoh
Extrae datos estructurados del HTML de contadores
"""
import requests
from bs4 import BeautifulSoup
import json
import urllib3
from .ricoh_auth import RicohAuthService

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PRINTER_IP = "192.168.91.251"


def parse_counter_html(html_content):
    """
    Parsea el HTML de contadores y extrae datos estructurados
    Usa análisis de contexto para detectar secciones correctamente
    
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
    
    # Buscar todas las filas staticProp
    rows = soup.find_all('tr', class_='staticProp')
    
    # Variable para rastrear la sección actual
    current_section = None
    
    for row in rows:
        cells = row.find_all('td')
        
        # Las filas tienen 5 celdas: ['', 'Label', ':', 'Value', '']
        if len(cells) < 4:
            continue
        
        # Skip fila de "Atrás"
        label = cells[1].get_text(strip=True)
        if label == "Atrás":
            continue
        
        separator = cells[2].get_text(strip=True)
        value_text = cells[3].get_text(strip=True)
        
        if separator != ":":
            continue
        
        # Convertir valor a entero
        try:
            value = int(value_text.replace(",", "").replace(".", ""))
        except:
            continue
        
        # Buscar el elemento de texto inmediatamente anterior que contenga nombre de sección
        # Buscar en los elementos previos cercanos
        prev_strings = []
        for elem in row.find_all_previous(string=True, limit=20):
            text = str(elem).strip()
            if text:
                prev_strings.append(text)
        
        # Buscar secciones en los últimos elementos (más cercanos primero)
        for prev_text in prev_strings:
            if "Envío por escáner" in prev_text or "Envio por escaner" in prev_text:
                current_section = 'escaner'
                break
            elif "Enviar/TX Total" in prev_text:
                current_section = 'enviar'
                break
            elif "Transmisión por fax" in prev_text or "Transmision por fax" in prev_text:
                current_section = 'transmision'
                break
            elif "Fax" in prev_text and "Transmisión" not in prev_text:
                current_section = 'fax'
                break
            elif "Impresora" in prev_text:
                current_section = 'impresora'
                break
            elif "Copiadora" in prev_text:
                current_section = 'copiadora'
                break
            elif "Otra función" in prev_text or "Otra funcion" in prev_text:
                current_section = 'otra'
                break
        
        # Asignar valor según label y sección detectada
        if label == "Total" and current_section is None:
            counters['total'] = value
        
        elif label == "Blanco y Negro":
            if current_section == 'copiadora':
                counters['copiadora']['blanco_negro'] = value
            elif current_section == 'impresora':
                counters['impresora']['blanco_negro'] = value
            elif current_section == 'fax':
                counters['fax']['blanco_negro'] = value
            elif current_section == 'enviar':
                counters['enviar_total']['blanco_negro'] = value
            elif current_section == 'escaner':
                counters['envio_escaner']['blanco_negro'] = value
        
        elif label == "A todo color":
            if current_section == 'copiadora':
                counters['copiadora']['color'] = value
            elif current_section == 'impresora':
                counters['impresora']['color'] = value
        
        elif label == "Color personalizado":
            if current_section == 'copiadora':
                counters['copiadora']['color_personalizado'] = value
            elif current_section == 'impresora':
                counters['impresora']['color_personalizado'] = value
        
        elif label == "Dos colores":
            if current_section == 'copiadora':
                counters['copiadora']['dos_colores'] = value
            elif current_section == 'impresora':
                counters['impresora']['dos_colores'] = value
        
        elif label == "Color":
            if current_section == 'enviar':
                counters['enviar_total']['color'] = value
            elif current_section == 'escaner':
                counters['envio_escaner']['color'] = value
        
        elif label == "Total" and current_section == 'transmision':
            counters['transmision_fax']['total'] = value
        
        elif label == "A3/DLT":
            counters['otras_funciones']['a3_dlt'] = value
        
        elif label == "Dúplex":
            counters['otras_funciones']['duplex'] = value
    
    return counters


def get_printer_counters(printer_ip=PRINTER_IP):
    """
    Obtiene los contadores de la impresora
    
    Returns:
        dict con contadores estructurados
    """
    session = requests.Session()
    session.verify = False
    
    # Login usando servicio unificado
    RicohAuthService.login_to_printer(session, printer_ip)
    
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
        print(f"   - Color Personalizado: {counters['copiadora']['color_personalizado']:,}")
        print(f"   - Dos Colores: {counters['copiadora']['dos_colores']:,}")
        total_cop = max(counters['copiadora']['blanco_negro'], counters['copiadora']['color'])
        print(f"   - Total: {total_cop:,}")
        print(f"\n🖨️  Impresora:")
        print(f"   - B/N: {counters['impresora']['blanco_negro']:,}")
        print(f"   - Color: {counters['impresora']['color']:,}")
        print(f"   - Color Personalizado: {counters['impresora']['color_personalizado']:,}")
        print(f"   - Dos Colores: {counters['impresora']['dos_colores']:,}")
        total_imp = max(counters['impresora']['blanco_negro'], counters['impresora']['color'])
        print(f"   - Total: {total_imp:,}")
        print(f"\n📠 Fax: {counters['fax']['blanco_negro']:,}")
        print(f"\n📤 Escáner:")
        print(f"   - B/N: {counters['envio_escaner']['blanco_negro']:,}")
        print(f"   - Color: {counters['envio_escaner']['color']:,}")
        total_esc = max(counters['envio_escaner']['blanco_negro'], counters['envio_escaner']['color'])
        print(f"   - Total: {total_esc:,}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
