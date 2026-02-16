"""
Apply database migration for user provisioning fields
"""
import sys
import os
from sqlalchemy import text
from db.database import engine, SessionLocal
from services.encryption import get_encryption_service


def apply_migration():
    """
    Apply migration to add user provisioning fields
    """
    print("=" * 60)
    print("DATABASE MIGRATION: User Provisioning Fields")
    print("=" * 60)
    
    db = SessionLocal()
    encryption_service = get_encryption_service()
    
    try:
        with engine.connect() as conn:
            print("\n[1/6] Renaming 'pin' column to 'codigo_de_usuario'...")
            try:
                conn.execute(text("ALTER TABLE users RENAME COLUMN pin TO codigo_de_usuario"))
                conn.commit()
                print("   ✓ Column renamed successfully")
            except Exception as e:
                if "does not exist" in str(e).lower() or "already exists" in str(e).lower():
                    print("   ⚠ Column already renamed (skipping)")
                else:
                    raise
            
            print("\n[2/6] Adding network credentials columns...")
            columns = [
                ("network_username", "VARCHAR(255) NOT NULL DEFAULT 'reliteltda\\\\scaner'"),
                ("network_password_encrypted", "TEXT NOT NULL DEFAULT ''"),
            ]
            
            for col_name, col_type in columns:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    print(f"   ✓ Added column '{col_name}'")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"   ⚠ Column '{col_name}' already exists (skipping)")
                    else:
                        raise
            
            print("\n[3/6] Adding SMB configuration columns...")
            smb_columns = [
                ("smb_server", "VARCHAR(255) NOT NULL DEFAULT ''"),
                ("smb_port", "INTEGER NOT NULL DEFAULT 21"),
            ]
            
            for col_name, col_type in smb_columns:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    print(f"   ✓ Added column '{col_name}'")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"   ⚠ Column '{col_name}' already exists (skipping)")
                    else:
                        raise
            
            print("\n[4/6] Adding available functions columns...")
            func_columns = [
                "func_copier",
                "func_printer",
                "func_document_server",
                "func_fax",
                "func_scanner",
                "func_browser"
            ]
            
            for col_name in func_columns:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} BOOLEAN NOT NULL DEFAULT FALSE"))
                    conn.commit()
                    print(f"   ✓ Added column '{col_name}'")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"   ⚠ Column '{col_name}' already exists (skipping)")
                    else:
                        raise
            
            print("\n[5/6] Migrating existing data...")
            
            # Get count of users to migrate
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"   Found {user_count} users to migrate")
            
            if user_count > 0:
                # Parse smb_path to extract server
                try:
                    # For paths like \\server\path, extract server name
                    conn.execute(text("""
                        UPDATE users 
                        SET smb_server = SPLIT_PART(REPLACE(smb_path, '\\\\', ''), '\\\\', 1)
                        WHERE smb_path IS NOT NULL 
                        AND smb_path LIKE '\\\\\\\\%'
                        AND smb_server = ''
                    """))
                    conn.commit()
                    print("   ✓ Parsed SMB server from smb_path")
                except Exception as e:
                    print(f"   ⚠ Could not parse smb_path: {e}")
                
                # Set default encrypted password for users without one
                default_password = "ChangeMe123!"
                encrypted_password = encryption_service.encrypt(default_password)
                
                result = conn.execute(text("""
                    UPDATE users 
                    SET network_password_encrypted = :pwd 
                    WHERE network_password_encrypted = ''
                """), {"pwd": encrypted_password})
                conn.commit()
                updated = result.rowcount
                print(f"   ✓ Set default password for {updated} users")
                
                # Enable scanner function by default
                conn.execute(text("UPDATE users SET func_scanner = TRUE WHERE func_scanner = FALSE"))
                conn.commit()
                print("   ✓ Enabled scanner function for all users")
            
            print("\n[6/6] Creating indexes...")
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_codigo_de_usuario ON users(codigo_de_usuario)"))
                conn.commit()
                print("   ✓ Created index on codigo_de_usuario")
            except Exception as e:
                print(f"   ⚠ Index may already exist: {e}")
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        if user_count > 0:
            print("\n⚠️  IMPORTANT NOTES:")
            print(f"   • {user_count} existing users have been migrated")
            print(f"   • Default password set: '{default_password}'")
            print("   • Please update passwords through the admin interface")
            print("   • Scanner function enabled by default for all users")
        
        print("\n")
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        print("\nRolling back changes...")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will modify your database schema!")
    print("   Make sure you have a backup before proceeding.\n")
    
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    
    if response == "yes":
        apply_migration()
    else:
        print("\nMigration cancelled.")
        sys.exit(0)
