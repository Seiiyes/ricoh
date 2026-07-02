"""
Search for entryId in adrsListAll.xjs.
"""
import re

with open("/tmp/adrsListAll.xjs", "r", encoding="utf-8") as f:
    content = f.read()

# Print lines containing entryId
for i, line in enumerate(content.split('\n'), 1):
    if 'entryId' in line:
        print(f"{i}: {line.strip()}")
