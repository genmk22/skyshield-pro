import React, { useState, useEffect } from 'react';
import type { ConjunctionEvent, RiskExplanation, MonteCarloResult } from '../types';
import { fetchRiskExplanation, runMonteCarlo } from '../services/api';
import { HelpCircle, Cpu, Play, RefreshCw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface RiskAnalysisPageProps {
  conjunction: ConjunctionEvent | null;
  onNavigate: (tab: any) => void;
}

export const RiskAnalysisPage: React.FC<RiskAnalysisPageProps> = ({ conjunction, onNavigate }) => {
  const [explanation, setExplanation] = useState<RiskExplanation | null>(null);
  const [mcResult, setMcResult] = useState<MonteCarloResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [samples, setSamples] = useState<number>(10000);

  useEffect(() => {
    if (conjunction) {
      fetchRiskExplanation(conjunction.id)
        .then(setExplanation)
        .catch(console.error);
    }
  }, [conjunction]);

  const handleRunMonteCarlo = async () => {
    if (!conjunction) return;
    setLoading(true);
    try {
      const res = await runMonteCarlo(conjunction.id, samples);
      setMcResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (!conjunction) {
    return (
      <div className="p-12 text-center text-gray-400 glass-panel rounded-xl">
        <HelpCircle className="w-12 h-12 text-blue-400 mx-auto mb-3 opacity-60" />
        <h3 className="text-lg font-bold text-white">No Conjunction Selected</h3>
        <p className="text-xs text-gray-500 mt-1">Select an active conjunction from the table to view explainability factor breakdown.</p>
        <button
          onClick={() => onNavigate('conjunctions')}
          className="mt-4 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs"
        >
          Select Conjunction
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="p-6 rounded-xl glass-panel border border-blue-900/40 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-bold text-white tracking-wide">
              {conjunction.primary_name} vs {conjunction.secondary_name}
            </h2>
          </div>
          <p className="text-xs text-gray-400 mt-1 font-mono">
            Conjunction ID: {conjunction.id} | TCA: {new Date(conjunction.tca).toISOString()}
          </p>
        </div>

        <button
          onClick={() => onNavigate('maneuvers')}
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-900/40"
        >
          Evaluate Avoidance Maneuver
        </button>
      </div>

      {/* Main Grid: Explainability vs Monte Carlo */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Physics Explainability Breakdown */}
        <div className="p-6 rounded-xl glass-panel space-y-6">
          <div className="flex items-center space-x-2 text-white font-bold text-base border-b border-gray-800 pb-3">
            <HelpCircle className="w-5 h-5 text-blue-400" />
            <span>Why is this encounter classified as {conjunction.risk_level}?</span>
          </div>

          {/* Factors List */}
          <div className="space-y-3">
            {explanation?.key_factors.map((factor, idx) => (
              <div
                key={idx}
                className={`p-3.5 rounded-lg border text-xs space-y-1 transition-all ${
                  factor.threshold_crossed
                    ? 'bg-amber-950/20 border-amber-800/40 text-amber-200'
                    : 'bg-slate-900/60 border-gray-800/80 text-gray-300'
                }`}
              >
                <div className="flex justify-between items-center font-semibold">
                  <span>{factor.name}</span>
                  <span className="font-mono text-sm">{factor.value}</span>
                </div>
                <p className="text-[11px] text-gray-400">{factor.description}</p>
              </div>
            ))}
          </div>

          {/* Tracking Data Freshness Impact */}
          <div className="p-4 rounded-lg bg-slate-900 border border-gray-800 text-xs space-y-1">
            <p className="font-semibold text-gray-300">Tracking Data Freshness & Uncertainty</p>
            <p className="text-gray-400 leading-relaxed">{explanation?.data_freshness_impact}</p>
          </div>
        </div>

        {/* Right: Monte Carlo Validation Engine */}
        <div className="p-6 rounded-xl glass-panel space-y-6">
          <div className="flex items-center justify-between border-b border-gray-800 pb-3">
            <div className="flex items-center space-x-2 text-white font-bold text-base">
              <Cpu className="w-5 h-5 text-cyan-400" />
              <span>Monte Carlo Validation Engine</span>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/50 font-mono font-bold">
              VECTORIZED SAMPLER
            </span>
          </div>

          {/* Sample selector & controls */}
          <div className="flex items-center space-x-4 bg-slate-900 p-3 rounded-lg border border-gray-800 text-xs">
            <label className="text-gray-400 font-medium">Simulations:</label>
            <select
              value={samples}
              onChange={(e) => setSamples(Number(e.target.value))}
              className="bg-slate-950 border border-gray-800 rounded px-2 py-1 text-gray-200 focus:outline-none"
            >
              <option value={1000}>1,000</option>
              <option value={5000}>5,000</option>
              <option value={10000}>10,000</option>
              <option value={50000}>50,000</option>
            </select>
            <button
              onClick={handleRunMonteCarlo}
              disabled={loading}
              className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-semibold flex items-center space-x-1.5"
            >
              {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
              <span>{loading ? 'Running...' : 'Run Simulation'}</span>
            </button>
          </div>

          {/* Comparison Cards */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3.5 rounded-lg bg-slate-900 border border-gray-800">
              <p className="text-gray-400">Analytical Pc (B-Plane)</p>
              <p className="text-lg font-bold text-amber-400 font-mono mt-1">
                {conjunction.estimated_pc.toExponential(2)}
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-gray-800">
              <p className="text-gray-400">Monte Carlo Estimated Pc</p>
              <p className="text-lg font-bold text-cyan-400 font-mono mt-1">
                {mcResult ? mcResult.monte_carlo_pc.toExponential(2) : 'NOT RUN'}
              </p>
            </div>
          </div>

          {/* Convergence Chart */}
          {mcResult && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-300">Monte Carlo Convergence Progression</p>
              <div className="h-44 w-full bg-slate-950 p-2 rounded-lg border border-gray-800">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={mcResult.convergence_series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="samples" stroke="#64748b" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', fontSize: '11px', color: '#fff' }} />
                    <Line type="monotone" dataKey="mc_pc" stroke="#06b6d4" strokeWidth={2} dot={false} name="Monte Carlo Pc" />
                    <Line type="monotone" dataKey="analytical_pc" stroke="#f59e0b" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="Analytical Pc" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
