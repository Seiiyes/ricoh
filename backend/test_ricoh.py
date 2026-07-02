import sys, os, logging
logging.basicConfig(level=logging.DEBUG)
sys.path.insert(0, '/app')

import asyncio
from services.ricoh_web_client import get_ricoh_web_client

async def test():
    try:
        ricoh_client = get_ricoh_web_client()
        
        print('Fetching details for 192.168.91.250 user 00201...')
        # Intentamos con None (password por defecto)
        res = ricoh_client._get_user_details('192.168.91.250', '00201', fast_sync=False, admin_password=None)
        print(f'\n\n=== RESULT ===\n{res}\n==============\n')
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
