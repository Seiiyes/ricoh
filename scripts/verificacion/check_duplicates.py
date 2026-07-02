import sys
sys.path.insert(0, '/app')

from db.database import SessionLocal
from db import models
from sqlalchemy import text

db = SessionLocal()
try:
    # Raw query to see all assignments with IDs
    result = db.execute(text("""
        SELECT upa.id, upa.user_id, upa.printer_id, upa.is_active, upa.entry_index,
               upa.func_copier, upa.func_printer, upa.func_scanner,
               upa.provisioned_at,
               p.ip_address, p.hostname
        FROM user_printer_assignments upa
        JOIN printers p ON p.id = upa.printer_id
        WHERE upa.user_id = 3
        ORDER BY upa.printer_id, upa.id
    """))
    rows = result.fetchall()
    print(f"Total rows for user 7104 (id=3): {len(rows)}")
    print()
    for row in rows:
        print(f"ID={row[0]}, printer_id={row[2]}, ip={row[9]}, is_active={row[3]}, "
              f"entry_index={row[4]}, copier={row[5]}, printer={row[6]}, scanner={row[7]}, "
              f"provisioned={row[8]}")
    
    # Check if there's a unique constraint
    print("\n--- Table constraints ---")
    result2 = db.execute(text("""
        SELECT conname, contype, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'user_printer_assignments'::regclass
    """))
    for row in result2:
        print(f"  {row[0]}: {row[2]}")

finally:
    db.close()
