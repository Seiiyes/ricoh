"""
Find external JS scripts in adrsList.html.
"""
from bs4 import BeautifulSoup

with open('/tmp/adrsList.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')
for s in scripts:
    if s.get('src'):
        print(s.get('src'))
