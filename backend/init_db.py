"""
Database initialization script
Run this to create all tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import engine, Base, init_db
from db.models import User, Printer, UserPrinterAssignment

def create_tables():
    """Create all database tables"""
    print("🔧 Creating database tables...")
    
    try:
        # Drop all tables (careful!)
        print("⚠️  Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("📊 Creating new tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tables created successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - printers")
        print("  - user_printer_assignments")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ Verified {len(tables)} tables in database:")
        for table in tables:
            print(f"  ✓ {table}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)


def seed_demo_data():
    """Insert demo data"""
    from db.database import SessionLocal
    from db.repository import UserRepository, PrinterRepository
    from db.models import PrinterStatus
    
    print("\n🌱 Seeding demo data...")
    db = SessionLocal()
    
    try:
        # Create demo users
        print("👤 Creating demo users...")
        users = [
            {
                "name": "Usuario Ejemplo",
                "pin": "1234",
                "smb_path": "\\\\10.0.0.5\\scans\\usuario",
                "email": "juan.lizarazo@company.com",
                "department": "IT"
            },
            {
                "name": "Maria Garcia",
                "pin": "5678",
                "smb_path": "\\\\10.0.0.5\\scans\\maria",
                "email": "maria.garcia@company.com",
                "department": "Finance"
            },
            {
                "name": "Carlos Rodriguez",
                "pin": "9012",
                "smb_path": "\\\\10.0.0.5\\scans\\carlos",
                "email": "carlos.rodriguez@company.com",
                "department": "HR"
            }
        ]
        
        for user_data in users:
            UserRepository.create(db, **user_data)
            print(f"  ✓ Created user: {user_data['name']}")
        
        # Create demo printers
        print("\n🖨️  Creating demo printers...")
        printers = [
            {
                "hostname": "RICOH-MP-C3004-001",
                "ip_address": "192.168.1.100",
                "location": "Main Office - Floor 1",
                "status": PrinterStatus.ONLINE,
                "detected_model": "RICOH MP C3004",
                "has_color": True,
                "has_scanner": True,
                "toner_cyan": 75,
                "toner_magenta": 60,
                "toner_yellow": 85,
                "toner_black": 90
            },
            {
                "hostname": "RICOH-SP-4510DN-001",
                "ip_address": "192.168.1.101",
                "location": "Main Office - Floor 2",
                "status": PrinterStatus.ONLINE,
                "detected_model": "RICOH SP 4510DN",
                "has_color": False,
                "has_scanner": False,
                "toner_cyan": 0,
                "toner_magenta": 0,
                "toner_yellow": 0,
                "toner_black": 45
            },
            {
                "hostname": "RICOH-IM-C2500-001",
                "ip_address": "192.168.1.102",
                "location": "Conference Room A",
                "status": PrinterStatus.ONLINE,
                "detected_model": "RICOH IM C2500",
                "has_color": True,
                "has_scanner": True,
                "toner_cyan": 90,
                "toner_magenta": 85,
                "toner_yellow": 80,
                "toner_black": 95
            }
        ]
        
        for printer_data in printers:
            PrinterRepository.create(db, **printer_data)
            print(f"  ✓ Created printer: {printer_data['hostname']}")
        
        print("\n✅ Demo data seeded successfully!")
        
        # Show counts
        user_count = len(UserRepository.get_all(db))
        printer_count = len(PrinterRepository.get_all(db))
        
        print(f"\n📊 Database summary:")
        print(f"  Users: {user_count}")
        print(f"  Printers: {printer_count}")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Ricoh Fleet Governance - Database Initialization")
    print("=" * 60)
    print()
    
    # Create tables
    create_tables()
    
    # Ask if user wants demo data
    print()
    response = input("Do you want to seed demo data? (y/n): ").lower()
    if response == 'y':
        seed_demo_data()
    
    print()
    print("=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print()
    print("You can now:")
    print("  1. Connect with DBeaver to view tables")
    print("  2. Start the backend: python main.py")
    print("  3. Access API docs: http://localhost:8000/docs")
