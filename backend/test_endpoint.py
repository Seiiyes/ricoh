#!/usr/bin/env python3
import requests

response = requests.get('http://localhost:8000/api/counters/monthly/7/detail')
data = response.json()
print(f'Status: {response.status_code}')
print(f'ID: {data.get("id")}')
print(f'Usuarios: {len(data.get("usuarios", []))}')
if data.get('usuarios'):
    print(f'Primer usuario: {data["usuarios"][0]["nombre_usuario"]} - Consumo: {data["usuarios"][0]["consumo_total"]}')
    print(f'Top 5:')
    for u in data["usuarios"][:5]:
        print(f'  - {u["nombre_usuario"]}: {u["consumo_total"]:,} páginas')

