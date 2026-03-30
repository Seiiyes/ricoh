# Diferencia: Hostname vs ID Máquina (Serial)

## ⚠️ IMPORTANTE: No Confundir

En las impresoras Ricoh hay DOS identificadores diferentes que pueden confundirse:

### 1. Hostname (Nombre de Host)
- **Campo en DB**: `hostname`
- **Ejemplo**: `RNP0026737FFBB8`
- **Formato**: Alfanumérico, generalmente empieza con `RNP`
- **Dónde aparece**: 
  - En la web de la impresora como "Nombre de host"
  - En la red como nombre del dispositivo
  - En SNMP como sysName

### 2. ID Máquina (Serial Number)
- **Campo en DB**: `serial_number`
- **Ejemplo**: `E174M210096`
- **Formato**: Alfanumérico, puede empezar con letra
- **Dónde aparece**:
  - En la web de la impresora como "ID máquina"
  - En SNMP como serial number
  - En la etiqueta física de la impresora

## Ejemplo Real (Impresora .250)

```
┌─────────────────────────────────────────┐
│  Interfaz Web de la Impresora Ricoh    │
├─────────────────────────────────────────┤
│                                         │
│  Nombre de host: RNP0026737FFBB8       │  ← Hostname
│  ID máquina:     E174M210096           │  ← Serial Number
│                                         │
└─────────────────────────────────────────┘
```

## En Nuestra Base de Datos

```sql
SELECT hostname, serial_number FROM printers WHERE ip_address = '192.168.91.250';

┌──────────────────┬───────────────┐
│    hostname      │ serial_number │
├──────────────────┼───────────────┤
│ RNP0026737FFBB8  │ E174M210096   │
└──────────────────┴───────────────┘
```

## En el Frontend

Cuando editas una impresora, verás:

```
┌─────────────────────────────────────────┐
│  Editar Impresora                       │
├─────────────────────────────────────────┤
│                                         │
│  Nombre:                                │
│  [RNP0026737FFBB8]                      │  ← Hostname
│                                         │
│  Dirección IP:                          │
│  [192.168.91.250]                       │
│                                         │
│  ID Máquina (Serial):                   │
│  [E174M210096]                          │  ← Serial Number
│  💡 No confundir con el hostname        │
│                                         │
└─────────────────────────────────────────┘
```

## ¿Cuál Usar Para Qué?

### Hostname (`hostname`)
- ✅ Identificar la impresora en la red
- ✅ Nombre amigable para usuarios
- ✅ Puede cambiar si se reconfigura la impresora

### Serial Number (`serial_number`)
- ✅ Identificador único de fábrica
- ✅ No cambia nunca (grabado en hardware)
- ✅ Útil para soporte técnico y garantías
- ✅ Rastreo de equipos físicos

## Errores Comunes

❌ **INCORRECTO**: Poner el hostname en el campo serial
```
serial_number: RNP0026737FFBB8  ← Esto es el hostname, NO el serial
```

✅ **CORRECTO**: Cada uno en su campo
```
hostname:      RNP0026737FFBB8
serial_number: E174M210096
```

## Cómo Obtener el ID Máquina

1. Accede a la interfaz web de la impresora: `http://192.168.91.250`
2. Ve a la sección de información del dispositivo
3. Busca "ID máquina" o "Machine ID"
4. Copia el valor (ejemplo: `E174M210096`)
5. Pégalo en el campo "ID Máquina (Serial)" del modal de edición

## Resumen Visual

```
Impresora Ricoh MP C3004
├── Hostname:      RNP0026737FFBB8  (Nombre de red)
├── IP Address:    192.168.91.250   (Dirección de red)
└── Serial Number: E174M210096      (ID de fábrica)
```

Cada uno tiene su propósito y NO deben confundirse.
