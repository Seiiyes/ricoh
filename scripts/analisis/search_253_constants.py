"""
Search for ADRS_DELETE and other constants in adrsListAll_253.xjs.
"""
import re

with open("/tmp/adrsListAll_253.xjs", "r", encoding="utf-8") as f:
    content = f.read()

# Print lines containing ADRS_DELETE or other ADRS_ constants
for i, line in enumerate(content.split('\n'), 1):
    if 'ADRS_DELETE' in line or 'ADRS_' in line:
        print(f"{i}: {line.strip()}")
