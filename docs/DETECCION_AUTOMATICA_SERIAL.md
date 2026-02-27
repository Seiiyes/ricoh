# Detección Automática del Serial (ID Máquina)

## Resumen

El sistema ahora detecta automáticamente el **ID Máquina (Serial)** de las impresoras Ricoh durante el descubrimiento de red.

## Cómo Funciona

### 1. Durante el Escaneo de Red

Cuando ejecutas "Descubrir Impresoras" (`POST /discovery/scan`):

```
Usuario → Frontend → Backend → NetworkScanner
                                    ↓
                            detect_printer(ip)
                                    ↓
                            ¿Es Ricoh? → Sí
                                    ↓
                            get_ricoh_serial(ip)
                                    ↓
                            Accede a web de impresora
                                    ↓
                            Busca "ID máquina"
                                    ↓
                            Retorna serial
```

### 2. Flujo Detallado

```python
# 1. Detectar impresora
is_printer, device_info = await detect_printer(ip)

# 2. Si es Ricoh, obtener serial desde web
if 'ricoh' in model.lower():
    serial_number = await get_ricoh_serial(ip)

# 3. Incluir serial en device_info
device_info = {
    "hostname": "RNP0026737FFBB8",
    "serial_number": "E174M210096",  # ← Obtenido automáticamente
    ...
}
```

### 3. Método `get_ricoh_serial()`

Este método:

1. **Accede a páginas de configuración** de la impresora:
   - `/web/guest/es/websys/status/configuration.cgi`
   - `/web/guest/en/websys/status/configuration.cgi`
   - `/web/guest/es/websys/webArch/mainFrame.cgi`

2. **Busca patrones** en el HTML:
   ```regex
   ID\s+m[áa]quina[:\s]+([A-Z0-9]+)
   Machine\s+ID[:\s]+([A-Z0-9]+)
   Serial\s+Number[:\s]+([A-Z0-9]+)
   ```

3. **Extrae el valor**:
   ```html
   <!-- Ejemplo de HTML de Ricoh -->
   <td>ID máquina:</td>
   <td>E174M210096</td>  ← Extrae esto
   ```

4. **Retorna el serial** o `None` si no lo encuentra

## Ejemplo Real

### Impresora .250

**Entrada:**
```
IP: 192.168.91.250
```

**Proceso:**
```
1. Detecta que es Ricoh MP Series
2. Accede a http://192.168.91.250/web/guest/es/websys/status/configuration.cgi
3. Encuentra: "ID máquina: E174M210096"
4. Extrae: "E174M210096"
```

**Resultado:**
```json
{
  "ip_address": "192.168.91.250",
  "hostname": "RNP0026737FFBB8",
  "serial_number": "E174M210096",
  "detected_model": "RICOH MP Series",
  "status": "online"
}
```

## Ventajas

✅ **Automático**: No necesitas ingresar el serial manualmente
✅ **Preciso**: Obtiene el valor directamente de la impresora
✅ **Rápido**: Se ejecuta durante el descubrimiento normal
✅ **Fallback**: Si falla, puedes ingresarlo manualmente después

## Limitaciones

⚠️ **Solo Ricoh**: Actualmente solo funciona con impresoras Ricoh
⚠️ **Requiere acceso web**: La impresora debe tener la interfaz web accesible
⚠️ **Idioma**: Busca en español e inglés, pero puede fallar con otros idiomas
⚠️ **Modelos antiguos**: Algunos modelos muy antiguos pueden no tener esta información en la web

## Fallback Manual

Si el sistema no puede detectar el serial automáticamente:

1. El campo `serial_number` quedará como `NULL`
2. Puedes editarlo manualmente desde el modal de edición
3. Ve a Equipos → Editar impresora → Campo "ID Máquina (Serial)"

## Logs

Durante el descubrimiento, verás logs como:

```
✅ Found Ricoh serial (ID máquina): E174M210096 for 192.168.91.250
✅ Found Ricoh serial (ID máquina): E174M210097 for 192.168.91.251
⚠️  No serial number found for 192.168.91.248
```

## Código Relevante

### NetworkScanner (`backend/services/network_scanner.py`)

```python
async def get_ricoh_serial(self, ip: str) -> Optional[str]:
    """Get serial number (ID máquina) from Ricoh web interface"""
    # Accede a páginas de configuración
    # Busca patrones de "ID máquina"
    # Retorna serial o None
```

```python
async def detect_printer(self, ip: str) -> Tuple[bool, Optional[Dict]]:
    """Detect printer and get info"""
    # ... detección normal ...
    
    # Si es Ricoh y no hay serial de SNMP
    if not serial_number and 'ricoh' in model.lower():
        serial_number = await self.get_ricoh_serial(ip)
    
    # Incluye serial en device_info
    device_info = {
        "serial_number": serial_number,
        ...
    }
```

## Pruebas

Para probar la detección automática:

1. Elimina las impresoras actuales (opcional)
2. Ejecuta "Descubrir Impresoras"
3. Verifica que las impresoras Ricoh tengan serial:

```sql
SELECT hostname, ip_address, serial_number 
FROM printers 
WHERE serial_number IS NOT NULL;
```

Deberías ver:
```
RNP0026737FFBB8 | 192.168.91.250 | E174M210096
RNP00267391F283 | 192.168.91.251 | E174M210097
...
```

## Mejoras Futuras

Posibles mejoras:
- Soporte para otras marcas (Kyocera, HP, etc.)
- Caché de seriales para evitar consultas repetidas
- Detección de cambios de serial (si se reemplaza la impresora)
- Validación de formato de serial por marca
