import sys
import bcrypt
sys.path.insert(0, '/app')

from db.database import SessionLocal
from db.models_auth import AdminUser

db = SessionLocal()
su = db.query(AdminUser).filter(AdminUser.username == 'superadmin').first()

if su:
    print(f"Hash in DB: {su.password_hash}")
    
    password = 'ricoh2026'
    password_bytes = password.encode('utf-8')
    hash_bytes = su.password_hash.encode('utf-8')
    
    try:
        is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
        print(f"Bcrypt verify: {is_valid}")
    except Exception as e:
        print(f"Bcrypt verify error: {e}")
else:
    print("User superadmin not found")

db.close()
