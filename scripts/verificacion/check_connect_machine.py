"""
Search for g_objConnectMachine definition to see if it does GET or POST.
"""
import re

# Read ajax.js and adrsBase.xjs
files_to_check = [
    '/tmp/adrsBase.xjs',
    '/tmp/adrsListAll.xjs',
    '/tmp/adrsUserWizard.xjs',
    '/tmp/adrsList.html'
]

# Let's also download ajax.js and list common JS files from container if they exist
# Wait, let's just search the files we already downloaded
for fn in files_to_check:
    try:
        with open(fn, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"\n--- Checking in {fn} ---")
        # Search for g_objConnectMachine or ConnectMachine definition
        matches = re.findall(r'(\w*ConnectMachine[\s\S]*?\{[\s\S]*?\})', content)
        for m in matches[:5]:
            print("Match:")
            print('\n'.join(m.split('\n')[:15]))
        
        # Search for .get or .post calls or definitions
        if 'g_objConnectMachine' in content:
            print("Found g_objConnectMachine reference(s)")
            # Find lines referencing g_objConnectMachine
            for line in content.split('\n'):
                if 'g_objConnectMachine' in line:
                    print("  ", line.strip())
    except Exception as e:
        print(f"Error checking {fn}: {e}")
