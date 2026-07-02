import sys
import os
sys.path.append('/home/odootic/ricoh-app/backend')
from services.password_service import PasswordService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import AdminUser

DATABASE_URL = 'postgresql://ricoh_admin:ricoh_secure_2024@localhost:5433/ricoh_fleet'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

user = db.query(AdminUser).filter(AdminUser.username == 'superadmin').first()
if user:
    new_hash = PasswordService.hash_password('zRpKpcqC|A9{C3*w')
    user.password_hash = new_hash
    db.commit()
    print('Password updated successfully')
else:
    print('User not found')
