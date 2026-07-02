import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Add backend directory to path
sys.path.insert(0, r"c:\Users\juan.lizarazo\Desktop\ricoh\backend")

from db.models import Printer

def main():
    db_url = "postgresql://ricoh_admin:ricoh_secure_2024@localhost:5432/ricoh_fleet"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    printers = session.query(Printer).all()
    print(f"Found {len(printers)} printers in DB:")
    for p in printers:
        print(f"ID: {p.id} | Hostname: {p.hostname} | IP: {p.ip_address} | Serial: {p.serial_number} | Status: {p.status} | Pwd: {p.admin_password}")

if __name__ == "__main__":
    main()
