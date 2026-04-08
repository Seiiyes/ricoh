"""
Script para sincronización masiva de usuarios.
Crea los 429 usuarios faltantes antes de ejecutar la migración 012.

Uso:
    python -m backend.scripts.sync_users_masivo
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.db.database import SessionLocal
from backend.services.user_sync_service import UserSyncService
from backend.logger import logger


def main():
    """Ejecutar sincronización masiva de usuarios"""
    
    print("=" * 80)
    print("SINCRONIZACIÓN MASIVA DE USUARIOS")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    
    try:
        # Obtener estadísticas antes
        print("📊 Estadísticas ANTES de la sincronización:")
        print("-" * 80)
        stats_before = UserSyncService.get_sync_stats(db)
        print(f"  • Usuarios en tabla 'users': {stats_before['users_in_db']}")
        print(f"  • Usuarios únicos en contadores (últimos 30 días): {stats_before['users_in_counters']}")
        print(f"  • Usuarios faltantes (sin registro): {stats_before['users_missing']}")
        print()
        
        if stats_before['users_missing'] == 0:
            print("✓ No hay usuarios faltantes. Todos los usuarios ya están sincronizados.")
            return
        
        # Confirmar
        print(f"⚠️  Se crearán {stats_before['users_missing']} usuarios nuevos.")
        print()
        respuesta = input("¿Deseas continuar? (s/n): ")
        
        if respuesta.lower() != 's':
            print("❌ Sincronización cancelada por el usuario.")
            return
        
        print()
        print("🔄 Iniciando sincronización masiva...")
        print("-" * 80)
        
        # Ejecutar sincronización
        result = UserSyncService.sync_all_users_from_counters(db, days=30)
        
        print()
        print("=" * 80)
        print("✓ SINCRONIZACIÓN COMPLETADA")
        print("=" * 80)
        print(f"  • Usuarios creados: {result['created']}")
        print(f"  • Usuarios ya existentes: {result['existing']}")
        print(f"  • Total usuarios: {result['total']}")
        if result['errors'] > 0:
            print(f"  • Errores: {result['errors']}")
        print()
        
        # Obtener estadísticas después
        print("📊 Estadísticas DESPUÉS de la sincronización:")
        print("-" * 80)
        stats_after = UserSyncService.get_sync_stats(db)
        print(f"  • Usuarios en tabla 'users': {stats_after['users_in_db']}")
        print(f"  • Usuarios únicos en contadores: {stats_after['users_in_counters']}")
        print(f"  • Usuarios faltantes: {stats_after['users_missing']}")
        print()
        
        if stats_after['users_missing'] == 0:
            print("✓ Todos los usuarios están sincronizados correctamente.")
            print()
            print("🎯 PRÓXIMO PASO:")
            print("   Ejecutar migración 012 para agregar columnas user_id:")
            print("   Get-Content backend/migrations/012_normalize_user_references.sql | docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet")
        else:
            print(f"⚠️  Aún quedan {stats_after['users_missing']} usuarios sin sincronizar.")
            print("   Revisa los logs para ver los errores.")
        
        print()
        
    except Exception as e:
        logger.error(f"Error en sincronización masiva: {e}")
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
