#!/usr/bin/env python3
"""
Apply migration 006: Add detailed counter fields
"""
import sys
import os
from datetime import datetime
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import engine

def apply_migration():
    """Apply migration 006"""
    print("=" * 80)
    print("MIGRATION 006: Add detailed counter fields")
    print("=" * 80)
    print()
    
    # Read migration file
    migration_file = "migrations/006_add_detailed_counter_fields.sql"
    
    print(f"Reading migration file: {migration_file}")
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print("\nSQL to execute:")
    print("-" * 80)
    print(sql)
    print("-" * 80)
    
    # Confirm
    response = input("\n¿Aplicar esta migración? (yes/no): ")
    if response.lower() != 'yes':
        print("Migración cancelada")
        return
    
    # Apply migration
    print("\nAplicando migración...")
    try:
        with engine.begin() as conn:  # Usar begin() para transacción automática
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    print(f"\nEjecutando statement {i}/{len(statements)}...")
                    conn.execute(text(statement))
        
        print("\n✅ Migración aplicada exitosamente")
        print(f"\nFecha: {datetime.now()}")
        
    except Exception as e:
        print(f"\n❌ Error al aplicar migración: {e}")
        print("\nLa transacción ha sido revertida automáticamente")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
