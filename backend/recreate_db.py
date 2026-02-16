"""
Recreate database tables from scratch
WARNING: This will DROP all existing tables and data!
Use only for development or fresh installations.
"""
import sys
from db.database import Base, engine
from db.models import User, Printer, UserPrinterAssignment


def recreate_database():
    """
    Drop all tables and recreate them with the new schema
    """
    print("=" * 60)
    print("DATABASE RECREATION")
    print("=" * 60)
    print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print("   All tables will be dropped and recreated.\n")
    
    response = input("Are you ABSOLUTELY SURE you want to continue? (type 'DELETE ALL' to confirm): ").strip()
    
    if response != "DELETE ALL":
        print("\nOperation cancelled.")
        sys.exit(0)
    
    try:
        print("\n[1/2] Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("   ✓ All tables dropped")
        
        print("\n[2/2] Creating tables with new schema...")
        Base.metadata.create_all(bind=engine)
        print("   ✓ All tables created")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE RECREATED SUCCESSFULLY!")
        print("=" * 60)
        print("\nTables created:")
        print("  • users (with new provisioning fields)")
        print("  • printers")
        print("  • user_printer_assignments")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ RECREATION FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    recreate_database()
