import type { TotalCounter } from '@/types/counter';

interface CounterBreakdownProps {
  counter: TotalCounter;
}

export const CounterBreakdown: React.FC<CounterBreakdownProps> = ({ counter }) => {
  // Calcular totales por función
  const totalCopiadora = counter.copiadora_bn + counter.copiadora_color + 
                         counter.copiadora_color_personalizado + counter.copiadora_dos_colores;
  const totalImpresora = counter.impresora_bn + counter.impresora_color + 
                         counter.impresora_color_personalizado + counter.impresora_dos_colores;
  const totalEscaner = counter.envio_escaner_bn + counter.envio_escaner_color;
  const totalFax = counter.fax_bn + counter.transmision_fax_total;

  const sections = [
    {
      title: 'TOTAL',
      items: [
        { label: 'Copiadora', value: totalCopiadora },
        { label: 'Impresora', value: totalImpresora },
        { label: 'Escáner', value: totalEscaner },
        { label: 'Fax', value: totalFax },
      ],
      highlight: true,
    },
    {
      title: 'Copiadora',
      items: [
        { label: 'B/N', value: counter.copiadora_bn },
        { label: 'Color', value: counter.copiadora_color },
        { label: 'Color Personalizado', value: counter.copiadora_color_personalizado },
        { label: 'Dos Colores', value: counter.copiadora_dos_colores },
      ],
    },
    {
      title: 'Impresora',
      items: [
        { label: 'B/N', value: counter.impresora_bn },
        { label: 'Color', value: counter.impresora_color },
        { label: 'Color Personalizado', value: counter.impresora_color_personalizado },
        { label: 'Dos Colores', value: counter.impresora_dos_colores },
      ],
    },
    {
      title: 'Escáner',
      items: [
        { label: 'B/N', value: counter.envio_escaner_bn },
        { label: 'Color', value: counter.envio_escaner_color },
        { label: 'Total Envíos', value: counter.enviar_total_bn + counter.enviar_total_color },
      ],
    },
    {
      title: 'Fax',
      items: [
        { label: 'B/N', value: counter.fax_bn },
        { label: 'Transmisiones', value: counter.transmision_fax_total },
      ],
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <h2 className="text-lg font-bold text-slate-700 mb-4">Desglose de Contadores</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {sections.map((section) => (
          <div 
            key={section.title} 
            className={`space-y-2 ${section.highlight ? 'bg-blue-50 p-3 rounded-lg border border-blue-200' : ''}`}
          >
            <h3 className={`text-sm font-bold uppercase tracking-wide border-b pb-1 ${
              section.highlight 
                ? 'text-blue-700 border-blue-300' 
                : 'text-slate-600 border-slate-200'
            }`}>
              {section.title}
            </h3>
            {section.items.map((item) => (
              <div key={item.label} className="flex justify-between items-baseline">
                <span className={`text-xs ${section.highlight ? 'text-blue-600' : 'text-slate-500'}`}>
                  {item.label}:
                </span>
                <span className={`text-sm font-semibold ${
                  section.highlight ? 'text-blue-900' : 'text-slate-900'
                }`}>
                  {item.value.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="flex justify-between items-baseline">
          <span className="text-sm font-bold text-slate-700">Total General:</span>
          <span className="text-2xl font-bold text-ricoh-red">
            {counter.total.toLocaleString()}
          </span>
        </div>
        <div className="text-xs text-slate-400 mt-1">
          Última lectura: {new Date(counter.fecha_lectura).toLocaleString()}
        </div>
      </div>
    </div>
  );
};
