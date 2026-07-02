import paramiko
from pathlib import Path
import sys

# Cargar configuración SSH
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

REMOTE_DIR = f"/home/{USER}/ricoh-app"

print(f"Connecting to remote server: {HOST}...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

# Comando inline de python3 para ejecutar en el servidor
cmd = f"""python3 -c "
import os
import shutil
from pathlib import Path

ROOT = Path('{REMOTE_DIR}')
SCRIPTS_DIR = ROOT / 'scripts'
VERIF_DIR = SCRIPTS_DIR / 'verificacion'
ANALISIS_DIR = SCRIPTS_DIR / 'analisis'
SCRATCH_DIR = SCRIPTS_DIR / 'scratch'
DEBUG_DIR = SCRIPTS_DIR / 'debug'
DOCS_SEGURIDAD = ROOT / 'docs' / 'seguridad'
DOCS_DEPLOY = ROOT / 'docs' / 'deployment'
BACKUPS_SRC = ROOT / 'backups' / 'src_bak'

# Crear directorios
for d in [VERIF_DIR, ANALISIS_DIR, SCRATCH_DIR, DEBUG_DIR, DOCS_SEGURIDAD, DOCS_DEPLOY, BACKUPS_SRC]:
    d.mkdir(parents=True, exist_ok=True)

moves = {{
    # Verificacion
    'apply_sprint5_migrations.bat': VERIF_DIR,
    'verify_sprint5_migrations.bat': VERIF_DIR,
    'check_migrations.py': VERIF_DIR,
    'verify_7104_hw.py': VERIF_DIR,
    'check_7104.py': VERIF_DIR,
    'check_connect_machine.py': VERIF_DIR,
    'check_delete_resp.py': VERIF_DIR,
    'check_duplicates.py': VERIF_DIR,
    'run_test_253_clean.py': VERIF_DIR,
    'test_delete_253.py': VERIF_DIR,
    'test_physical_delete.py': VERIF_DIR,
    'verify_migrations.sql': VERIF_DIR,

    # Analisis / Scrapers
    'analyze_js_delete.py': ANALISIS_DIR,
    'download_js_files.py': ANALISIS_DIR,
    'extract_delete_func.py': ANALISIS_DIR,
    'extract_obj_connect_machine.py': ANALISIS_DIR,
    'extract_obj_connect_machine_v2.py': ANALISIS_DIR,
    'find_253_checkbox.py': ANALISIS_DIR,
    'find_253_checkbox_base.py': ANALISIS_DIR,
    'find_253_constants_base.py': ANALISIS_DIR,
    'find_253_listcount.py': ANALISIS_DIR,
    'find_253_load_entry.py': ANALISIS_DIR,
    'find_253_load_num.py': ANALISIS_DIR,
    'find_253_test_users.py': ANALISIS_DIR,
    'find_all_253_listcount.py': ANALISIS_DIR,
    'find_dataidx_entryid.py': ANALISIS_DIR,
    'find_entry_id.py': ANALISIS_DIR,
    'find_obj_connect_machine.py': ANALISIS_DIR,
    'find_raw_user_details.py': ANALISIS_DIR,
    'find_select_id_list.py': ANALISIS_DIR,
    'fix_duplicates.py': ANALISIS_DIR,
    'fix_entry_index.py': ANALISIS_DIR,
    'get_252_user_form.py': ANALISIS_DIR,
    'get_253_user_form.py': ANALISIS_DIR,
    'get_ajax_async.py': ANALISIS_DIR,
    'inspect_253_js.py': ANALISIS_DIR,
    'inspect_253_list_html.py': ANALISIS_DIR,
    'inspect_adrs_list.py': ANALISIS_DIR,
    'inspect_ajax_send.py': ANALISIS_DIR,
    'list_js_sources.py': ANALISIS_DIR,
    'read_253_lines.py': ANALISIS_DIR,
    'read_obj_ajax_req.py': ANALISIS_DIR,
    'scan_all_printers.py': ANALISIS_DIR,
    'scan_checkboxes.py': ANALISIS_DIR,
    'search_253_batches.py': ANALISIS_DIR,
    'search_253_constants.py': ANALISIS_DIR,
    'search_253_entry_index.py': ANALISIS_DIR,

    # Debug / HTML Temp
    'debug_delete_flow.py': DEBUG_DIR,
    'debug_delete_v2.py': DEBUG_DIR,
    'debug_delete_v3.py': DEBUG_DIR,
    'debug_delete_v4.py': DEBUG_DIR,
    'debug_delete_v5.py': DEBUG_DIR,
    'debug_step2_fail.html': DEBUG_DIR,
    'password_step2_error.html': DEBUG_DIR,
    'update_user_response_00195.html': DEBUG_DIR,
    'update_user_response_00231.html': DEBUG_DIR,

    # Documentacion
    'CREDENCIALES_SEGURAS_6_MAYO_2026.txt': DOCS_SEGURIDAD,
    'MIGRACION_PRODUCCION.md': DOCS_DEPLOY,
}}

root_scripts = [
    'backup-db.bat',
    'restore-db.bat',
    'instalar-dependencias.bat',
    'limpiar_cache_frontend.bat',
    'limpiar_cache_navegador.bat',
    'docker-start.bat',
    'docker-start.sh',
    'start-dev.bat',
    'start-dev.sh',
    'start-local.bat',
    'update.sh',
]
for script in root_scripts:
    moves[script] = SCRIPTS_DIR

# Buscar scratch files
for f in ROOT.glob('scratch_*.py'):
    moves[f.name] = SCRATCH_DIR

# Ejecutar movimientos
moved = 0
for filename, dest_dir in moves.items():
    src = ROOT / filename
    if src.exists():
        dest = dest_dir / filename
        shutil.move(str(src), str(dest))
        print(f'MOVED REMOTE: {{filename}} -> {{dest.relative_to(ROOT)}}')
        moved += 1

# Mover backups del frontend
src_path = ROOT / 'src'
moved_bak = 0
if src_path.exists():
    for bak_file in src_path.rglob('*.bak'):
        rel_path = bak_file.relative_to(src_path)
        dest_path = BACKUPS_SRC / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(bak_file), str(dest_path))
        print(f'CLEANED REMOTE BAK: src/{{rel_path}} -> backups/src_bak/{{rel_path}}')
        moved_bak += 1

print(f'REMOTE REORG COMPLETED. Moved {{moved}} root files, {{moved_bak}} .bak files.')
"
"""

print("Executing reorganization script on remote server...")
stdin, stdout, stderr = client.exec_command(cmd)

out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')

print("\n=== REMOTE STDOUT ===")
print(out)

if err:
    print("\n=== REMOTE STDERR ===")
    print(err)

client.close()
print("Remote script executed.")
