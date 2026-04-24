import * as XLSX from 'xlsx';
import { jsPDF } from 'jspdf';
import autoTable, { UserOptions } from 'jspdf-autotable';

// Configuración recomendada para autotable en TypeScript
interface jsPDFWithAutoTable extends jsPDF {
  lastAutoTable: {
    finalY: number;
  };
}

export const exportChartDataToCSV = (data: any[], filename: string) => {
  if (!data || data.length === 0) return;
  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Data");
  XLSX.writeFile(wb, `${filename}.csv`);
};

export const exportTableToExcel = (data: any[], filename: string) => {
  if (!data || data.length === 0) return;
  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Reporte");
  XLSX.writeFile(wb, `${filename}.xlsx`);
};

export const exportReportToPDF = (
  title: string, 
  data: any[], 
  columns: { header: string, dataKey: string }[], 
  filename: string
) => {
  const doc = new jsPDF() as jsPDFWithAutoTable;
  
  // Título del documento
  doc.setFontSize(18);
  doc.setTextColor(15, 23, 42); // slate-900
  doc.text(title, 14, 22);
  
  // Metadatos
  doc.setFontSize(10);
  doc.setTextColor(100);
  doc.text(`Generado: ${new Date().toLocaleDateString()}`, 14, 30);

  // Tabla
  const autoTableOptions: UserOptions = {
    startY: 40,
    head: [columns.map(c => c.header)],
    body: data.map(row => columns.map(c => row[c.dataKey] || '')),
    headStyles: { fillColor: [227, 6, 19], textColor: [255, 255, 255] }, // Ricoh Red
    styles: { font: 'helvetica', fontSize: 9 },
    alternateRowStyles: { fillColor: [248, 250, 252] }, // slate-50
  };

  autoTable(doc, autoTableOptions);
  
  doc.save(`${filename}.pdf`);
};

export const copyChartDataToClipboard = async (data: any[]) => {
  try {
    const csvContent = data.map(row => Object.values(row).join('\t')).join('\n');
    await navigator.clipboard.writeText(csvContent);
    return true;
  } catch (err) {
    console.error('Error al copiar al portapapeles:', err);
    return false;
  }
};
