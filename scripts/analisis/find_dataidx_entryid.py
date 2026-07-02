"""
Search for DATAIDX_ENTRYID in adrsListAll.xjs.
"""
with open("/tmp/adrsListAll.xjs", "r", encoding="utf-8") as f:
    content = f.read()

# Print lines containing DATAIDX_ENTRYID
for i, line in enumerate(content.split('\n'), 1):
    if 'DATAIDX_ENTRYID' in line:
        print(f"{i}: {line.strip()}")
