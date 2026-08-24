import React, { useState } from 'react';
import type { ConjunctionEvent } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { Search } from 'lucide-react';

interface ConjunctionsPageProps {
  conjunctions: ConjunctionEvent[];
  onSelectConjunction: (conj: ConjunctionEvent) => void;
  onNavigate: (tab: any) => void;
}

export const ConjunctionsPage: React.FC<ConjunctionsPageProps> = ({
  conjunctions, onSelectConjunction, onNavigate
}) => {
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');

  const filtered = conjunctions.filter((c) => {
    const matchesSearch = c.secondary_name.toLowerCase().includes(search.toLowerCase()) ||
                          c.secondary_norad_id.toString().includes(search);
    const matchesFilter = riskFilter === 'ALL' || c.risk_level === riskFilter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide">Conjunction Threat Management</h2>
          <p className="text-xs text-gray-400">All predicted orbital close approaches within prediction window</p>
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          {/* Search Input */}
          <div className="relative flex-1 md:w-64">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-500" />
            <input
              type="text"
              placeholder="Search NORAD ID or name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900 border border-gray-800 rounded-lg pl-9 pr-3 py-2 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Filter Dropdown */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-slate-900 border border-gray-800 rounded-lg px-3 py-2 text-xs text-gray-200 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH RISK">High Risk</option>
            <option value="WARNING">Warning</option>
            <option value="MONITOR">Monitor</option>
            <option value="SAFE">Safe</option>
          </select>
        </div>
      </div>

      {/* Main Conjunction Table */}
      <div className="p-6 rounded-xl glass-panel space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-gray-400 uppercase font-mono border-b border-gray-800">
              <tr>
                <th className="p-3">Conjunction ID</th>
                <th className="p-3">Secondary Object</th>
                <th className="p-3">Time of Closest Approach (TCA)</th>
                <th className="p-3">Miss Distance</th>
                <th className="p-3">Rel Velocity</th>
                <th className="p-3">Analytical Pc</th>
                <th className="p-3">TLE Age</th>
                <th className="p-3">Risk Level</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {filtered.map((c) => (
                <tr key={c.id} className="hover:bg-slate-900/50 transition-colors">
                  <td className="p-3 font-mono font-semibold text-blue-400">
                    {c.id}
                  </td>
                  <td className="p-3">
                    <span className="font-semibold text-white">{c.secondary_name}</span>
                    <span className="block text-[10px] text-gray-500 font-mono">NORAD #{c.secondary_norad_id} ({c.secondary_type})</span>
                  </td>
                  <td className="p-3 font-mono text-gray-300">
                    {new Date(c.tca).toISOString().replace('T', ' ').slice(0, 19)}
                    <span className="block text-[10px] text-gray-500">TCA in {c.time_to_tca_hours} hrs</span>
                  </td>
                  <td className="p-3 font-mono font-bold text-gray-200">
                    {c.geometry.miss_distance_km.toFixed(3)} km
                    <span className="block text-[10px] text-gray-500 font-normal">
                      R: {c.geometry.radial_sep_km}km | T: {c.geometry.along_track_sep_km}km
                    </span>
                  </td>
                  <td className="p-3 font-mono text-gray-300">
                    {c.geometry.relative_velocity_kms.toFixed(2)} km/s
                  </td>
                  <td className="p-3 font-mono font-bold text-amber-400">
                    {c.estimated_pc.toExponential(2)}
                  </td>
                  <td className="p-3 font-mono text-gray-400">
                    {c.secondary_tle_age_hours}h
                  </td>
                  <td className="p-3">
                    <RiskBadge level={c.risk_level} />
                  </td>
                  <td className="p-3 text-right space-x-2">
                    <button
                      onClick={() => {
                        onSelectConjunction(c);
                        onNavigate('risk');
                      }}
                      className="px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 text-xs font-semibold border border-blue-500/30"
                    >
                      Explain Risk
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
