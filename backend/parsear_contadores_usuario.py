#!/usr/bin/env python3
"""
Parser de Contadores por Usuario - Ricoh
Extrae datos estructurados del HTML de contadores por usuario
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

def parse_user_counter_html(html_content):
    """
    Parsea el HTML de contadores por usuario y extrae datos estructurados
    
    Estructura de la tabla:
    - Usuario (código)
    - Nombre
    - Total impresiones (ByN, Color)
    - Copiadora/Document Server (Blanco y negro, Mono Color, Dos colores, A Todo Color)
    - Impresora (Blanco y negro, Mono Color, Dos colores, Color)
    - Escáner (Blanco y negro, A Todo Color)
    - Fax (Blanco y negro, Páginas transmitidas)
    - Revelado (Negro, Color YMC)
    
    Returns:
        list de dict con datos de cada usuario
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    users = []
    
    # Buscar la tabla principal de datos
    table = soup.find('table', class_='adTable')
    
    if not table:
        return users
    
    # Buscar todas las filas de datos (skip headers)
    rows = table.find_all('tr')
    
    for row in rows:
        # Skip header rows
        if row.find('th'):
            continue
        
        cells = row.find_all('td', class_='listData')
        
        if len(cells) < 18:  # Debe tener al menos 18 columnas
            continue
        
        try:
            user_data = {
                'codigo_usuario': cells[0].get_text(strip=True),
                'nombre_usuario': cells[1].get_text(strip=True),
                'total_impresiones': {
                    'bn': int(cells[2].get_text(strip=True) or 0),
                    'color': int(cells[3].get_text(strip=True) or 0)
                },
                'copiadora': {
                    'blanco_negro': int(cells[4].get_text(strip=True) or 0),
                    'mono_color': int(cells[5].get_text(strip=True) or 0),
                    'dos_colores': int(cells[6].get_text(strip=True) or 0),
                    'todo_color': int(cells[7].get_text(strip=True) or 0)
                },
                'impresora': {
                    'blanco_negro': int(cells[8].get_text(strip=True) or 0),
                    'mono_color': int(cells[9].get_text(strip=True) or 0),
                    'dos_colores': int(cells[10].get_text(strip=True) or 0),
                    'color': int(cells[11].get_text(strip=True) or 0)
                },
                'escaner': {
                    'blanco_negro': int(cells[12].get_text(strip=True) or 0),
                    'todo_color': int(cells[13].get_text(strip=True) or 0)
                },
                'fax': {
                    'blanco_negro': int(cells[14].get_text(strip=True) or 0),
                    'paginas_transmitidas': int(cells[15].get_text(strip=True) or 0)
                },
                'revelado': {
                    'negro': int(cells[16].get_text(strip=True) or 0),
                    'color_ymc': int(cells[17].get_text(strip=True) or 0)
                }
            }
            
            # Calcular totales
            user_data['total_paginas'] = (
                user_data['total_impresiones']['bn'] + 
                user_data['total_impresiones']['color']
            )
            
            users.append(user_data)
            
        except (ValueError, IndexError) as e:
            # Skip rows with invalid data
            continue
    
    return users

def get_user_counters(printer_ip=PRINTER_IP, offset=0, count=10):
    """
    Obtiene los contadores por usuario de la impresora
    
    Args:
        printer_ip: IP de la impresora
        offset: Offset para paginación
        count: Cantidad de registros por página
    
    Returns:
        dict con:
            - users: lista de usuarios con sus contadores
            - total_users: total de usuarios registrados
            - page_info: información de paginación
    """
    session = requests.Session()
    session.verify = False
    
    # Login
    login_to_printer(session, printer_ip)
    
    # Obtener contadores por usuario
    counter_url = f"http://{printer_ip}/web/entry/es/websys/status/getUserCounter.cgi"
    
    # Parámetros para paginación
    data = {
        'offset': offset,
        'count': count
    }
    
    resp = session.post(counter_url, data=data, timeout=10)
    
    if resp.status_code != 200:
        raise Exception(f"Error al obtener contadores por usuario: {resp.status_code}")
    
    # Parsear HTML
    users = parse_user_counter_html(resp.text)
    
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
    
    return {
        'users': users,
        'total_users': total_users,
        'page_info': {
            'current_page': current_page,
            'total_pages': total_pages,
            'offset': offset,
            'count': count,
            'users_in_page': len(users)
        }
    }

def get_all_user_counters(printer_ip=PRINTER_IP):
    """
    Obtiene TODOS los contadores de usuarios (todas las páginas)
    
    Returns:
        list de dict con todos los usuarios
    """
    all_users = []
    offset = 0
    count = 20  # Obtener 20 por página para ser más eficiente
    
    session = requests.Session()
    session.verify = False
    login_to_printer(session, printer_ip)
    
    while True:
        counter_url = f"http://{printer_ip}/web/entry/es/websys/status/getUserCounter.cgi"
        data = {
            'offset': offset,
            'count': count
        }
        
        resp = session.post(counter_url, data=data, timeout=10)
        
        if resp.status_code != 200:
            break
        
        users = parse_user_counter_html(resp.text)
        
        if not users:
            break
        
        all_users.extend(users)
        
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
    
    return all_users

if __name__ == "__main__":
    print("=" * 80)
    print("📊 PARSER DE CONTADORES POR USUARIO - RICOH")
    print("=" * 80)
    print(f"\nImpresora: {PRINTER_IP}")
    print()
    
    try:
        # Obtener primera página
        print("1. Obteniendo primera página de usuarios...")
        result = get_user_counters()
        
        print(f"   ✅ {result['page_info']['users_in_page']} usuarios obtenidos")
        print(f"   📊 Total de usuarios registrados: {result['total_users']}")
        print(f"   📄 Página {result['page_info']['current_page']} de {result['page_info']['total_pages']}")
        
        # Mostrar primeros 3 usuarios
        print("\n2. Primeros 3 usuarios:")
        for i, user in enumerate(result['users'][:3]):
            print(f"\n   Usuario {i+1}:")
            print(f"      Código: {user['codigo_usuario']}")
            print(f"      Nombre: {user['nombre_usuario']}")
            print(f"      Total páginas: {user['total_paginas']}")
            print(f"      Copiadora: {sum(user['copiadora'].values())}")
            print(f"      Impresora: {sum(user['impresora'].values())}")
            print(f"      Escáner: {sum(user['escaner'].values())}")
        
        # Obtener TODOS los usuarios
        print(f"\n3. Obteniendo TODOS los usuarios ({result['total_users']})...")
        all_users = get_all_user_counters()
        
        print(f"   ✅ {len(all_users)} usuarios obtenidos en total")
        
        # Guardar en JSON
        with open('contadores_usuarios_completo.json', 'w', encoding='utf-8') as f:
            json.dump(all_users, f, indent=2, ensure_ascii=False)
        print("   💾 Datos guardados en: contadores_usuarios_completo.json")
        
        # Estadísticas
        print("\n" + "=" * 80)
        print("ESTADÍSTICAS")
        print("=" * 80)
        
        users_with_activity = [u for u in all_users if u['total_paginas'] > 0]
        users_without_activity = [u for u in all_users if u['total_paginas'] == 0]
        
        print(f"\n📊 Total de usuarios: {len(all_users)}")
        print(f"✅ Usuarios con actividad: {len(users_with_activity)}")
        print(f"⚪ Usuarios sin actividad: {len(users_without_activity)}")
        
        if users_with_activity:
            total_pages = sum(u['total_paginas'] for u in users_with_activity)
            print(f"\n📄 Total de páginas impresas por usuarios: {total_pages:,}")
            
            # Top 5 usuarios
            top_users = sorted(users_with_activity, key=lambda x: x['total_paginas'], reverse=True)[:5]
            print(f"\n🏆 Top 5 usuarios con más impresiones:")
            for i, user in enumerate(top_users, 1):
                print(f"   {i}. {user['nombre_usuario']} ({user['codigo_usuario']}): {user['total_paginas']:,} páginas")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
