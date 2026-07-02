import sys
sys.path.insert(0, '/app')

from db.database import SessionLocal
from db import models
from sqlalchemy import text

db = SessionLocal()
try:
    # Fix entry_index=None for printer 192.168.91.250
    result = db.execute(text("""
        UPDATE user_printer_assignments upa
        SET entry_index = '00231'
        WHERE upa.id = 14
        AND upa.entry_index IS NULL
        RETURNING id, user_id, printer_id, entry_index
    """))
    row = result.fetchone()
    if row:
        print(f"Updated assignment ID={row[0]}: entry_index now = {row[3]}")
    else:
        print("No update (entry_index already set or row not found)")
    
    db.commit()
    
    # Show final state for user 7104
    print("\n=== FINAL DB STATE FOR USER 7104 ===")
    result2 = db.execute(text("""
        SELECT upa.id, upa.printer_id, upa.is_active, upa.entry_index,
               upa.func_copier, upa.func_printer, upa.func_scanner,
               p.ip_address, p.hostname
        FROM user_printer_assignments upa
        JOIN printers p ON p.id = upa.printer_id
        WHERE upa.user_id = 3
        ORDER BY upa.printer_id
    """))
    for row in result2.fetchall():
        print(f"\n  ID={row[0]}, Printer {row[7]} ({row[8]}):")
        print(f"    is_active={row[2]}, entry_index={row[3]}")
        print(f"    copier={row[4]}, printer={row[5]}, scanner={row[6]}")
        
finally:
    db.close()
