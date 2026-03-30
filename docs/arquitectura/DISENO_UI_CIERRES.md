# 🎨 DISEÑO DE INTERFAZ: Módulo de Cierres

## 📐 ESTRUCTURA DE NAVEGACIÓN

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 CONTADORES                                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Dashboard] [Cierres]                                       │
│  ─────────── ────────                                        │
│                                                               │
│  ... contenido ...                                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Pestañas del Módulo

1. **Dashboard** (existente)
   - Lista de impresoras
   - Contadores actuales
   - Lectura manual

2. **Cierres** (NUEVO)
   - Vista de cierres por impresora
   - Calendario de cierres
   - Comparación de períodos
   - Formulario de cierre

---

## 🎯 VISTA 1: Dashboard de Cierres

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 CONTADORES                                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Dashboard] [Cierres]                                       │
│              ────────                                        │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🔍 Filtros                                           │   │
│  │                                                       │   │
│  │ Impresora: [Todas ▼]  Año: [2026 ▼]  Tipo: [Mensual ▼] │
│  │                                                       │   │
│  │ [🔄 Actualizar]                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📅 Impresora 251 - Oficina Principal                │   │
│  │ ─────────────────────────────────────────────────── │   │
│  │                                                       │   │
│  │ 2026                                                  │   │
│  │ ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐ │   │
│  │ │Ene │Feb │Mar │Abr │May │Jun │Jul │Ago │Sep │Oct │ │   │
│  │ ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤ │   │
│  │ │ ✅ │ ✅ │ ⏳ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ │   │
│  │ │4.8K│4.5K│ -- │ -- │ -- │ -- │ -- │ -- │ -- │ -- │ │   │
│  │ └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘ │   │
│  │                                                       │   │
│  │ Último cierre: Febrero 2026 (hace 5 días)           │   │
│  │ Consumo Feb: 4,523 páginas                          │   │
│  │                                                       │   │
│  │ [Ver Detalles] [Cerrar Marzo]                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📅 Impresora 252 - Sala de Juntas                   │   │
│  │ ─────────────────────────────────────────────────── │   │
│  │                                                       │   │
│  │ 2026                                                  │   │
│  │ ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐ │   │
│  │ │Ene │Feb │Mar │Abr │May │Jun │Jul │Ago │Sep │Oct │ │   │
│  │ ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤ │   │
│  │ │ ✅ │ ✅ │ ✅ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ │   │
│  │ │3.1K│3.0K│3.2K│ -- │ -- │ -- │ -- │ -- │ -- │ -- │ │   │
│  │ └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘ │   │
│  │                                                       │   │
│  │ Último cierre: Marzo 2026 (hace 2 días)             │   │
│  │ Consumo Mar: 3,127 páginas                          │   │
│  │                                                       │   │
│  │ [Ver Detalles]                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Leyenda:
✅ Cerrado    ⏳ Pendiente (mes actual)    ⚪ Futuro    ❌ Falta cierre
```

---

## 🎯 VISTA 2: Comparación de Cierres

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Comparación de Cierres                          [X]      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Impresora: 251 - Oficina Principal                         │
│  Período: Enero - Marzo 2026                                │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📊 Gráfico de Consumo                               │   │
│  │                                                       │   │
│  │     5K ┤                                             │   │
│  │        │     ╭─╮                                     │   │
│  │     4K ┤     │ │     ╭─╮                             │   │
│  │        │     │ │     │ │                             │   │
│  │     3K ┤ ╭─╮ │ │     │ │                             │   │
│  │        │ │ │ │ │     │ │                             │   │
│  │     2K ┤ │ │ │ │     │ │                             │   │
│  │        │ │ │ │ │     │ │                             │   │
│  │     1K ┤ │ │ │ │     │ │                             │   │
│  │        │ │ │ │ │     │ │                             │   │
│  │      0 └─┴─┴─┴─┴─────┴─┴─────────────────────────   │   │
│  │         Ene  Feb  Mar                                │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📋 Tabla Comparativa                                 │   │
│  │                                                       │   │
│  │ ┌──────┬────────┬────────┬────────┬──────────┐      │   │
│  │ │ Mes  │ Total  │ Copiad.│ Impres.│ Variación│      │   │
│  │ ├──────┼────────┼────────┼────────┼──────────┤      │   │
│  │ │ Ene  │ 3,200  │   500  │ 2,700  │    --    │      │   │
│  │ │ Feb  │ 4,523  │   550  │ 3,973  │  +41.3%  │      │   │
│  │ │ Mar  │ 4,800  │   500  │ 4,300  │   +6.1%  │      │   │
│  │ └──────┴────────┴────────┴────────┴──────────┘      │   │
│  │                                                       │   │
│  │ Promedio mensual: 4,174 páginas                     │   │
│  │ Tendencia: ↗️ Creciente (+25% vs Enero)             │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [Exportar Excel] [Exportar PDF] [Cerrar]                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 VISTA 3: Detalle de Cierre con Usuarios

```
┌─────────────────────────────────────────────────────────────┐
│ 📋 Cierre: Marzo 2026                              [X]      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Impresora: 251 - Oficina Principal                         │
│  Fecha de cierre: 31/03/2026 23:45                          │
│  Cerrado por: admin                                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📊 Resumen del Cierre                               │   │
│  │                                                       │   │
│  │ ┌───────────────────────────────────────────────┐   │   │
│  │ │              Al Cierre   Feb 2026    Consumo  │   │   │
│  │ ├───────────────────────────────────────────────┤   │   │
│  │ │ Total        372,600    367,800     +4,800    │   │   │
│  │ │ Copiadora     59,200     58,700       +500    │   │   │
│  │ │ Impresora    313,100    308,900     +4,200    │   │   │
│  │ │ Escáner      170,300    170,000       +300    │   │   │
│  │ │ Fax               0          0          0     │   │   │
│  │ └───────────────────────────────────────────────┘   │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 👥 Usuarios del Mes (265 usuarios)                  │   │
│  │                                                       │   │
│  │ 🔍 Buscar: [                    ] [Buscar]          │   │
│  │                                                       │   │
│  │ ┌─────────────────────────────────────────────────┐ │   │
│  │ │ Usuario          │ Código │ Consumo │ % Total  │ │   │
│  │ ├──────────────────┼────────┼─────────┼──────────┤ │   │
│  │ │ SANDRA GARCIA    │  9967  │  1,245  │  25.9%   │ │   │
│  │ │ JUAN PEREZ       │  1234  │    987  │  20.6%   │ │   │
│  │ │ MARIA LOPEZ      │  5678  │    856  │  17.8%   │ │   │
│  │ │ CARLOS RUIZ      │  9012  │    723  │  15.1%   │ │   │
│  │ │ ANA MARTINEZ     │  3456  │    612  │  12.7%   │ │   │
│  │ │ ...              │  ...   │   ...   │   ...    │ │   │
│  │ └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  │ [◀ Anterior] Página 1 de 27 [Siguiente ▶]           │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Notas: Cierre mensual de marzo 2026                        │
│                                                               │
│  [Exportar PDF] [Exportar Excel] [Cerrar]                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 VISTA 4: Formulario de Cierre

```
┌─────────────────────────────────────────────────────────────┐
│ 🔒 Cerrar Mes: Marzo 2026                          [X]      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Impresora: 251 - Oficina Principal                         │
│  IP: 192.168.91.251                                          │
│                                                               │
│  ⚠️ IMPORTANTE: El cierre mensual es irreversible           │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📊 Validaciones Previas                             │   │
│  │                                                       │   │
│  │ ✅ Último contador: 03/03/2026 10:45 (hace 3 horas) │   │
│  │ ✅ Cierre anterior: Febrero 2026 (completado)       │   │
│  │ ✅ Usuarios registrados: 265                         │   │
│  │ ✅ Datos consistentes                                │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📊 Resumen de Contadores                            │   │
│  │                                                       │   │
│  │ ┌───────────────────────────────────────────────┐   │   │
│  │ │              Actual    Feb 2026    Consumo    │   │   │
│  │ ├───────────────────────────────────────────────┤   │   │
│  │ │ Total        372,600   367,800     +4,800     │   │   │
│  │ │ Copiadora     59,200    58,700       +500     │   │   │
│  │ │ Impresora    313,100   308,900     +4,200     │   │   │
│  │ │ Escáner      170,300   170,000       +300     │   │   │
│  │ │ Fax               0         0          0      │   │   │
│  │ └───────────────────────────────────────────────┘   │   │
│  │                                                       │   │
│  │ 👥 Usuarios activos: 265                             │   │
│  │ 📄 Páginas por usuario (promedio): 18               │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📝 Información del Cierre                            │   │
│  │                                                       │   │
│  │ Cerrado por: [admin                              ]   │   │
│  │                                                       │   │
│  │ Notas (opcional):                                    │   │
│  │ ┌─────────────────────────────────────────────────┐ │   │
│  │ │ Cierre mensual de marzo 2026                    │ │   │
│  │ │                                                   │ │   │
│  │ └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ☑️ Confirmo que los datos son correctos                    │
│                                                               │
│  [Cancelar]                    [🔒 Cerrar Mes de Marzo]     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 VISTA 5: Cierres Diarios (Opcional - Futuro)

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 CONTADORES                                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Dashboard] [Cierres]                                       │
│              ────────                                        │
│                                                               │
│  Tipo de cierre: [Mensual ▼] [Diario ▼]                    │
│                  ────────                                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📅 Cierres Diarios - Marzo 2026                     │   │
│  │ Impresora: 251 - Oficina Principal                  │   │
│  │                                                       │   │
│  │ ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐ │   │
│  │ │ 01 │ 02 │ 03 │ 04 │ 05 │ 06 │ 07 │ 08 │ 09 │ 10 │ │   │
│  │ ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤ │   │
│  │ │ ✅ │ ✅ │ ✅ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ ⚪ │ │   │
│  │ │150 │165 │148 │ -- │ -- │ -- │ -- │ -- │ -- │ -- │ │   │
│  │ └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘ │   │
│  │                                                       │   │
│  │ Promedio diario: 154 páginas                        │   │
│  │ Total del mes (hasta hoy): 463 páginas              │   │
│  │                                                       │   │
│  │ [Ver Detalles] [Cerrar Día]                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 COMPONENTES A CREAR

### 1. CierresView.tsx (Principal)
```typescript
interface CierresViewProps {
  // Props si es necesario
}

export const CierresView: React.FC<CierresViewProps> = () => {
  const [selectedYear, setSelectedYear] = useState(2026);
  const [selectedPrinter, setSelectedPrinter] = useState<number | null>(null);
  const [tipoCierre, setTipoCierre] = useState<'mensual' | 'diario'>('mensual');
  
  return (
    <div>
      {/* Filtros */}
      {/* Lista de impresoras con calendarios */}
      {/* Botones de acción */}
    </div>
  );
};
```

### 2. CalendarioCierres.tsx
```typescript
interface CalendarioCierresProps {
  printer: Printer;
  year: number;
  cierres: CierreMensual[];
  onVerDetalle: (cierre: CierreMensual) => void;
  onCerrarMes: (mes: number) => void;
}
```

### 3. CierreModal.tsx
```typescript
interface CierreModalProps {
  printer: Printer;
  year: number;
  month: number;
  onClose: () => void;
  onSuccess: () => void;
}
```

### 4. CierreDetalleModal.tsx
```typescript
interface CierreDetalleModalProps {
  cierre: CierreMensual;
  onClose: () => void;
}
```

### 5. ComparacionCierresModal.tsx
```typescript
interface ComparacionCierresModalProps {
  printer: Printer;
  cierres: CierreMensual[];
  onClose: () => void;
}
```

---

## 🎨 PALETA DE COLORES

```css
/* Estados de cierre */
.cierre-completado { background: #10b981; } /* Verde */
.cierre-pendiente { background: #f59e0b; }  /* Amarillo */
.cierre-futuro { background: #6b7280; }     /* Gris */
.cierre-faltante { background: #ef4444; }   /* Rojo */

/* Variaciones */
.consumo-alto { color: #ef4444; }      /* Rojo */
.consumo-normal { color: #10b981; }    /* Verde */
.consumo-bajo { color: #3b82f6; }      /* Azul */
```

---

## 📊 FLUJO DE NAVEGACIÓN

```
Dashboard de Contadores
    │
    ├─→ [Pestaña Dashboard]
    │       └─→ Lista de impresoras
    │           └─→ Ver detalle de impresora
    │
    └─→ [Pestaña Cierres]
            ├─→ Vista de cierres mensuales
            │   ├─→ Ver detalle de cierre
            │   │   └─→ Ver usuarios del cierre
            │   ├─→ Comparar cierres
            │   └─→ Cerrar mes
            │       └─→ Formulario de cierre
            │           └─→ Confirmación
            │
            └─→ Vista de cierres diarios (futuro)
                ├─→ Ver detalle de día
                └─→ Cerrar día
```

---

## ✅ PRIORIDADES DE IMPLEMENTACIÓN

### Fase 1 (Ahora)
1. ✅ CierresView con filtros
2. ✅ CalendarioCierres mensual
3. ✅ CierreModal (formulario)
4. ✅ CierreDetalleModal (ver cierre)

### Fase 2 (Después)
5. ⏳ ComparacionCierresModal
6. ⏳ Gráficos de tendencias
7. ⏳ Exportación a Excel/PDF

### Fase 3 (Futuro)
8. 🔮 Cierres diarios
9. 🔮 Alertas automáticas
10. 🔮 Reportes avanzados

---

## 🚀 SIGUIENTE PASO

Implementar la estructura base del módulo de cierres con las pestañas y la vista principal.
