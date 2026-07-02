import sys
sys.path.insert(0, '/app')

from db.database import SessionLocal
from db.models_auth import AdminUser

db = SessionLocal()
su = db.query(AdminUser).filter(AdminUser.username == 'superadmin').first()

if su:
    print(f"Username: {su.username}")
    print(f"Is Active: {su.is_active}")
    print(f"Failed Logins: {su.failed_login_attempts}")
    print(f"Locked Until: {su.locked_until}")
else:
    print("User superadmin not found")

db.close()
