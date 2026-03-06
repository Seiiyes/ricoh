# Validaciones de Integridad de Datos - Módulo de Contadores

**Fecha:** 2 de Marzo de 2026  
**Estado:** ✅ IMPLEMENTADO  
**Criticidad:** ALTA

---

## 📋 Resumen

Se han implementado validaciones exhaustivas para garantizar la integridad de los datos de contadores antes de almacenarlos en la base de datos. Esto es crítico para evitar datos incorrectos que puedan afectar reportes y decisiones de negocio.

---

## ✅ Validaciones Implementadas

### 1. Validación de Contadores Totales

**Método:** `CounterService.validate_counter_data(counters)`

**Validaciones:**

1. **Tipo de datos**
   - Verifica que `counters` no sea `None`
   - Verifica que `counters` sea un `dict`
   - Verifica que `total` sea un `int`

2. **Campos requeridos**
   - `total`
   - `copiadora`
   - `impresora`
   - `fax`
   - `enviar_total`
   - `transmision_fax`
   - `envio_escaner`
   - `otras_funciones`

3. **Consistencia de datos**
   - Si `total = 0`, verifica que todos los contadores sean 0
   - Si hay contadores > 0, el total NO puede ser 0
   - Detecta inconsistencias: `total=0` pero `suma_parcial > 0`

**Ejemplo de error detectado:**
```python
# Esto lanzaría ValueError
counters = {
    'total': 0,
    'copiadora': {'blanco_negro': 1000, 'color': 500},
    'impresora': {'blanco_negro': 2000, 'color': 1000},
    ...
}
# Error: "Inconsistencia: total=0 pero suma de contadores=4500"
```

---

### 2. Validación de Contadores por Usuario

**Método:** `CounterService.validate_user_counter_data(user, tipo)`

**Validaciones:**

1. **Tipo de datos**
   - Verifica que `user` no sea `None`
   - Verifica que `user` sea un `dict`

2. **Campos requeridos comunes**
   - `codigo_usuario`
   - `nombre_usuario`

3. **Campos específicos por tipo**
   
   **Tipo "usuario" (getUserCounter):**
   - `total_paginas` (debe ser `int`)
   
   **Tipo "ecologico" (getEcoCounter):**
   - `total_paginas_actual` (debe ser `int`)

**Ejemplo de error detectado:**
```python
# Esto lanzaría ValueError
user = {
    'codigo_usuario': '1234',
    # Falta 'nombre_usuario'
    'total_paginas': 1000
}
# Error: "Campo 'nombre_usuario' no encontrado"
```

---

### 3. Validación de Estructura de Datos

**En `read_printer_counters()`:**
```python
# Validar antes de guardar
CounterService.validate_counter_data(counters)
```

**En `read_user_counters()`:**
```python
# Validar tipo de retorno
if not isinstance(users, list):
    raise ValueError(f"get_all_user_counters retornó tipo inválido: {type(users)}")

# Validar cada usuario
for user in users:
    CounterService.validate_user_counter_data(user, tipo_contador)
```

---

## 🔍 Diagnóstico de Impresoras con Total = 0

Se creó el script `backend/verificar_contadores_todas.py` para diagnosticar por qué algunas impresoras retornan total = 0.

**Resultados del diagnóstico:**

| ID | Hostname | IP | Total | Diagnóstico |
|----|----------|----|----|-------------|
| 3 | RNP0026737FFBB8 | 250 | 0 | ✅ Todos los contadores en 0 (impresora nueva/reseteada) |
| 4 | RNP00267391F283 | 251 | 372,525 | ✅ Funcionando correctamente |
| 5 | RNP002673CA501E | 252 | 0 | ✅ Todos los contadores en 0 (impresora nueva/reseteada) |
| 6 | RNP002673721B98 | 253 | 0 | ✅ Todos los contadores en 0 (impresora nueva/reseteada) |
| 7 | RNP002673C01D88 | 110.250 | 0 | ✅ Todos los contadores en 0 (impresora nueva/reseteada) |

**Conclusión:** No hay error en el parser. Las impresoras realmente tienen contadores en 0.

**Razones posibles:**
1. Impresoras recién instaladas
2. Contadores reseteados manualmente
3. Impresoras de prueba/desarrollo
4. Impresoras que no han sido usadas

---

## 🛡️ Protección Contra Datos Incorrectos

### Caso 1: Parser retorna None

```python
counters = None
CounterService.validate_counter_data(counters)
# ValueError: "Datos de contadores son None"
```

### Caso 2: Parser retorna tipo incorrecto

```python
counters = "invalid"
CounterService.validate_counter_data(counters)
# ValueError: "Datos de contadores tienen tipo inválido: <class 'str'>"
```

### Caso 3: Falta campo requerido

```python
counters = {'total': 1000}  # Faltan otros campos
CounterService.validate_counter_data(counters)
# ValueError: "Campo requerido 'copiadora' no encontrado en contadores"
```

### Caso 4: Inconsistencia en datos

```python
counters = {
    'total': 0,
    'copiadora': {'blanco_negro': 1000, 'color': 0},
    'impresora': {'blanco_negro': 2000, 'color': 0},
    ...
}
CounterService.validate_counter_data(counters)
# ValueError: "Inconsistencia: total=0 pero suma de contadores=3000"
```

### Caso 5: Usuario sin campos requeridos

```python
user = {'codigo_usuario': '1234'}  # Falta nombre_usuario
CounterService.validate_user_counter_data(user, "usuario")
# ValueError: "Campo 'nombre_usuario' no encontrado"
```

---

## 📊 Flujo de Validación

```
1. Parser lee datos de impresora
   ↓
2. Validar estructura de datos (validate_counter_data)
   ↓
3. Si hay error → Lanzar ValueError con mensaje descriptivo
   ↓
4. Si OK → Crear objeto ContadorImpresora
   ↓
5. Guardar en base de datos con transacción
   ↓
6. Si error en DB → Rollback automático
   ↓
7. Si OK → Commit y retornar objeto
```

---

## 🧪 Tests de Validación

### Test 1: Datos Válidos

```python
counters = {
    'total': 372525,
    'copiadora': {'blanco_negro': 53301, 'color': 5835, ...},
    'impresora': {'blanco_negro': 226787, 'color': 86228, ...},
    ...
}
CounterService.validate_counter_data(counters)
# ✅ Pasa validación
```

### Test 2: Total = 0 con todos los contadores en 0

```python
counters = {
    'total': 0,
    'copiadora': {'blanco_negro': 0, 'color': 0, ...},
    'impresora': {'blanco_negro': 0, 'color': 0, ...},
    ...
}
CounterService.validate_counter_data(counters)
# ✅ Pasa validación (impresora nueva/reseteada)
```

### Test 3: Inconsistencia detectada

```python
counters = {
    'total': 0,
    'copiadora': {'blanco_negro': 1000, 'color': 0, ...},
    'impresora': {'blanco_negro': 0, 'color': 0, ...},
    ...
}
CounterService.validate_counter_data(counters)
# ❌ ValueError: "Inconsistencia: total=0 pero suma de contadores=1000"
```

---

## 🔧 Mantenimiento

### Agregar Nueva Validación

1. Agregar método en `CounterService`
2. Llamar método antes de guardar datos
3. Documentar en este archivo
4. Agregar test

### Modificar Validación Existente

1. Actualizar método en `CounterService`
2. Verificar que no rompa tests existentes
3. Actualizar documentación
4. Ejecutar tests completos

---

## 📝 Recomendaciones

### Para Desarrollo

1. **Siempre validar antes de guardar**
   - Nunca guardar datos sin validar
   - Usar `validate_counter_data()` y `validate_user_counter_data()`

2. **Manejar errores apropiadamente**
   - Capturar `ValueError` en endpoints API
   - Retornar mensajes de error claros al frontend
   - Loggear errores para debugging

3. **Tests exhaustivos**
   - Probar casos válidos
   - Probar casos inválidos
   - Probar casos límite (total=0, valores negativos, etc.)

### Para Producción

1. **Monitoreo**
   - Alertar si muchas impresoras retornan total=0
   - Alertar si hay errores de validación frecuentes
   - Revisar logs regularmente

2. **Auditoría**
   - Mantener histórico completo
   - No borrar registros antiguos
   - Permitir comparación temporal

3. **Backup**
   - Backup diario de base de datos
   - Backup antes de cierres mensuales
   - Procedimiento de restauración documentado

---

## ✅ Checklist de Integridad

- [x] Validación de tipo de datos
- [x] Validación de campos requeridos
- [x] Validación de consistencia de datos
- [x] Validación de estructura de datos
- [x] Manejo de errores con rollback
- [x] Mensajes de error descriptivos
- [x] Documentación completa
- [x] Script de diagnóstico
- [x] Tests exitosos

---

## 📚 Referencias

**Archivos relacionados:**
- `backend/services/counter_service.py` - Servicio con validaciones
- `backend/verificar_contadores_todas.py` - Script de diagnóstico
- `backend/test_counter_service.py` - Tests del servicio

**Documentación relacionada:**
- `docs/FASE_3_COMPLETADA.md` - Servicio de lectura
- `docs/RESUMEN_MODULO_CONTADORES.md` - Resumen completo

---

**Última Actualización:** 2 de Marzo de 2026  
**Autor:** Kiro AI Assistant  
**Proyecto:** Sistema de Gestión de Impresoras Ricoh  
**Estado:** ✅ VALIDACIONES IMPLEMENTADAS Y PROBADAS
