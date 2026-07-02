"""
Find how batches are requested in .253 JS files.
"""
import re

for fn in ["/tmp/adrsListAll_253.xjs", "/tmp/adrsBase_253.xjs"]:
    with open(fn, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"\n--- Checking in {fn} ---")
    for line in text.split('\n'):
        if any(w in line.lower() for w in ['batch', 'getcountin', 'listcountin', 'loadbatch']):
            print("  ", line.strip())
