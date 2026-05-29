# Eliminación Completa de Soporte CSV — 29 Mayo 2026

## Contexto

Por solicitud del cliente, se eliminó completamente el formato CSV del sistema Ricoh Suite. A partir de la versión **2.5.0**, todas las exportaciones usan exclusivamente **Excel (`.xlsx`)**.

---

## Alcance de la Eliminación

### Backend

#### `backend/api/export.py`

| Elemento eliminado | Tipo | Ruta |
|---|---|---|
| `export_cierre()` | Endpoint | `GET /api/export/cierre/{cierre_id}` |
| `export_comparacion()` | Endpoint | `GET /api/export/comparacion/{cierre1_id}/{cierre2_id}` |
| `import csv` | Import | — |

**Endpoints que PERMANECEN:**

| Endpoint | Formato | Descripción |
|---|---|---|
| `GET /api/export/cierre/{id}/excel` | `.xlsx` | Cierre individual, formato simple |
| `GET /api/export/comparacion/{id1}/{id2}/excel` | `.xlsx` | Comparación, formato simple |
| `GET /api/export/comparacion/{id1}/{id2}/excel-ricoh` | `.xlsx` (3 hojas, 52 col) | Formato original Ricoh |

---

### Frontend

#### `src/services/exportService.ts`

```typescript
// ELIMINADOS
exportCierreCSV(cierreId: number): Promise<void>
exportComparacionCSV(cierre1Id: number, cierre2Id: number): Promise<void>

// PERMANECEN
exportCierreExcel(cierreId: number): Promise<void>
exportComparacionExcel(cierre1Id: number, cierre2Id: number): Promise<void>
exportComparacionExcelRicoh(cierre1Id: number, cierre2Id: number): Promise<void>
```

#### `src/utils/exportUtils.ts`

```typescript
// ELIMINADOS
exportChartDataToCSV(data: any[], filename: string): void
exportTableToCSV(data: any[], filename: string): void

// PERMANECEN
exportTableToExcel(data: any[], filename: string): void
exportReportToPDF(title, data, columns, filename): void
copyChartDataToClipboard(data: any[]): Promise<boolean>  // clipboard interno, no es CSV público
```

#### `src/pages/AnalyticsPage.tsx`

| Cambio | Antes | Después |
|---|---|---|
| Import | `exportTableToExcel, exportTableToCSV` | `exportTableToExcel` |
| Handler comparativa | `handleExportCSV()` | `handleExportExcel()` |
| Handler usuarios | `handleExportUsersCSV()` | `handleExportUsersExcel()` |
| Función interna | `exportTableToCSV(data, filename)` | `exportTableToExcel(data, filename)` |
| Botón comparativa | "CSV" | "Excel" |
| Botón usuarios | "Exportar CSV" | "Exportar Excel" |

#### `src/components/contadores/cierres/ComparacionPage.tsx`

- ❌ Eliminado import `FileText` de `lucide-react`
- ❌ Eliminado botón "CSV" del footer de tabla de comparación

#### `src/components/contadores/cierres/ComparacionModal.tsx`

- ❌ Eliminado botón "CSV" del footer del modal de comparación

#### `src/components/contadores/cierres/CierreDetalleModal.tsx`

- ❌ Eliminado import `Download` de `lucide-react` (solo se usaba para el botón CSV)
- ❌ Eliminado botón "Exportar CSV" del footer del modal de detalle

---

## Validación

```bash
# Verificar cero referencias CSV en frontend
grep -r "CSV\|csv\|exportCierreCSV\|exportComparacionCSV\|exportTableToCSV" src/ --include="*.ts" --include="*.tsx"
# Resultado: 0 coincidencias en lógica de exportación ✅

# Compilación TypeScript sin errores
node node_modules/typescript/bin/tsc --noEmit
# Resultado: 0 errores ✅
```

---

## Impacto en el Usuario Final

Los usuarios que anteriormente exportaban en CSV ahora reciben automáticamente archivos `.xlsx`. No se requiere ningún cambio en los flujos de trabajo — Excel abre `.xlsx` igual que antes; la única diferencia es que los archivos son nativamente Excel, no texto delimitado por comas.

---

## Flujo de exportación resultante

```
┌─────────────────────────────────────┐
│           USUARIO FINAL             │
└─────────────────────────────────────┘
         │
         ▼ Click en botón de exportar
┌─────────────────────────────────────┐
│         exportService.ts            │
│  ┌─ exportCierreExcel()             │
│  ├─ exportComparacionExcel()         │
│  └─ exportComparacionExcelRicoh()    │
└─────────────────────────────────────┘
         │ fetch() con Bearer token
         ▼
┌─────────────────────────────────────┐
│         backend/api/export.py        │
│  ┌─ /cierre/{id}/excel              │
│  ├─ /comparacion/{id1}/{id2}/excel  │
│  └─ /comparacion/{id1}/{id2}/excel-ricoh │
└─────────────────────────────────────┘
         │ StreamingResponse
         ▼ Blob → <a download> click
┌─────────────────────────────────────┐
│   Archivo descargado en cliente     │
│   Formato: SERIAL DD.MM.YYYY.xlsx   │
└─────────────────────────────────────┘
```

---

*Cambio implementado el 29 de mayo de 2026.*  
*Relacionado con: `RESUMEN_TRABAJO_26_29_MAYO_2026.md`*
