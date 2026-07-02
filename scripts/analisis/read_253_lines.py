"""
Read adrsListAll_253.xjs lines 140 to 180.
"""
with open("/tmp/adrsListAll_253.xjs", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(139, min(180, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end="")
