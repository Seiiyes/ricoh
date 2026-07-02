"""
Analyze how the delete action is executed in adrsList.cgi HTML/JS.
"""
import re

with open('/tmp/adrsList.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("--- JS function definitions containing 'delete' or 'del' or 'remove' ---")
# Find all script blocks
scripts = re.findall(r'<script.*?>([\s\S]*?)</script>', html, re.IGNORECASE)
for i, script in enumerate(scripts):
    # Find functions inside script
    funcs = re.findall(r'function\s+(\w+)\s*\([\s\S]*?\{([\s\S]*?)\}', script)
    for name, body in funcs:
        if any(w in name.lower() or w in body.lower() for w in ['delete', 'remove', 'del', 'cmd']):
            print(f"Function: {name}")
            # print first 5 lines of body
            body_lines = [l.strip() for l in body.split('\n') if l.strip()]
            for l in body_lines[:15]:
                print(f"  {l}")
            print("  ...")

print("\n--- HTML elements referencing cmdDelete ---")
soup_matches = re.findall(r'<[^>]*?cmdDelete[^>]*?>', html, re.IGNORECASE)
for m in soup_matches:
    print(m)

print("\n--- HTML elements with onclick handlers ---")
onclick_matches = re.findall(r'<[^>]*?onclick\s*=\s*["\']([^"\']*)["\'][^>]*?>', html, re.IGNORECASE)
for m in onclick_matches:
    if any(w in m.lower() for w in ['delete', 'remove', 'del', 'click', 'cmd']):
        print(m)
