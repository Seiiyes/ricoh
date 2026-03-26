/**
 * Export Service
 * Servicio para exportación de cierres y comparaciones
 * Maneja la descarga de archivos con autenticación
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Descarga un archivo desde el backend con autenticación
 * Usa fetch() en lugar de axios para evitar problemas de CORS con blobs
 * @param url - URL relativa del endpoint
 * @param filename - Nombre del archivo a descargar
 */
async function downloadFile(url: string, filename: string): Promise<void> {
  try {
    // Obtener el token del sessionStorage
    const token = sessionStorage.getItem('access_token');
    if (!token) {
      throw new Error('No hay sesión activa');
    }

    // Hacer la petición con fetch() y el token
    const response = await fetch(`${API_URL}${url}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      // Intentar leer el error del backend
      const errorText = await response.text();
      let errorMessage = `Error ${response.status}`;
      
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        errorMessage = errorText || response.statusText;
      }
      
      throw new Error(errorMessage);
    }

    // Obtener el blob y descargarlo
    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  } catch (error: any) {
    throw new Error(error.message || 'Error al descargar archivo');
  }
}

export const exportService = {
  /**
   * Exportar cierre a CSV
   */
  exportCierreCSV: async (cierreId: number): Promise<void> => {
    await downloadFile(
      `/api/export/cierre/${cierreId}`,
      `cierre_${cierreId}.csv`
    );
  },

  /**
   * Exportar cierre a Excel
   */
  exportCierreExcel: async (cierreId: number): Promise<void> => {
    await downloadFile(
      `/api/export/cierre/${cierreId}/excel`,
      `cierre_${cierreId}.xlsx`
    );
  },

  /**
   * Exportar comparación a CSV
   */
  exportComparacionCSV: async (cierre1Id: number, cierre2Id: number): Promise<void> => {
    await downloadFile(
      `/api/export/comparacion/${cierre1Id}/${cierre2Id}`,
      `comparacion_${cierre1Id}_${cierre2Id}.csv`
    );
  },

  /**
   * Exportar comparación a Excel
   */
  exportComparacionExcel: async (cierre1Id: number, cierre2Id: number): Promise<void> => {
    await downloadFile(
      `/api/export/comparacion/${cierre1Id}/${cierre2Id}/excel`,
      `comparacion_${cierre1Id}_${cierre2Id}.xlsx`
    );
  },

  /**
   * Exportar comparación a Excel formato Ricoh
   */
  exportComparacionExcelRicoh: async (cierre1Id: number, cierre2Id: number): Promise<void> => {
    await downloadFile(
      `/api/export/comparacion/${cierre1Id}/${cierre2Id}/excel-ricoh`,
      `comparacion_ricoh_${cierre1Id}_${cierre2Id}.xlsx`
    );
  },
};

export default exportService;
