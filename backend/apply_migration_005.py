#!/usr/bin/env python3
"""
Aplicar migración 005: Agregar tablas de contadores
"""
import psycopg2
from psycopg2 import sql
import os
import re

# Intentar cargar dotenv si está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv no instalado, usando valores por defecto")

# Leer DATABASE_URL del .env
database_url = os.getenv('DATABASE_URL', 'postgresql://ricoh_admin:ricoh_secure_2024@localhost:5432/ricoh_fleet')

# Parsear DATABASE_URL
# Formato: postgresql://user:password@host:port/database
match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)

if match:
    host = match.group(3)
    # Si el host es 'postgres' (nombre del contenedor Docker), usar 'localhost'
    if host == 'postgres':
        host = 'localhost'
    
    DB_CONFIG = {
        'user': match.group(1),
        'password': match.group(2),
        'host': host,
        'port': int(match.group(4)),
        'database': match.group(5)
    }
else:
    # Fallback a valores por defecto
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'ricoh_fleet'),
        'user': os.getenv('DB_USER', 'ricoh_admin'),
        'password': os.getenv('DB_PASSWORD', 'ricoh_secure_2024')
    }

def apply_migration():
    """Aplica la migración 005"""
    conn = None
    cursor = None
    
    print("=" * 80)
    print("🔄 APLICANDO MIGRACIÓN 005: Tablas de Contadores")
    print("=" * 80)
    
    print(f"\n📊 Configuración de conexión:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Port: {DB_CONFIG['port']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    
    try:
        # Conectar a la base de datos
        print("\n1. Conectando a la base de datos...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cursor = conn.cursor()
        print("   ✅ Conectado")
        
        # Leer el archivo de migración
        print("\n2. Leyendo archivo de migración...")
        # Obtener el directorio del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        migration_file = os.path.join(script_dir, 'migrations', '005_add_contador_tables.sql')
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        print(f"   ✅ Archivo leído: {migration_file}")
        
        # Ejecutar la migración
        print("\n3. Ejecutando migración...")
        cursor.execute(migration_sql)
        print("   ✅ Migración ejecutada")
        
        # Verificar tablas creadas
        print("\n4. Verificando tablas creadas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('contadores_impresora', 'contadores_usuario', 'cierres_mensuales')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if len(tables) == 3:
            print("   ✅ Tablas creadas correctamente:")
            for table in tables:
                print(f"      - {table[0]}")
        else:
            print(f"   ⚠️  Solo se encontraron {len(tables)} de 3 tablas")
        
        # Verificar campos agregados a printers
        print("\n5. Verificando campos agregados a 'printers'...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'printers' 
            AND column_name IN ('tiene_contador_usuario', 'usar_contador_ecologico')
            ORDER BY column_name
        """)
        columns = cursor.fetchall()
        
        if len(columns) == 2:
            print("   ✅ Campos agregados correctamente:")
            for col in columns:
                print(f"      - {col[0]}")
        else:
            print(f"   ⚠️  Solo se encontraron {len(columns)} de 2 campos")
        
        # Verificar configuración de impresora ID 6
        print("\n6. Verificando configuración de impresora ID 6...")
        cursor.execute("""
            SELECT id, hostname, tiene_contador_usuario, usar_contador_ecologico
            FROM printers
            WHERE id = 6
        """)
        printer = cursor.fetchone()
        
        if printer:
            print(f"   ✅ Impresora ID 6 configurada:")
            print(f"      - Hostname: {printer[1]}")
            print(f"      - tiene_contador_usuario: {printer[2]}")
            print(f"      - usar_contador_ecologico: {printer[3]}")
        else:
            print("   ⚠️  Impresora ID 6 no encontrada")
        
        # Commit
        print("\n7. Confirmando cambios...")
        conn.commit()
        print("   ✅ Cambios confirmados")
        
        print("\n" + "=" * 80)
        print("✅ MIGRACIÓN 005 APLICADA EXITOSAMENTE")
        print("=" * 80)
        
        print("\n📋 Resumen:")
        print("   - Tablas creadas: contadores_impresora, contadores_usuario, cierres_mensuales")
        print("   - Campos agregados a printers: tiene_contador_usuario, usar_contador_ecologico")
        print("   - Impresora ID 6 configurada para usar contador ecológico")
        
    except Exception as e:
        print(f"\n❌ Error al aplicar migración: {e}")
        if conn:
            conn.rollback()
            print("   🔄 Cambios revertidos (rollback)")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("\n🔌 Conexión cerrada")
    
    return True

if __name__ == "__main__":
    success = apply_migration()
    exit(0 if success else 1)
