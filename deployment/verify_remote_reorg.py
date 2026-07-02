import paramiko
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

cmd = """python3 -c "
from pathlib import Path
ROOT = Path('/home/odootic/ricoh-app')

# 1. Comprobar archivos en raíz
root_files = [f.name for f in ROOT.iterdir() if f.is_file()]
patterns = [
    'scratch_', 'apply_sprint5', 'verify_sprint5', 'check_migrations', 
    'verify_7104_hw', 'check_7104', 'check_connect_machine', 'check_delete_resp', 
    'check_duplicates', 'run_test_253_clean', 'test_delete_253', 'test_physical_delete', 
    'verify_migrations.sql', 'backup-db.bat', 'restore-db.bat', 'instalar-dependencias.bat',
    'limpiar_cache', 'docker-start', 'start-dev', 'start-local', 'update.sh'
]

orphans = []
for f in root_files:
    for pat in patterns:
        if pat in f:
            orphans.append(f)
            break

print('STATUS_ROOT_CLEAN:', 'OK' if not orphans else 'FAIL')
if orphans:
    print('ORPHANS:', orphans)

# 2. Comprobar subcarpetas de forma recursiva
dirs = [
    'scripts/verificacion',
    'scripts/analisis',
    'scripts/scratch',
    'scripts/debug',
    'backups/src_bak'
]

for d in dirs:
    path = ROOT / d
    if path.exists():
        count = len([x for x in path.rglob('*') if x.is_file()])
        files_list = [x.relative_to(path).as_posix() for x in path.rglob('*') if x.is_file()]
        print(f'DIR_{d.replace(\\"/\\", \\"_\\").upper()}: {count} files (List: {files_list[:4]}...)')
    else:
        print(f'DIR_{d.replace(\\"/\\", \\"_\\").upper()}: NOT_FOUND')
"
"""

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8'))
client.close()
