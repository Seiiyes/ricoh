# 🎨 DISEÑO UI MEJORADO: Comparación de Cierres Mensuales

## 📋 ANÁLISIS DE FORMATO REAL

Basado en los CSV reales de las impresoras, el formato de comparación debe mostrar:

### Formato de Comparación por Impresora
```
Código de impresora | Mes | Total de impresiones
──────────────────────────────────────────────────
W533L900719         | ENERO   | 988,587
W533L900719         | FEBRERO | 1,010,592
                    | CONSUMO | 22,005 (B/N: 21,985 | Color: 20)
```

### Formato de Comparación por Usuario (Detalle)
```
Usuario | Nombre              | B/N   | COLOR | TOTAL
────────────────────────────────────────────────────────
[3905]  | ADRIANA VARGAS     | 275   | 0     | 275
[4576]  | INGRID FANDIÑO     | 114   | 0     | 114
[5527]  | CATALINA AMEZQUITA | 0     | 34    | 34
```

---

## 🎯 VISTA MEJORADA: Comparación de Cierres

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 Comparación de Cierres Mensuales                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Impresora: E174M210096 - 2DO PISO ELITE BOYACA REAL                │
│  Período: Enero - Febrero 2026                                       │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 📈 RESUMEN GENERAL                                             │ │
│  │                                                                 │ │
│  │  ┌──────────┬─────────────┬─────────────┬──────────────────┐  │ │
│  │  │   Mes    │    Total    │   Anterior  │     Consumo      │  │ │
│  │  ├──────────┼─────────────┼─────────────┼──────────────────┤  │ │
│  │  │  ENERO   │   439,150   │      --     │       --         │  │ │
│  │  │  FEBRERO │   451,657   │   439,150   │    12,507        │  │ │
│  │  └──────────┴─────────────┴─────────────┴──────────────────┘  │ │
│  │                                                                 │ │
│  │  Desglose del consumo:                                         │ │
│  │  • Blanco y Negro: 12,503 páginas                             │ │
│  │  • Color: 4 páginas                                            │ │
│  │                                                                 │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 👥 CONSUMO POR USUARIO (Febrero 2026)                         │ │
│  │                                                                 │ │
│  │  Mostrando usuarios con consumo > 0                           │ │
│  │                                                                 │ │
│  │  🔍 Buscar: [                    ] [🔄 Actualizar]            │ │
│  │                                                                 │ │
│  │  ┌────────┬──────────────────────┬────────┬────────┬────────┐ │ │
│  │  │ Código │       Nombre         │  B/N   │ Color  │ Total  │ │ │
│  │  ├────────┼──────────────────────┼────────┼────────┼────────┤ │ │
│  │  │ 2788   │ NAYIB TORRES         │ 3,099  │    0   │ 3,099  │ │ │
│  │  │ 9130   │ MARIA CARRIZOSA      │ 1,393  │    0   │ 1,393  │ │ │
│  │  │ 0535   │ LILIANA PRADA        │ 1,200  │    0   │ 1,200  │ │ │
│  │  │ 3222   │ CLAUDIA PERALTA      │ 1,153  │    0   │ 1,153  │ │ │
│  │  │ 6793   │ MONICA PEÑA          │ 1,022  │    0   │ 1,022  │ │ │
│  │  │ 8756   │ MILDRED VERGARA      │   784  │    0   │   784  │ │ │
│  │  │ 8968   │ DAYANA MARISELLA     │   783  │    0   │   783  │ │ │
│  │  │ 5594   │ MARTHA CORREDOR      │   489  │    0   │   489  │ │ │
│  │  │ 1061   │ JESSICA GUZMAN       │   384  │    0   │   384  │ │ │
│  │  │ 3182   │ JHIMALLY ORTIZ       │   351  │    0   │   351  │ │ │
│  │  │ ...    │ ...                  │  ...   │  ...   │  ...   │ │ │
│  │  └────────┴──────────────────────┴────────┴────────┴────────┘ │ │
│  │                                                                 │ │
│  │  Total usuarios: 842 (160 con consumo, 682 sin consumo)       │ │
│  │  [◀ Anterior] Página 1 de 16 [Siguiente ▶]                    │ │
│  │                                                                 │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  [📥 Exportar Excel] [📄 Exportar PDF] [✖ Cerrar]                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 VISTA MEJORADA: Comparación Multi-Período

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 Comparación Multi-Período                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Impresora: W533L900719 - 3ER PISO ELITE BOYACA REAL B/N            │
│  Período: Diciembre 2025 - Febrero 2026                             │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 📈 EVOLUCIÓN DE CONTADORES                                     │ │
│  │                                                                 │ │
│  │  ┌───────────┬─────────────┬─────────────┬──────────────────┐ │ │
│  │  │    Mes    │    Total    │   Anterior  │     Consumo      │ │ │
│  │  ├───────────┼─────────────┼─────────────┼──────────────────┤ │ │
│  │  │ DICIEMBRE │   967,499   │      --     │       --         │ │ │
│  │  │   ENERO   │   988,587   │   967,499   │    21,088        │ │ │
│  │  │  FEBRERO  │ 1,010,592   │   988,587   │    22,005        │ │ │
│  │  └───────────┴─────────────┴─────────────┴──────────────────┘ │ │
│  │                                                                 │ │
│  │  Desglose por período:                                         │ │
│  │                                                                 │ │
│  │  Enero 2026:                                                   │ │
│  │  • Blanco y Negro: 21,068 páginas                             │ │
│  │  • Color: 20 páginas                                           │ │
│  │                                                                 │ │
│  │  Febrero 2026:                                                 │ │
│  │  • Blanco y Negro: 21,985 páginas                             │ │
│  │  • Color: 20 páginas                                           │ │
│  │                                                                 │ │
│  │  Promedio mensual: 21,547 páginas                             │ │
│  │  Tendencia: → Estable (+4.4% vs Enero)                        │ │
│  │                                                                 │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 📊 GRÁFICO DE TENDENCIA                                        │ │
│  │                                                                 │ │
│  │  23K ┤                                     ●                   │ │
│  │      │                                                          │ │
│  │  22K ┤                         ●                               │ │
│  │      │                                                          │ │
│  │  21K ┤             ●                                           │ │
│  │      │                                                          │ │
│  │  20K ┤                                                          │ │
│  │      └─────────────────────────────────────────────────────    │ │
│  │       DIC 2025      ENE 2026      FEB 2026                     │ │
│  │                                                                 │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  [📥 Exportar Excel] [📄 Exportar PDF] [✖ Cerrar]                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 FORMATO DE EXPORTACIÓN A EXCEL

### Hoja 1: COMPARATIVO FINAL
```
┌────────────────────┬──────────┬────────────────────┐
│ Codigo de impresora│   Mes    │ Total de impresiones│
├────────────────────┼──────────┼────────────────────┤
│ W533L900719        │  ENERO   │      988,587       │
│ W533L900719        │  FEBRERO │    1,010,592       │
│                    │ CONSUMO  │       22,005       │
│                    │          │ B/N: 21,985        │
│                    │          │ Color: 20          │
└────────────────────┴──────────┴────────────────────┘
```

### Hoja 2: DETALLE POR USUARIO (E174M210096)
```
┌─────────┬──────────────────────┬────────┬────────┬────────┐
│ Usuario │       Nombre         │  B/N   │ COLOR  │ TOTAL  │
├─────────┼──────────────────────┼────────┼────────┼────────┤
│ [0116]  │ JULIAN DE LA OS      │    0   │    0   │    0   │
│ [9735]  │ INEFRAY MENDOZA      │    0   │    0   │    0   │
│ [3905]  │ ADRIANA VARGAS       │  275   │    0   │  275   │
│ [4576]  │ INGRID FANDIÑO       │  114   │    0   │  114   │
│ [5527]  │ CATALINA AMEZQUITA   │    0   │   34   │   34   │
│ ...     │ ...                  │  ...   │  ...   │  ...   │
├─────────┼──────────────────────┼────────┼────────┼────────┤
│         │ TOTAL                │ 12,503 │    4   │ 12,507 │
└─────────┴──────────────────────┴────────┴────────┴────────┘
```

---

## 🎨 PALETA DE COLORES MEJORADA (Más Limpia)

```css
/* Fondo y contenedores */
.bg-primary { background: #ffffff; }
.bg-secondary { background: #f9fafb; }
.border-color { border-color: #e5e7eb; }

/* Texto */
.text-primary { color: #111827; }
.text-secondary { color: #6b7280; }
.text-muted { color: #9ca3af; }

/* Acentos sutiles */
.accent-blue { color: #3b82f6; }
.accent-green { color: #10b981; }
.accent-orange { color: #f59e0b; }

/* Estados (más sutiles) */
.status-success { 
  background: #d1fae5; 
  color: #065f46; 
  border: 1px solid #10b981;
}

.status-warning { 
  background: #fef3c7; 
  color: #92400e; 
  border: 1px solid #f59e0b;
}

.status-info { 
  background: #dbeafe; 
  color: #1e40af; 
  border: 1px solid #3b82f6;
}

/* Tablas */
.table-header { 
  background: #f3f4f6; 
  font-weight: 600;
  color: #374151;
}

.table-row:hover { 
  background: #f9fafb; 
}

.table-border { 
  border: 1px solid #e5e7eb; 
}
```

---

## 📊 COMPONENTES REACT MEJORADOS

### 1. ComparacionCierresModal.tsx (Mejorado)

```typescript
interface ComparacionCierresModalProps {
  printer: Printer;
  cierres: CierreMensual[];
  onClose: () => void;
}

export const ComparacionCierresModal: React.FC<ComparacionCierresModalProps> = ({
  printer,
  cierres,
  onClose
}) => {
  const [mostrarSoloConConsumo, setMostrarSoloConConsumo] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [paginaActual, setPaginaActual] = useState(1);
  const usuariosPorPagina = 10;

  // Calcular consumo entre períodos
  const calcularConsumo = (actual: number, anterior: number) => {
    return {
      total: actual - anterior,
      porcentaje: anterior > 0 ? ((actual - anterior) / anterior) * 100 : 0
    };
  };

  // Filtrar usuarios
  const usuariosFiltrados = cierres[cierres.length - 1]?.usuarios
    .filter(u => {
      if (mostrarSoloConConsumo && u.total_impresiones === 0) return false;
      if (busqueda) {
        return u.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
               u.codigo.includes(busqueda);
      }
      return true;
    })
    .sort((a, b) => b.total_impresiones - a.total_impresiones);

  return (
    <Modal size="xl" onClose={onClose}>
      <ModalHeader>
        <h2>📊 Comparación de Cierres Mensuales</h2>
        <p className="text-secondary">
          {printer.nombre} - {printer.ubicacion}
        </p>
      </ModalHeader>

      <ModalBody>
        {/* Resumen General */}
        <Card className="mb-4">
          <CardHeader>
            <h3>📈 RESUMEN GENERAL</h3>
          </CardHeader>
          <CardBody>
            <Table>
              <thead>
                <tr>
                  <th>Mes</th>
                  <th>Total</th>
                  <th>Anterior</th>
                  <th>Consumo</th>
                </tr>
              </thead>
              <tbody>
                {cierres.map((cierre, index) => {
                  const anterior = index > 0 ? cierres[index - 1] : null;
                  const consumo = anterior 
                    ? calcularConsumo(cierre.total_impresiones, anterior.total_impresiones)
                    : null;

                  return (
                    <tr key={cierre.id}>
                      <td>{cierre.mes_nombre.toUpperCase()}</td>
                      <td>{cierre.total_impresiones.toLocaleString()}</td>
                      <td>{anterior?.total_impresiones.toLocaleString() || '--'}</td>
                      <td>
                        {consumo ? (
                          <>
                            {consumo.total.toLocaleString()}
                            <span className="text-muted ml-2">
                              ({consumo.porcentaje > 0 ? '+' : ''}
                              {consumo.porcentaje.toFixed(1)}%)
                            </span>
                          </>
                        ) : '--'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </Table>

            {/* Desglose del último período */}
            {cierres.length > 0 && (
              <div className="mt-4">
                <h4>Desglose del consumo:</h4>
                <ul className="list-none">
                  <li>• Blanco y Negro: {cierres[cierres.length - 1].total_bn?.toLocaleString() || 0} páginas</li>
                  <li>• Color: {cierres[cierres.length - 1].total_color?.toLocaleString() || 0} páginas</li>
                </ul>
              </div>
            )}
          </CardBody>
        </Card>

        {/* Consumo por Usuario */}
        <Card>
          <CardHeader>
            <h3>👥 CONSUMO POR USUARIO ({cierres[cierres.length - 1]?.mes_nombre})</h3>
          </CardHeader>
          <CardBody>
            {/* Filtros */}
            <div className="flex gap-4 mb-4">
              <Input
                type="text"
                placeholder="🔍 Buscar por nombre o código..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="flex-1"
              />
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={mostrarSoloConConsumo}
                  onChange={(e) => setMostrarSoloConConsumo(e.target.checked)}
                />
                Solo con consumo
              </label>
            </div>

            {/* Tabla de usuarios */}
            <Table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Nombre</th>
                  <th className="text-right">B/N</th>
                  <th className="text-right">Color</th>
                  <th className="text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                {usuariosFiltrados
                  ?.slice(
                    (paginaActual - 1) * usuariosPorPagina,
                    paginaActual * usuariosPorPagina
                  )
                  .map((usuario) => (
                    <tr key={usuario.codigo}>
                      <td>{usuario.codigo}</td>
                      <td>{usuario.nombre}</td>
                      <td className="text-right">{usuario.bn?.toLocaleString() || 0}</td>
                      <td className="text-right">{usuario.color?.toLocaleString() || 0}</td>
                      <td className="text-right font-semibold">
                        {usuario.total_impresiones.toLocaleString()}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </Table>

            {/* Paginación */}
            <div className="flex justify-between items-center mt-4">
              <span className="text-secondary">
                Total usuarios: {usuariosFiltrados?.length || 0}
              </span>
              <Pagination
                currentPage={paginaActual}
                totalPages={Math.ceil((usuariosFiltrados?.length || 0) / usuariosPorPagina)}
                onPageChange={setPaginaActual}
              />
            </div>
          </CardBody>
        </Card>
      </ModalBody>

      <ModalFooter>
        <Button variant="secondary" onClick={onClose}>
          ✖ Cerrar
        </Button>
        <Button variant="primary" onClick={() => exportarExcel(cierres, printer)}>
          📥 Exportar Excel
        </Button>
        <Button variant="primary" onClick={() => exportarPDF(cierres, printer)}>
          📄 Exportar PDF
        </Button>
      </ModalFooter>
    </Modal>
  );
};
```

---

## ✅ MEJORAS IMPLEMENTADAS

### 1. Diseño más limpio
- ✅ Colores más sutiles y profesionales
- ✅ Menos elementos decorativos innecesarios
- ✅ Espaciado consistente
- ✅ Tipografía clara y legible

### 2. Formato basado en CSV reales
- ✅ Estructura de tabla igual a los CSV
- ✅ Desglose B/N y Color visible
- ✅ Formato de números con separadores de miles
- ✅ Códigos de usuario entre corchetes [XXXX]

### 3. Funcionalidad mejorada
- ✅ Filtro para mostrar solo usuarios con consumo
- ✅ Búsqueda por nombre o código
- ✅ Paginación clara
- ✅ Exportación a Excel con formato correcto

### 4. Información clara
- ✅ Resumen general destacado
- ✅ Desglose de consumo visible
- ✅ Porcentajes de variación
- ✅ Totales y promedios

---

## 🚀 PRÓXIMOS PASOS

1. Implementar el componente ComparacionCierresModal mejorado
2. Crear la función de exportación a Excel con el formato correcto
3. Agregar gráficos de tendencia simples
4. Implementar la exportación a PDF

