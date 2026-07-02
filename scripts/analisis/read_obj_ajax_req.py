"""
Read _obj_ajaxReq definition from ajax.js.
"""
with open("/tmp/ajax.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(51, min(115, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end="")
