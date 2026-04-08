"""
Script para analizar la estructura de respuesta AJAX de las 5 impresoras
y determinar en qué posición está la carpeta SMB en cada una
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Printer
from services.ricoh_web_client import RicohWebClient
import logging
import ast
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_all_printer_formats():
    """Analiza el formato de respuesta AJAX de cada impresora"""
    db = SessionLocal()
    
    try:
        printers = db.query(Printer).filter(Printer.status != 'offline').all()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"ANÁLISIS DE ESTRUCTURA DE LAS {len(printers)} IMPRESORAS")
        logger.info(f"{'='*80}\n")
        
        client = RicohWebClient(admin_user="admin", admin_password="")
        
        formats_by_printer = {}
        
        for i, printer in enumerate(printers, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"[{i}/{len(printers)}] {printer.hostname} ({printer.ip_address})")
            logger.info(f"{'='*80}")
            
            try:
                # Autenticar
                if not client._authenticate(printer.ip_address):
                    logger.error("❌ No se pudo autenticar")
                    continue
                
                # Request AJAX
                ajax_url = f"http://{printer.ip_address}/web/entry/es/address/adrsListLoadEntry.cgi"
                
                headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': f'http://{printer.ip_address}/web/entry/es/address/adrsList.cgi'
                }
                
                payload = {
                    'listCountIn': '50',
                    'getCountIn': '1'
                }
                
                response = client.session.post(ajax_url, data=payload, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    logger.error(f"❌ Error HTTP: {response.status_code}")
                    continue
                
                # Parsear
                try:
                    data = ast.literal_eval(response.text.strip())
                except:
                    data = json.loads(response.text.replace("'", '"'))
                
                if not data:
                    logger.warning("⚠️  Sin datos")
                    continue
                
                # Analizar primer usuario
                first_entry = data[0]
                total_fields = len(first_entry)
                
                logger.info(f"\nPrimer usuario:")
                logger.info(f"  Total de campos: {total_fields}")
                logger.info(f"  Tipo primer campo: {type(first_entry[0]).__name__} = '{first_entry[0]}'")
                
                # Determinar formato
                if first_entry[0] == '':
                    formato = "Formato .253 (campo vacío al inicio)"
                    logger.info(f"  Formato detectado: .253")
                else:
                    formato = "Formato .252 (estándar)"
                    logger.info(f"  Formato detectado: .252")
                
                # Mostrar TODOS los campos del primer usuario
                logger.info(f"\n  Campos del primer usuario:")
                for idx, field in enumerate(first_entry):
                    field_str = str(field)
                    if len(field_str) > 60:
                        field_str = field_str[:60] + "..."
                    logger.info(f"    [{idx}] = '{field_str}'")
                
                # Buscar campo que parece ser carpeta SMB (contiene \\ o está vacío)
                smb_candidates = []
                for idx, field in enumerate(first_entry):
                    field_str = str(field)
                    if '\\\\' in field_str or (idx > 5 and field_str == ''):
                        smb_candidates.append(idx)
                
                logger.info(f"\n  Candidatos para carpeta SMB (campos con \\\\): {smb_candidates}")
                
                # Buscar usuarios con carpeta SMB para confirmar
                users_with_smb = []
                for entry in data[:20]:
                    for idx in smb_candidates:
                        if idx < len(entry):
                            field = str(entry[idx])
                            if '\\\\' in field and len(field) > 5:
                                users_with_smb.append({
                                    'nombre': str(entry[3]) if len(entry) > 3 else 'N/A',
                                    'campo_idx': idx,
                                    'valor': field
                                })
                                break
                
                if users_with_smb:
                    logger.info(f"\n  ✅ Usuarios con carpeta SMB encontrados: {len(users_with_smb)}")
                    logger.info(f"  Ejemplos (primeros 3):")
                    for j, user in enumerate(users_with_smb[:3], 1):
                        logger.info(f"    {j}. {user['nombre']} → campo[{user['campo_idx']}] = {user['valor']}")
                    
                    # Determinar posición más común
                    smb_position = users_with_smb[0]['campo_idx']
                else:
                    logger.warning(f"  ⚠️  No se encontraron usuarios con carpeta SMB en los primeros 20")
                    smb_position = None
                
                # Guardar formato
                formats_by_printer[printer.hostname] = {
                    'ip': printer.ip_address,
                    'formato': formato,
                    'total_campos': total_fields,
                    'primer_campo_vacio': first_entry[0] == '',
                    'posicion_smb': smb_position,
                    'usuarios_con_smb': len(users_with_smb)
                }
                
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Resumen final
        logger.info(f"\n\n{'='*80}")
        logger.info(f"RESUMEN DE FORMATOS")
        logger.info(f"{'='*80}\n")
        
        for hostname, info in formats_by_printer.items():
            logger.info(f"{hostname} ({info['ip']})")
            logger.info(f"  Formato: {info['formato']}")
            logger.info(f"  Total campos: {info['total_campos']}")
            logger.info(f"  Posición carpeta SMB: campo[{info['posicion_smb']}]")
            logger.info(f"  Usuarios con SMB: {info['usuarios_con_smb']}")
            logger.info("")
        
        # Generar código de corrección
        logger.info(f"{'='*80}")
        logger.info(f"CÓDIGO DE CORRECCIÓN SUGERIDO")
        logger.info(f"{'='*80}\n")
        
        logger.info("if entry[0] == '' and len(entry) >= 11:")
        logger.info("    # Formato .253")
        logger.info("    idx = str(entry[2])")
        logger.info("    name = str(entry[3])")
        logger.info("    code = str(entry[8])")
        
        # Buscar impresoras .253
        pos_253 = None
        for hostname, info in formats_by_printer.items():
            if info['primer_campo_vacio'] and info['posicion_smb']:
                pos_253 = info['posicion_smb']
                break
        
        if pos_253:
            logger.info(f"    folder = str(entry[{pos_253}]) if len(entry) >= {pos_253+1} else ''")
        else:
            logger.info(f"    folder = str(entry[10]) if len(entry) >= 11 else ''  # VERIFICAR")
        
        logger.info("else:")
        logger.info("    # Formato .252")
        logger.info("    idx = str(entry[2])")
        logger.info("    name = str(entry[3])")
        logger.info("    code = str(entry[4])")
        
        # Buscar impresoras .252
        pos_252 = None
        for hostname, info in formats_by_printer.items():
            if not info['primer_campo_vacio'] and info['posicion_smb']:
                pos_252 = info['posicion_smb']
                break
        
        if pos_252:
            logger.info(f"    folder = str(entry[{pos_252}]) if len(entry) >= {pos_252+1} else ''")
        else:
            logger.info(f"    folder = str(entry[8]) if len(entry) >= 9 else ''  # VERIFICAR")
        
    finally:
        db.close()


if __name__ == "__main__":
    analyze_all_printer_formats()
