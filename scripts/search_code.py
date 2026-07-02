import re

path = r"c:\Users\juan.lizarazo\Desktop\ricoh\backend\services\ricoh_web_client.py"
pattern = re.compile(r'def _authenticate', re.IGNORECASE)

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line_no, line in enumerate(f, 1):
        if pattern.search(line):
            # Safe print: encode to utf-8 bytes and decode with replace, or replace non-ascii
            safe_line = line.strip().encode('ascii', errors='replace').decode('ascii')
            print(f"{line_no}: {safe_line}")
