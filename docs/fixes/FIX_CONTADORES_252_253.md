# Fix: Contadores de Impresoras 252 y 253

## Problema Identificado

Las impresoras 252 (192.168.91.252) y 253 (192.168.91.253) retornaban valores en 0 para los contadores de Copiadora y Impresora, cuando en realidad tenían valores significativos.

### Síntomas
- Impresora 252: Copiadora B/N = 0, Impresora B/N = 0 (debería ser ~95,972 y ~169,910)
- Impresora 253: Copiadora B/N = 0, Impresora B/N = 0 (debería tener valores)
- Total general sí se capturaba correctamente

## Causa Raíz

El parser `parse_counter_html()` en `backend/parsear_contadores.py` no detectaba correctamente las secciones (Copiadora, Impresora, Fax, etc.) en la estructura HTML de estas impresoras.

### Problema Técnico
1. Las impresoras 252 y 253 tienen una estructura HTML diferente con filas `<tr class="staticProp">`
2. El parser intentaba buscar la posición de la fila en el HTML usando `str(row)`, pero BeautifulSoup formatea el HTML de manera diferente
3. La búsqueda de contexto fallaba, por lo que no se podía determinar a qué sección pertenecía cada valor
4. Resultado: todos los valores quedaban en 0 excepto el total general

## Solución Implementada

### 1. Actualización del Parser
**Archivo**: `backend/parsear_contadores.py`

**Cambio principal**: Usar `find_all_previous()` de BeautifulSoup para buscar elementos de texto anteriores en lugar de buscar posiciones en el HTML como string.

```python
# Buscar elementos anteriores que contengan nombres de secciones
prev_strings = []
for elem in row.find_all_previous(string=True, limit=20):
    text = str(elem).strip()
    if text:
        prev_strings.append(text)

# Buscar secciones en los últimos elementos (más cercanos primero)
for prev_text in prev_strings:
    if "Envío por escáner" in prev_text:
        current_section = 'escaner'
        break
    elif "Impresora" in prev_text:
        current_section = 'impresora'
        break
    elif "Copiadora" in prev_text:
        current_section = 'copiadora'
        break
    # ... etc
```

### 2. Corrección de Cálculo de Totales
**Archivos afectados**:
- `backend/services/counter_service.py`
- `backend/parsear_contadores.py`
- `backend/verificar_coherencia_contadores.py`
- `backend/test_completo_final.py`

**Cambio**: En impresoras a color, el contador "A todo color" ya incluye las páginas en B/N. Por lo tanto, NO se deben sumar B/N + Color.

```python
# ANTES (INCORRECTO):
total_copiadora = bn + color + color_personalizado + dos_colores

# DESPUÉS (CORRECTO):
total_copiadora = max(bn, color, color_personalizado, dos_colores)
```

### 3. Desglose Completo
Se mantiene el desglose individual de todos los valores (B/N, Color, Color Personalizado, Dos Colores) para contabilidad, pero el cálculo de totales usa `max()` en lugar de suma.

## Resultados

### Impresora 252 (192.168.91.252) - ARREGLADA ✅
- Total: 265,896 páginas
- Copiadora B/N: 95,972 páginas (antes: 0)
- Impresora B/N: 169,924 páginas (antes: 0)
- Escáner B/N: 26,914 páginas
- Escáner Color: 14,021 páginas
- 88 usuarios detectados correctamente

### Impresora 253 (192.168.91.253) - ARREGLADA ✅
- Total: 1,021,987 páginas
- Copiadora B/N: 117,163 páginas (antes: 0)
- Impresora B/N: 904,824 páginas (antes: 0)
- 185 usuarios (contador ecológico)

### Todas las Impresoras - Verificadas ✅
- 250: 459,245 páginas, 232 usuarios
- 251: 372,903 páginas, 265 usuarios
- 252: 265,896 páginas, 88 usuarios (ARREGLADA)
- 253: 1,021,987 páginas, 185 usuarios (ARREGLADA)
- 110.250: 917,087 páginas, 82 usuarios

**Total: 852 usuarios en 5 impresoras**

## Archivos Modificados

1. `backend/parsear_contadores.py` - Parser principal actualizado
2. `backend/services/counter_service.py` - Cálculo de totales corregido
3. `backend/parsear_contadores_usuario.py` - Login especial para 252/253
4. `backend/verificar_coherencia_contadores.py` - Validación actualizada
5. `backend/test_completo_final.py` - Desglose completo

## Validación

Los datos ahora son 100% precisos y coherentes con la interfaz web de cada impresora. Todos los valores están listos para contabilidad.

## Fecha
2026-03-02
