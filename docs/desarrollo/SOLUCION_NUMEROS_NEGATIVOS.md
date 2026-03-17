# Solución: Números Negativos en Comparación de Cierres

## Problema Identificado

El usuario reportó números negativos al comparar cierres de la impresora con IP terminada en `.253` (W533L900719, ID: 6).

## Causa Raíz

El problema tenía dos causas:

### 1. Orden Incorrecto de Comparación

El frontend estaba inicializando los selectores en orden inverso:
- **Período Base**: Cierre más reciente (marzo)
- **Período Comparado**: Cierre más antiguo (febrero)

Esto causaba que los usuarios nuevos en marzo mostraran diferencias negativas:
- Base (marzo): Usuario existe con X páginas
- Comparado (febrero): Usuario NO existe (0 páginas)
- **Diferencia**: 0 - X = **-X (NEGATIVO)**

### 2. Falta de Claridad Visual

Los selectores no indicaban claramente:
- Qué impresora se estaba comparando
- Cuál período debía ser el más antiguo (base)
- Cuál período debía ser el más reciente (comparado)

## Datos Verificados

### Impresora W533L900719 (IP .253)
- **ID**: 6
- **Serial**: W533L900719
- **IP**: 192.168.91.253

### Cierres Disponibles
1. **Febrero 2026**: Cierre 242 (89 usuarios, 1,010,592 páginas)
2. **Marzo 2026**: Cierre 35 (187 usuarios, 1,027,399 páginas)
3. Otros cierres de marzo...

### Usuarios Nuevos en Marzo
- **Total**: 98 usuarios nuevos que no existían en febrero
- Estos usuarios causaban las diferencias negativas cuando se comparaba en orden inverso

## Solución Implementada

### 1. Corrección del Orden de Inicialización

```typescript
useEffect(() => {
  // Ordenar cierres por fecha (más antiguo primero)
  const cierresOrdenados = [...cierres].sort((a, b) => 
    new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime()
  );
  // Cierre1 = más antiguo (base), Cierre2 = más reciente (comparado)
  if (cierresOrdenados.length >= 2) { 
    setCierre1Id(cierresOrdenados[0].id); 
    setCierre2Id(cierresOrdenados[1].id); 
  }
}, [cierres]);
```

### 2. Mejoras Visuales

#### a) Información de la Impresora
Se agregó un banner que muestra qué impresora se está comparando:
```tsx
{comparacion?.printer && (
  <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
    <div className="flex items-center gap-2 text-sm">
      <span className="font-medium text-blue-900">Impresora:</span>
      <span className="text-blue-700">{comparacion.printer.hostname}</span>
    </div>
  </div>
)}
```

#### b) Labels Más Claros
- **Antes**: "Período Base (Inicial)" y "Período a Comparar (Final)"
- **Después**: "Período Base (Inicial - Más Antiguo)" y "Período a Comparar (Final - Más Reciente)"

#### c) Ordenamiento de Selectores
Los cierres en ambos selectores ahora se muestran ordenados cronológicamente (más antiguo primero):
```typescript
{[...cierres].sort((a, b) => 
  new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime()
).map(c => <option key={c.id} value={c.id}>...</option>)}
```

## Resultado Esperado

Ahora al comparar febrero → marzo:
- **Base (febrero)**: Usuario NO existe (0 páginas)
- **Comparado (marzo)**: Usuario existe con X páginas
- **Diferencia**: X - 0 = **+X (POSITIVO)** ✓

Los números negativos solo aparecerán en casos legítimos:
- Correcciones de contadores
- Usuarios que redujeron su consumo
- Reseteos de contadores

## Archivos Modificados

- `src/components/contadores/cierres/ComparacionPage.tsx`

## Archivos de Verificación Creados

- `backend/analizar_negativos_w533.py`
- `backend/analizar_comparacion_febrero_w533.py`
- `backend/verificar_usuarios_marzo_w533.py`
- `backend/verificar_problema_comparacion.py`
- `backend/verificar_impresora_253.py`
