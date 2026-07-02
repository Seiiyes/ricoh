"""
Search for LOAD_NUM in adrsListAll_253.xjs.
"""
with open("/tmp/adrsListAll_253.xjs", "r", encoding="utf-8") as f:
    text = f.read()

for i, line in enumerate(text.split('\n'), 1):
    if 'LOAD_NUM' in line:
        print(f"{i}: {line.strip()}")
