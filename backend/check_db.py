import sqlite3

conn = sqlite3.connect('ricoh_users.db')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print('Tables:', [t[0] for t in tables])

print('\n=== ASSIGNMENTS WITH PERMISSIONS ===')
cur.execute('''
    SELECT 
        u.id, u.name, u.codigo_de_usuario,
        ua.printer_id, ua.entry_index,
        ua.func_copier, ua.func_printer, ua.func_scanner,
        ua.func_copier_color, ua.func_printer_color,
        ua.func_document_server, ua.func_fax, ua.func_browser,
        p.name as printer_name, p.ip_address
    FROM users u
    JOIN user_assignments ua ON u.id = ua.user_id
    JOIN printers p ON ua.printer_id = p.id
    LIMIT 10
''')
rows = cur.fetchall()
for r in rows:
    print(f'User: {r[1]} ({r[2]}) | Printer: {r[13]} ({r[14]})')
    print(f'  entry_index: {r[4]}')
    print(f'  copier={r[5]}, printer={r[6]}, scanner={r[7]}')
    print(f'  copier_color={r[8]}, printer_color={r[9]}')
    print(f'  doc_server={r[10]}, fax={r[11]}, browser={r[12]}')
    print()
conn.close()
