import React from 'react';
import {
  LayoutDashboard, AlertOctagon, HelpCircle, Navigation, Orbit, ShieldCheck, PlayCircle, FileText
} from 'lucide-react';

export type ActiveTab = 
  | 'overview'
  | 'conjunctions'
  | 'risk'
  | 'maneuvers'
  | 'orbit3d'
  | 'security'
  | 'scenarios'
  | 'logs';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'overview', label: 'Mission Overview', icon: LayoutDashboard },
    { id: 'conjunctions', label: 'Active Conjunctions', icon: AlertOctagon },
    { id: 'risk', label: 'Risk & Explainability', icon: HelpCircle },
    { id: 'maneuvers', label: 'Maneuver Advisor', icon: Navigation },
    { id: 'orbit3d', label: '3D Orbital Digital Twin', icon: Orbit },
    { id: 'security', label: 'Security & Signatures', icon: ShieldCheck },
    { id: 'scenarios', label: 'Demo Scenarios', icon: PlayCircle },
    { id: 'logs', label: 'Audit Logs', icon: FileText },
  ];

  return (
    <aside className="w-64 border-r border-gray-800 bg-slate-950 p-4 flex flex-col justify-between shrink-0">
      <nav className="space-y-1.5">
        <div className="px-3 py-2 text-[11px] font-semibold text-gray-500 tracking-wider uppercase">
          Mission Control
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as ActiveTab)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-lg shadow-blue-950/50'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-gray-500'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-3 rounded-lg bg-slate-900/80 border border-gray-800/80 text-xs text-gray-400">
        <p className="font-semibold text-gray-300">Decision-Support Notice</p>
        <p className="mt-1 text-[11px] text-gray-500 leading-relaxed">
          Human Operator approval required for all maneuver commands. Physics model: SGP4 & 2D B-Plane $P_c$.
        </p>
      </div>
    </aside>
  );
};
