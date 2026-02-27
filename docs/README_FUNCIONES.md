# Gestión de Funciones de Usuarios Ricoh

## Solución Definitiva

Usa Playwright para modificar funciones de usuarios en impresoras Ricoh.

## Instalación

```bash
# Ya instalado
pip install playwright
playwright install chromium
```

## Uso

### Modificar Funciones de un Usuario

```bash
cd backend
.\venv\Scripts\python.exe gestionar_funciones.py
```

El script:
1. Abrirá un navegador Chrome
2. Hará login en la impresora
3. Buscará el usuario 7104
4. Modificará las funciones
5. Guardará los cambios

### Personalizar

Edita `gestionar_funciones.py` y cambia:

```python
# Configuración
printer_ip = "192.168.91.251"  # IP de tu impresora
user_code = "7104"              # Código del usuario

# Funciones a habilitar/deshabilitar
funciones_deseadas = {
    'copiadora': True,          # Habilitar
    'impresora': True,          # Habilitar
    'escaner': True,            # Habilitar SCAN
    'fax': False,               # Deshabilitar
    # etc.
}
```

### Usar desde tu Código

```python
from gestionar_funciones import modificar_funciones
import asyncio

async def ejemplo():
    funciones = {
        'copiadora': True,
        'impresora': True,
        'escaner': True,
        'fax': False
    }
    
    success = await modificar_funciones(
        printer_ip="192.168.91.251",
        user_code="7104",
        funciones_deseadas=funciones
    )
    
    if success:
        print("Funciones modificadas correctamente")
    else:
        print("Error al modificar funciones")

# Ejecutar
asyncio.run(ejemplo())
```

## Funciones Disponibles

- `copiadora` - Copiadora B/N (COPY_BW)
- `copiadora_color` - Copiadora Color (COPY_FC)
- `impresora` - Impresora B/N (PRT_BW)
- `impresora_color` - Impresora Color (PRT_FC)
- `escaner` - Escáner (SCAN)
- `document_server` - Document Server (DBX)
- `fax` - Fax (FAX)
- `navegador` - Navegador (MFPBROWSER)

## Notas

- El navegador se abre en modo visible (no headless) para que puedas ver el proceso
- Tarda aproximadamente 30-40 segundos por usuario
- Si falla, revisa que:
  - La impresora esté accesible
  - El código de usuario sea correcto
  - El usuario exista en la impresora

## Troubleshooting

### "Usuario no encontrado"
- Verifica que el código de usuario sea correcto
- Asegúrate de que el usuario existe en la impresora

### "No se encontraron checkboxes"
- El formulario puede no haberse cargado
- Aumenta los timeouts en el código

### El navegador se cierra inmediatamente
- Verifica que Playwright esté instalado correctamente
- Ejecuta: `playwright install chromium`

---

**Archivo principal:** `gestionar_funciones.py`  
**Tecnología:** Playwright (navegador automatizado)  
**Tiempo:** ~30-40 segundos por usuario
