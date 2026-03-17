import { useState } from 'react';
import { DashboardView } from './dashboard/DashboardView';
import { PrinterDetailView } from './detail/PrinterDetailView';
import { CierresView } from './cierres/CierresView';

type CounterView = 'resumen' | 'printer-detail' | 'cierres';
type Tab = 'resumen' | 'cierres';

export const ContadoresModule: React.FC = () => {
  const [currentView, setCurrentView] = useState<CounterView>('resumen');
  const [activeTab, setActiveTab] = useState<Tab>('resumen');
  const [selectedPrinterId, setSelectedPrinterId] = useState<number | null>(null);

  const handleNavigateToPrinter = (printerId: number) => {
    setSelectedPrinterId(printerId);
    setCurrentView('printer-detail');
  };

  const handleNavigateBack = () => {
    setCurrentView(activeTab === 'cierres' ? 'cierres' : 'resumen');
    setSelectedPrinterId(null);
  };

  const handleTabChange = (tab: Tab) => {
    setActiveTab(tab);
    setCurrentView(tab);
    setSelectedPrinterId(null);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header con pestañas */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h1 className="text-2xl font-bold text-gray-900">CONTADORES</h1>
          </div>
          
          {/* Pestañas */}
          {currentView !== 'printer-detail' && (
            <div className="flex gap-1 border-b border-gray-200">
              <button
                onClick={() => handleTabChange('resumen')}
                className={`px-4 py-2 font-medium text-sm transition-colors ${
                  activeTab === 'resumen'
                    ? 'text-red-600 border-b-2 border-red-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Resumen
              </button>
              <button
                onClick={() => handleTabChange('cierres')}
                className={`px-4 py-2 font-medium text-sm transition-colors ${
                  activeTab === 'cierres'
                    ? 'text-red-600 border-b-2 border-red-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Cierres
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Contenido */}
      <div className="flex-1 overflow-auto">
        {currentView === 'resumen' && (
          <DashboardView onNavigateToPrinter={handleNavigateToPrinter} />
        )}
        
        {currentView === 'cierres' && (
          <CierresView />
        )}
        
        {currentView === 'printer-detail' && selectedPrinterId && (
          <PrinterDetailView
            printerId={selectedPrinterId}
            onNavigateBack={handleNavigateBack}
          />
        )}
      </div>
    </div>
  );
};
