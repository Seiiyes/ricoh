import os
import re

search_dir = r"c:\Users\juan.lizarazo\Desktop\ricoh\backend"
pattern = re.compile(r'wimtoken', re.IGNORECASE)

print("Searching for files containing 'wimtoken':")
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, 1):
                        if pattern.search(line):
                            print(f"{path}:{line_no}: {line.strip()}")
            except Exception as e:
                pass
