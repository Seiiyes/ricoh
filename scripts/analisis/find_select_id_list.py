"""
Search for selectIdList in adrsListAll.xjs.
"""
import re

with open("/tmp/adrsListAll.xjs", "r", encoding="utf-8") as f:
    content = f.read()

# Find all occurrences of selectIdList
for i, line in enumerate(content.split('\n'), 1):
    if 'selectIdList' in line:
        print(f"{i}: {line.strip()}")
