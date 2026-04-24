import React from 'react';

const FleetManagementPage = () => {
  return (
    <div className="flex flex-col h-full animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-black text-slate-800 tracking-tight">Gestión de Equipos</h1>
        <p className="text-sm font-bold text-slate-500 uppercase tracking-widest mt-1">Catálogo e Inventario</p>
      </div>
      <div className="flex-1 bg-white rounded-2xl border border-slate-100 flex items-center justify-center">
        <p className="text-slate-400">Implementación en Sprint 3</p>
      </div>
    </div>
  );
};

export default FleetManagementPage;
