import sys
sys.path.insert(0, '/app')

from db.database import SessionLocal
from db import models
from sqlalchemy import text

db = SessionLocal()
try:
    print("=== DEDUPLICATION SCRIPT FOR user_printer_assignments ===\n")
    
    # Find all duplicates
    result = db.execute(text("""
        SELECT user_id, printer_id, COUNT(*) as cnt
        FROM user_printer_assignments
        GROUP BY user_id, printer_id
        HAVING COUNT(*) > 1
        ORDER BY user_id, printer_id
    """))
    duplicates = result.fetchall()
    
    if not duplicates:
        print("No duplicates found!")
    else:
        print(f"Found {len(duplicates)} duplicate groups:")
        for dup in duplicates:
            print(f"  user_id={dup[0]}, printer_id={dup[1]}, count={dup[2]}")
        
        print("\n--- Resolving duplicates ---")
        for dup in duplicates:
            user_id, printer_id, cnt = dup[0], dup[1], dup[2]
            
            # Get all rows for this pair ordered by:
            # 1. Rows with any permissions True first
            # 2. Latest provisioned_at
            rows = db.execute(text("""
                SELECT id, is_active, entry_index, func_copier, func_printer, func_scanner,
                       func_copier_color, func_printer_color, func_document_server, func_fax, func_browser,
                       provisioned_at
                FROM user_printer_assignments
                WHERE user_id = :uid AND printer_id = :pid
                ORDER BY 
                    (func_copier::int + func_printer::int + func_scanner::int + 
                     func_copier_color::int + func_printer_color::int + func_fax::int) DESC,
                    provisioned_at DESC
            """), {"uid": user_id, "pid": printer_id}).fetchall()
            
            # Keep the best row (first one), delete the rest
            best_row = rows[0]
            rows_to_delete = rows[1:]
            
            print(f"\n  user_id={user_id}, printer_id={printer_id}:")
            print(f"    KEEPING id={best_row[0]} (copier={best_row[3]}, printer={best_row[4]}, scanner={best_row[5]}, entry_index={best_row[2]})")
            
            for row in rows_to_delete:
                print(f"    DELETING id={row[0]}")
                db.execute(text("DELETE FROM user_printer_assignments WHERE id = :id"), {"id": row[0]})
        
        db.commit()
        print("\n=== Deduplication complete ===")
    
    # Verify result
    print("\n--- Verification ---")
    result = db.execute(text("""
        SELECT upa.id, upa.user_id, upa.printer_id, upa.is_active, upa.entry_index,
               upa.func_copier, upa.func_printer, upa.func_scanner,
               u.codigo_de_usuario, u.name, p.ip_address
        FROM user_printer_assignments upa
        JOIN users u ON u.id = upa.user_id
        JOIN printers p ON p.id = upa.printer_id
        WHERE u.codigo_de_usuario = '7104'
        ORDER BY upa.printer_id
    """))
    rows = result.fetchall()
    print(f"\nUser 7104 assignments after dedup ({len(rows)} rows):")
    for row in rows:
        print(f"  ID={row[0]}, printer_id={row[2]}, ip={row[10]}, is_active={row[3]}, "
              f"entry_index={row[4]}, copier={row[5]}, printer={row[6]}, scanner={row[7]}")
    
    # Now try to add UNIQUE constraint
    print("\n--- Adding UNIQUE constraint ---")
    try:
        db.execute(text("""
            ALTER TABLE user_printer_assignments 
            ADD CONSTRAINT uq_user_printer UNIQUE (user_id, printer_id)
        """))
        db.commit()
        print("UNIQUE constraint added successfully!")
    except Exception as e:
        db.rollback()
        print(f"Could not add UNIQUE constraint: {e}")

finally:
    db.close()
