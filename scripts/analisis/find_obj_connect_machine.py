"""
Find which file defines obj_connectMachine.
"""
import glob
import re

for fn in glob.glob('/tmp/*') + glob.glob('/app/services/*'):
    if not fn.endswith('.xjs') and not fn.endswith('.html') and not fn.endswith('.js'):
        continue
    try:
        with open(fn, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'obj_connectMachine' in content:
            print(f"Found in {fn}")
            # Find definition
            m = re.search(r'function\s+obj_connectMachine', content)
            if m:
                print(f"  Definition found in {fn} at index {m.start()}!")
    except Exception as e:
        pass
