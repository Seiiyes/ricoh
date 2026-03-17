# Verificación de Cálculos de Cierres

## Fecha: 2026-03-16

---

## ✅ Backend - Cálculos Correctos

### Prueba Realizada:

```bash
curl http://localhost:8000/api/counters/monthly/compare/210/208
```

### Resultados:

**Cierres:**
- Cierre 1 (ID: 210 - Febrero 2026): 1,010,592 páginas
- Cierre 2 (ID: 208 - Marzo 2026): 1,029,844 páginas
- Diferencia Total: 19,252 páginas ✅

**Usuario Ejemplo (SONIA CORTES - 3581):**
- Consumo Cierre 1: 48,887 páginas ✅
- Consumo Cierre 2: 52,623 páginas ✅
- Diferencia: 3,736 páginas ✅

**Información de Impresora:**
- ID: 6
- Hostname: RNP002673721B98
- has_color: False ✅
- has_scanner: True
- has_fax: False

---

## ❌ Frontend - Problema Identificado

### Lo que se ve en la pantalla:

**Usuario SONIA CORTES (3581):**
- Período Base Total: 48,847 (❌ debería ser 48,887)
- Período Comparado Total: 0 (❌ debería ser 52,623)
- Consumo Total: +3,736 (✅ correcto, pero no tiene sentido si el comparado es 0)

### Posibles Causas:

1. **Problema de Mapeo de Datos:**
   - Los datos del backend están correctos
   - El frontend no está mapeando correctamente `consumo_cierre1` y `consumo_cierre2`
   - Puede estar usando campos incorrectos

2. **Problema de Caché:**
   - El navegador puede tener datos en caché
   - Necesita hacer hard refresh (Ctrl+Shift+R)

3. **Problema de Orden:**
   - Los cierres pueden estar invertidos en el frontend
   - El cierre1 y cierre2 pueden estar al revés

---

## 🔍 Diagnóstico

### Verificar en Consola del Navegador:

Abrir DevTools (F12) y ejecutar en Console:

```javascript
// Ver qué datos está recibiendo el componente
console.log('Comparacion:', comparacion);
console.log('Primer usuario:', comparacion?.top_usuarios_aumento[0]);
```

### Verificar Network Tab:

1. Abrir DevTools → Network
2. Hacer la comparación
3. Buscar la petición a `/api/counters/monthly/compare/...`
4. Ver la respuesta JSON
5. Verificar que los datos son correctos

---

## 🛠️ Soluciones

### Solución 1: Hard Refresh del Navegador

```
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)
```

### Solución 2: Limpiar Caché del Navegador

1. DevTools → Application → Storage
2. Click en "Clear site data"
3. Recargar la página

### Solución 3: Verificar Código Frontend

El código en `ComparacionPage.tsx` línea 367 muestra:

```typescript
<td className="px-3 py-3 text-xs text-right text-gray-900 font-semibold border-l-2 border-gray-300 bg-gray-50/50">
  {fmt(u.consumo_cierre1)}
</td>
```

Esto debería estar mostrando el valor correcto. Si no lo hace, puede ser que:
- `u.consumo_cierre1` no existe en el objeto
- El objeto `u` no tiene la estructura esperada
- Hay un problema con el mapeo en `allUsers`

### Solución 4: Verificar Mapeo de Datos

En `ComparacionPage.tsx` línea 70-90, el código mapea los usuarios:

```typescript
const allUsers = useMemo(() => {
  if (!comparacion) return [];
  const raw = [...comparacion.top_usuarios_aumento, ...comparacion.top_usuarios_disminucion];
  
  const filtered = raw.filter(u =>
    u.nombre_usuario.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.codigo_usuario.includes(searchTerm)
  ).map(u => ({
    ...u,
    difCopia: (u.consumo_copiadora_cierre2 || 0) - (u.consumo_copiadora_cierre1 || 0),
    // ... más campos
  }));
  
  return filtered;
}, [comparacion, searchTerm, sortKey, sortDir]);
```

El problema puede estar aquí. Los datos originales de `comparacion.top_usuarios_aumento` ya tienen `consumo_cierre1` y `consumo_cierre2`, así que el mapeo debería preservarlos con `...u`.

---

## 🎯 Acción Inmediata

### Paso 1: Verificar en Consola

Abre la consola del navegador y ejecuta:

```javascript
// Copiar y pegar en la consola cuando estés en la página de comparación
const checkData = () => {
  const comparacion = window.__REACT_DEVTOOLS_GLOBAL_HOOK__?.renderers?.get(1)?.getCurrentFiber()?.return?.memoizedState?.memoizedState;
  console.log('Comparacion:', comparacion);
  if (comparacion?.top_usuarios_aumento?.[0]) {
    const user = comparacion.top_usuarios_aumento[0];
    console.log('Primer usuario:', {
      codigo: user.codigo_usuario,
      nombre: user.nombre_usuario,
      consumo_cierre1: user.consumo_cierre1,
      consumo_cierre2: user.consumo_cierre2,
      diferencia: user.diferencia
    });
  }
};
checkData();
```

### Paso 2: Verificar Network

1. F12 → Network tab
2. Hacer la comparación de nuevo
3. Buscar la petición que empieza con `compare`
4. Click en ella → Preview tab
5. Expandir `top_usuarios_aumento` → `0`
6. Verificar que `consumo_cierre1` y `consumo_cierre2` tienen valores correctos

### Paso 3: Si los datos son correctos en Network pero incorrectos en pantalla

Entonces el problema está en el frontend. Necesitamos:
1. Agregar console.log en `ComparacionPage.tsx` para ver qué está pasando
2. Verificar que el mapeo de `allUsers` está preservando los campos correctamente

---

## 📝 Notas Adicionales

- El backend está funcionando correctamente ✅
- Los cálculos son precisos ✅
- La información de la impresora (has_color: false) está disponible ✅
- El problema está en el frontend, probablemente en el mapeo o visualización de datos

---

## 🚀 Próximos Pasos

1. Hacer hard refresh del navegador (Ctrl+Shift+R)
2. Verificar en Network tab que los datos llegan correctos
3. Si los datos llegan correctos pero se muestran mal, revisar el código de mapeo en `allUsers`
4. Agregar console.log para debuggear

Si después de hacer hard refresh sigue mostrando mal, necesitamos agregar logs de debug al código del frontend.
