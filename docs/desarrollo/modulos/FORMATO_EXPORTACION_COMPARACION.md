# 📊 FORMATO DE EXPORTACIÓN - COMPARACIÓN DE CIERRES

## 🎯 OBJETIVO

Definir el formato exacto para exportar comparaciones de cierres mensuales a Excel, replicando el formato de los archivos originales de Ricoh.

---

## 📋 ESTRUCTURA DEL ARCHIVO EXCEL

### Nombre del Archivo

**Formato**: `{SERIAL_NUMBER} {MES1} - {MES2}.xlsx`

**Ejemplos**:
- `E174M210096 ENERO - FEBRERO.xlsx`
- `E174MA11130 DICIEMBRE - ENERO.xlsx`

### Hojas del Archivo

El archivo debe contener 3 hojas:

1. **{SERIAL} {MES1}** - Datos del primer período
2. **{SERIAL} {MES2}** - Datos del segundo período  
3. **{SERIAL} COMPARATIVO** - Comparación entre períodos

**Ejemplo para E174M210096 ENERO-FEBRERO**:
- `E174M210096 ENERO`
- `E174M210096 FEBRERO`
- `E174M210096 COMPARATIVO`

---

## 📊 FORMATO DE HOJA DE PERÍODO (ENERO, FEBRERO, etc.)

### Estructura General

- **Filas**: Una fila por usuario + fila final de totales
- **Columnas**: 52 columnas con todos los detalles
- **Última fila**: Totales de la impresora (Usuario=vacío, Nombre=vacío, Total=suma)

### Columnas (en orden exacto)

#### Columnas Principales (1-7)

| # | Nombre | Descripción | Ejemplo |
|---|--------|-------------|---------|
| 1 | Usuario | Código del usuario con corchetes | `[0116]` |
| 2 | Nombre | Nombre del usuario con corchetes | `[JULIAN DE LA OS]` |
| 3 | Total impresiones | Total acumulado de páginas | `204` |
| 4 | ByN(Total impresiones) | Total B/N | `88` |
| 5 | Color(Total impresiones) | Total Color | `116` |
| 6 | ByN:Resultado(Total impresiones) | Resultado B/N | `88` |
| 7 | Color:Resultado(Total impresiones) | Resultado Color | `116` |

#### Copiadora/Document Server (8-19)

| # | Nombre | Descripción |
|---|--------|-------------|
| 8 | Blanco y negroTotal(Copiadora/Document Server) | Total B/N copiadora |
| 9 | Blanco y negro(Tamaño pequeño)(Copiadora/Document Server) | B/N pequeño |
| 10 | Blanco y negro(Tamaño grande)(Copiadora/Document Server) | B/N grande |
| 11 | Mono ColorTotal(Copiadora/Document Server) | Total mono color |
| 12 | Mono Color(Tamaño pequeño)(Copiadora/Document Server) | Mono pequeño |
| 13 | Mono Color(Tamaño grande)(Copiadora/Document Server) | Mono grande |
| 14 | Dos coloresTotal(Copiadora/Document Server) | Total dos colores |
| 15 | Dos colores(Tamaño pequeño)(Copiadora/Document Server) | Dos colores pequeño |
| 16 | Dos colores(Tamaño grande)(Copiadora/Document Server) | Dos colores grande |
| 17 | A Todo ColorTotal(Copiadora/Document Server) | Total a todo color |
| 18 | A Todo Color(Tamaño pequeño)(Copiadora/Document Server) | Color pequeño |
| 19 | A Todo Color(Tamaño grande)(Copiadora/Document Server) | Color grande |

#### Impresora (20-31)

| # | Nombre | Descripción |
|---|--------|-------------|
| 20 | Blanco y negroTotal(Impresora) | Total B/N impresora |
| 21 | Blanco y negro(Tamaño pequeño)(Impresora) | B/N pequeño |
| 22 | Blanco y negro(Tamaño grande)(Impresora) | B/N grande |
| 23 | Mono ColorTotal(Impresora) | Total mono color |
| 24 | Mono Color(Tamaño pequeño)(Impresora) | Mono pequeño |
| 25 | Mono Color(Tamaño grande)(Impresora) | Mono grande |
| 26 | Dos coloresTotal(Impresora) | Total dos colores |
| 27 | Dos colores(Tamaño pequeño)(Impresora) | Dos colores pequeño |
| 28 | Dos colores(Tamaño grande)(Impresora) | Dos colores grande |
| 29 | ColorTotal(Impresora) | Total color |
| 30 | Color(Tamaño pequeño)(Impresora) | Color pequeño |
| 31 | Color(Tamaño grande)(Impresora) | Color grande |

#### Escáner (32-38)

| # | Nombre | Descripción |
|---|--------|-------------|
| 32 | EscánerTotal(Escáner) | Total escáner |
| 33 | Blanco y negroTotal(Escáner) | Total B/N escáner |
| 34 | Blanco y negro(Tamaño pequeño)(Escáner) | B/N pequeño |
| 35 | Blanco y negro(Tamaño grande)(Escáner) | B/N grande |
| 36 | A Todo ColorTotal(Escáner) | Total color escáner |
| 37 | A Todo Color(Tamaño pequeño)(Escáner) | Color pequeño |
| 38 | A Todo Color(Tamaño grande)(Escáner) | Color grande |

#### Fax (39-46)

| # | Nombre | Descripción |
|---|--------|-------------|
| 39 | Blanco y negroTotal(Fax) | Total B/N fax |
| 40 | Blanco y negro(Tamaño pequeño)(Fax) | B/N pequeño |
| 41 | Blanco y negro(Tamaño grande)(Fax) | B/N grande |
| 42 | ColorTotal(Fax) | Total color fax |
| 43 | Color(Tamaño pequeño)(Fax) | Color pequeño |
| 44 | Color(Tamaño grande)(Fax) | Color grande |
| 45 | Páginas transmitidas(Fax) | Páginas transmitidas |
| 46 | Cargo por transmisión(Fax) | Cargo |

#### Otros (47-52)

| # | Nombre | Descripción |
|---|--------|-------------|
| 47 | Volumen usado(Limitación uso volumen impresión) | Volumen usado |
| 48 | Valor límite(Limitación uso volumen impresión) | Límite |
| 49 | Volumen usado anterior(Limitación uso volumen impresión) | Anterior |
| 50 | Última fecha reinicio(Limitación uso volumen impresión) | Fecha reinicio |
| 51 | Negro(Revelado) | Revelado negro |
| 52 | Color (YMC)(Revelado) | Revelado color |

### Formato de Valores

#### Códigos y Nombres
- **Con corchetes**: `[0116]`, `[JULIAN DE LA OS]`
- **Sin espacios extra**: Trim antes de agregar corchetes

#### Números
- **Sin formato**: `204` (no `204.0`)
- **Sin separadores de miles**: `1840` (no `1,840`)
- **Cero para valores vacíos**: `0` (no vacío o `-`)

#### Última Fila (Totales)
- **Usuario**: Vacío (NaN)
- **Nombre**: Vacío (NaN)
- **Total impresiones**: Suma de todos los usuarios
- **Resto de columnas**: Suma correspondiente

---

## 📊 FORMATO DE HOJA COMPARATIVO

### Estructura

Comparación lado a lado de dos períodos con cálculo de diferencias.

### Columnas

| # | Nombre | Descripción | Ejemplo |
|---|--------|-------------|---------|
| 1 | Usuario | Código con corchetes | `[0116]` |
| 2 | Nombre | Nombre con corchetes | `[JULIAN DE LA OS]` |
| 3 | B/N | Total B/N período 1 | `88` |
| 4 | COLOR | Total Color período 1 | `116` |
| 5 | TOTAL IMPRESIONES | Total período 1 | `204` |
| 6 | (vacía) | Separador visual | |
| 7 | B/N | Total B/N período 2 | `95` |
| 8 | COLOR | Total Color período 2 | `120` |
| 9 | TOTAL IMPRESIONES | Total período 2 | `215` |

**Nota**: Las columnas 6-9 pueden tener encabezados con el nombre del mes

### Cálculo de Diferencias

Opcionalmente se pueden agregar columnas de diferencia:
- **Diferencia B/N**: Período 2 - Período 1
- **Diferencia Color**: Período 2 - Período 1
- **Diferencia Total**: Período 2 - Período 1

---

## 🎨 FORMATO VISUAL (OPCIONAL)

### Encabezados
- **Fondo**: Gris claro o azul claro
- **Texto**: Negrita
- **Alineación**: Centrado

### Datos
- **Números**: Alineados a la derecha
- **Texto**: Alineado a la izquierda
- **Última fila (totales)**: Negrita

### Ancho de Columnas
- **Usuario**: 10 caracteres
- **Nombre**: 30 caracteres
- **Números**: 15 caracteres
- **Resto**: Auto-ajustar

---

## 💻 IMPLEMENTACIÓN EN BACKEND

### Endpoint Propuesto

```
GET /api/cierres/comparar/export
```

**Parámetros**:
- `serial_number`: Serial de la impresora
- `periodo1`: Año-Mes del primer período (ej: `2026-01`)
- `periodo2`: Año-Mes del segundo período (ej: `2026-02`)
- `formato`: `excel` (default)

**Respuesta**:
- Archivo Excel con el formato especificado
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Filename: `{SERIAL} {MES1} - {MES2}.xlsx`

### Librerías Recomendadas

**Python**:
- `openpyxl` - Para crear archivos Excel con formato
- `pandas` - Para manipular datos
- `xlsxwriter` - Alternativa con más opciones de formato

**Ejemplo básico**:
```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

def exportar_comparacion(serial_number, periodo1, periodo2):
    # Crear workbook
    wb = Workbook()
    
    # Crear hojas
    ws1 = wb.active
    ws1.title = f"{serial_number} {periodo1}"
    
    ws2 = wb.create_sheet(f"{serial_number} {periodo2}")
    ws3 = wb.create_sheet(f"{serial_number} COMPARATIVO")
    
    # Agregar datos...
    
    return wb
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Datos
- [ ] Obtener usuarios del cierre desde BD
- [ ] Formatear códigos con corchetes `[codigo]`
- [ ] Formatear nombres con corchetes `[nombre]`
- [ ] Calcular totales por columna
- [ ] Agregar fila de totales al final

### Estructura
- [ ] Crear 3 hojas con nombres correctos
- [ ] Agregar 52 columnas en hojas de período
- [ ] Agregar columnas correctas en hoja comparativo
- [ ] Ordenar usuarios alfabéticamente o por código

### Formato
- [ ] Aplicar formato a encabezados (negrita, fondo)
- [ ] Alinear números a la derecha
- [ ] Alinear texto a la izquierda
- [ ] Aplicar negrita a fila de totales
- [ ] Ajustar ancho de columnas

### Validación
- [ ] Verificar que suma de usuarios = total del cierre
- [ ] Verificar que todas las columnas tengan datos
- [ ] Verificar formato de corchetes
- [ ] Probar descarga del archivo

---

## 📝 NOTAS IMPORTANTES

1. **Corchetes obligatorios**: Todos los códigos y nombres deben tener corchetes
2. **Última fila siempre**: Debe existir la fila de totales
3. **52 columnas exactas**: No omitir columnas aunque estén en 0
4. **Orden de columnas**: Debe ser exactamente el especificado
5. **Nombres de hojas**: Deben incluir el serial number

---

## 🔄 COMPATIBILIDAD

Este formato es compatible con:
- ✅ Microsoft Excel 2016+
- ✅ LibreOffice Calc
- ✅ Google Sheets
- ✅ Scripts de importación existentes

---

**Versión**: 1.0  
**Fecha**: 2026  
**Estado**: ✅ Especificación completa
