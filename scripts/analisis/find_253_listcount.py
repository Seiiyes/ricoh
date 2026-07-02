"""
Search for listCount in adrsListAll_253.xjs.
"""
with open("/tmp/adrsListAll_253.xjs", "r", encoding="utf-8") as f:
    text = f.read()

for line in text.split('\n'):
    if 'listCount' in line and ('=' in line or 'var' in line):
        print(line.strip())
