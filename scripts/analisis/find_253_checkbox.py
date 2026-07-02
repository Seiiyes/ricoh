"""
Search for checkbox rendering in adrsListAll_253.xjs.
"""
import re

with open("/tmp/adrsListAll_253.xjs", "r", encoding="utf-8") as f:
    content = f.read()

# Print lines containing type='checkbox' or type=\"checkbox\" or checkbox
for i, line in enumerate(content.split('\n'), 1):
    if 'checkbox' in line.lower() or 'selectcell' in line.lower():
        print(f"{i}: {line.strip()}")
