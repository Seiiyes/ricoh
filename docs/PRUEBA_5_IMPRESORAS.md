# 🖨️ Prueba de Contadores en las 5 Impresoras

**Fecha:** 2 de Marzo de 2026  
**Script:** `backend/probar_5_impresoras.py`

---

## 📊 Resultados de la Prueba

### Impresoras Probadas

| Impresora | IP | Login | Contador Unificado | Contador Usuario | Contador Ecológico |
|-----------|-------|-------|-------------------|------------------|-------------------|
| RICOH-251 | 192.168.91.251 | ✅ | ✅ (23.6 KB) | ✅ (15.1 KB) | ✅ (16.6 KB) |
| RICOH-252 | 192.168.91.252 | ❌ | - | - | - |
| RICOH-253 | 192.168.91.253 | ✅ | ✅ (21.8 KB) | ❌ | ✅ (15.5 KB) |
| RICOH-254 | 192.168.91.254 | ❌ | - | - | - |
| RICOH-255 | 192.168.91.255 | ❌ | - | - | - |

### Resumen por Tipo de Contador

**📊 Contador Unificado:** 2/5 impresoras (40%)
- ✅ RICOH-251 (192.168.91.251)
- ✅ RICOH-253 (192.168.91.253)

**👥 Contador por Usuario:** 1/5 impresoras (20%)
- ✅ RICOH-251 (192.168.91.251)

**🌿 Contador Ecológico:** 2/5 impresoras (40%)
- ✅ RICOH-251 (192.168.91.251)
- ✅ RICOH-253 (192.168.91.253)

---

## 🔍 Análisis Detallado

### RICOH-251 (192.168.91.251) - ✅ COMPLETA

**Estado:** Todas las URLs funcionan

**URLs Disponibles:**
- `/web/entry/es/websys/status/getUnificationCounter.cgi` ✅
- `/web/entry/es/websys/status/getUserCounter.cgi` ✅
- `/web/entry/es/websys/getEcoCounter.cgi` ✅

**Datos Disponibles:**
- Contadores totales (copiadora, impresora, fax, escáner)
- Contadores por usuario (265 usuarios)
- Contadores ecológicos (uso 2 caras, combinar, reducción papel)

**Recomendación:** Usar como impresora de referencia para desarrollo

---

### RICOH-253 (192.168.91.253) - ⚠️ PARCIAL

**Estado:** Sin contador por usuario, usar contador ecológico

**URLs Disponibles:**
- `/web/entry/es/websys/status/getUnificationCounter.cgi` ✅
- `/web/entry/es/websys/status/getUserCounter.cgi` ❌
- `/web/entry/es/websys/getEcoCounter.cgi` ✅

**Datos Disponibles:**
- Contadores totales: ✅
- Contadores por usuario: ❌ (NO disponible)
- Contadores ecológicos: ✅ (185 usuarios con datos ecológicos)

**Contador Ecológico - Datos:**
- Total páginas impresión: 318,820
- Uso 2 caras: 53%
- Uso Combinar: 0%
- Reducción papel: 27%
- **Contadores por usuario:** 185 usuarios con:
  * Código de usuario
  * Nombre de usuario
  * Total páginas impresión (actual y anterior)
  * Uso 2 caras (%)
  * Uso Combinar (%)
  * Reducción papel (%)

**Recomendación:** Usar contador ecológico como alternativa para contadores por usuario

---

### RICOH-252, 254, 255 - ❌ NO ACCESIBLES

**Estado:** No se pudo hacer login

**Posibles Causas:**
1. Impresoras apagadas
2. Credenciales diferentes (no usan admin/sin contraseña)
3. Problemas de red
4. Configuración de seguridad diferente

**Acción Requerida:**
1. Verificar que las impresoras estén encendidas
2. Verificar credenciales de administrador
3. Probar acceso manual desde navegador
4. Actualizar credenciales en el script si son diferentes

---

## 🎯 Estrategia de Implementación

### Opción 1: Lógica Condicional por Impresora (RECOMENDADA)

```python
def get_counters(printer_ip):
    """
    Obtiene contadores según las capacidades de cada impresora
    """
    # Intentar contador unificado primero
    try:
        counters = get_unification_counter(printer_ip)
        if counters:
            return {'type': 'unificado', 'data': counters}
    except:
        pass
    
    # Si no funciona, intentar contador ecológico
    try:
        counters = get_eco_counter(printer_ip)
        if counters:
            return {'type': 'ecologico', 'data': counters}
    except:
        pass
    
    return None

def get_user_counters(printer_ip):
    """
    Obtiene contadores por usuario según disponibilidad
    """
    # Intentar contador por usuario primero
    try:
        users = get_user_counter(printer_ip)
        if users:
            return {'type': 'usuario', 'data': users}
    except:
        pass
    
    # Si no funciona, usar contador ecológico
    try:
        users = get_eco_counter_users(printer_ip)
        if users:
            return {'type': 'ecologico', 'data': users}
    except:
        pass
    
    return None
```

### Opción 2: Configuración por Impresora en Base de Datos

Agregar campos a la tabla `printers`:
```sql
ALTER TABLE printers ADD COLUMN contador_tipo VARCHAR(20) DEFAULT 'unificado';
-- Valores: 'unificado', 'ecologico', 'usuario'

ALTER TABLE printers ADD COLUMN tiene_contador_usuario BOOLEAN DEFAULT TRUE;
```

Luego consultar la configuración antes de obtener contadores.

---

## 📋 Próximos Pasos

### Inmediato

1. ✅ **Crear parser para contador ecológico**
   - Parsear contadores totales del dispositivo
   - Parsear contadores por usuario (185 usuarios en RICOH-253)
   - Extraer métricas ecológicas (uso 2 caras, combinar, reducción)

2. ⏳ **Verificar impresoras 252, 254, 255**
   - Confirmar que estén encendidas
   - Verificar credenciales
   - Actualizar lista de impresoras accesibles

3. ⏳ **Actualizar modelos de base de datos**
   - Agregar campo `contador_tipo` a tabla `printers`
   - Agregar campo `tiene_contador_usuario` a tabla `printers`
   - Agregar tabla `contadores_ecologicos` si es necesario

### Fase 2

4. ⏳ **Implementar servicio unificado de contadores**
   - Detectar automáticamente qué URLs funcionan por impresora
   - Usar la mejor opción disponible
   - Guardar configuración en base de datos

5. ⏳ **Crear API endpoints**
   - GET `/api/contadores/{impresora_id}` - Obtiene contadores (cualquier tipo)
   - GET `/api/contadores/usuario/{impresora_id}` - Contadores por usuario
   - POST `/api/contadores/detectar/{impresora_id}` - Detecta URLs disponibles

---

## 💡 Recomendaciones

### Para RICOH-253 (sin contador por usuario)

**Usar Contador Ecológico como alternativa:**
- ✅ Tiene 185 usuarios registrados
- ✅ Proporciona total de páginas por usuario
- ✅ Incluye métricas ecológicas adicionales
- ⚠️ No tiene desglose por tipo de trabajo (copia/impresión/scan)
- ⚠️ No tiene desglose por color (B/N vs Color)

**Ventajas:**
- Mejor que no tener nada
- Datos útiles para facturación básica
- Métricas ecológicas son un plus

**Desventajas:**
- Menos detalle que contador por usuario completo
- No se puede diferenciar entre copia e impresión

### Para Impresoras No Accesibles (252, 254, 255)

1. Verificar físicamente que estén encendidas
2. Intentar acceso manual desde navegador
3. Consultar con IT sobre credenciales
4. Si usan credenciales diferentes, actualizar script
5. Si están apagadas, considerar si son necesarias para el proyecto

---

## 📊 Comparación de Tipos de Contador

| Característica | Contador Unificado | Contador Usuario | Contador Ecológico |
|----------------|-------------------|------------------|-------------------|
| Total páginas | ✅ | ✅ | ✅ |
| Por tipo (copia/impresión) | ✅ | ✅ | ❌ |
| Por color (B/N/Color) | ✅ | ✅ | ❌ |
| Por usuario | ❌ | ✅ | ✅ |
| Métricas ecológicas | ❌ | ❌ | ✅ |
| Uso 2 caras | ❌ | ❌ | ✅ |
| Reducción papel | ❌ | ❌ | ✅ |
| Disponibilidad | 2/5 | 1/5 | 2/5 |

---

## 🎯 Conclusión

**Estado Actual:**
- 2 de 5 impresoras accesibles (40%)
- 1 impresora con todas las funciones (RICOH-251)
- 1 impresora con funcionalidad parcial (RICOH-253)
- 3 impresoras no accesibles (requieren verificación)

**Estrategia Recomendada:**
1. Implementar soporte para los 3 tipos de contador
2. Detectar automáticamente qué URLs funcionan por impresora
3. Usar la mejor opción disponible para cada impresora
4. Crear parser para contador ecológico
5. Verificar y configurar impresoras 252, 254, 255

**Próximo Paso Inmediato:**
Crear parser para contador ecológico (`backend/parsear_contador_ecologico.py`)

---

**Última Actualización:** 2 de Marzo de 2026  
**Autor:** Kiro AI Assistant  
**Proyecto:** Sistema de Gestión de Impresoras Ricoh
