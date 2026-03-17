# Mapeo Final Completo CSV → Base de Datos

**Fecha**: 16 de marzo de 2026  
**Estado**: Validado con datos reales ✅

---

## 📊 Formato W533L900719 (Simple)

### Campos Disponibles en CSV:
1. Nº de registro
2. Código de usuario
3. Nombre de usuario
4. **Total páginas impresión** ✅
5. Total páginas impresión (Anterior)
6. Uso Color (%)
7. Uso Color (Anterior) (%)
8. Uso 2 caras (%)
9. Uso 2 caras (Anterior) (%)
10. Uso Combinar (%)
11. Uso Combinar (Anterior) (%)
12. Reducción papel (%)
13. Reducción papel (Anterior) (%)
14-17. Periodos contador (fechas)

### Mapeo a `cierres_mensuales_usuarios`:

| Campo BD | Fuente CSV | Valor |
|----------|------------|-------|
| `codigo_usuario` | Código de usuario | ✅ |
| `nombre_usuario` | Nombre de usuario | ✅ |
| `total_paginas` | Total páginas impresión | ✅ |
| `total_bn` | - | **0** (no disponible) |
| `total_color` | - | **0** (no disponible) |
| `copiadora_bn` | - | **0** (no disponible) |
| `copiadora_color` | - | **0** (no disponible) |
| `impresora_bn` | - | **0** (no disponible) |
| `impresora_color` | - | **0** (no disponible) |
| `escaner_bn` | - | **0** (no disponible) |
| `escaner_color` | - | **0** (no disponible) |
| `fax_bn` | - | **0** (no disponible) |
| `consumo_total` | CSV Comparativo | ✅ Buscar por código |
| `consumo_copiadora` | - | **0** (no disponible) |
| `consumo_impresora` | - | **0** (no disponible) |
| `consumo_escaner` | - | **0** (no disponible) |
| `consumo_fax` | - | **0** (no disponible) |

### Campos Adicionales (NO en BD):
- Uso Color (%)
- Uso 2 caras (%)
- Uso Combinar (%)
- Reducción papel (%)

---

## 📊 Formato G986XA16285 / E174MA11130 (Detallado)

### Campos Disponibles en CSV (56 columnas):

#### Totales:
1. Usuario
2. Nombre
3. **Total impresiones** ✅
4. **ByN(Total impresiones)** ✅
5. **Color (Total impresiones)** ✅
6. ByN:Resultado(Total impresiones)
7. Color :Resultado(Total impresiones)

#### Copiadora/Document Server:
8. **Blanco y NegroTotal(Copiadora/Document Server)** ✅
9. Blanco y Negro(Tamaño pequeño)(Copiadora/Document Server)
10. Blanco y Negro(Tamaño grande)(Copiadora/Document Server)
11. Color personalizadoTotal(Copiadora/Document Server)
12. Color personalizado(Tamaño pequeño)(Copiadora/Document Server)
13. Color personalizado(Tamaño grande)(Copiadora/Document Server)
14. Dos coloresTotal(Copiadora/Document Server)
15. Dos colores(Tamaño pequeño)(Copiadora/Document Server)
16. Dos colores(Tamaño grande)(Copiadora/Document Server)
17. **A todo colorTotal(Copiadora/Document Server)** ✅
18. A todo color(Tamaño pequeño)(Copiadora/Document Server)
19. A todo color(Tamaño grande)(Copiadora/Document Server)

#### Impresora:
20. **Blanco y NegroTotal(Impresora)** ✅
21. Blanco y Negro(Tamaño pequeño)(Impresora)
22. Blanco y Negro(Tamaño grande)(Impresora)
23. Color personalizadoTotal(Impresora)
24. Color personalizado(Tamaño pequeño)(Impresora)
25. Color personalizado(Tamaño grande)(Impresora)
26. Dos coloresTotal(Impresora)
27. Dos colores(Tamaño pequeño)(Impresora)
28. Dos colores(Tamaño grande)(Impresora)
29. **Color Total(Impresora)** ✅
30. Color (Tamaño pequeño)(Impresora)
31. Color (Tamaño grande)(Impresora)

#### Escáner:
32. EscánerTotal(Escáner)
33. **Blanco y NegroTotal(Escáner)** ✅
34. Blanco y Negro(Tamaño pequeño)(Escáner)
35. Blanco y Negro(Tamaño grande)(Escáner)
36. **A todo colorTotal(Escáner)** ✅
37. A todo color(Tamaño pequeño)(Escáner)
38. A todo color(Tamaño grande)(Escáner)

#### Fax:
39. **Blanco y NegroTotal(Fax)** ✅
40. Blanco y Negro(Tamaño pequeño)(Fax)
41. Blanco y Negro(Tamaño grande)(Fax)
42. Color Total(Fax)
43. Color (Tamaño pequeño)(Fax)
44. Color (Tamaño grande)(Fax)
45. Páginas transmitidas(Fax)
46. Cargo por transmisión(Fax)

#### Otros:
47-50. Limitación uso volumen impresión
51. Negro(Revelado)
52. Color (YMC)(Revelado)
53. **Hojas a 2 caras(Copiadora/Document Server)** (adicional)
54. **Páginas combinadas(Copiadora/Document Server)** (adicional)
55. **Hojas a 2 caras(Impresora)** (adicional)
56. **Páginas combinadas(Impresora)** (adicional)

### Mapeo a `cierres_mensuales_usuarios`:

| Campo BD | Fuente CSV | Notas |
|----------|------------|-------|
| `codigo_usuario` | Usuario | Sin corchetes [] |
| `nombre_usuario` | Nombre | Sin corchetes [] |
| `total_paginas` | Total impresiones | ✅ |
| `total_bn` | ByN(Total impresiones) | ✅ |
| `total_color` | Color (Total impresiones) | ✅ Puede ser 0 o "-" |
| `copiadora_bn` | Blanco y NegroTotal(Copiadora/Document Server) | ✅ |
| `copiadora_color` | A todo colorTotal(Copiadora/Document Server) | ✅ |
| `impresora_bn` | Blanco y NegroTotal(Impresora) | ✅ |
| `impresora_color` | Color Total(Impresora) | ✅ |
| `escaner_bn` | Blanco y NegroTotal(Escáner) | ✅ |
| `escaner_color` | A todo colorTotal(Escáner) | ✅ |
| `fax_bn` | Blanco y NegroTotal(Fax) | ✅ |
| `consumo_total` | CSV Comparativo | ✅ Buscar por código |
| `consumo_copiadora` | copiadora_bn + copiadora_color | Calculado |
| `consumo_impresora` | impresora_bn + impresora_color | Calculado |
| `consumo_escaner` | escaner_bn + escaner_color | Calculado |
| `consumo_fax` | fax_bn | Calculado |

### Campos Adicionales (NO en BD):
- Hojas a 2 caras (Copiadora/Impresora)
- Páginas combinadas (Copiadora/Impresora)
- Negro(Revelado)
- Color (YMC)(Revelado)
- Tamaños pequeño/grande por función

---

## 🗂️ Mapeo para `cierres_mensuales`

### Campos Principales:

| Campo BD | Fuente | Cálculo |
|----------|--------|---------|
| `printer_id` | BD | ID de la impresora |
| `mes` | Fijo | 2 (febrero) |
| `anio` | Fijo | 2026 |
| `total_paginas` | **CSV Comparativo** | Contador REAL (ej: 1,010,592) |
| `diferencia_total` | **CSV Comparativo** | feb - ene (ej: 22,005) |

### Campos Calculados (suma de usuarios):

#### Para W533L900719:
```python
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

#### Para G986/E174:
```python
total_bn = SUM(usuarios.ByN(Total impresiones))
total_color = SUM(usuarios.Color(Total impresiones))
copiadora_bn = SUM(usuarios.Blanco y NegroTotal(Copiadora))
copiadora_color = SUM(usuarios.A todo colorTotal(Copiadora))
impresora_bn = SUM(usuarios.Blanco y NegroTotal(Impresora))
impresora_color = SUM(usuarios.Color Total(Impresora))
escaner_bn = SUM(usuarios.Blanco y NegroTotal(Escáner))
escaner_color = SUM(usuarios.A todo colorTotal(Escáner))
fax_bn = SUM(usuarios.Blanco y NegroTotal(Fax))
```

---

## 🔍 Obtención del Consumo por Usuario

### CSV Comparativo - Estructura:
```csv
codigo,nombre,CONSUMO_MES,col4,col5,ENERO_TOTAL,FEBRERO_TOTAL
3581.0,SONIA CORTES,4401,,,988587.0,1010592.0
```

### Lógica de Búsqueda:
```python
def obtener_consumo_usuario(codigo_usuario, csv_comparativo):
    """
    Busca el consumo mensual del usuario en el CSV comparativo
    
    Returns:
        int: Consumo del mes, 0 si no se encuentra
    """
    for row in csv_comparativo:
        codigo_csv = str(row[0]).replace('.0', '').strip()
        if codigo_csv == codigo_usuario:
            return int(row[2])  # Columna 3 = consumo
    return 0  # Usuario sin consumo en el mes
```

---

## ⚠️ Casos Especiales

### 1. Valores "-" en CSV
- Algunos campos tienen "-" en lugar de 0
- Convertir "-" a 0 al importar

### 2. Usuario SYSTEM
- Código: "-" o "SYSTEM"
- **NO importar** a `cierres_mensuales_usuarios`
- Su contador ya está en el total de la impresora

### 3. Códigos con corchetes
- Formato G986/E174: `[2902]`
- Limpiar corchetes al importar: `2902`

### 4. Códigos con .0
- CSV comparativo: `3581.0`
- Limpiar `.0` al comparar: `3581`

### 5. Usuarios sin consumo
- Aparecen en CSV usuarios con total > 0
- NO aparecen en CSV comparativo
- `consumo_total` = 0

---

## ✅ Validaciones

### Antes de importar:
- [ ] CSV comparativo existe y tiene contador real
- [ ] CSV usuarios existe y tiene usuarios
- [ ] Contador real > 100,000
- [ ] Suma usuarios < contador real
- [ ] Diferencia entre 20% y 80%

### Durante importación:
- [ ] Skip usuario SYSTEM (código "-")
- [ ] Skip usuarios con código vacío
- [ ] Limpiar corchetes [] de códigos
- [ ] Convertir "-" a 0
- [ ] Validar números no negativos

### Después de importar:
- [ ] `total_paginas` = contador real
- [ ] Cantidad usuarios coincide con CSV
- [ ] Suma consumos <= diferencia_total
- [ ] No hay usuarios duplicados
- [ ] Desgloses suman correctamente

---

## 📝 Ejemplo Real: Usuario MANTENIMIENTO (G986)

### CSV Usuarios:
```csv
[2902],[MANTENIMIENTO],6066,6066,-,6066,-,2024,2024,-,...,4042,4042,-,...,3975,3975,...,9,9,...
```

### CSV Comparativo:
```csv
2902.0,MANTENIMIENTO,<consumo_mes>,...
```

### Importación:
```python
{
    'codigo_usuario': '2902',  # Sin corchetes
    'nombre_usuario': 'MANTENIMIENTO',
    'total_paginas': 6066,
    'total_bn': 6066,
    'total_color': 0,  # "-" → 0
    'copiadora_bn': 2024,
    'copiadora_color': 0,
    'impresora_bn': 4042,
    'impresora_color': 0,
    'escaner_bn': 3975,
    'escaner_color': 9,
    'fax_bn': 0,
    'consumo_total': <buscar_en_comparativo>,
    'consumo_copiadora': 2024,  # 2024 + 0
    'consumo_impresora': 4042,  # 4042 + 0
    'consumo_escaner': 3984,    # 3975 + 9
    'consumo_fax': 0
}
```

---

**Generado por**: `backend/mapeo_detallado_campos.py`
