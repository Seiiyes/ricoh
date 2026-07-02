import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_real_delete")

# Set dummy password in environment to avoid ValueError
os.environ["RICOH_ADMIN_PASSWORD"] = "dummy-password"

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.models import Printer
from db.database import Base
from services.ricoh_web_client import get_ricoh_web_client

def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL is not set.")
        sys.exit(1)
        
    logger.info(f"Connecting to database: {db_url}")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    printer_ip = "192.168.91.253"
    job_id = "7416"
    
    logger.info(f"Searching for printer with IP {printer_ip} in database...")
    printer = session.query(Printer).filter(Printer.ip_address == printer_ip).first()
    
    if not printer:
        logger.error(f"Printer with IP {printer_ip} not found in database!")
        sys.exit(1)
        
    logger.info(f"Printer found: ID={printer.id}, Hostname={printer.hostname}, Serial={printer.serial_number}")
    
    admin_password = printer.admin_password
    logger.info(f"Original admin password from database: {admin_password}")
    
    # If password is None, pass empty string explicitly to avoid falling back to RICOH_ADMIN_PASSWORD env var
    resolved_password = admin_password if admin_password is not None else ""
    logger.info(f"Resolved admin password: '{resolved_password}'")
    
    # Initialize Ricoh client
    client = get_ricoh_web_client()
    
    logger.info(f"Executing client.delete_stored_job on IP={printer_ip}, JobID={job_id}...")
    success = client.delete_stored_job(printer_ip, job_id, admin_password=resolved_password)
    
    if success:
        logger.info("🎉 SUCCESS: The job delete request was processed successfully by the printer!")
    else:
        logger.error("❌ FAILURE: The job delete request failed. Check WIM logs above.")

if __name__ == "__main__":
    main()
