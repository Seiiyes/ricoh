#!/usr/bin/env python3
"""
Script para aplicar migración 007 AUTOMÁTICAMENTE (sin input interactivo)
Usar cuando se ejecuta desde Docker sin TTY
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import SessionLocal
from sqlalchemy import text

def apply_migration_007_auto():
    """Aplica la migración 007 automáticamente"""
    
    print("=" * 80)
    print("🔧 APLICANDO MIGRACIÓN 007 (MODO AUTOMÁTICO)")
    print("=" * 80)
    print()
    print("Descripción: Agrega tabla de snapshot de usuarios en cierres")
    print("             y corrige problemas críticos de base de datos")
    print()
    print("Cambios:")
    print("  1. Crear tabla cierres_mensuales_usuarios")
    print("  2. Agregar CHECK constraints de validación")
    print("  3. Agregar índices compuestos para optimización")
    print("  4. Eliminar índices duplicados")
    print("  5. Agregar columnas de auditoría")
    print("  6. Agregar comentarios de documentación")
    print()
    
    print("📋 Creando backup antes de migración...")
    
    # Crear backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"../backups/ricoh_backup_antes_migracion_007_{timestamp}.sql"
    
    os.makedirs("../backups", exist_ok=True)
    
    backup_cmd = f'docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > {backup_file}'
    result = os.system(backup_cmd)
    
    if result != 0:
        print(f"⚠️  Advertencia: No se pudo crear backup automático")
        print(f"   Continuando sin backup...")
    else:
        print(f"✅ Backup creado: {backup_file}")
    
    print()
    print("🚀 Aplicando migración...")
    print()
    
    db = SessionLocal()
    
    try:
        # Leer archivo de migración
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', '007_add_snapshot_and_fixes.sql')
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Ejecutar migración
        db.execute(text(migration_sql))
        db.commit()
        
        print("✅ Migración aplicada exitosamente")
        print()
        
        # Verificar resultados
        print("=" * 80)
        print("📊 VERIFICACIÓN DE MIGRACIÓN")
        print("=" * 80)
        print()
        
        # Verificar tabla
        result = db.execute(text("""
            SELECT COUNT(*) as existe
            FROM information_schema.tables
            WHERE table_name = 'cierres_mensuales_usuarios'
        """)).fetchone()
        
        if result[0] > 0:
            print("✅ Tabla cierres_mensuales_usuarios creada")
        else:
            print("❌ ERROR: Tabla cierres_mensuales_usuarios NO se creó")
            return False
        
        # Verificar índices
        result = db.execute(text("""
            SELECT COUNT(*) as total
            FROM pg_indexes
            WHERE tablename = 'cierres_mensuales_usuarios'
        """)).fetchone()
        
        print(f"✅ {result[0]} índices creados en cierres_mensuales_usuarios")
        
        # Verificar constraints
        result = db.execute(text("""
            SELECT COUNT(*) as total
            FROM information_schema.table_constraints
            WHERE constraint_type = 'CHECK'
            AND table_name IN ('cierres_mensuales', 'contadores_usuario', 'contadores_impresora', 'cierres_mensuales_usuarios')
        """)).fetchone()
        
        print(f"✅ {result[0]} CHECK constraints agregados")
        
        # Verificar columnas de auditoría
        result = db.execute(text("""
            SELECT COUNT(*) as total
            FROM information_schema.columns
            WHERE table_name = 'cierres_mensuales'
            AND column_name IN ('modified_at', 'modified_by', 'hash_verificacion')
        """)).fetchone()
        
        print(f"✅ {result[0]} columnas de auditoría agregadas")
        
        # Verificar índices compuestos
        result = db.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE indexname LIKE 'idx_contadores_usuario_%'
            AND tablename = 'contadores_usuario'
            ORDER BY indexname
        """)).fetchall()
        
        print(f"\n✅ Índices compuestos creados:")
        for idx in result:
            print(f"   - {idx[0]}")
        
        # Verificar relaciones
        print(f"\n✅ Verificando relaciones...")
        result = db.execute(text("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'cierres_mensuales_usuarios'
        """)).fetchall()
        
        for rel in result:
            print(f"   - {rel[1]}.{rel[2]} → {rel[3]}.{rel[4]}")
        
        print()
        print("=" * 80)
        print("✅ MIGRACIÓN 007 COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print()
        print("Próximos pasos:")
        print("  1. Verificar que la aplicación funciona correctamente")
        print("  2. Ejecutar tests de integración")
        print("  3. Implementar lógica de cierre mensual con snapshot")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR AL APLICAR MIGRACIÓN")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        print("La base de datos NO fue modificada (rollback automático)")
        print()
        
        if os.path.exists(backup_file):
            print(f"Puede restaurar el backup desde: {backup_file}")
            print(f"Comando: docker exec -i ricoh-postgres psql -U ricoh_admin ricoh_fleet < {backup_file}")
        
        db.rollback()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = apply_migration_007_auto()
    sys.exit(0 if success else 1)
