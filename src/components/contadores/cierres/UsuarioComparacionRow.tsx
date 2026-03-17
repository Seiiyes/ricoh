import { UsuarioComparacion } from './types';

interface UsuarioComparacionRowProps {
  usuario: UsuarioComparacion;
  index: number;
  formatNumber: (num: number) => string;
  formatDiferencia: (num: number) => string;
  getDiferenciaColor: (num: number) => string;
}

export const UsuarioComparacionRow: React.FC<UsuarioComparacionRowProps> = ({
  usuario,
  index,
  formatNumber,
  formatDiferencia,
  getDiferenciaColor
}) => {
  return (
    <tr className="hover:bg-gray-50">
      <td className="px-4 py-3 text-sm text-gray-600">{index + 1}</td>
      <td className="px-4 py-3 text-sm text-gray-900 font-medium">{usuario.nombre_usuario}</td>
      <td className="px-4 py-3 text-sm text-gray-600">{usuario.codigo_usuario}</td>
      
      {/* Consumo Período 1 */}
      <td className="px-4 py-3 text-sm text-right text-gray-500 border-l border-gray-200">
        {formatNumber(usuario.consumo_cierre1)}
      </td>
      <td className="px-4 py-3 text-sm text-right text-gray-400">
        {formatNumber(usuario.consumo_copiadora_cierre1 || 0)}
      </td>
      <td className="px-4 py-3 text-sm text-right text-gray-400">
        {formatNumber(usuario.consumo_impresora_cierre1 || 0)}
      </td>
      <td className="px-4 py-3 text-sm text-right text-gray-400">
        {formatNumber(usuario.consumo_escaner_cierre1 || 0)}
      </td>
      <td className="px-4 py-3 text-sm text-right text-gray-400">
        {formatNumber(usuario.consumo_fax_cierre1 || 0)}
      </td>
      
      {/* Consumo Período 2 */}
      <td className="px-4 py-3 text-sm text-right text-gray-900 font-medium border-l border-gray-200">
        {formatNumber(usuario.consumo_cierre2)}
      </td>
      <td className="px-4 py-3 text-sm text-right text-gray-600">
        {formatNumber(usuario.consumo_copiadora_cierre2 || 0)}
      </td>
      <td className="px-4 py-3 text-sm text-right text-gray-600">
        {formatNumber(usuario.consumo_impresora_cierre2 || 0)}
      </td>
      <td className="px-4 py-3 text-sm text-right text-gray-600">
        {formatNumber(usuario.consumo_escaner_cierre2 || 0)}
      </td>
      <td className="px-4 py-3 text-sm text-right text-gray-600">
        {formatNumber(usuario.consumo_fax_cierre2 || 0)}
      </td>
      
      {/* Diferencia */}
      <td className={`px-4 py-3 text-sm text-right font-semibold border-l border-gray-200 ${getDiferenciaColor(usuario.diferencia)}`}>
        {formatDiferencia(usuario.diferencia)}
      </td>
      <td className={`px-4 py-3 text-sm text-right ${getDiferenciaColor(usuario.diferencia - (usuario.consumo_copiadora_cierre2 || 0) + (usuario.consumo_copiadora_cierre1 || 0))}`}>
        {formatDiferencia((usuario.consumo_copiadora_cierre2 || 0) - (usuario.consumo_copiadora_cierre1 || 0))}
      </td>
      <td className={`px-4 py-3 text-sm text-right ${getDiferenciaColor(usuario.diferencia - (usuario.consumo_impresora_cierre2 || 0) + (usuario.consumo_impresora_cierre1 || 0))}`}>
        {formatDiferencia((usuario.consumo_impresora_cierre2 || 0) - (usuario.consumo_impresora_cierre1 || 0))}
      </td>
      <td className={`px-4 py-3 text-sm text-right ${getDiferenciaColor(usuario.diferencia - (usuario.consumo_escaner_cierre2 || 0) + (usuario.consumo_escaner_cierre1 || 0))}`}>
        {formatDiferencia((usuario.consumo_escaner_cierre2 || 0) - (usuario.consumo_escaner_cierre1 || 0))}
      </td>
      <td className={`px-4 py-3 text-sm text-right ${getDiferenciaColor(usuario.diferencia - (usuario.consumo_fax_cierre2 || 0) + (usuario.consumo_fax_cierre1 || 0))}`}>
        {formatDiferencia((usuario.consumo_fax_cierre2 || 0) - (usuario.consumo_fax_cierre1 || 0))}
      </td>
    </tr>
  );
};
