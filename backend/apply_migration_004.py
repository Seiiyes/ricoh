"""
Apply Migration 004: Remove unique constraint from serial_number
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection
# Check if running in Docker or locally
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/ricoh_db')

# If DATABASE_URL contains 'postgres' as hostname (Docker), replace with localhost for local execution
if '@postgres:' in DATABASE_URL:
    logger.info("⚠️  Detectada configuración de Docker, cambiando a localhost...")
    DATABASE_URL = DATABASE_URL.replace('@postgres:', '@localhost:')
    logger.info(f"   Nueva URL: {DATABASE_URL.split('@')[0]}@localhost:...")

def apply_migration():
    """Apply migration 004"""
    logger.info("=" * 70)
    logger.info("Aplicando Migración 004: Eliminar constraint unique de serial_number")
    logger.info("=" * 70)
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Read migration SQL
            migration_file = os.path.join(os.path.dirname(__file__), 'migrations', '004_remove_serial_unique_constraint.sql')
            
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            logger.info("📝 Ejecutando SQL...")
            
            # Execute migration
            for statement in sql.split(';'):
                statement = statement.strip()
                if statement:
                    logger.info(f"   Ejecutando: {statement[:80]}...")
                    conn.execute(text(statement))
            
            conn.commit()
            logger.info("✅ Migración aplicada exitosamente")
            
            # Verify changes
            logger.info("📋 Verificando cambios...")
            
            # Check if unique constraint was removed
            result = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'printers' 
                AND constraint_type = 'UNIQUE'
                AND constraint_name LIKE '%serial%'
            """))
            
            constraints = result.fetchall()
            if not constraints:
                logger.info("✅ Constraint unique eliminado correctamente")
            else:
                logger.warning(f"⚠️  Aún existen constraints: {constraints}")
            
            # Check if index exists
            result = conn.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'printers' 
                AND indexname = 'idx_printers_serial_number'
            """))
            
            index = result.fetchone()
            if index:
                logger.info("✅ Índice creado correctamente")
            else:
                logger.warning("⚠️  Índice no encontrado")
            
            # Show current printers with serial numbers
            result = conn.execute(text("""
                SELECT id, hostname, ip_address, serial_number 
                FROM printers 
                ORDER BY id
            """))
            
            printers = result.fetchall()
            logger.info(f"📊 Impresoras actuales ({len(printers)}):")
            for printer in printers:
                serial = printer[3] if printer[3] else "(sin serial)"
                logger.info(f"   {printer[0]}. {printer[1]} ({printer[2]}) - ID Máquina: {serial}")
            
            logger.info("")
            logger.info("💡 NOTA: El ID Máquina (serial) es diferente del hostname")
            logger.info("   Ejemplo:")
            logger.info("   - Hostname: RNP0026737FFBB8")
            logger.info("   - ID Máquina: E174M210096")
            
    except Exception as e:
        logger.error(f"❌ Error aplicando migración: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("Migración completada")
    logger.info("=" * 70)

if __name__ == "__main__":
    apply_migration()
