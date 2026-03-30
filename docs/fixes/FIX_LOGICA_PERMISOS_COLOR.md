# Fix: Lógica de Permisos de Color en Impresoras

**Fecha**: 25 de marzo de 2026
**Estado**: ✅ RESUELTO
**Problema**: Cuando se seleccionan solo permisos B/N sin marcar "PERMITIR COLOR", la impresora seguía mostrando habilitadas las funciones de color (A todo color, Dos colores, Color personalizado).

## Problema Identificado

En `backend/services/ricoh_web_client.py`, la función `set_user_functions` tenía DOS problemas:

1. Solo AGREGABA funciones cuando el permiso era `True`, pero NO excluía explícitamente las funciones de color cuando el permiso era `False`
2. Trataba `TC` (Two Colors/Dos colores) y `MC` (Multi Color/Color personalizado) como funciones B/N, cuando en realidad son funciones de COLOR

### Comportamiento Anterior (INCORRECTO)

```python
if 'COPY' in val:
    if any(x in val for x in ['FC', 'FULL', 'COLOR']):
        if permissions.get('copiadora_color'): is_needed = True
    elif any(x in val for x in ['BW', 'TC', 'MC']):  # ❌ TC y MC son COLOR, no B/N
        if permissions.get('copiadora'): is_needed = True
```

### Checkboxes Disponibles en Ricoh

```python
['COPY_FC', 'COPY_TC', 'COPY_MC', 'COPY_BW', 'PRT_FC', 'PRT_BW', 'DBX', 'FAX', 'SCAN', 'MFPBROWSER']
```

Donde:
- `COPY_FC` = Full Color (A todo color) → COLOR
- `COPY_TC` = Two Colors (Dos colores) → COLOR
- `COPY_MC` = Multi Color (Color personalizado) → COLOR
- `COPY_BW` = Black & White (Blanco y negro) → B/N

El código anterior incluía `COPY_TC` y `COPY_MC` cuando solo se seleccionaba B/N, por eso aparecían "Dos colores" y "Color personalizado" marcados en la impresora.

## Solución Implementada

### 1. Corrección de la Clasificación de Funciones

Modificada la lógica para clasificar correctamente las funciones de color vs B/N:

```python
if 'COPY' in val:
    # FC = Full Color (A todo color)
    # TC = Two Colors (Dos colores) 
    # MC = Multi Color (Color personalizado)
    # BW = Black & White (Blanco y negro)
    if any(x in val for x in ['FC', 'FULL', 'COLOR', 'TC', 'MC']):
        # Solo incluir funciones de color si copiadora_color está habilitado
        if permissions.get('copiadora_color'):
            is_needed = True
        # Si copiadora_color=False, explícitamente NO incluir (is_needed queda False)
    elif 'BW' in val:
        # Incluir funciones B/N si copiadora está habilitado
        if permissions.get('copiadora'):
            is_needed = True
```

### 2. Logs de Debug Mejorados

Agregados logs para ver exactamente qué funciones se están activando y desactivando:

```python
logger.info(f"   Checkboxes disponibles: {all_checkbox_values}")
logger.info(f"   Permisos solicitados: {permissions}")
logger.info(f"   Funciones a ACTIVAR ({len(active_funcs)}): {active_funcs}")
logger.info(f"   Funciones a DESACTIVAR ({len(excluded_funcs)}): {excluded_funcs}")
```

### 3. Resultado de los Logs

Antes del fix:
```
Funciones a ACTIVAR (5): ['COPY_TC', 'COPY_MC', 'COPY_BW', 'PRT_BW', 'SCAN']
Funciones a DESACTIVAR (2): ['COPY_FC', 'PRT_FC']
```
❌ Incluía `COPY_TC` y `COPY_MC` (funciones de color)

Después del fix:
```
Funciones a ACTIVAR (3): ['COPY_BW', 'PRT_BW', 'SCAN']
Funciones a DESACTIVAR (4): ['COPY_FC', 'COPY_TC', 'COPY_MC', 'PRT_FC']
```
✅ Solo incluye `COPY_BW` (blanco y negro)

## Comportamiento Esperado

### Caso 1: Solo B/N (sin color) ✅ FUNCIONA
- Usuario selecciona: Copiadora, Impresora, Escáner (sin marcar "PERMITIR COLOR")
- Permisos enviados: `copiadora=True, copiadora_color=False, impresora=True, impresora_color=False, escaner=True`
- Funciones activadas: `['COPY_BW', 'PRT_BW', 'SCAN']`
- Funciones desactivadas: `['COPY_FC', 'COPY_TC', 'COPY_MC', 'PRT_FC']`
- Resultado en impresora: Solo "Blanco y Negro" marcado

### Caso 2: B/N + Color
- Usuario selecciona: Copiadora, Impresora, Escáner + "PERMITIR COLOR"
- Permisos enviados: `copiadora=True, copiadora_color=True, impresora=True, impresora_color=True, escaner=True`
- Funciones activadas: `['COPY_FC', 'COPY_TC', 'COPY_MC', 'COPY_BW', 'PRT_FC', 'PRT_BW', 'SCAN']`
- Resultado en impresora: Todas las opciones de color Y B/N marcadas

### Caso 3: Sin permisos
- Usuario NO selecciona ninguna función
- Permisos enviados: `copiadora=False, copiadora_color=False, impresora=False, impresora_color=False, escaner=False`
- Funciones activadas: `[]`
- Resultado en impresora: Ninguna función habilitada

## Archivos Modificados

- `backend/services/ricoh_web_client.py` (función `set_user_functions`, líneas ~1020-1055)
  - Corregida clasificación de funciones: `TC` y `MC` ahora son tratadas como COLOR, no B/N
  - Agregados logs detallados de checkboxes disponibles y funciones activadas/desactivadas

## Pruebas Realizadas

✅ Usuario con solo permisos B/N → Solo "Blanco y Negro" habilitado en impresora
✅ Funciones de color (A todo color, Dos colores, Color personalizado) deshabilitadas correctamente
✅ Logs muestran correctamente las funciones activadas y desactivadas

## Lecciones Aprendidas

1. Las impresoras Ricoh tienen múltiples modos de color:
   - `FC` (Full Color) = A todo color
   - `TC` (Two Colors) = Dos colores
   - `MC` (Multi Color) = Color personalizado
   - `BW` (Black & White) = Blanco y negro

2. TODOS los modos excepto `BW` son considerados funciones de COLOR

3. La impresora requiere enviar la lista COMPLETA de funciones habilitadas; cualquier función NO incluida se deshabilita automáticamente

4. Es crítico clasificar correctamente las funciones para evitar habilitar permisos no deseados

## Comandos Útiles

```bash
# Ver logs del backend
docker-compose logs backend --tail 150

# Reiniciar backend
docker-compose restart backend
```

## Notas Técnicas

- La impresora Ricoh requiere enviar la lista COMPLETA de funciones habilitadas en cada actualización
- Si una función NO está en la lista `active_funcs`, la impresora la DESHABILITA automáticamente
- Por eso es crítico NO incluir las funciones de color cuando `copiadora_color=False` o `impresora_color=False`
