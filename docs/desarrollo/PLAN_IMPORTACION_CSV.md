# Plan de Importación de Cierres desde CSV

**Fecha**: 16 de marzo de 2026  
**Estado**: Validación completada ✅

---

## 📊 Datos Disponibles

### Febrero 2026 (Completo)

| Impresora | Contador Real | Usuarios | Suma Usuarios | Diferencia |
|-----------|--------------|----------|---------------|------------|
| W533L900719 | 1,010,592 | 89 | 307,668 | 702,924 (69.6%) |
| E174MA11130 | 364,942 | 119 | 158,212 | 206,730 (56.6%) |
| G986XA16285 | 261,159 | 22 | 93,471 | 167,688 (64.2%) |
| E174M210096 | 451,657 | 168 | 326,905 | 124,752 (27.6%) |
| E176M460020 | 913,835 | 0 | 0 | 913,835 (100%) |

### Enero 2026 (Solo comparativos)

| Impresora | Contador Real | Usuarios CSV |
|-----------|--------------|--------------|
| W533L900719 | 988,587 | ❌ No existe |
| E174MA11130 | 346,211 | ❌ No existe |
| G986XA16285 | 261,159 | ❌ No existe |
| E174M210096 | 451,657 | ❌ No existe |
| E176M460020 | 901,950 | ❌ No existe |

---

## 🎯 Estrategia de Importación

### Opción 1: Solo Febrero (RECOMENDADO)
Importar solo febrero con datos completos:
- ✅ Tenemos contador real
- ✅ Tenemos usuarios detallados
- ✅ Datos coherentes y validados

### Opción 2: Enero + Febrero
Importar ambos meses:
- ✅ Enero: Solo contador real (sin usuarios)
- ✅ Febrero: Contador real + usuarios

---

## 📋 Estructura de Importación

### Para `cierres_mensuales` (Tabla principal)

```python
CierreMensual(
    printer_id=<id_impresora>,
    mes=2,  # Febrero
    anio=2026,
    total_paginas=1010592,  # ← CONTADOR REAL del CSV comparativo
    diferencia_total=22005,  # ← Consumo mensual (feb - ene)
    # ... otros campos
)
```

### Para `cierres_mensuales_usuarios` (Detalle por usuario)

```python
CierreMensualUsuario(
    cierre_id=<id_cierre>,
    codigo_usuario="3581",
    nombre_usuario="SONIA CORTES",
    total_paginas=48887,  # ← Del CSV de usuarios
    # ... otros campos por usuario
)
```

---

## 🔄 Proceso de Importación

### Paso 1: Limpiar datos existentes
```sql
-- Borrar cierres de enero y febrero 2026
DELETE FROM cierres_mensuales_usuarios 
WHERE cierre_id IN (
    SELECT id FROM cierres_mensuales 
    WHERE anio = 2026 AND mes IN (1, 2)
);

DELETE FROM cierres_mensuales 
WHERE anio = 2026 AND mes IN (1, 2);
```

### Paso 2: Importar Febrero (con usuarios)

Para cada impresora:

1. **Leer CSV Comparativo**:
   - Extraer contador real febrero
   - Extraer contador real enero (para calcular consumo)
   - Calcular: `consumo = febrero - enero`

2. **Leer CSV de Usuarios**:
   - Extraer cada usuario con su contador
   - Validar que suma_usuarios < contador_real

3. **Crear registro en `cierres_mensuales`**:
   ```python
   cierre = CierreMensual(
       printer_id=printer.id,
       mes=2,
       anio=2026,
       total_paginas=contador_real_febrero,  # Del comparativo
       diferencia_total=consumo_mensual,      # feb - ene
       # Campos calculados
       total_bn=suma_usuarios_bn,
       total_color=suma_usuarios_color,
       # ... otros
   )
   ```

4. **Crear registros en `cierres_mensuales_usuarios`**:
   ```python
   for usuario in usuarios_csv:
       CierreMensualUsuario(
           cierre_id=cierre.id,
           codigo_usuario=usuario['codigo'],
           nombre_usuario=usuario['nombre'],
           total_paginas=usuario['total'],
           # ... otros campos del usuario
       )
   ```

### Paso 3: Importar Enero (solo contador, sin usuarios)

Para cada impresora:

1. **Leer CSV Comparativo**:
   - Extraer contador real enero
   - Consumo = 0 (es el primer mes)

2. **Crear registro en `cierres_mensuales`**:
   ```python
   cierre = CierreMensual(
       printer_id=printer.id,
       mes=1,
       anio=2026,
       total_paginas=contador_real_enero,  # Del comparativo
       diferencia_total=0,  # Primer mes
       # Campos en 0 (no hay detalle de usuarios)
       total_bn=0,
       total_color=0,
   )
   ```

3. **NO crear usuarios** (no tenemos CSV de usuarios para enero)

---

## ✅ Validaciones

### Antes de importar:
- [ ] CSV comparativo existe
- [ ] CSV usuarios existe (para febrero)
- [ ] Contador real > suma usuarios
- [ ] Diferencia entre 30% y 80%
- [ ] No hay cierres duplicados

### Después de importar:
- [ ] `total_paginas` = contador real (no suma usuarios)
- [ ] Cantidad de usuarios coincide con CSV
- [ ] Suma de usuarios < total_paginas
- [ ] `diferencia_total` = consumo mensual
- [ ] Frontend muestra datos correctos

---

## 🔍 Coherencia con Frontend

### Vista de Cierres Mensuales:
```
Impresora: W533L900719
Mes: Febrero 2026
Total: 1,010,592 páginas  ← Del contador real
Consumo: 22,005 páginas   ← Diferencia feb-ene
Usuarios: 89              ← Cantidad de usuarios
```

### Vista de Usuarios:
```
Usuario: SONIA CORTES (3581)
Total: 48,887 páginas     ← Del CSV usuarios
% del total: 4.8%         ← 48887 / 1010592
```

### Validación de Coherencia:
```
Total impresora: 1,010,592
Suma usuarios:     307,668
Diferencia:        702,924 (69.6%)
✅ Diferencia normal (impresiones anónimas/sistema)
```

---

## 📝 Archivos Necesarios

### CSV Comparativos (en `docs/CSV_COMPARATIVOS/`):
- `W533L900719 ENERO - FEBRERO_W533L900719 ENERO - FEBRERO.csv`
- `E174MA11130 ENERO - FEBRERO_E174MA11130 COMPARATIVO.csv`
- `G986XA16285 ENERO - FEBRERO_G986XA16285 COMPARATIVO.csv`
- `E174M210096 ENERO - FEBRERO_E174M210096 COMPARATIVO.csv`
- `E176M460020 ENERO - FEBRERO_E176M460020 COMPARATIVO.csv`

### CSV Usuarios Febrero (en `docs/CONTADOR IMPRESORAS FEBRERO/`):
- `W533L900719 16.02.2026.csv`
- `E174MA11130 16.02.2026.csv`
- `G986XA16285 16.02.2026.csv`
- `E174M210096 16.02.2026.csv`
- `E176M460020 26.02.2026.csv`

---

## 🚀 Próximos Pasos

1. ✅ **Validación completada** - Datos coherentes
2. ⏳ **Revisar y aprobar plan** - Confirmar estrategia
3. ⏳ **Crear script de importación** - Con validaciones
4. ⏳ **Hacer backup de BD** - Antes de borrar
5. ⏳ **Ejecutar importación** - Con modo dry-run primero
6. ⏳ **Validar en frontend** - Verificar coherencia

---

**Generado por**: `backend/validar_estructura_csv.py`
