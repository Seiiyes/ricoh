import re

path = r"c:\Users\juan.lizarazo\Desktop\ricoh\backend\services\ricoh_web_client.py"
pattern = re.compile(r'wim_token|wimtoken', re.IGNORECASE)

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line_no, line in enumerate(f, 1):
        if pattern.search(line):
            print(f"{line_no}: {line.strip()}")
