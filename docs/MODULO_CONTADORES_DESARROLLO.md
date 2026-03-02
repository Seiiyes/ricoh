# 📊 Módulo de Contadores - Documentación de Desarrollo

**Fecha de Inicio:** 2 de Marzo de 2026  
**Estado:** 🔄 En Desarrollo  
**Versión:** 1.0

---

## 🎯 Objetivo del Módulo

Implementar un sistema de gestión de contadores de impresión que permita:

1. **Leer contadores de impresión:**
   - Contador total de la impresora
   - Contadores por usuario
   - Desglose por tipo de trabajo (copia, impresión, scan)

2. **Sistema de Cierre Mensual:**
   - Registrar estado de contadores en día específico del mes
   - Comparar con mes anterior (ej: 27/02 vs 27/01)
   - Calcular páginas impresas en el período

3. **Selección de Impresoras:**
   - Elegir qué impresoras incluir en el cierre
   - Cierre individual o masivo

4. **Exportación:**
   - Exportar reportes a Excel
   - Exportar reportes a CSV

---

## 📋 Especificaciones Técnicas

### Información Requerida

**Por Impresora:**
- Contador total de páginas
- Páginas a color
- Páginas blanco y negro

**Por Usuario:**
- Nombre y código de usuario
- Total de páginas impresas
- Desglose por tipo:
  - Copias (B/N y Color)
  - Impresiones (B/N y Color)
  - Escaneos

**Cierres:**
- Fecha del cierre
- Snapshot completo de contadores
- Comparación con mes anterior
- Diferencias calculadas

### Frecuencia de Cierres

- **Mensual:** Día específico del mes (configurable)
- **Manual:** Cuando el usuario lo requiera

---

## 🏗️ Arquitectura Propuesta

### Modelos de Base de Datos (en español)

```python
# Tabla: contadores_impresora
- id
- impresora_id (FK)
- total_paginas
- paginas_color
- paginas_bn
- fecha_lectura

# Tabla: contadores_usuario
- id
- impresora_id (FK)
- codigo_usuario
- nombre_usuario
- total_paginas
- copias_bn
- copias_color
- impresiones_bn
- impresiones_color
- escaneos
- fecha_lectura

# Tabla: cierres_mensuales
- id
- fecha_cierre (Date)
- impresora_id (FK)
- total_paginas
- datos_usuarios (JSON)
- notas
- fecha_creacion
```

---

## 📝 Fase 1: Investigación y Pruebas

**Objetivo:** Identificar cómo leer contadores de las impresoras Ricoh

**Fecha:** 2 de Marzo de 2026  
**Estado:** 🔄 En Progreso

### 1.1 Información de Prueba

**Impresora de Prueba:**
- IP: 192.168.91.251
- Modelo: RICOH MP C3004
- Usuario Admin: admin (sin contraseña)

### 1.2 Métodos a Investigar

#### Opción A: SNMP
- **Puerto:** 161
- **Comunidad:** public (por defecto)
- **OIDs a probar:**
  - Contador total: `1.3.6.1.2.1.43.10.2.1.4.1.1`
  - Modelo: `1.3.6.1.2.1.25.3.2.1.3.1`
  - Serial: `1.3.6.1.2.1.43.5.1.1.17.1`

**Estado:** ⏳ Por probar

#### Opción B: Interfaz Web
- **URL Base:** `http://192.168.91.251/web/entry/es/`
- **URLs a investigar:**
  - Contadores generales: `/web/entry/es/websys/status/`
  - Contadores por usuario: `/web/entry/es/address/` (posible)
  - Estadísticas: `/web/entry/es/websys/webArch/` (posible)

**Estado:** ⏳ Por probar

#### Opción C: API REST
- **URL a probar:** `http://192.168.91.251/api/v1/`
- **Documentación:** Buscar en interfaz web

**Estado:** ⏳ Por probar

### 1.3 Pruebas Realizadas

#### Prueba 1: SNMP - Contador Total
**Fecha:** 2 de Marzo de 2026  
**Resultado:** ❌ No viable  
**Notas:** 
- Librería `pysnmp` v7.1.22 instalada
- API de pysnmp v7 completamente diferente a versiones anteriores
- Requiere uso de async/await y API compleja
- SNMP fue intentado anteriormente sin éxito
- **DECISIÓN: Descartar SNMP, usar interfaz web**

#### Prueba 2: Web Interface - Navegación
**Fecha:** 2 de Marzo de 2026  
**Resultado:** ✅ EXITOSO  
**Notas:**
- Login exitoso ✅
- **URL de contadores encontrada:** `/web/entry/es/websys/status/getUnificationCounter.cgi`
- Retorna HTML con 42 tablas conteniendo todos los contadores
- Parser implementado y funcionando correctamente
- **Datos disponibles:**
  * Total general de páginas
  * Copiadora (B/N, Color, Color personalizado, Dos colores)
  * Impresora (B/N, Color, Color personalizado, Dos colores)
  * Fax (B/N)
  * Enviar/TX Total (B/N, Color)
  * Transmisión por fax (Total)
  * Envío por escáner (B/N, Color)
  * Otras funciones (A3/DLT, Dúplex)

#### Prueba 3: Exploración de Menú
**Fecha:** 2 de Marzo de 2026  
**Resultado:** ✅ URL ENCONTRADA  
**Notas:**
- Probadas 20+ URLs comunes de contadores
- **URL correcta encontrada:** `getUnificationCounter.cgi`
- Script de prueba creado: `probar_url_contadores.py`
- Parser implementado: `parsear_contadores.py`

#### Prueba 4: API REST
**Fecha:** 2 de Marzo de 2026  
**Resultado:** ❌ No disponible  
**Notas:**
- No hay API REST en esta impresora
- Endpoints `/api/`, `/rest/`, `/webapi/` no existen

---

## 📊 Hallazgos y Decisiones

### Hallazgos

**Fecha:** 2 de Marzo de 2026

1. **SNMP No Viable:**
   - La librería pysnmp v7.1.22 está instalada pero tiene API completamente diferente
   - Requiere async/await y configuración compleja
   - Intentos previos de usar SNMP no fueron exitosos
   - **DECISIÓN: Descartar SNMP como opción**

2. **Interfaz Web - ✅ EXITOSO:**
   - **URL encontrada:** `/web/entry/es/websys/status/getUnificationCounter.cgi`
   - Retorna HTML estructurado con todos los contadores
   - Parser implementado y funcionando
   - **Método seleccionado para el proyecto**

3. **API REST No Disponible:**
   - Esta impresora no tiene API REST
   - Solo interfaz web disponible

4. **Datos Disponibles:**
   - ✅ Total general de páginas
   - ✅ Contadores por tipo de trabajo (Copiadora, Impresora, Fax, Escáner)
   - ✅ Desglose por color (B/N, Color, Color personalizado, Dos colores)
   - ✅ Funciones adicionales (A3/DLT, Dúplex)
   - ❌ Contadores por usuario (NO disponibles en esta URL)

5. **Próximo Paso:**
   - Investigar si existe URL para contadores por usuario
   - Si no existe, considerar implementar solo contadores totales
   - Continuar con Fase 2: Modelos de base de datos

### Decisiones Técnicas

**Decisión 1: Método de Lectura**
- ✅ **Usar Interfaz Web** (única opción disponible)
- ❌ SNMP descartado
- ❌ API REST no existe

**Decisión 2: Enfoque de Implementación**
- Parsear HTML de la interfaz web
- Usar sesiones HTTP (ya implementado en `ricoh_web_client.py`)
- Reutilizar lógica de autenticación existente

**Decisión 3: Siguiente Acción**
- **PAUSAR desarrollo automático**
- **REQUERIR navegación manual** para identificar URLs correctas
- Una vez identificadas las URLs, continuar con implementación

---

## 🚀 Próximas Fases

### Fase 2: Backend - Modelos (Pendiente)
- Crear modelos de base de datos
- Crear migración
- Aplicar migración

### Fase 3: Backend - Servicio de Contadores (Pendiente)
- Implementar lectura de contadores
- Implementar guardado de contadores
- Implementar lógica de cierre

### Fase 4: Backend - API (Pendiente)
- Crear endpoints REST
- Documentar API

### Fase 5: Frontend - Componentes (Pendiente)
- Crear interfaz de contadores
- Crear interfaz de cierres
- Crear comparaciones

### Fase 6: Exportación (Pendiente)
- Implementar exportación a Excel
- Implementar exportación a CSV

---

## 📝 Notas de Desarrollo

[Se irán agregando notas conforme se desarrolle el módulo]

---

**Última Actualización:** 2 de Marzo de 2026


---

## 🔍 ACCIÓN REQUERIDA: Navegación Manual

### Objetivo
Identificar las URLs reales donde se encuentran los contadores en la interfaz web de Ricoh.

### Pasos a Seguir

1. **Acceder a la Impresora:**
   - Abrir navegador
   - Ir a: http://192.168.91.251
   - Login: admin (sin contraseña)

2. **Buscar Contadores Totales:**
   - Navegar por el menú principal
   - Buscar secciones como:
     * "Estado del Dispositivo"
     * "Información del Sistema"
     * "Contadores"
     * "Estadísticas"
   - **Documentar la URL** cuando encuentres los contadores

3. **Buscar Contadores por Usuario:**
   - Buscar en:
     * Libreta de Direcciones
     * Gestión de Usuarios
     * Reportes de Uso
   - **Documentar la URL** si existe esta funcionalidad

4. **Capturar Información:**
   - Tomar captura de pantalla de la página de contadores
   - Copiar la URL completa
   - Hacer clic derecho → "Ver código fuente" o F12
   - Identificar:
     * Nombres de campos/variables
     * Estructura de datos
     * Formato de números

5. **Documentar Hallazgos:**
   - Actualizar este documento con:
     * URL exacta de contadores
     * Estructura HTML
     * Campos disponibles
     * Ejemplo de datos

### Información a Buscar

**Contadores Totales:**
- [ ] Total de páginas impresas
- [ ] Páginas a color
- [ ] Páginas blanco y negro
- [ ] Copias totales
- [ ] Impresiones totales
- [ ] Escaneos totales

**Contadores por Usuario (si existe):**
- [ ] Nombre/código de usuario
- [ ] Total por usuario
- [ ] Desglose por tipo de trabajo
- [ ] Desglose color/B&N

### Resultado Esperado

Una vez completada la navegación manual, deberías tener:

```
URL de Contadores Totales:
http://192.168.91.251/web/entry/es/[RUTA_REAL]/[ARCHIVO].cgi

Campos Disponibles:
- total_pages: 125450
- color_pages: 45230
- bw_pages: 80220
- etc...

Estructura HTML:
<div class="counter">
  <span class="label">Total:</span>
  <span class="value">125450</span>
</div>
```

---

## 📝 Notas Adicionales

### Alternativa: Consultar Manual de la Impresora

Si la navegación manual es difícil, se puede:
1. Buscar el manual de usuario de RICOH MP C3004
2. Buscar sección de "Contadores" o "Counters"
3. Identificar cómo acceder a esta información

### Alternativa: Contactar Soporte Ricoh

Si no se encuentran los contadores en la interfaz web:
1. Verificar si esta funcionalidad requiere licencia adicional
2. Consultar con soporte técnico de Ricoh
3. Preguntar por API o método programático para leer contadores

---

**Estado Actual:** ✅ FASE 1 COMPLETADA - Listo para Fase 2  
**Próximo Paso:** Crear modelos de base de datos para contadores  
**URL de Contadores:** `/web/entry/es/websys/status/getUnificationCounter.cgi`  
**Parser Implementado:** `backend/parsear_contadores.py`  
**Última Actualización:** 2 de Marzo de 2026

---

## 📌 Resumen Ejecutivo

### ✅ Fase 1 Completada
- ✅ Análisis de requerimientos del módulo de contadores
- ✅ Definición de modelos de base de datos en español
- ✅ Investigación de métodos de acceso (SNMP, Web, API)
- ✅ **URL de contadores encontrada y funcionando**
- ✅ **Parser de HTML implementado y probado**
- ✅ Scripts de prueba creados y documentados

### 📊 Datos Disponibles
**Contadores Totales (por impresora):**
- Total general: 372,407 páginas
- Copiadora: B/N (53,257) + Color (5,835) = 59,092
- Impresora: B/N (226,721) + Color (86,228) = 312,949
- Fax: 46 páginas
- Escáner: B/N (135,152) + Color (35,116) = 170,268
- Otras funciones: A3/DLT (2,811), Dúplex (46,830)

**Contadores por Usuario:**
- ⚠️ No disponibles en la URL encontrada
- Requiere investigación adicional o ajuste de requerimientos

### 🎯 Decisión Técnica
**Método seleccionado:** Interfaz Web HTTP
- URL: `/web/entry/es/websys/status/getUnificationCounter.cgi`
- Formato: HTML estructurado
- Parser: BeautifulSoup + Regex
- Cliente HTTP: Ya implementado en el proyecto

### 📋 Próximas Fases

#### Fase 2: Backend - Modelos (SIGUIENTE)
- Crear tabla `contadores_impresora` en la base de datos
- Crear migración SQL
- Actualizar `models.py` con el nuevo modelo
- Aplicar migración

#### Fase 3: Backend - Servicio de Contadores
- Integrar `parsear_contadores.py` en `services/`
- Implementar servicio de lectura periódica
- Implementar guardado en base de datos
- Implementar lógica de cierre mensual

#### Fase 4: Backend - API
- Crear endpoints REST para contadores
- Endpoint: GET /api/contadores/{impresora_id}
- Endpoint: GET /api/contadores/historial/{impresora_id}
- Endpoint: POST /api/contadores/cierre
- Documentar API

#### Fase 5: Frontend - Componentes
- Crear interfaz de visualización de contadores
- Crear interfaz de cierres mensuales
- Crear comparaciones mes a mes
- Gráficos de evolución

#### Fase 6: Exportación
- Implementar exportación a Excel
- Implementar exportación a CSV

### ⚠️ Nota sobre Contadores por Usuario
Los contadores por usuario NO están disponibles en la URL encontrada. Opciones:
1. Buscar otra URL específica para contadores por usuario
2. Ajustar requerimientos para trabajar solo con contadores totales
3. Implementar entrada manual de contadores por usuario si es crítico

**Recomendación:** Continuar con contadores totales por ahora, investigar contadores por usuario en paralelo.
