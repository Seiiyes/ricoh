#!/usr/bin/env python3
"""
Analiza el HTML guardado para determinar estructura de columnas
"""
from bs4 import BeautifulSoup

def analyze_html(html_file):
    """Analiza el HTML guardado"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find table
    table = soup.find('table', class_='adTable')
    if not table:
        table = soup.find('table', class_='tbl_border')
    
    if not table:
        print("❌ No se encontró tabla")
        return
    
    print("="*80)
    print("ANÁLISIS DE TABLA")
    print("="*80)
    
    # Analyze headers
    print("\nENCabezados:")
    print("-"*80)
    rows = table.find_all('tr')
    
    for i, row in enumerate(rows[:3]):
        headers = row.find_all('th')
        if headers:
            print(f"\nFila {i+1} - {len(headers)} columnas:")
            for j, th in enumerate(headers):
                colspan = th.get('colspan', '1')
                rowspan = th.get('rowspan', '1')
                text = th.get_text(strip=True)
                print(f"  [{j:2d}] colspan={colspan} rowspan={rowspan} | {text}")
    
    # Find first data row
    print("\n" + "="*80)
    print("PRIMERA FILA DE DATOS:")
    print("-"*80)
    
    for row in rows:
        if row.find('th'):
            continue
        
        cells = row.find_all('td')
        cells_with_class = row.find_all('td', class_='listData')
        
        if cells:
            print(f"\nTotal celdas: {len(cells)}")
            print(f"Celdas con class='listData': {len(cells_with_class)}")
            
            if cells_with_class:
                print("\nContenido (solo listData):")
                for i, cell in enumerate(cells_with_class):
                    text = cell.get_text(strip=True)
                    print(f"  [{i:2d}] {text}")
            else:
                print("\nContenido (todas las celdas):")
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    print(f"  [{i:2d}] {text}")
            
            break
    
    print("\n" + "="*80)

if __name__ == '__main__':
    analyze_html("printer_251_counters.html")
