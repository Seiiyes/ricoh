#!/usr/bin/env python3
"""
Corregir capacidades de impresoras según datos reales de CSV
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import re

BACKEND_DIR = Path(__file__).parent
load_dotenv(BACKEND_DIR / '.env')

def conectar_db():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
        if match:
            user, password, host, port, dbname = match.groups()
            if host == 'postgres':
                host = 'localhost'
            return psycopg2.connect(host=host, port=port, database=dbname, user=user, password=password)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "ricoh_fleet"),
        user=os.getenv("DB_USER", "ricoh_admin"),
        password=os.getenv("DB_PASSWORD", "ricoh_secure_2024")
    )

# Capacidades reales según CSV
CAPACIDADES_REALES = {
    "E174M210096": {"has_color": True, "has_scanner": True, "has_fax": False},
    "E174MA11130": {"has_color": True, "has_scanner": True, "has_fax": False},
    "G986XA16285": {"has_color": False, "has_scanner": True, "has_fax": False},
    "E176M460020": {"has_color": True, "has_scanner": True, "has_fax": False},
    "W533L900719": {"has_color": False, "has_scanner": True, "has_fax": False},
}

def main():
    print("="*80)
    print("🔧 CORRECCIÓN DE CAPACIDADES DE IMPRESORAS")
    print("="*80)
    
    conn = conectar_db()
    cur = conn.cursor()
    
    print("\n📊 CAPACIDADES ACTUALES vs REALES:\n")
    
    for serial, caps_reales in CAPACIDADES_REALES.items():
        # Obtener capacidades actuales
        cur.execute("""
            SELECT id, has_color, has_scanner, has_fax
            FROM printers
            WHERE serial_number = %s
        """, (serial,))
        
        result = cur.fetchone()
        if not result:
            print(f"❌ {serial}: No encontrada en BD")
            continue
        
        printer_id, has_color_actual, has_scanner_actual, has_fax_actual = result
        
        print(f"🖨️  {serial}")
        print(f"   Actual:  Color={has_color_actual}, Escáner={has_scanner_actual}, Fax={has_fax_actual}")
        print(f"   Real:    Color={caps_reales['has_color']}, Escáner={caps_reales['has_scanner']}, Fax={caps_reales['has_fax']}")
        
        # Verificar si necesita actualización
        necesita_actualizacion = (
            has_color_actual != caps_reales['has_color'] or
            has_scanner_actual != caps_reales['has_scanner'] or
            has_fax_actual != caps_reales['has_fax']
        )
        
        if necesita_actualizacion:
            print(f"   ⚠️  NECESITA ACTUALIZACIÓN")
            
            # Actualizar
            cur.execute("""
                UPDATE printers
                SET has_color = %s, has_scanner = %s, has_fax = %s
                WHERE id = %s
            """, (caps_reales['has_color'], caps_reales['has_scanner'], caps_reales['has_fax'], printer_id))
            
            print(f"   ✅ ACTUALIZADO")
        else:
            print(f"   ✅ Ya está correcto")
        
        print()
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("="*80)
    print("✅ CORRECCIÓN COMPLETADA")
    print("="*80)

if __name__ == "__main__":
    main()
