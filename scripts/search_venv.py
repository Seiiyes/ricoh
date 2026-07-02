import os

print("Searching for venv or virtualenvs in workspace:")
for root, dirs, files in os.walk(r"c:\Users\juan.lizarazo\Desktop\ricoh"):
    for d in dirs:
        if d in ['venv', '.venv', 'env', '.env-py']:
            print(os.path.join(root, d))
    # only search top 3 levels to be fast
    if root.count(os.sep) - r"c:\Users\juan.lizarazo\Desktop\ricoh".count(os.sep) > 3:
        dirs.clear()
