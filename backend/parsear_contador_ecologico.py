#!/usr/bin/env python3
"""
Parser de Contador Ecológico - Ricoh
Extrae datos del contador ecológico (getEcoCounter.cgi)
Usado en impresoras que no tienen getUserCounter.cgi
"""
import requests
import re
import base64
from bs4 import BeautifulSoup
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ADMIN_USER = "admin"
ADMIN_PASS = ""

def login_to_printer(session, printer_ip):
    """Login a la impresora"""
    login_form_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi"
    form_resp = session.get(login_form_url, timeout=10)
    token_match = re.search(r'name="wimToken"\s+value="(\d+)"', form_resp.text)
    login_token = token_match.group(1) if token_match else ""
    
    userid_b64 = base64.b64encode(ADMIN_USER.encode()).decode()
    login_url = f"http://{printer_ip}/web/guest/es/websys/webArch/login.cgi"
    login_data = {
        'wimToken': login_token,
        'userid_work': '',
        'userid': userid_b64,
        'password_work': '',
        'password': ADMIN_PASS,
        'open': '',
    }
    
    session.post(login_url, data=login_data, timeout=10, allow_redirects=True)

def parse_eco_counter_html(html_content):
    """
    Parsea el HTML del contador ecológico
    
    Returns:
        dict con:
            - device_total: contadores totales del dispositivo
            - users: lista de usuarios con sus contadores ecológicos
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {
        'device_total': {},
        'users': []
    }
    
    # Buscar todas las tablas
    tables = soup.find_all('table', class_='adTable')
    
    if not tables:
        return result
    
    # Primera tabla: Contador total del dispositivo
    device_table = tables[0]
    device_rows = device_table.find_all('tr')
    
    for row in device_rows:
        cells = row.find_all('td', class_='listData')
        if len(cells) >= 8:
            try:
                result['device_total'] = {
                    'total_paginas_actual': int(cells[0].get_text(strip=True) or 0),
                    'total_paginas_anterior': int(cells[1].get_text(strip=True) or 0),
                    'uso_2_caras_actual': cells[2].get_text(strip=True).strip(),
                    'uso_2_caras_anterior': cells[3].get_text(strip=True).strip(),
                    'uso_combinar_actual': cells[4].get_text(strip=True).strip(),
                    'uso_combinar_anterior': cells[5].get_text(strip=True).strip(),
                    'reduccion_papel_actual': cells[6].get_text(strip=True).strip(),
                    'reduccion_papel_anterior': cells[7].get_text(strip=True).strip(),
                }
            except (ValueError, IndexError):
                pass
    
    # Segunda tabla (si existe): Contador por usuario
    if len(tables) > 1:
        user_table = tables[1]
        user_rows = user_table.find_all('tr')
        
        for row in user_rows:
            # Skip header rows
            if row.find('th'):
                continue
            
            cells = row.find_all('td', class_='listData')
            
            if len(cells) >= 11:
                try:
                    codigo_usuario = cells[1].get_text(strip=True)
                    
                    user_data = {
                        'numero_registro': cells[0].get_text(strip=True),
                        'codigo_usuario': codigo_usuario,
                        'nombre_usuario': cells[2].get_text(strip=True),
                        'total_paginas_actual': int(cells[3].get_text(strip=True) or 0),
                        'total_paginas_anterior': int(cells[4].get_text(strip=True) or 0),
                        'uso_2_caras_actual': cells[5].get_text(strip=True).strip(),
                        'uso_2_caras_anterior': cells[6].get_text(strip=True).strip(),
                        'uso_combinar_actual': cells[7].get_text(strip=True).strip(),
                        'uso_combinar_anterior': cells[8].get_text(strip=True).strip(),
                        'reduccion_papel_actual': cells[9].get_text(strip=True).strip(),
                        'reduccion_papel_anterior': cells[10].get_text(strip=True).strip(),
                    }
                    
                    result['users'].append(user_data)
                    
                except (ValueError, IndexError):
                    continue
    
    return result

def get_eco_counter(printer_ip, offset=0, count=10):
    """
    Obtiene el contador ecológico de la impresora
    
    Args:
        printer_ip: IP de la impresora
        offset: Offset para paginación
        count: Cantidad de registros por página
    
    Returns:
        dict con device_total y users
    """
    session = requests.Session()
    session.verify = False
    
    # Login
    login_to_printer(session, printer_ip)
    
    # Obtener contador ecológico
    counter_url = f"http://{printer_ip}/web/entry/es/websys/getEcoCounter.cgi"
    
    # Parámetros para paginación
    data = {
        'userCounterListOffset': offset,
        'userCounterListCount': count
    }
    
    resp = session.post(counter_url, data=data, timeout=10)
    
    if resp.status_code != 200:
        raise Exception(f"Error al obtener contador ecológico: {resp.status_code}")
    
    # Parsear HTML
    result = parse_eco_counter_html(resp.text)
    
    # Extraer información de paginación
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Total de usuarios
    total_users_text = soup.find(text=re.compile(r'Usuario\s+\d+'))
    total_users = 0
    if total_users_text:
        match = re.search(r'Usuario\s+(\d+)', total_users_text)
        if match:
            total_users = int(match.group(1))
    
    # Página actual y total de páginas
    current_page_span = soup.find('span', id='span_currentPage')
    total_page_span = soup.find('span', id='span_totalPage')
    
    current_page = int(current_page_span.get_text(strip=True)) if current_page_span else 1
    total_pages = int(total_page_span.get_text(strip=True)) if total_page_span else 1
    
    result['page_info'] = {
        'current_page': current_page,
        'total_pages': total_pages,
        'offset': offset,
        'count': count,
        'total_users': total_users,
        'users_in_page': len(result['users'])
    }
    
    return result

def get_all_eco_users(printer_ip):
    """
    Obtiene TODOS los usuarios del contador ecológico (todas las páginas)
    
    Returns:
        dict con device_total y lista completa de users
    """
    session = requests.Session()
    session.verify = False
    login_to_printer(session, printer_ip)
    
    all_users = []
    device_total = {}
    offset = 0
    count = 20  # Obtener 20 por página
    
    while True:
        counter_url = f"http://{printer_ip}/web/entry/es/websys/getEcoCounter.cgi"
        data = {
            'userCounterListOffset': offset,
            'userCounterListCount': count
        }
        
        resp = session.post(counter_url, data=data, timeout=10)
        
        if resp.status_code != 200:
            break
        
        result = parse_eco_counter_html(resp.text)
        
        # Guardar device_total de la primera página
        if offset == 0:
            device_total = result['device_total']
        
        if not result['users']:
            break
        
        all_users.extend(result['users'])
        
        # Verificar si hay más páginas
        soup = BeautifulSoup(resp.text, 'html.parser')
        current_page_span = soup.find('span', id='span_currentPage')
        total_page_span = soup.find('span', id='span_totalPage')
        
        if current_page_span and total_page_span:
            current_page = int(current_page_span.get_text(strip=True))
            total_pages = int(total_page_span.get_text(strip=True))
            
            if current_page >= total_pages:
                break
        
        offset += count
    
    return {
        'device_total': device_total,
        'users': all_users
    }

if __name__ == "__main__":
    PRINTER_IP = "192.168.91.253"  # Impresora que usa contador ecológico
    
    print("=" * 80)
    print("🌿 PARSER DE CONTADOR ECOLÓGICO - RICOH")
    print("=" * 80)
    print(f"\nImpresora: {PRINTER_IP}")
    print()
    
    try:
        # Obtener primera página
        print("1. Obteniendo primera página...")
        result = get_eco_counter(PRINTER_IP)
        
        print(f"   ✅ Datos obtenidos")
        print(f"   📊 Total usuarios: {result['page_info']['total_users']}")
        print(f"   📄 Página {result['page_info']['current_page']} de {result['page_info']['total_pages']}")
        
        # Mostrar contador total del dispositivo
        print("\n2. Contador Total del Dispositivo:")
        device = result['device_total']
        print(f"   Total páginas (actual): {device.get('total_paginas_actual', 0):,}")
        print(f"   Total páginas (anterior): {device.get('total_paginas_anterior', 0):,}")
        print(f"   Uso 2 caras: {device.get('uso_2_caras_actual', 'N/A')}")
        print(f"   Uso Combinar: {device.get('uso_combinar_actual', 'N/A')}")
        print(f"   Reducción papel: {device.get('reduccion_papel_actual', 'N/A')}")
        
        # Mostrar primeros 3 usuarios
        print("\n3. Primeros 3 usuarios:")
        for i, user in enumerate(result['users'][:3]):
            print(f"\n   Usuario {i+1}:")
            print(f"      Código: {user['codigo_usuario']}")
            print(f"      Nombre: {user['nombre_usuario']}")
            print(f"      Total páginas: {user['total_paginas_actual']:,}")
            print(f"      Uso 2 caras: {user['uso_2_caras_actual']}")
        
        # Obtener TODOS los usuarios
        print(f"\n4. Obteniendo TODOS los usuarios ({result['page_info']['total_users']})...")
        all_data = get_all_eco_users(PRINTER_IP)
        
        print(f"   ✅ {len(all_data['users'])} usuarios obtenidos")
        
        # Guardar en JSON
        with open('contador_ecologico_completo.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print("   💾 Datos guardados en: contador_ecologico_completo.json")
        
        # Estadísticas
        print("\n" + "=" * 80)
        print("ESTADÍSTICAS")
        print("=" * 80)
        
        users_with_activity = [u for u in all_data['users'] if u['total_paginas_actual'] > 0]
        users_without_activity = [u for u in all_data['users'] if u['total_paginas_actual'] == 0]
        
        print(f"\n📊 Total de usuarios: {len(all_data['users'])}")
        print(f"✅ Usuarios con actividad: {len(users_with_activity)}")
        print(f"⚪ Usuarios sin actividad: {len(users_without_activity)}")
        
        if users_with_activity:
            total_pages = sum(u['total_paginas_actual'] for u in users_with_activity)
            print(f"\n📄 Total de páginas impresas por usuarios: {total_pages:,}")
            
            # Top 5 usuarios
            top_users = sorted(users_with_activity, key=lambda x: x['total_paginas_actual'], reverse=True)[:5]
            print(f"\n🏆 Top 5 usuarios con más impresiones:")
            for i, user in enumerate(top_users, 1):
                print(f"   {i}. {user['nombre_usuario']} ({user['codigo_usuario']}): {user['total_paginas_actual']:,} páginas")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
