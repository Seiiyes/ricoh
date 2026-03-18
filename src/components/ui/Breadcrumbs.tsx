import React from 'react';
import { ChevronRight } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  onClick?: () => void;
}

export interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items,
  className = '',
}) => {
  return (
    <nav className={`flex items-center gap-2 text-sm ${className}`}>
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          {index > 0 && (
            <ChevronRight size={16} className="text-gray-400" />
          )}
          
          {item.onClick ? (
            <button
              onClick={item.onClick}
              className="text-gray-600 hover:text-ricoh-red transition-colors font-medium"
            >
              {item.label}
            </button>
          ) : (
            <span className="text-gray-900 font-bold">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
};
