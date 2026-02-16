"""
Quick database initialization script
Run from project root: python create_db.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("Ricoh Fleet - Database Initialization")
print("=" * 60)
print()

try:
    print("📦 Importing modules...")
    from backend.db.database import engine, Base, SessionLocal
    from backend.db.models import User, Printer, UserPrinterAssignment, PrinterStatus
    from backend.db.repository import UserRepository, PrinterRepository
    
    print("✅ Modules imported successfully")
    print()
    
    # Create tables
    print("🔧 Creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created!")
    print()
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"📊 Created {len(tables)} tables:")
    for table in tables:
        print(f"  ✓ {table}")
    print()
    
    # Ask for demo data
    response = input("Add demo data? (y/n): ").lower()
    
    if response == 'y':
        print()
        print("🌱 Adding demo data...")
        db = SessionLocal()
        
        try:
            # Create users
            print("👤 Creating users...")
            users_data = [
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
            
            for user_data in users_data:
                UserRepository.create(db, **user_data)
                print(f"  ✓ {user_data['name']}")
            
            # Create printers
            print()
            print("🖨️  Creating printers...")
            printers_data = [
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
            
            for printer_data in printers_data:
                PrinterRepository.create(db, **printer_data)
                print(f"  ✓ {printer_data['hostname']}")
            
            print()
            print("✅ Demo data added successfully!")
            
            # Show counts
            user_count = len(UserRepository.get_all(db))
            printer_count = len(PrinterRepository.get_all(db))
            
            print()
            print(f"📊 Database summary:")
            print(f"  Users: {user_count}")
            print(f"  Printers: {printer_count}")
            
        except Exception as e:
            print(f"❌ Error adding demo data: {e}")
            db.rollback()
        finally:
            db.close()
    
    print()
    print("=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Open DBeaver and refresh (F5)")
    print("  2. Start backend: cd backend && python main.py")
    print("  3. Or use Docker: docker-compose up")
    print()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("Make sure you have installed dependencies:")
    print("  cd backend")
    print("  pip install -r requirements.txt")
    print()
    sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
