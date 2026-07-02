"""
Search for entryIndexIn or entryIndex in adrsListAll_253.xjs.
"""
import re

with open("/tmp/adrsListAll_253.xjs", "r", encoding="utf-8") as f:
    content = f.read()

# Print lines containing entryIndexIn or entryIndex
for i, line in enumerate(content.split('\n'), 1):
    if 'entryindexin' in line.lower() or 'entryindex' in line.lower():
        print(f"{i}: {line.strip()}")
