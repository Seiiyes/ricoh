# Refactorización del Módulo Governance

**Fecha inicio:** 18 de marzo de 2026  
**Módulo:** ProvisioningPanel.tsx  
**Estado:** 🟡 En progreso

---

## 📋 ANÁLISIS DEL ARCHIVO

**Archivo:** `src/components/governance/ProvisioningPanel.tsx`  
**Líneas totales:** ~450 líneas  
**Componentes a refactorizar:**

### Botones Identificados (2)

1. **Botón "Descubrir Impresoras"** (línea ~430)
   - Actual: 3 líneas de className inline
   - Reemplazar con: `<Button variant="primary" size="sm" icon={<Wifi />}>`
   
2. **Botón "Enviar Configuración"** (línea ~420)
   - Actual: 3 líneas de className inline + lógica de loading
   - Reemplazar con: `<Button variant="secondary" loading={isProvisioning}>`

### Inputs Identificados (6)

1. **Input "Nombre Completo"** (línea ~230)
2. **Input "Código de Usuario"** (línea ~240)
3. **Input "Nombre de usuario de inicio de sesión"** (línea ~255)
4. **Input "Contraseña de inicio de sesión"** (línea ~265)
5. **Input "Ruta SMB"** (línea ~395)

### Alertas Identificadas (1)

1. **Alerta de advertencia** (línea ~380)
   - Actual: div con clases inline
   - Reemplazar con: `<Alert variant="warning">`

### Spinners Identificados (2)

1. **Spinner de carga de impresoras** (línea ~440)
   - Actual: `<Loader2 className="animate-spin" />`
   - Reemplazar con: `<Spinner text="Cargando impresoras..." />`

2. **Spinner en botón** (línea ~420)
   - Ya manejado por prop `loading` del Button

---

## 🎯 PLAN DE REFACTORIZACIÓN

### Fase 1: Preparación (COMPLETADO ✅)
- [x] Analizar archivo completo
- [x] Identificar componentes a reemplazar
- [x] Crear plan de acción
- [x] Documentar cambios

### Fase 2: Refactorizar Botones (SIGUIENTE)
- [ ] Importar componente Button
- [ ] Reemplazar botón "Descubrir Impresoras"
- [ ] Reemplazar botón "Enviar Configuración"
- [ ] Probar funcionalidad
- [ ] Commit cambios

### Fase 3: Refactorizar Inputs
- [ ] Importar componente Input
- [ ] Reemplazar input "Nombre Completo"
- [ ] Reemplazar input "Código de Usuario"
- [ ] Reemplazar input "Nombre de usuario"
- [ ] Reemplazar input "Contraseña"
- [ ] Reemplazar input "Ruta SMB"
- [ ] Probar validación
- [ ] Commit cambios

### Fase 4: Refactorizar Alert y Spinner
- [ ] Importar Alert y Spinner
- [ ] Reemplazar alerta de advertencia
- [ ] Reemplazar spinner de carga
- [ ] Probar funcionalidad
- [ ] Commit cambios

### Fase 5: Verificación Final
- [ ] Probar flujo completo de aprovisionamiento
- [ ] Verificar que no hay errores en consola
- [ ] Verificar estilos visuales
- [ ] Actualizar documentación
- [ ] Commit final

---

## 📊 MÉTRICAS

### Antes de Refactorización
```
Líneas totales:        ~450
Botones inline:        2 (6 líneas)
Inputs inline:         6 (30 líneas)
Alertas inline:        1 (5 líneas)
Spinners inline:       2 (4 líneas)
Total código inline:   ~45 líneas
```

### Después de Refactorización (Estimado)
```
Líneas totales:        ~420 (-30 líneas, -7%)
Botones UI:            2 (2 líneas)
Inputs UI:             6 (12 líneas)
Alertas UI:            1 (1 línea)
Spinners UI:           2 (2 líneas)
Total código UI:       ~17 líneas
Reducción:             -62% de código en componentes
```

---

## 🔄 CAMBIOS DETALLADOS

### Cambio 1: Botón "Descubrir Impresoras"

**ANTES:**
```typescript
<button
  onClick={() => setIsDiscoveryOpen(true)}
  className="flex items-center gap-2 bg-ricoh-red text-white px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wide hover:bg-red-700 transition-colors"
>
  <Wifi size={14} />
  Descubrir Impresoras
</button>
```

**DESPUÉS:**
```typescript
<Button
  variant="primary"
  size="sm"
  icon={<Wifi size={14} />}
  onClick={() => setIsDiscoveryOpen(true)}
  className="rounded-full"
>
  Descubrir Impresoras
</Button>
```

**Beneficios:**
- ✅ 67% menos código (3 líneas → 1 línea efectiva)
- ✅ Estilos consistentes
- ✅ Más legible

### Cambio 2: Botón "Enviar Configuración"

**ANTES:**
```typescript
<button 
  onClick={handleProvision}
  disabled={isProvisioning || selectedPrinters.length === 0 || !userName.trim() || !userPin.trim() || !networkPassword.trim()}
  className="w-full bg-industrial-gray text-white py-3 text-xs font-bold uppercase tracking-widest hover:bg-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
>
  {isProvisioning ? (
    <>
      <Loader2 size={14} className="animate-spin" />
      Configurando...
    </>
  ) : (
    <>
      <Send size={14} />
      Enviar Configuración
    </>
  )}
</button>
```

**DESPUÉS:**
```typescript
<Button
  variant="secondary"
  size="md"
  icon={<Send size={14} />}
  loading={isProvisioning}
  disabled={isProvisioning || selectedPrinters.length === 0 || !userName.trim() || !userPin.trim() || !networkPassword.trim()}
  onClick={handleProvision}
  className="w-full py-3 tracking-widest"
>
  {isProvisioning ? 'Configurando...' : 'Enviar Configuración'}
</Button>
```

**Beneficios:**
- ✅ 70% menos código (15 líneas → 4 líneas)
- ✅ Loading automático con spinner
- ✅ Más mantenible

### Cambio 3: Inputs con Input Component

**ANTES (ejemplo):**
```typescript
<div className="space-y-1">
  <label className="text-[10px] font-bold text-slate-400 uppercase">Nombre Completo</label>
  <input 
    className="w-full border-b border-slate-200 py-1 focus:border-ricoh-red outline-none text-sm" 
    placeholder="Nombre del Usuario"
    value={userName}
    onChange={(e) => setUserName(e.target.value)}
  />
</div>
```

**DESPUÉS:**
```typescript
<Input
  label="Nombre Completo"
  placeholder="Nombre del Usuario"
  value={userName}
  onChange={(e) => setUserName(e.target.value)}
  variant="underline"
/>
```

**Beneficios:**
- ✅ 60% menos código (7 líneas → 3 líneas)
- ✅ Label integrado
- ✅ Estilos consistentes

### Cambio 4: Alert Component

**ANTES:**
```typescript
<div className="bg-amber-50 border-l-4 border-amber-400 p-3 mt-3">
  <p className="text-[10px] text-amber-800">
    <span className="font-bold">⚠️ Importante:</span> Habilita color en Copiadora/Impresora solo cuando sea necesario. La mayoría de usuarios solo necesitan B/N.
  </p>
</div>
```

**DESPUÉS:**
```typescript
<Alert variant="warning" className="mt-3">
  <span className="font-bold">⚠️ Importante:</span> Habilita color en Copiadora/Impresora solo cuando sea necesario. La mayoría de usuarios solo necesitan B/N.
</Alert>
```

**Beneficios:**
- ✅ 50% menos código (5 líneas → 2 líneas)
- ✅ Icono automático
- ✅ Estilos consistentes

### Cambio 5: Spinner Component

**ANTES:**
```typescript
<div className="col-span-full flex flex-col items-center justify-center py-16 text-slate-400">
  <Loader2 className="animate-spin mb-3" size={32} />
  <p className="text-sm">Cargando impresoras...</p>
</div>
```

**DESPUÉS:**
```typescript
<div className="col-span-full flex flex-col items-center justify-center py-16">
  <Spinner size="lg" text="Cargando impresoras..." />
</div>
```

**Beneficios:**
- ✅ 40% menos código (4 líneas → 2 líneas)
- ✅ Texto integrado
- ✅ Estilos consistentes

---

## ⚠️ PRECAUCIONES

### Antes de Cada Cambio
1. ✅ Hacer commit del estado actual
2. ✅ Crear branch para cambios
3. ✅ Probar que el módulo funciona

### Durante los Cambios
1. ✅ Cambiar UNO por UNO
2. ✅ Probar después de cada cambio
3. ✅ Verificar consola sin errores

### Después de los Cambios
1. ✅ Probar flujo completo
2. ✅ Verificar estilos visuales
3. ✅ Hacer commit descriptivo

---

## 📝 LOG DE CAMBIOS

### 2026-03-18 - Análisis Inicial
- ✅ Archivo analizado completamente
- ✅ Identificados 2 botones, 6 inputs, 1 alerta, 2 spinners
- ✅ Plan de refactorización creado
- ✅ Documentación generada

### Próximo: Refactorizar Botones
- [ ] Importar Button component
- [ ] Reemplazar botones
- [ ] Probar funcionalidad

---

**Estado actual:** 📋 Análisis completado, listo para refactorización  
**Próximo paso:** Refactorizar botones  
**Riesgo estimado:** 5% (cambios simples y graduales)
