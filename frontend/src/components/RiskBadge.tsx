import React from 'react';

interface RiskBadgeProps {
  level: string;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, className = '' }) => {
  let badgeStyle = 'bg-emerald-950/80 text-emerald-400 border-emerald-700/50';
  
  if (level === 'MONITOR') {
    badgeStyle = 'bg-cyan-950/80 text-cyan-400 border-cyan-700/50';
  } else if (level === 'WARNING') {
    badgeStyle = 'bg-amber-950/80 text-amber-400 border-amber-700/50';
  } else if (level === 'HIGH RISK') {
    badgeStyle = 'bg-orange-950/80 text-orange-400 border-orange-700/50';
  } else if (level === 'CRITICAL') {
    badgeStyle = 'bg-red-950/80 text-red-400 border-red-700/50 animate-pulse';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeStyle} ${className}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5" />
      {level}
    </span>
  );
};
