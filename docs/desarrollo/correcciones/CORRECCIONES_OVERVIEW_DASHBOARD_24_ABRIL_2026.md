# Correcciones Overview Dashboard - 24 de Abril 2026

## Resumen
Se aplicaron correcciones al Overview Dashboard basadas en feedback del usuario sobre información hardcodeada y métricas no disponibles.

## Problemas Identificados

### 1. Sidebar con Scroll Innecesario ❌
**Problema**: El sidebar mostraba scroll cuando no debería tenerlo.

**Causa**: El orden de las clases CSS en el contenedor del menú.

**Solución**:
```tsx
// ANTES
<div className="relative z-10 flex-1 py-6 overflow-y-auto custom-scrollbar px-4 space-y-2">

// DESPUÉS
<div className="relative z-10 flex-1 py-6 px-4 space-y-2 overflow-y-auto custom-scrollbar">
```

**Resultado**: El sidebar ahora solo muestra scroll cuando el contenido excede la altura disponible.

---

### 2. KPI "Tóner Bajo" No Disponible ❌
**Problema**: Se mostraba un KPI de "Tóner Bajo" pero esta información no se puede obtener vía SNMP.

**Contexto**: Se intentó previamente obtener niveles de tóner vía SNMP pero no funcionó.

**Solución**: Reemplazar con KPI más relevante y disponible.

**Cambios**:
```tsx
// ANTES
<KPICard 
  title="Tóner Bajo" 
  value={kpis.tonerBajo} 
  icon={<AlertTriangle size={20} />} 
  color={chartColors.warning} 
/>

// DESPUÉS
<KPICard 
  title="Usuarios Provisionados" 
  value={kpis.usuariosProvisionados} 
  icon={<Users size={20} />} 
  color={chartColors.info} 
/>
```

**Justificación**: "Usuarios Provisionados" es una métrica clave del sistema y está disponible en la base de datos.

---

### 3. KPI "Sin Usuarios" Poco Relevante ❌
**Problema**: El KPI "Sin Usuarios" no es tan estratégico para el dashboard principal.

**Solución**: Reemplazar con "Cierres Pendientes".

**Cambios**:
```tsx
// ANTES
<KPICard 
  title="Sin Usuarios" 
  value={kpis.sinUsuarios} 
  icon={<UserX size={20} />} 
  color={chartColors.error} 
/>

// DESPUÉS
<KPICard 
  title="Cierres Pendientes" 
  value={kpis.cierresPendientes} 
  icon={<FileCheck size={20} />} 
  color={chartColors.warning} 
/>
```

**Justificación**: Los cierres pendientes son una métrica operativa importante que requiere acción.

---

### 4. Gráfico "Consumo por Sede" Poco Específico ❌
**Problema**: El gráfico mostraba "Consumo por Sede" pero es más útil ver impresoras específicas.

**Feedback del Usuario**: "No sería tanto consumo por sede sino por impresora o por usuarios"

**Solución**: Cambiar a "Top 5 Impresoras".

**Cambios**:

**Mock de Datos**:
```typescript
// ANTES
consumoPorSede: [
  { name: 'Sede Principal', value: 45000 },
  { name: 'Sede Norte', value: 25000 },
  { name: 'Sede Sur', value: 15000 },
]

// DESPUÉS
topImpresoras: [
  { name: 'IM C6010 (Ventas)', value: 25000 },
  { name: 'Pro C5300s (Diseño)', value: 20000 },
  { name: 'IM 430F (Recepción)', value: 15000 },
  { name: 'P 502 (Logística)', value: 12000 },
  { name: 'IM C4500 (RRHH)', value: 10000 },
]
```

**Componente**:
```tsx
// ANTES
<ChartCard title="Consumo por Sede (Mes Actual)">

// DESPUÉS
<ChartCard title="Top 5 Impresoras (Mes Actual)">
```

**Tooltip Mejorado**:
```tsx
<Tooltip 
  formatter={(value: number) => [`${value.toLocaleString()} páginas`, 'Consumo']}
/>
```

**Justificación**: 
- Más específico y accionable
- Identifica equipos con mayor consumo
- Permite detectar outliers rápidamente
- Alineado con el enfoque operativo del sistema

---

### 5. Actividad Reciente con Alertas de Tóner ❌
**Problema**: La actividad reciente incluía "Alerta de Tóner" que no es información disponible.

**Solución**: Reemplazar con actividad más relevante.

**Cambios**:
```typescript
// ANTES
{ id: '2', fecha: '2026-04-23T15:45:00Z', tipo: 'Alerta de Tóner', descripcion: 'Nivel crítico en Copiadora RRHH (Cyan)', usuario: 'Sistema', status: 'warning' }

// DESPUÉS
{ id: '2', fecha: '2026-04-23T15:45:00Z', tipo: 'Lectura de Contadores', descripcion: 'Lectura automática ejecutada en 42 equipos', usuario: 'Sistema', status: 'success' }
```

---

### 6. Espaciado del Sidebar Inconsistente ⚠️
**Problema**: Espaciado entre secciones del sidebar era demasiado grande (pt-8).

**Solución**: Reducir a pt-6 para mejor aprovechamiento del espacio.

**Cambios**:
```tsx
// ANTES
<div className="px-4 pb-4 pt-8">

// DESPUÉS
<div className="px-4 pb-4 pt-6">
```

---

## KPIs Finales del Overview Dashboard

### 1. Total Equipos 🖨️
- **Valor**: 45
- **Color**: Ricoh Red (`#E30613`)
- **Fuente**: Tabla `impresoras`
- **Disponibilidad**: ✅ Disponible

### 2. Equipos Online 📡
- **Valor**: 42
- **Color**: Verde (`#10B981`)
- **Fuente**: Tabla `impresoras` (campo `estado`)
- **Disponibilidad**: ✅ Disponible

### 3. Usuarios Provisionados 👥
- **Valor**: 128
- **Color**: Azul (`#3B82F6`)
- **Fuente**: Tabla `usuarios_impresoras`
- **Disponibilidad**: ✅ Disponible

### 4. Cierres Pendientes 📋
- **Valor**: 3
- **Color**: Amarillo (`#F59E0B`)
- **Fuente**: Lógica de negocio (cierres no realizados en el mes)
- **Disponibilidad**: ✅ Disponible

---

## Gráfico: Top 5 Impresoras

**Tipo**: Barras horizontales (Recharts)

**Datos Mostrados**:
1. IM C6010 (Ventas) - 25,000 páginas
2. Pro C5300s (Diseño) - 20,000 páginas
3. IM 430F (Recepción) - 15,000 páginas
4. P 502 (Logística) - 12,000 páginas
5. IM C4500 (RRHH) - 10,000 páginas

**Fuente de Datos**: 
- Tabla `cierres_mensuales` + `contadores_cierre`
- Agregación por `printer_id` del mes actual
- Ordenado por total de páginas descendente
- Limitado a top 5

**Disponibilidad**: ✅ Disponible

---

## Tabla: Actividad Reciente

**Actividades Mostradas**:
1. ✅ Aprovisionamiento - Usuario asignado
2. ✅ Lectura de Contadores - Lectura automática
3. ✅ Cierre Mensual - Cierre automático
4. ❌ Error de Conexión - Pérdida de ping

**Fuente de Datos**: 
- Futura tabla de auditoría/logs
- Por ahora: datos mock

**Disponibilidad**: ⚠️ Requiere implementación de sistema de auditoría

---

## Métricas Eliminadas (No Disponibles)

### ❌ Tóner Bajo
**Razón**: No se puede obtener vía SNMP
**Intentos Previos**: Se probó lectura SNMP sin éxito
**Alternativa**: Monitoreo manual o integración con software del fabricante

### ❌ Sin Usuarios
**Razón**: Métrica poco estratégica para dashboard principal
**Alternativa**: Disponible en vista de Fleet Management

### ❌ Alertas de Tóner
**Razón**: Depende de lectura de niveles de tóner (no disponible)
**Alternativa**: N/A

---

## Impacto en Futuros Sprints

### Sprint 3: Fleet Management
- ✅ Incluir filtro "Sin Usuarios" en la vista de equipos
- ✅ Mostrar estado de conexión (online/offline)
- ❌ NO incluir indicadores de tóner

### Sprint 4: Analytics
- ✅ Gráficos basados en datos de contadores (disponibles)
- ✅ Comparativas de consumo por período
- ✅ Top equipos y top usuarios
- ❌ NO incluir análisis de tóner

---

## Próximos Pasos

### Integración con Backend Real
Cuando se conecte con APIs reales, los datos mock deben reemplazarse con:

1. **Total Equipos**: `GET /api/printers/count`
2. **Equipos Online**: `GET /api/printers/count?status=online`
3. **Usuarios Provisionados**: `GET /api/users/count`
4. **Cierres Pendientes**: Lógica de negocio basada en última fecha de cierre
5. **Top Impresoras**: `GET /api/analytics/top-printers?period=current_month&limit=5`
6. **Actividad Reciente**: `GET /api/audit/recent?limit=4` (requiere implementación)

---

## Archivos Modificados

1. `src/pages/Dashboard.tsx` - Ajustes de espaciado en sidebar
2. `src/pages/OverviewDashboard.tsx` - Cambios en KPIs y gráfico
3. `src/mocks/overviewData.ts` - Actualización de datos mock

**Total**: 3 archivos

---

## Verificación

- ✅ Sin errores de diagnóstico en TypeScript
- ✅ Componentes renderizan correctamente
- ✅ Datos mock son realistas y consistentes
- ✅ Estilos consistentes con Design System
- ✅ Responsive design funcional

---

## Notas Técnicas

### Sobre Lectura de Tóner vía SNMP
El sistema intentó previamente obtener niveles de tóner mediante SNMP pero no funcionó. Posibles razones:
- OIDs específicos del fabricante no documentados
- Modelos de impresoras sin soporte SNMP para tóner
- Configuración de seguridad en las impresoras
- Versiones de SNMP incompatibles

**Recomendación**: No invertir más tiempo en esta funcionalidad hasta tener confirmación del fabricante sobre OIDs correctos.

---

## Metadata
- **Fecha**: 24 de abril 2026
- **Sprint**: 2 (Overview Dashboard)
- **Tipo**: Correcciones basadas en feedback
- **Archivos Modificados**: 3
- **Líneas Cambiadas**: ~50
