import { useState } from 'react';
import { DashboardView } from './dashboard/DashboardView';
import { PrinterDetailView } from './detail/PrinterDetailView';
import { CierresView } from './cierres/CierresView';
import { Tabs } from '@/components/ui';
import { BarChart3, Calendar, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

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
    <div className="h-full flex flex-col bg-slate-50 relative">
      {/* Dynamic Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30 select-none">
        <div className="absolute top-[10%] left-[5%] w-[600px] h-[600px] bg-red-100 rounded-full blur-[140px]"></div>
        <div className="absolute bottom-[20%] right-[10%] w-[500px] h-[500px] bg-slate-200 rounded-full blur-[120px]"></div>
      </div>
 
      {/* Header Premium */}
      <div className="relative z-10 bg-white/60 backdrop-blur-xl border-b border-slate-200 px-8 py-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-ricoh-red to-red-600 rounded-2xl flex items-center justify-center shadow-[0_8px_30px_rgb(206,17,38,0.25)] ring-4 ring-red-50">
              <Activity className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tighter uppercase">Gestión de Lecturas</h1>
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em]">Control de Consumo y Facturación</p>
            </div>
          </div>
          
          {currentView !== 'printer-detail' && (
            <div className="bg-slate-100/50 p-1 rounded-xl border border-slate-200/60">
              <Tabs
                tabs={[
                  { id: 'resumen', label: 'Estado de Equipos', icon: <BarChart3 size={15} /> },
                  { id: 'cierres', label: 'Historial de Cierres', icon: <Calendar size={15} /> }
                ]}
                activeTab={activeTab}
                onChange={(tab) => handleTabChange(tab as Tab)}
                variant="pills"
              />
            </div>
          )}
        </div>
      </div>
 
      {/* Contenido */}
      <div className="flex-1 overflow-auto relative z-10 custom-scrollbar">
        <div className="max-w-[1600px] mx-auto p-8">
          {currentView === 'resumen' && (
            <div className="animate-fade-in">
              <DashboardView onNavigateToPrinter={handleNavigateToPrinter} />
            </div>
          )}
          
          {currentView === 'cierres' && (
            <div className="animate-fade-in">
              <CierresView />
            </div>
          )}
          
          {currentView === 'printer-detail' && selectedPrinterId && (
            <div className="animate-slide-up">
              <PrinterDetailView
                printerId={selectedPrinterId}
                onNavigateBack={handleNavigateBack}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
