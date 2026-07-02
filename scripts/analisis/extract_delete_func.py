"""
Read the full Delete function from adrsListAll.xjs
"""
import re

with open('/tmp/adrsListAll.xjs', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Find the delete function starting at function Delete()
start_match = re.search(r'function\s+Delete\s*\(', js_content)
if start_match:
    start_idx = start_match.start()
    # Find matching brace
    brace_count = 0
    end_idx = -1
    for i in range(start_idx, len(js_content)):
        if js_content[i] == '{':
            brace_count += 1
        elif js_content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    if end_idx != -1:
        print(js_content[start_idx:end_idx])
    else:
        print("Matching brace not found.")
else:
    print("Delete function not found.")
