/**
 * Tabs Component
 * 
 * Componente de pestañas reutilizable con indicador visual y soporte para iconos.
 * 
 * @created 2026-03-18
 * @author Kiro AI
 */

import React from 'react';

export interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

export interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (tabId: string) => void;
  variant?: 'default' | 'pills' | 'underline';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  variant = 'underline',
  size = 'md',
  className = '',
}) => {
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  const variantStyles = {
    default: {
      container: 'bg-slate-100/80 rounded-xl p-1 backdrop-blur-sm',
      tab: 'rounded-xl transition-all duration-300',
      active: 'bg-white text-ricoh-red shadow-[0_2px_10px_rgba(0,0,0,0.08)]',
      inactive: 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50',
    },
    pills: {
      container: 'gap-2',
      tab: 'rounded-full transition-all duration-300',
      active: 'bg-ricoh-red text-white shadow-md',
      inactive: 'bg-slate-100/80 text-slate-600 hover:bg-slate-200 hover:text-slate-900 backdrop-blur-sm',
    },
    underline: {
      container: 'border-b border-slate-200',
      tab: 'border-b-2 border-transparent transition-all duration-300',
      active: 'text-ricoh-red border-ricoh-red',
      inactive: 'text-slate-500 hover:text-slate-900 hover:border-slate-300',
    },
  };

  const styles = variantStyles[variant];

  return (
    <div className={`flex ${styles.container} ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => !tab.disabled && onChange(tab.id)}
          disabled={tab.disabled}
          className={`
            ${sizeStyles[size]}
            ${styles.tab}
            ${activeTab === tab.id ? styles.active : styles.inactive}
            ${tab.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            font-medium
            flex items-center gap-2
          `}
        >
          {tab.icon && <span>{tab.icon}</span>}
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  );
};
