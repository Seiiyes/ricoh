import os
import re

search_dir = r"c:\Users\juan.lizarazo\Desktop\ricoh"
pattern = re.compile(r'baseID', re.IGNORECASE)

print("Searching for files containing 'baseID':")
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(('.html', '.py', '.ts', '.tsx')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, 1):
                        if pattern.search(line):
                            safe_line = line.strip().encode('ascii', errors='replace').decode('ascii')
                            print(f"{path}:{line_no}: {safe_line}")
            except Exception as e:
                pass
