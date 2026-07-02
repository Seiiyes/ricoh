import sys

path = '/app/api/discovery.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''        ricoh_client = get_ricoh_web_client()

        # Ejecutar la llamada s\xedncrona al hardware en un thread separado
        # para no bloquear el event loop (permite paralelismo real desde el frontend)
        loop = asyncio.get_event_loop()
        details = await loop.run_in_executor(
            None,
            lambda: ricoh_client._get_user_details(printer_ip, entry_index, fast_sync=False, admin_password=printer_pwd)
        )'''

new_code = '''        # Usar una instancia NUEVA para evitar colisiones de session/tokens en threads
        from services.ricoh_web_client import RicohWebClient
        
        loop = asyncio.get_event_loop()
        details = await loop.run_in_executor(
            None,
            lambda: RicohWebClient()._get_user_details(printer_ip, entry_index, fast_sync=False, admin_password=printer_pwd)
        )'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: patched discovery.py to use isolated RicohWebClient instances')
else:
    # try crlf
    old_crlf = old_code.replace('\n', '\r\n')
    new_crlf = new_code.replace('\n', '\r\n')
    if old_crlf in content:
        content = content.replace(old_crlf, new_crlf)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('OK: patched discovery.py (CRLF)')
    else:
        print('ERROR: could not find code to patch in discovery.py')
