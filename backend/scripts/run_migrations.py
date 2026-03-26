#!/usr/bin/env python3
"""
Script para ejecutar migraciones de base de datos
Lee archivos .sql de la carpeta migrations y los ejecuta en orden

Uso:
    python backend/scripts/run_migrations.py [migration_number]
    
Ejemplos:
    python backend/scripts/run_migrations.py           # Ejecuta todas las migraciones pendientes
    python backend/scripts/run_migrations.py 010       # Ejecuta solo la migración 010
"""

import os
import sys
from pathlib import Path
import re

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

try:
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Error: Falta instalar dependencias: {e}")
    print("   Ejecutar: pip install sqlalchemy python-dotenv psycopg2-binary")
    sys.exit(1)


def get_database_url() -> str:
    """Obtiene la URL de la base de datos desde variables de entorno"""
    # Priorizar .env.local para desarrollo local (fuera de Docker)
    env_local = backend_dir / '.env.local'
    env_file = backend_dir / '.env'
    
    if env_local.exists():
        load_dotenv(env_local)
        print(f"✅ Variables de entorno cargadas desde: .env.local")
    elif env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Variables de entorno cargadas desde: .env")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: Variable de entorno DATABASE_URL no configurada")
        sys.exit(1)
    
    return database_url


def get_migration_files(migrations_dir: Path, specific_migration: str = None) -> list:
    """
    Obtiene lista de archivos de migración ordenados
    
    Args:
        migrations_dir: Directorio de migraciones
        specific_migration: Número de migración específica (opcional)
        
    Returns:
        list: Lista de tuplas (número, nombre_archivo, ruta_completa)
    """
    migrations = []
    
    for file in migrations_dir.glob('*.sql'):
        # Extraer número de migración del nombre del archivo
        match = re.match(r'^(\d+)_(.+)\.sql$', file.name)
        if match:
            migration_num = match.group(1)
            migration_name = match.group(2)
            
            # Si se especificó una migración, filtrar
            if specific_migration and migration_num != specific_migration:
                continue
            
            migrations.append((migration_num, migration_name, file))
    
    # Ordenar por número de migración
    migrations.sort(key=lambda x: x[0])
    
    return migrations


def create_migrations_table(engine):
    """Crea tabla para rastrear migraciones ejecutadas"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                migration_number VARCHAR(10) PRIMARY KEY,
                migration_name VARCHAR(255) NOT NULL,
                executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()


def is_migration_executed(engine, migration_num: str) -> bool:
    """Verifica si una migración ya fue ejecutada"""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM schema_migrations WHERE migration_number = :num"),
            {"num": migration_num}
        )
        return result.fetchone() is not None


def mark_migration_executed(engine, migration_num: str, migration_name: str):
    """Marca una migración como ejecutada"""
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO schema_migrations (migration_number, migration_name)
                VALUES (:num, :name)
            """),
            {"num": migration_num, "name": migration_name}
        )
        conn.commit()


def execute_migration(engine, migration_num: str, migration_name: str, migration_file: Path) -> bool:
    """
    Ejecuta un archivo de migración
    
    Returns:
        bool: True si se ejecutó correctamente, False en caso contrario
    """
    print(f"\n{'=' * 80}")
    print(f"📝 Migración {migration_num}: {migration_name}")
    print(f"{'=' * 80}")
    
    # Verificar si ya fue ejecutada
    if is_migration_executed(engine, migration_num):
        print(f"⏭️  Migración {migration_num} ya fue ejecutada anteriormente")
        return True
    
    # Leer archivo SQL
    try:
        sql_content = migration_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error al leer archivo: {e}")
        return False
    
    # Ejecutar SQL
    try:
        with engine.connect() as conn:
            # Ejecutar el SQL completo (incluye BEGIN/COMMIT)
            conn.execute(text(sql_content))
            conn.commit()
        
        # Marcar como ejecutada
        mark_migration_executed(engine, migration_num, migration_name)
        
        print(f"✅ Migración {migration_num} ejecutada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al ejecutar migración: {e}")
        return False


def main():
    """Función principal"""
    print("=" * 80)
    print("🗄️  Ejecutor de Migraciones - Ricoh Suite")
    print("=" * 80)
    
    # Obtener argumentos
    specific_migration = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Obtener DATABASE_URL
    database_url = get_database_url()
    print(f"✅ DATABASE_URL configurada")
    
    # Conectar a base de datos
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Conectado a PostgreSQL")
            print(f"   Versión: {version.split(',')[0]}")
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        sys.exit(1)
    
    # Crear tabla de migraciones
    create_migrations_table(engine)
    
    # Obtener archivos de migración
    migrations_dir = backend_dir / 'migrations'
    if not migrations_dir.exists():
        print(f"❌ Error: Directorio de migraciones no encontrado: {migrations_dir}")
        sys.exit(1)
    
    migrations = get_migration_files(migrations_dir, specific_migration)
    
    if not migrations:
        if specific_migration:
            print(f"\n❌ Migración {specific_migration} no encontrada")
        else:
            print("\n✅ No hay migraciones pendientes")
        sys.exit(0)
    
    print(f"\n📋 Migraciones a ejecutar: {len(migrations)}")
    for num, name, _ in migrations:
        status = "✅ Ejecutada" if is_migration_executed(engine, num) else "⏳ Pendiente"
        print(f"   [{num}] {name} - {status}")
    
    # Ejecutar migraciones
    success_count = 0
    failed_count = 0
    
    for migration_num, migration_name, migration_file in migrations:
        if execute_migration(engine, migration_num, migration_name, migration_file):
            success_count += 1
        else:
            failed_count += 1
            print(f"\n❌ Deteniendo ejecución debido a error en migración {migration_num}")
            break
    
    # Resumen
    print(f"\n{'=' * 80}")
    print(f"📊 RESUMEN DE MIGRACIONES")
    print(f"{'=' * 80}")
    print(f"✅ Exitosas: {success_count}")
    print(f"❌ Fallidas: {failed_count}")
    print(f"{'=' * 80}")
    
    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
