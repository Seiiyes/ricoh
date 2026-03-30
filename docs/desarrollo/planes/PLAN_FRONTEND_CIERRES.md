# Plan de Implementación - Frontend de Cierres Mensuales

**Fecha:** 3 de Marzo de 2026  
**Estado Backend:** ✅ 100% completado  
**Estado Frontend:** ⏳ Pendiente

---

## 📋 Resumen

Este documento describe el plan de implementación del frontend para el módulo de cierres mensuales. El backend está completamente funcional con 5 endpoints API listos para consumir.

---

## 🎯 Objetivos

1. Crear interfaz visual para gestionar cierres mensuales
2. Mostrar calendario con estados de cierres
3. Permitir crear nuevos cierres con validaciones
4. Mostrar detalle de cierres con usuarios
5. Comparar cierres entre diferentes períodos

---

## 🏗️ Arquitectura de Componentes

```
src/components/contadores/cierres/
├── CierresView.tsx                    ⭐ Ya existe (estructura base)
├── CalendarioCierres.tsx              🆕 A crear
├── CierreModal.tsx                    🆕 A crear
├── CierreDetalleModal.tsx             🆕 A crear
├── ComparacionCierresModal.tsx        🆕 A crear
└── types.ts                           🆕 A crear
```

---

## 📦 Componentes a Implementar

### 1. CalendarioCierres.tsx

**Propósito:** Mostrar calendario visual con estados de cierres

**Props:**
```typescript
interface CalendarioCierresProps {
  printerId: number;
  year: number;
  cierres: CierreMensual[];
  onSelectCierre: (cierre: CierreMensual) => void;
  onCreateCierre: (mes: number) => void;
}
```

**Estados Visuales:**
- ✅ **Cerrado** - Verde, con ícono de check
- ⏳ **Pendiente** - Amarillo, con ícono de reloj
- ⚪ **Futuro** - Gris, deshabilitado
- ❌ **Falta** - Rojo, con ícono de alerta

**Funcionalidades:**
- Mostrar 12 meses del año
- Click en mes cerrado → Abrir detalle
- Click en mes pendiente → Abrir formulario de cierre
- Tooltip con información resumida
- Navegación entre años (← 2025 | 2026 →)

**API a consumir:**
```typescript
GET /api/counters/monthly?printer_id={id}&year={year}
```

---

### 2. CierreModal.tsx

**Propósito:** Formulario para crear nuevo cierre mensual

**Props:**
```typescript
interface CierreModalProps {
  printerId: number;
  year: number;
  month: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (cierre: CierreMensual) => void;
}
```

**Campos del Formulario:**
1. **Impresora** (readonly, pre-seleccionada)
2. **Período** (readonly, pre-seleccionado)
3. **Cerrado por** (input text, opcional)
4. **Notas** (textarea, opcional)

**Validaciones Frontend:**
- Impresora seleccionada
- Período válido
- Cerrado por: max 100 caracteres
- Notas: max 1000 caracteres

**Flujo:**
1. Usuario hace click en mes pendiente
2. Se abre modal con datos pre-cargados
3. Usuario completa campos opcionales
4. Click en "Cerrar Mes"
5. Loading mientras se procesa
6. Si éxito → Mostrar resumen y cerrar modal
7. Si error → Mostrar mensaje de error

**API a consumir:**
```typescript
POST /api/counters/monthly
Body: {
  printer_id: number,
  anio: number,
  mes: number,
  cerrado_por?: string,
  notas?: string
}
```

**Manejo de Errores:**
- Cierre duplicado → Mostrar info del cierre existente
- Mes futuro → "No se puede cerrar un mes futuro"
- Contador antiguo → "Ejecute una lectura manual primero"
- Secuencia rota → "Debe cerrar {mes} antes"
- Reset detectado → Mostrar mensaje detallado con acciones

---

### 3. CierreDetalleModal.tsx

**Propósito:** Mostrar detalle completo de un cierre con usuarios

**Props:**
```typescript
interface CierreDetalleModalProps {
  cierreId: number;
  isOpen: boolean;
  onClose: () => void;
}
```

**Secciones:**

#### A. Encabezado
- Impresora (hostname o IP)
- Período (Febrero 2026)
- Fecha de cierre (01/03/2026 10:30)
- Cerrado por (admin)

#### B. Resumen de Totales
```
┌─────────────────────────────────────────┐
│ TOTALES ACUMULADOS                      │
├─────────────────────────────────────────┤
│ Total páginas:     125,430              │
│ Total copiadora:    45,230              │
│ Total impresora:    78,200              │
│ Total escáner:       2,000              │
│ Total fax:               0              │
└─────────────────────────────────────────┘
```

#### C. Consumo del Mes
```
┌─────────────────────────────────────────┐
│ CONSUMO DEL MES                         │
├─────────────────────────────────────────┤
│ Diferencia total:     8,450             │
│ Diferencia copiadora: 3,200             │
│ Diferencia impresora: 5,100             │
│ Diferencia escáner:     150             │
│ Diferencia fax:           0             │
└─────────────────────────────────────────┘
```

#### D. Tabla de Usuarios
```
┌──────────┬────────────────────┬──────────┬────────────┬────────────┬──────────┐
│ Código   │ Nombre             │ Consumo  │ Copiadora  │ Impresora  │ Escáner  │
├──────────┼────────────────────┼──────────┼────────────┼────────────┼──────────┤
│ 00000252 │ Juan Pérez         │   1,250  │      600   │      630   │      20  │
│ 00000253 │ María García       │     850  │      400   │      430   │      20  │
│ ...      │ ...                │     ...  │      ...   │      ...   │     ...  │
└──────────┴────────────────────┴──────────┴────────────┴────────────┴──────────┘
```

**Funcionalidades:**
- Ordenar tabla por cualquier columna
- Buscar usuario por código o nombre
- Exportar a Excel
- Copiar hash de verificación
- Ver notas completas

**API a consumir:**
```typescript
GET /api/counters/monthly/{cierre_id}/detail
```

---

### 4. ComparacionCierresModal.tsx

**Propósito:** Comparar dos cierres lado a lado

**Props:**
```typescript
interface ComparacionCierresModalProps {
  printerId: number;
  isOpen: boolean;
  onClose: () => void;
}
```

**Flujo:**
1. Usuario selecciona primer cierre (dropdown)
2. Usuario selecciona segundo cierre (dropdown)
3. Se muestra comparación lado a lado

**Vista de Comparación:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    Febrero 2026  vs  Enero 2026                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Consumo Total:        8,450           7,200      (+1,250)  ↑   │
│ Consumo Copiadora:    3,200           2,800      (+  400)  ↑   │
│ Consumo Impresora:    5,100           4,300      (+  800)  ↑   │
│ Consumo Escáner:        150             100      (+   50)  ↑   │
│                                                                 │
│ Usuarios Activos:        45              42      (+    3)  ↑   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Gráficos:**
- Gráfico de barras comparativo
- Gráfico de línea de tendencia
- Top 10 usuarios con mayor cambio

**API a consumir:**
```typescript
GET /api/counters/monthly/{cierre_id_1}/detail
GET /api/counters/monthly/{cierre_id_2}/detail
```

---

### 5. types.ts

**Propósito:** Definir tipos TypeScript

```typescript
export interface CierreMensual {
  id: number;
  printer_id: number;
  anio: number;
  mes: number;
  total_paginas: number;
  total_copiadora: number;
  total_impresora: number;
  total_escaner: number;
  total_fax: number;
  diferencia_total: number;
  diferencia_copiadora: number;
  diferencia_impresora: number;
  diferencia_escaner: number;
  diferencia_fax: number;
  fecha_cierre: string;
  cerrado_por: string | null;
  notas: string | null;
  hash_verificacion: string | null;
  created_at: string;
}

export interface CierreMensualUsuario {
  id: number;
  cierre_mensual_id: number;
  codigo_usuario: string;
  nombre_usuario: string;
  total_paginas: number;
  total_bn: number;
  total_color: number;
  copiadora_bn: number;
  copiadora_color: number;
  impresora_bn: number;
  impresora_color: number;
  escaner_bn: number;
  escaner_color: number;
  fax_bn: number;
  consumo_total: number;
  consumo_copiadora: number;
  consumo_impresora: number;
  consumo_escaner: number;
  consumo_fax: number;
  created_at: string;
}

export interface CierreMensualDetalle extends CierreMensual {
  usuarios: CierreMensualUsuario[];
}

export enum EstadoCierre {
  CERRADO = 'cerrado',
  PENDIENTE = 'pendiente',
  FUTURO = 'futuro',
  FALTA = 'falta'
}
```

---

## 🔄 Actualización de CierresView.tsx

**Estado Actual:** Estructura base con mensaje temporal

**Cambios Necesarios:**

```typescript
import { useState, useEffect } from 'react';
import CalendarioCierres from './CalendarioCierres';
import CierreModal from './CierreModal';
import CierreDetalleModal from './CierreDetalleModal';
import ComparacionCierresModal from './ComparacionCierresModal';

export default function CierresView() {
  const [printerId, setPrinterId] = useState<number>(1);
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [cierres, setCierres] = useState<CierreMensual[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Modals
  const [cierreModalOpen, setCierreModalOpen] = useState(false);
  const [detalleModalOpen, setDetalleModalOpen] = useState(false);
  const [comparacionModalOpen, setComparacionModalOpen] = useState(false);
  
  // Selected data
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [selectedCierre, setSelectedCierre] = useState<CierreMensual | null>(null);
  
  useEffect(() => {
    loadCierres();
  }, [printerId, year]);
  
  const loadCierres = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/counters/monthly?printer_id=${printerId}&year=${year}`
      );
      const data = await response.json();
      setCierres(data);
    } catch (error) {
      console.error('Error loading cierres:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSelectCierre = (cierre: CierreMensual) => {
    setSelectedCierre(cierre);
    setDetalleModalOpen(true);
  };
  
  const handleCreateCierre = (mes: number) => {
    setSelectedMonth(mes);
    setCierreModalOpen(true);
  };
  
  const handleCierreSuccess = () => {
    loadCierres();
    setCierreModalOpen(false);
  };
  
  return (
    <div className="cierres-view">
      {/* Filtros */}
      <div className="filters">
        <select value={printerId} onChange={(e) => setPrinterId(Number(e.target.value))}>
          {/* Opciones de impresoras */}
        </select>
        
        <div className="year-navigation">
          <button onClick={() => setYear(year - 1)}>←</button>
          <span>{year}</span>
          <button onClick={() => setYear(year + 1)}>→</button>
        </div>
        
        <button onClick={() => setComparacionModalOpen(true)}>
          Comparar Cierres
        </button>
      </div>
      
      {/* Calendario */}
      {loading ? (
        <div>Cargando...</div>
      ) : (
        <CalendarioCierres
          printerId={printerId}
          year={year}
          cierres={cierres}
          onSelectCierre={handleSelectCierre}
          onCreateCierre={handleCreateCierre}
        />
      )}
      
      {/* Modals */}
      <CierreModal
        printerId={printerId}
        year={year}
        month={selectedMonth || 1}
        isOpen={cierreModalOpen}
        onClose={() => setCierreModalOpen(false)}
        onSuccess={handleCierreSuccess}
      />
      
      <CierreDetalleModal
        cierreId={selectedCierre?.id || 0}
        isOpen={detalleModalOpen}
        onClose={() => setDetalleModalOpen(false)}
      />
      
      <ComparacionCierresModal
        printerId={printerId}
        isOpen={comparacionModalOpen}
        onClose={() => setComparacionModalOpen(false)}
      />
    </div>
  );
}
```

---

## 🎨 Estilos y UX

### Colores de Estados

```css
.cierre-cerrado {
  background-color: #10b981; /* Verde */
  color: white;
}

.cierre-pendiente {
  background-color: #f59e0b; /* Amarillo */
  color: white;
}

.cierre-futuro {
  background-color: #6b7280; /* Gris */
  color: white;
  opacity: 0.5;
  cursor: not-allowed;
}

.cierre-falta {
  background-color: #ef4444; /* Rojo */
  color: white;
}
```

### Animaciones

- Hover en meses → Escala 1.05
- Click en mes → Pulse animation
- Loading → Spinner
- Success → Check animation
- Error → Shake animation

---

## 📊 Manejo de Estados

### Loading States

```typescript
const [loading, setLoading] = useState(false);
const [submitting, setSubmitting] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### Error Handling

```typescript
try {
  const response = await fetch(...);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  const data = await response.json();
  // Success
} catch (error) {
  setError(error.message);
  // Show error toast
}
```

---

## 🧪 Testing

### Tests a Implementar

1. **CalendarioCierres.test.tsx**
   - Renderiza 12 meses
   - Muestra estados correctos
   - Click en mes cerrado abre detalle
   - Click en mes pendiente abre formulario

2. **CierreModal.test.tsx**
   - Validación de campos
   - Submit exitoso
   - Manejo de errores
   - Cierre de modal

3. **CierreDetalleModal.test.tsx**
   - Carga datos correctamente
   - Muestra usuarios
   - Ordenamiento de tabla
   - Búsqueda de usuarios

4. **ComparacionCierresModal.test.tsx**
   - Selección de cierres
   - Cálculo de diferencias
   - Renderizado de gráficos

---

## 📦 Dependencias Necesarias

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "recharts": "^2.5.0",
    "date-fns": "^2.30.0",
    "xlsx": "^0.18.5"
  },
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.0",
    "@testing-library/user-event": "^14.5.0"
  }
}
```

---

## 🚀 Plan de Implementación

### Fase 1: Estructura Base (2-3 horas)
1. Crear `types.ts` con interfaces
2. Actualizar `CierresView.tsx` con estructura completa
3. Crear componente `CalendarioCierres.tsx` básico
4. Integrar con API de listado

### Fase 2: Formulario de Cierre (2-3 horas)
1. Crear `CierreModal.tsx`
2. Implementar validaciones
3. Integrar con API de creación
4. Manejo de errores

### Fase 3: Detalle de Cierre (3-4 horas)
1. Crear `CierreDetalleModal.tsx`
2. Implementar tabla de usuarios
3. Agregar búsqueda y ordenamiento
4. Implementar exportación a Excel

### Fase 4: Comparación (2-3 horas)
1. Crear `ComparacionCierresModal.tsx`
2. Implementar selección de cierres
3. Calcular diferencias
4. Agregar gráficos con Recharts

### Fase 5: Pulido y Testing (2-3 horas)
1. Agregar animaciones
2. Mejorar UX
3. Escribir tests
4. Documentar componentes

**Total estimado:** 11-16 horas

---

## ✅ Checklist de Implementación

### Componentes
- [ ] `types.ts` creado
- [ ] `CalendarioCierres.tsx` implementado
- [ ] `CierreModal.tsx` implementado
- [ ] `CierreDetalleModal.tsx` implementado
- [ ] `ComparacionCierresModal.tsx` implementado
- [ ] `CierresView.tsx` actualizado

### Funcionalidades
- [ ] Listar cierres por impresora y año
- [ ] Mostrar calendario con estados
- [ ] Crear nuevo cierre
- [ ] Ver detalle de cierre
- [ ] Comparar dos cierres
- [ ] Exportar a Excel
- [ ] Búsqueda de usuarios
- [ ] Ordenamiento de tabla

### Integración API
- [ ] GET /api/counters/monthly
- [ ] POST /api/counters/monthly
- [ ] GET /api/counters/monthly/{cierre_id}/detail
- [ ] Manejo de errores
- [ ] Loading states

### Testing
- [ ] Tests de CalendarioCierres
- [ ] Tests de CierreModal
- [ ] Tests de CierreDetalleModal
- [ ] Tests de ComparacionCierresModal

### Documentación
- [ ] Comentarios en código
- [ ] README de componentes
- [ ] Guía de uso

---

## 📞 Soporte

Para dudas durante la implementación:

1. Revisar `docs/API_CIERRES_MENSUALES.md` para detalles de API
2. Revisar `docs/DISENO_UI_CIERRES.md` para diseño de interfaz
3. Probar endpoints con `backend/test_cierre_mensual.py`
4. Consultar ejemplos en componentes existentes

---

**Próximo paso:** Comenzar con Fase 1 - Estructura Base
