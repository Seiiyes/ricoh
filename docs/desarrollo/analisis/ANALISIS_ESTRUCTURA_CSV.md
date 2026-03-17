# Análisis de Estructura de CSV y Datos de Importación

## 🔍 PROBLEMA IDENTIFICADO

El script actual está mezclando dos tipos de datos diferentes:

### 1. COMPARATIVOS (CSV_COMPARATIVOS)
**Propósito**: Mostrar CONSUMO entre dos meses (diferencias)

#### Archivos tipo "COMPARATIVO":
- `E176M460020 ENERO - FEBRERO_E176M460020 COMPARATIVO.csv`
- Formato: `Usuario,Nombre,B/N,COLOR,TOTAL IMPRESORAS`
- **IMPORTANTE**: Estos datos son CONSUMOS (diferencia entre enero y febrero)
- Ejemplo: Usuario [1805] tiene 5478 páginas = consumo de febrero

#### Archivos tipo "FEBRERO" en comparativos:
- `E176M460020 ENERO - FEBRERO_E176M460020 FEBRERO.csv`
- Formato completo con todos los campos detallados
- **IMPORTANTE**: Estos son SNAPSHOTS ACUMULADOS (contadores totales al final de febrero)
- Incluye: Total impresiones, Copiadora, Impresora, Escáner, Fax con desglose B/N y Color

### 2. CONTADOR IMPRESORAS FEBRERO
**Propósito**: Snapshots de contadores al final de febrero

#### Archivos:
- `W533L900719 16.02.2026.csv` - Formato simple (solo total páginas impresión)
- `E176M460020 26.02.2026.csv` - Formato con B/N, COLOR, TOTAL IMPRESORAS

**IMPORTANTE**: 
- Para E176M460020, el archivo en CONTADOR IMPRESORAS FEBRERO muestra CONSUMOS
- El archivo correcto para snapshots está en CSV_COMPARATIVOS

### 3. COMPARATIVO FINAL
**Propósito**: Resumen de totales por impresora

Archivo: `COMPARATIVO FINAL ENERO - FEBRERO_COMPARATIVO  FINAL.csv`
- Muestra totales generales por impresora
- Ejemplo:
  ```
  W533L900719, ENERO, 988587
  W533L900719, FEBRERO, 1010592
  Diferencia: 22005
  ```

## 📊 DATOS CORRECTOS A IMPORTAR

### Para CIERRES MENSUALES (tabla principal):
**Fuente**: COMPARATIVO FINAL
- `total_paginas`: Contador acumulado de febrero (ej: 1010592)
- `diferencia_total`: Consumo del mes (ej: 22005)

### Para USUARIOS (tabla detalle):
**Fuente**: Depende de la impresora

#### Impresoras con formato detallado (E174M210096, E174MA11130, G986XA16285, E176M460020):
**Archivo**: `CSV_COMPARATIVOS/[SERIAL] ENERO - FEBRERO_[SERIAL] FEBRERO.csv`
- Contiene SNAPSHOTS ACUMULADOS con desglose completo
- Campos disponibles:
  - Total impresiones (snapshot acumulado)
  - Copiadora B/N y Color
  - Impresora B/N y Color
  - Escáner B/N y Color
  - Fax B/N

#### Impresora W533L900719:
**Archivo**: `CONTADOR IMPRESORAS FEBRERO/W533L900719 16.02.2026.csv`
- Formato simple: solo total páginas impresión
- No tiene desglose por función

## ⚠️ ERRORES EN SCRIPT ACTUAL

### Error 1: Uso incorrecto de archivos COMPARATIVO
```python
# INCORRECTO - archivo de consumos
"E176M460020": ("COMPARATIVO", "E176M460020 ENERO - FEBRERO_E176M460020 COMPARATIVO.csv")
```

### Error 2: Interpretación de datos
El script actual trata todos los datos como snapshots, pero:
- Archivos COMPARATIVO = consumos (diferencias)
- Archivos FEBRERO en comparativos = snapshots acumulados ✅
- Archivos en CONTADOR IMPRESORAS FEBRERO = mixto (depende de impresora)

## ✅ SOLUCIÓN CORRECTA

### Mapeo de archivos correcto:
```python
ARCHIVOS_USUARIOS = {
    "W533L900719": ("CONTADOR", "W533L900719 16.02.2026.csv"),
    "E174M210096": ("CSV_COMPARATIVOS", "E174M210096 ENERO - FEBRERO_E174M210096 FEBRERO.csv"),
    "E174MA11130": ("CSV_COMPARATIVOS", "E174MA11130 ENERO - FEBRERO_E174MA11130 FEBRERO.csv"),
    "G986XA16285": ("CSV_COMPARATIVOS", "G986XA16285 ENERO - FEBRERO_G986XA16285 FEBRERO.csv"),
    "E176M460020": ("CSV_COMPARATIVOS", "E176M460020 ENERO - FEBRERO_E176M460020 FEBRERO.csv"),
}
```

### Interpretación de datos:
1. **Snapshots (campos snapshot_*)**: Usar valores directamente de archivos FEBRERO
2. **Consumos (campos consumo_*)**: Calcular diferencia con mes anterior O usar archivos COMPARATIVO

## 🎯 CAMPOS EN BASE DE DATOS

### Tabla: cierres_mensuales_usuarios

#### Campos SNAPSHOT (contadores acumulados):
- `total_paginas`: Snapshot acumulado total
- `total_bn`: Snapshot B/N
- `total_color`: Snapshot Color
- `copiadora_bn`, `copiadora_color`
- `impresora_bn`, `impresora_color`
- `escaner_bn`, `escaner_color`
- `fax_bn`

#### Campos CONSUMO (uso del mes):
- `consumo_total`: Páginas usadas en febrero
- `consumo_copiadora`: Páginas copiadora en febrero
- `consumo_impresora`: Páginas impresora en febrero
- `consumo_escaner`: Páginas escáner en febrero
- `consumo_fax`: Páginas fax en febrero

## 📝 RECOMENDACIÓN

Para febrero 2026 (primer mes):
- **Snapshots**: Usar valores de archivos FEBRERO ✅
- **Consumos**: Como no hay mes anterior, consumo = snapshot ✅

Para meses siguientes:
- **Snapshots**: Usar valores de archivos del mes actual
- **Consumos**: Calcular diferencia (snapshot_actual - snapshot_anterior)
