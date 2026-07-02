"""
Extract obj_connectMachine definition from adrsListAll.xjs.
"""
import re

with open('/tmp/adrsListAll.xjs', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for function obj_connectMachine
match = re.search(r'function\s+obj_connectMachine\s*\(', content)
if match:
    start_idx = match.start()
    brace_count = 0
    end_idx = -1
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    if end_idx != -1:
        print("Found obj_connectMachine definition:")
        print(content[start_idx:end_idx])
    else:
        print("Matching brace not found.")
else:
    print("obj_connectMachine not found.")
