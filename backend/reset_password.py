import sys
import bcrypt
sys.path.insert(0, '/app')

from db.database import SessionLocal
from db.models_auth import AdminUser

# Hash the password using bcrypt directly
password = b'ricoh2026'
salt = bcrypt.gensalt(rounds=12) # FastAPI often uses 12 rounds
hashed = bcrypt.hashpw(password, salt).decode('utf-8')

db = SessionLocal()
admin_user = db.query(AdminUser).filter(AdminUser.username == 'admin').first()

if admin_user:
    admin_user.password_hash = hashed
    db.commit()
    print('OK: Contrasena de admin restablecida a ricoh2026')
else:
    print('ERROR: Usuario admin no encontrado. Buscando superadmin...')
    su = db.query(AdminUser).filter(AdminUser.username == 'superadmin').first()
    if su:
        su.password_hash = hashed
        db.commit()
        print('OK: Contrasena de superadmin restablecida a ricoh2026')
    else:
        print('Ningun admin o superadmin encontrado.')

db.close()
