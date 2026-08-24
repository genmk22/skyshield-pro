import React from 'react';
import type { ConjunctionEvent, SatelliteSummary } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { AlertOctagon, Satellite, ShieldAlert, Clock, ArrowRight, Zap } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface OverviewPageProps {
  satellites: SatelliteSummary[];
  conjunctions: ConjunctionEvent[];
  onNavigate: (tab: any) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ satellites, conjunctions, onNavigate }) => {
  const primarySat = satellites[0] || { name: 'ISS (ZARYA)', norad_id: 25544, age_hours: 6.2, confidence_level: 'HIGH' };
  
  const highRiskCount = conjunctions.filter(c => c.risk_level === 'HIGH RISK' || c.risk_level === 'CRITICAL').length;
  const warningCount = conjunctions.filter(c => c.risk_level === 'WARNING').length;
  const monitorCount = conjunctions.filter(c => c.risk_level === 'MONITOR').length;
  const safeCount = conjunctions.filter(c => c.risk_level === 'SAFE').length;

  const pieData = [
    { name: 'CRITICAL / HIGH', value: highRiskCount || 1, color: '#f97316' },
    { name: 'WARNING', value: warningCount, color: '#f59e0b' },
    { name: 'MONITOR', value: monitorCount, color: '#06b6d4' },
    { name: 'SAFE', value: safeCount, color: '#10b981' },
  ].filter(d => d.value > 0);

  const nextCritical = conjunctions
    .filter(c => c.risk_level !== 'SAFE')
    .sort((a, b) => a.time_to_tca_hours - b.time_to_tca_hours)[0];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-xl glass-panel border border-blue-900/40 relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800/60 text-xs font-mono font-bold">
              PRIMARY ASSET
            </span>
            <h2 className="text-2xl font-bold text-white tracking-wide">{primarySat.name}</h2>
          </div>
          <p className="text-sm text-gray-400">
            NORAD ID: <span className="text-gray-200 font-mono">{primarySat.norad_id}</span> | Altitude: <span className="text-gray-200 font-mono">418.5 km</span> | Inclination: <span className="text-gray-200 font-mono">51.64°</span>
          </p>
        </div>

        <div className="flex items-center space-x-4 bg-slate-900/90 p-3 rounded-lg border border-gray-800 text-xs">
          <div>
            <p className="text-gray-400">TLE Data Age</p>
            <p className="text-sm font-bold text-white font-mono">{primarySat.age_hours || 6.2} hrs</p>
          </div>
          <div className="h-8 w-px bg-gray-800" />
          <div>
            <p className="text-gray-400">Data Confidence</p>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
              {primarySat.confidence_level || 'HIGH'}
            </span>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl glass-panel flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-400 font-medium uppercase">Active Objects</p>
            <h3 className="text-3xl font-bold text-white font-mono mt-1">{satellites.length || 5}</h3>
            <p className="text-[11px] text-gray-500 mt-1">LEO Orbital Sector</p>
          </div>
          <div className="p-3 rounded-lg bg-blue-950/60 border border-blue-800/40 text-blue-400">
            <Satellite className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-xl glass-panel flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-400 font-medium uppercase">Active Conjunctions</p>
            <h3 className="text-3xl font-bold text-amber-400 font-mono mt-1">{conjunctions.length}</h3>
            <p className="text-[11px] text-gray-500 mt-1">Next 72 Hours</p>
          </div>
          <div className="p-3 rounded-lg bg-amber-950/60 border border-amber-800/40 text-amber-400">
            <AlertOctagon className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-xl glass-panel flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-400 font-medium uppercase">High Risk Events</p>
            <h3 className="text-3xl font-bold text-orange-400 font-mono mt-1">{highRiskCount}</h3>
            <p className="text-[11px] text-gray-500 mt-1">Requires Operator Action</p>
          </div>
          <div className="p-3 rounded-lg bg-orange-950/60 border border-orange-800/40 text-orange-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-xl glass-panel flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-400 font-medium uppercase">Next Critical TCA</p>
            <h3 className="text-2xl font-bold text-cyan-400 font-mono mt-1">
              {nextCritical ? `${nextCritical.time_to_tca_hours}h` : 'NONE'}
            </h3>
            <p className="text-[11px] text-gray-500 mt-1">Countdown to Approach</p>
          </div>
          <div className="p-3 rounded-lg bg-cyan-950/60 border border-cyan-800/40 text-cyan-400">
            <Clock className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Main Grid: Threats & Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Threats Table */}
        <div className="lg:col-span-2 p-6 rounded-xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white tracking-wide">Threat Overview</h3>
            <button
              onClick={() => onNavigate('conjunctions')}
              className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center space-x-1"
            >
              <span>View All Conjunctions</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-gray-400 uppercase font-mono border-b border-gray-800">
                <tr>
                  <th className="p-3">Secondary Object</th>
                  <th className="p-3">TCA (UTC)</th>
                  <th className="p-3">Miss Distance</th>
                  <th className="p-3">Estimated Pc</th>
                  <th className="p-3">Risk Level</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {conjunctions.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-900/50 transition-colors">
                    <td className="p-3 font-semibold text-white">
                      {c.secondary_name}
                      <span className="block text-[10px] text-gray-500 font-mono">NORAD #{c.secondary_norad_id} ({c.secondary_type})</span>
                    </td>
                    <td className="p-3 font-mono text-gray-300">
                      {new Date(c.tca).toISOString().slice(11, 19)}
                      <span className="block text-[10px] text-gray-500">In {c.time_to_tca_hours} hrs</span>
                    </td>
                    <td className="p-3 font-mono text-gray-200">
                      {c.geometry.miss_distance_km.toFixed(3)} km
                    </td>
                    <td className="p-3 font-mono font-semibold text-amber-400">
                      {c.estimated_pc.toExponential(2)}
                    </td>
                    <td className="p-3">
                      <RiskBadge level={c.risk_level} />
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => onNavigate('risk')}
                        className="px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 text-xs font-semibold border border-blue-500/30"
                      >
                        Analyze
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Risk Distribution & Action Panel */}
        <div className="space-y-6">
          <div className="p-6 rounded-xl glass-panel space-y-4">
            <h3 className="text-base font-bold text-white">Risk Distribution</h3>
            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {pieData.map((d) => (
                <div key={d.name} className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                  <span className="text-gray-400">{d.name}:</span>
                  <span className="font-bold text-white font-mono">{d.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recommended Advisory Action */}
          <div className="p-6 rounded-xl bg-gradient-to-br from-blue-950/70 via-slate-900 to-indigo-950/70 border border-blue-800/50 space-y-3">
            <div className="flex items-center space-x-2 text-blue-400 font-bold text-sm">
              <Zap className="w-4 h-4" />
              <span>RECOMMENDED ADVISORY</span>
            </div>
            <p className="text-xs text-gray-300 leading-relaxed">
              Conjunction <span className="text-amber-300 font-semibold">{nextCritical?.id || 'conj-25544-33442'}</span> presents high risk. Grid-search maneuver advisor generated candidate avoidance burns.
            </p>
            <button
              onClick={() => onNavigate('maneuvers')}
              className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center justify-center space-x-2 shadow-lg shadow-blue-900/40"
            >
              <span>Open Maneuver Advisor</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
