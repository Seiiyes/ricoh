# Fix: Error en Exportaciones - TypeError con fecha_inicio

**Fecha:** 25 de marzo de 2026  
**Tipo:** Bug - Error de tipo en manejo de fechas  
**Severidad:** Alta  
**Estado:** ✅ Resuelto

---

## Problema

Todas las exportaciones (CSV y Excel) de cierres y comparaciones fallaban con error 500 y CORS.

### Síntomas

```
Access to XMLHttpRequest at 'http://localhost:8000/api/export/comparacion/301/304/excel' 
from origin 'http://localhost:5173' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.

GET http://localhost:8000/api/export/comparacion/301/304/excel 
net::ERR_FAILED 500 (Internal Server Error)
```

**Error en logs del backend:**
```python
File "/app/api/export.py", line 91, in export_cierre
    fecha_str = cierre.fecha_inicio.replace('-', '')
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'str' object cannot be interpreted as an integer
```

---

## Causa Raíz

**Error de tipo al intentar formatear fechas**

El código intentaba usar el método `.replace('-', '')` directamente en objetos `date` de Python, pero este método no existe para objetos de tipo `datetime.date`. 

### Código Incorrecto (ANTES)

```python
# ❌ INCORRECTO - cierre.fecha_inicio es un objeto date, no un string
fecha_str = cierre.fecha_inicio.replace('-', '')
```

**¿Por qué falla?**

1. `cierre.fecha_inicio` es un objeto `datetime.date` de SQLAlchemy
2. Los objetos `date` NO tienen el método `.replace()`
3. El método `.replace()` en objetos `date` se usa para reemplazar componentes de fecha (año, mes, día), no strings
4. Python intenta interpretar `'-'` como un entero para el método `date.replace()` → TypeError

---

## Solución

**Convertir el objeto `date` a string usando `.strftime()` antes de manipularlo**

### Código Correcto (DESPUÉS)

```python
# ✅ CORRECTO - Convertir a string primero con formato YYYYMMDD
fecha_str = cierre.fecha_inicio.strftime('%Y%m%d')
```

**¿Por qué funciona?**

1. `.strftime('%Y%m%d')` convierte el objeto `date` a string con formato `20260325`
2. Ya no necesitamos `.replace()` porque el formato no incluye guiones
3. El resultado es un string limpio para usar en nombres de archivo

---

## Archivos Modificados

### `backend/api/export.py`

**4 correcciones realizadas:**

1. **Línea 91** - Exportación de cierre CSV
   ```python
   # ANTES
   fecha_str = cierre.fecha_inicio.replace('-', '')
   
   # DESPUÉS
   fecha_str = cierre.fecha_inicio.strftime('%Y%m%d')
   ```

2. **Líneas 209-210** - Exportación de comparación CSV
   ```python
   # ANTES
   fecha1_str = cierre1.fecha_inicio.replace('-', '')
   fecha2_str = cierre2.fecha_inicio.replace('-', '')
   
   # DESPUÉS
   fecha1_str = cierre1.fecha_inicio.strftime('%Y%m%d')
   fecha2_str = cierre2.fecha_inicio.strftime('%Y%m%d')
   ```

3. **Línea 311** - Exportación de cierre Excel
   ```python
   # ANTES
   fecha_str = cierre.fecha_inicio.replace('-', '')
   
   # DESPUÉS
   fecha_str = cierre.fecha_inicio.strftime('%Y%m%d')
   ```

4. **Líneas 450-451** - Exportación de comparación Excel
   ```python
   # ANTES
   fecha1_str = cierre1.fecha_inicio.replace('-', '')
   fecha2_str = cierre2.fecha_inicio.replace('-', '')
   
   # DESPUÉS
   fecha1_str = cierre1.fecha_inicio.strftime('%Y%m%d')
   fecha2_str = cierre2.fecha_inicio.strftime('%Y%m%d')
   ```

---

## Verificación

### Antes del Fix
```bash
# Intentar exportar comparación
curl -X GET http://localhost:8000/api/export/comparacion/301/304/excel
# 500 Internal Server Error
# TypeError: 'str' object cannot be interpreted as an integer
```

### Después del Fix
```bash
# Exportar comparación
curl -X GET http://localhost:8000/api/export/comparacion/301/304/excel
# 200 OK
# Descarga archivo: comparacion_RNP002673721898_20260324_20260325.xlsx
```

---

## Lecciones Aprendidas

1. **Los objetos `date` no son strings** - No se pueden usar métodos de string directamente
2. **Usar `.strftime()` para formatear fechas** - Es el método correcto para convertir fechas a strings
3. **Verificar tipos de datos** - Especialmente cuando se trabaja con objetos de SQLAlchemy
4. **Probar todas las variantes** - Si hay múltiples endpoints similares, verificar que todos funcionen

---

## Prevención

Para evitar este tipo de errores en el futuro:

1. **Siempre usar `.strftime()` para formatear fechas** - No asumir que son strings
2. **Type hints en Python** - Agregar anotaciones de tipo para detectar errores temprano
   ```python
   from datetime import date
   
   def format_fecha(fecha: date) -> str:
       return fecha.strftime('%Y%m%d')
   ```
3. **Tests unitarios** - Probar exportaciones con datos reales
4. **Logging mejorado** - Agregar logs antes de operaciones críticas

---

## Patrones Comunes de Formateo de Fechas

```python
from datetime import date, datetime

# Objeto date
fecha = date(2026, 3, 25)

# ✅ CORRECTO - Formatear a string
fecha.strftime('%Y%m%d')        # '20260325'
fecha.strftime('%Y-%m-%d')      # '2026-03-25'
fecha.strftime('%d/%m/%Y')      # '25/03/2026'

# ❌ INCORRECTO - Intentar usar métodos de string
fecha.replace('-', '')          # TypeError!
str(fecha).replace('-', '')     # Funciona pero no es idiomático

# ✅ MEJOR - Usar strftime con el formato deseado directamente
fecha.strftime('%Y%m%d')        # Más claro y eficiente
```

---

## Impacto

**Funcionalidades afectadas:**
- ✅ Exportación de cierres a CSV
- ✅ Exportación de cierres a Excel
- ✅ Exportación de comparaciones a CSV
- ✅ Exportación de comparaciones a Excel

**Todas las exportaciones ahora funcionan correctamente.**

---

## Referencias

- [Python datetime.strftime() documentation](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
- [SQLAlchemy Date and Time Types](https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Date)
- Documentación interna: `backend/api/export.py`

---

## Relacionado

- **Task 11:** Fix orden de rutas en endpoint read-all
- **Task 12:** Fix error de tipo en exportaciones (este documento)
