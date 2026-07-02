import re

path = r"c:\Users\juan.lizarazo\Desktop\ricoh\backend\stored_jobs_page.html"

# Search for forms
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

print("Form tags found:")
for match in re.finditer(r'<form[^>]*>', html, re.IGNORECASE):
    print(match.group(0))

print("\nInput names/ids/values found in forms:")
inputs = re.findall(r'<input[^>]*>', html, re.IGNORECASE)
for inp in inputs:
    if any(k in inp.lower() for k in ['wimtoken', 'baseid', 'exec', 'mode', 'selected', 'display_id', 'id']):
        print(inp)
