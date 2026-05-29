# Mapeo de Campos CSV → Base de Datos

**Fecha**: 16 de marzo de 2026  
**Análisis**: Estructura completa de CSV validada

---

## 📊 Resumen de Formatos Disponibles

### Formato W533L900719 (Simple - 17 columnas)
- ✅ Total páginas impresión
- ❌ NO tiene desglose por función (copiadora/impresora/escáner)
- ❌ NO tiene B/N vs Color separado
- ✅ Tiene porcentajes de uso (2 caras, combinar, etc.)

### Formato G986XA16285 y E174MA11130 (Detallado - 52-56 columnas)
- ✅ Total impresiones
- ✅ Desglose B/N vs Color
- ✅ Desglose por función: Copiadora, Impresora, Escáner, Fax
- ✅ Desglose por tamaño (pequeño/grande)
- ✅ Hojas a 2 caras y páginas combinadas

---

## 🗂️ Mapeo para `cierres_mensuales`

### Campos Obligatorios

| Campo BD | Fuente | Valor |
|----------|--------|-------|
| `printer_id` | BD | ID de la impresora |
| `mes` | Fijo | 2 (febrero) |
| `anio` | Fijo | 2026 |
| `total_paginas` | **CSV Comparativo** | Contador REAL (ej: 1,010,592) |
| `diferencia_total` | **CSV Comparativo** | feb - ene (ej: 22,005) |

### Campos Calculados (desde usuarios)

#### Para Formato W533L900719:
```python
# Solo tenemos total, no hay desglose
total_bn = 0  # No disponible
total_color = 0  # No disponible
copiadora_bn = 0  # No disponible
copiadora_color = 0  # No disponible
impresora_bn = 0  # No disponible
impresora_color = 0  # No disponible
escaner_bn = 0  # No disponible
escaner_color = 0  # No disponible
fax_bn = 0  # No disponible
```

#### Para Formato G986/E174:
```python
# Sumar de todos los usuarios
total_bn = SUM(usuarios.ByN(Total impresiones))
total_color = SUM(usuarios.Color(Total impresiones))

copiadora_bn = SUM(usuarios.Blanco y negroTotal(Copiadora/Document Server))
copiadora_color = SUM(usuarios.A Todo ColorTotal(Copiadora/Document Server))

impresora_bn = SUM(usuarios.Blanco y negroTotal(Impresora))
impresora_color = SUM(usuarios.ColorTotal(Impresora))

escaner_bn = SUM(usuarios.Blanco y negroTotal(Escáner))
escaner_color = SUM(usuarios.A Todo ColorTotal(Escáner))

fax_bn = SUM(usuarios.Blanco y negroTotal(Fax))
```

---

## 👥 Mapeo para `cierres_mensuales_usuarios`

### Formato W533L900719

| Campo BD | Campo CSV | Notas |
|----------|-----------|-------|
| `codigo_usuario` | Código de usuario | |
| `nombre_usuario` | Nombre de usuario | |
| `total_paginas` | Total páginas impresión | |
| `total_bn` | 0 | No disponible |
| `total_color` | 0 | No disponible |
| `copiadora_bn` | 0 | No disponible |
| `copiadora_color` | 0 | No disponible |
| `impresora_bn` | 0 | No disponible |
| `impresora_color` | 0 | No disponible |
| `escaner_bn` | 0 | No disponible |
| `escaner_color` | 0 | No disponible |
| `fax_bn` | 0 | No disponible |
| `consumo_total` | **CSV Comparativo** | Buscar usuario en comparativo |
| `consumo_copiadora` | 0 | No disponible |
| `consumo_impresora` | 0 | No disponible |
| `consumo_escaner` | 0 | No disponible |
| `consumo_fax` | 0 | No disponible |

### Formato G986XA16285 / E174MA11130

| Campo BD | Campo CSV | Notas |
|----------|-----------|-------|
| `codigo_usuario` | Usuario | Sin corchetes |
| `nombre_usuario` | Nombre | Sin corchetes |
| `total_paginas` | Total impresiones | |
| `total_bn` | ByN(Total impresiones) | |
| `total_color` | Color(Total impresiones) | Puede ser 0 |
| `copiadora_bn` | Blanco y negroTotal(Copiadora/Document Server) | |
| `copiadora_color` | A Todo ColorTotal(Copiadora/Document Server) | |
| `impresora_bn` | Blanco y negroTotal(Impresora) | |
| `impresora_color` | ColorTotal(Impresora) | |
| `escaner_bn` | Blanco y negroTotal(Escáner) | |
| `escaner_color` | A Todo ColorTotal(Escáner) | |
| `fax_bn` | Blanco y negroTotal(Fax) | |
| `consumo_total` | **CSV Comparativo** | Buscar usuario en comparativo |
| `consumo_copiadora` | copiadora_bn + copiadora_color | Calculado |
| `consumo_impresora` | impresora_bn + impresora_color | Calculado |
| `consumo_escaner` | escaner_bn + escaner_color | Calculado |
| `consumo_fax` | fax_bn | Calculado |

---

## 🔍 Obtención del Consumo por Usuario

El consumo mensual de cada usuario se obtiene del **CSV Comparativo**:

### Estructura del CSV Comparativo:
```csv
codigo,nombre,CONSUMO_MES,,,ENERO_TOTAL,FEBRERO_TOTAL
3581.0,SONIA CORTES,4401,,,988587.0,1010592.0
```

### Lógica:
1. Leer CSV comparativo
2. Para cada usuario en CSV de usuarios:
   - Buscar su código en el comparativo
   - Si existe: `consumo_total` = valor de columna 3
   - Si no existe: `consumo_total` = 0 (usuario sin consumo en el mes)

---

## ⚠️ Casos Especiales

### 1. W533L900719 (Sin desglose)
- Solo importar `total_paginas` y `consumo_total`
- Todos los desgloses en 0
- El frontend debe mostrar solo el total

### 2. Usuarios sin consumo
- Aparecen en CSV de usuarios con total > 0
- NO aparecen en CSV comparativo
- `consumo_total` = 0 (acumulado, no consumo del mes)

### 3. Usuario SYSTEM
- Código: "-" o "SYSTEM"
- NO importar a `cierres_mensuales_usuarios`
- Su contador ya está en el total de la impresora

### 4. Usuarios duplicados
- Algunos usuarios pueden aparecer con códigos diferentes
- Validar por nombre si es necesario

---

## 📋 Validaciones Requeridas

### Antes de importar:
- [ ] CSV comparativo existe
- [ ] CSV usuarios existe
- [ ] Contador real > 100,000 (es válido)
- [ ] Suma usuarios < contador real
- [ ] Diferencia entre 20% y 80%

### Durante importación:
- [ ] Skip usuario SYSTEM
- [ ] Skip usuarios con código vacío
- [ ] Validar números no negativos
- [ ] Consumo <= total_paginas

### Después de importar:
- [ ] `total_paginas` = contador real (no suma usuarios)
- [ ] Cantidad usuarios coincide con CSV
- [ ] Suma de consumos <= diferencia_total
- [ ] No hay usuarios duplicados

---

## 🎯 Ejemplo Completo: W533L900719 Febrero

### CSV Comparativo:
```
Enero: 988,587
Febrero: 1,010,592
Consumo: 22,005
```

### CSV Usuarios (extracto):
```
3581,SONIA CORTES,48887
0931,SOFIA CRISTANCHO,37028
```

### Importación:

**`cierres_mensuales`**:
```python
{
    'printer_id': 5,
    'mes': 2,
    'anio': 2026,
    'total_paginas': 1010592,  # Del comparativo
    'diferencia_total': 22005,  # Del comparativo
    'total_bn': 0,  # No disponible
    'total_color': 0,  # No disponible
    # ... otros en 0
}
```

**`cierres_mensuales_usuarios`** (SONIA CORTES):
```python
{
    'cierre_mensual_id': <id_cierre>,
    'codigo_usuario': '3581',
    'nombre_usuario': 'SONIA CORTES',
    'total_paginas': 48887,  # Del CSV usuarios
    'total_bn': 0,  # No disponible
    'total_color': 0,  # No disponible
    'consumo_total': 4401,  # Del CSV comparativo
    # ... otros en 0
}
```

---

## 🎯 Ejemplo Completo: E174MA11130 Febrero

### CSV Comparativo:
```
Enero: 346,211
Febrero: 364,942
Consumo: 18,731
```

### CSV Usuarios (extracto):
```
[1010],[LINA JIMENEZ],6,6.0,0.0,6.0,0.0,6.0,6.0,0.0,...
```

### Importación:

**`cierres_mensuales`**:
```python
{
    'printer_id': 3,
    'mes': 2,
    'anio': 2026,
    'total_paginas': 364942,  # Del comparativo
    'diferencia_total': 18731,  # Del comparativo
    'total_bn': 158212,  # Suma usuarios ByN
    'total_color': 0,  # Suma usuarios Color
    'copiadora_bn': 91_usuarios_suma,
    'impresora_bn': 113_usuarios_suma,
    'escaner_bn': 76_usuarios_suma,
    # ...
}
```

**`cierres_mensuales_usuarios`** (LINA JIMENEZ):
```python
{
    'cierre_mensual_id': <id_cierre>,
    'codigo_usuario': '1010',
    'nombre_usuario': 'LINA JIMENEZ',
    'total_paginas': 6,
    'total_bn': 6,
    'total_color': 0,
    'copiadora_bn': 6,
    'copiadora_color': 0,
    'impresora_bn': 0,
    'impresora_color': 0,
    'escaner_bn': 0,
    'escaner_color': 0,
    'fax_bn': 0,
    'consumo_total': <buscar_en_comparativo>,
    'consumo_copiadora': 6,
    'consumo_impresora': 0,
    'consumo_escaner': 0,
    'consumo_fax': 0
}
```

---

**Generado por**: `backend/analizar_estructura_completa_csv.py`
