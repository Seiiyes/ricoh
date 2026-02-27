import { useState } from 'react';
import { ProvisioningPanel } from './components/governance/ProvisioningPanel';
import { AdministracionUsuarios } from './components/usuarios/AdministracionUsuarios';
import { UserCog, UserPlus, Search } from 'lucide-react';

function App() {
  const [vistaActual, setVistaActual] = useState<'descubrimiento' | 'aprovisionamiento' | 'administracion'>('descubrimiento');

  return (
    <div className="flex h-screen">
      {/* Menú lateral */}
      <nav className="w-64 bg-industrial-gray text-white shadow-lg flex flex-col">
        <div className="px-6 py-4 border-b border-slate-700">
          <h1 className="text-sm font-bold uppercase tracking-tight">
            Ricoh Equipment Manager
          </h1>
        </div>
        
        <div className="flex-1 py-4">
          <button
            onClick={() => setVistaActual('descubrimiento')}
            className={`w-full flex items-center gap-3 px-6 py-3 text-sm font-bold uppercase tracking-wide transition-colors ${
              vistaActual === 'descubrimiento'
                ? 'bg-ricoh-red text-white border-l-4 border-white'
                : 'text-slate-300 hover:bg-slate-800'
            }`}
          >
            <Search size={18} />
            Descubrir Impresoras
          </button>
          
          <button
            onClick={() => setVistaActual('aprovisionamiento')}
            className={`w-full flex items-center gap-3 px-6 py-3 text-sm font-bold uppercase tracking-wide transition-colors ${
              vistaActual === 'aprovisionamiento'
                ? 'bg-ricoh-red text-white border-l-4 border-white'
                : 'text-slate-300 hover:bg-slate-800'
            }`}
          >
            <UserPlus size={18} />
            Crear Usuarios
          </button>
          
          <button
            onClick={() => setVistaActual('administracion')}
            className={`w-full flex items-center gap-3 px-6 py-3 text-sm font-bold uppercase tracking-wide transition-colors ${
              vistaActual === 'administracion'
                ? 'bg-ricoh-red text-white border-l-4 border-white'
                : 'text-slate-300 hover:bg-slate-800'
            }`}
          >
            <UserCog size={18} />
            Administrar Usuarios
          </button>
        </div>
      </nav>

      {/* Contenido */}
      <div className="flex-1 overflow-hidden">
        {vistaActual === 'descubrimiento' ? (
          <ProvisioningPanel showDiscoveryOnly={true} />
        ) : vistaActual === 'aprovisionamiento' ? (
          <ProvisioningPanel showDiscoveryOnly={false} />
        ) : (
          <AdministracionUsuarios />
        )}
      </div>
    </div>
  );
}

export default App;