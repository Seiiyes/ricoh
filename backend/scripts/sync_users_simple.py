"""
Script simple para sincronización masiva de usuarios.
Ejecutar dentro del contenedor Docker.

UBICACIÓN: backend/scripts/sync_users_simple.py
USO: docker exec -it ricoh-backend python scripts/sync_users_simple.py
"""

import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from services.user_sync_service import UserSyncService


def main():
    print("=" * 80)
    print("SINCRONIZACIÓN MASIVA DE USUARIOS")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    
    try:
        # Estadísticas antes
        print("📊 Estadísticas ANTES:")
        stats_before = UserSyncService.get_sync_stats(db)
        print(f"  • Usuarios en 'users': {stats_before['users_in_db']}")
        print(f"  • Usuarios en contadores: {stats_before['users_in_counters']}")
        print(f"  • Usuarios faltantes: {stats_before['users_missing']}")
        print()
        
        if stats_before['users_missing'] == 0:
            print("✓ Todos los usuarios ya están sincronizados.")
            return
        
        print(f"🔄 Creando {stats_before['users_missing']} usuarios...")
        print()
        
        # Sincronizar
        result = UserSyncService.sync_all_users_from_counters(db, days=30)
        
        print()
        print("=" * 80)
        print("✓ COMPLETADO")
        print("=" * 80)
        print(f"  • Creados: {result['created']}")
        print(f"  • Ya existían: {result['existing']}")
        print(f"  • Total: {result['total']}")
        print()
        
        # Estadísticas después
        stats_after = UserSyncService.get_sync_stats(db)
        print("📊 Estadísticas DESPUÉS:")
        print(f"  • Usuarios en 'users': {stats_after['users_in_db']}")
        print(f"  • Usuarios faltantes: {stats_after['users_missing']}")
        print()
        
        if stats_after['users_missing'] == 0:
            print("✓ Todos los usuarios sincronizados correctamente.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
