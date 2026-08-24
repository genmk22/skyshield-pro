import React, { useState, useEffect } from 'react';
import type { MultiThreatEvaluationResult, ManeuverCandidate, SignedCommandPayload } from '../types';
import { evaluateManeuvers, createCommand, signCommand } from '../services/api';
import { Navigation, CheckCircle2, ArrowRight, XCircle, FileSignature } from 'lucide-react';

interface ManeuverAdvisorPageProps {
  onNavigate: (tab: any) => void;
  setSignedCommand: (cmd: SignedCommandPayload) => void;
}

export const ManeuverAdvisorPage: React.FC<ManeuverAdvisorPageProps> = ({ onNavigate, setSignedCommand }) => {
  const [evalResult, setEvalResult] = useState<MultiThreatEvaluationResult | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<ManeuverCandidate | null>(null);
  const [isApproving, setIsApproving] = useState(false);
  const [signedPayload, setSignedPayloadLocal] = useState<SignedCommandPayload | null>(null);

  const loadManeuvers = async (forceNoSafe: boolean = false) => {
    try {
      const res = await evaluateManeuvers("25544", forceNoSafe);
      setEvalResult(res);
      if (res.best_candidate) {
        setSelectedCandidate(res.best_candidate);
      } else {
        setSelectedCandidate(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadManeuvers();
  }, []);

  const handleApproveAndSign = async () => {
    if (!selectedCandidate) return;
    setIsApproving(true);
    try {
      const cmdPayload = await createCommand("25544", selectedCandidate.id);
      const signed = await signCommand(cmdPayload, "FLIGHT_DYNAMICS_OPERATOR_01");
      setSignedPayloadLocal(signed);
      setSignedCommand(signed);
    } catch (e) {
      console.error(e);
    } finally {
      setIsApproving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Workflow Header */}
      <div className="p-6 rounded-xl glass-panel border border-blue-900/40 space-y-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-xl font-bold text-white tracking-wide">Multi-Threat Maneuver Advisor</h2>
            <p className="text-xs text-gray-400">Evaluate candidate avoidance burns against all active LEO conjunction threats</p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => loadManeuvers(false)}
              className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
            >
              Evaluate Candidates
            </button>
            <button
              onClick={() => loadManeuvers(true)}
              className="px-3.5 py-2 rounded-lg bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-700/60 text-xs font-semibold"
            >
              Simulate No-Safe State
            </button>
          </div>
        </div>

        {/* Step Progress Indicator */}
        <div className="grid grid-cols-4 lg:grid-cols-8 gap-2 pt-2 border-t border-gray-800 text-[11px]">
          {['1. Threats', '2. Constraints', '3. Grid Search', '4. Sim Burns', '5. Multi-Threat', '6. Ranking', '7. Approval', '8. Sign'].map((step, idx) => (
            <div key={idx} className="p-2 rounded bg-slate-900 border border-gray-800 text-center font-medium text-gray-300">
              {step}
            </div>
          ))}
        </div>
      </div>

      {/* Honest Failure Banner: NO SAFE MANEUVER FOUND */}
      {evalResult && !evalResult.has_safe_maneuver && (
        <div className="p-6 rounded-xl bg-rose-950/80 border-2 border-rose-600 text-rose-200 space-y-2 animate-pulse">
          <div className="flex items-center space-x-2 font-bold text-lg text-rose-100">
            <XCircle className="w-6 h-6 text-rose-400" />
            <span>NO SAFE MANEUVER FOUND</span>
          </div>
          <p className="text-xs text-rose-200 leading-relaxed font-mono">
            {evalResult.no_safe_maneuver_reason}
          </p>
          <p className="text-[11px] text-rose-300">
            System advisory: All candidate burns exceed maximum allowed delta-v (5.0 m/s), violate safety margins (1.0 km), or exacerbate secondary threat collisions. Operator intervention required.
          </p>
        </div>
      )}

      {/* Candidate Grid Search & Ranking Table */}
      {evalResult && evalResult.has_safe_maneuver && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Candidates Ranking Table */}
          <div className="lg:col-span-2 p-6 rounded-xl glass-panel space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white">Evaluated Candidate Burns ({evalResult.evaluated_candidates_count})</h3>
              <span className="text-xs text-gray-400 font-mono">Sorted by Multi-Threat Score</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/90 text-gray-400 uppercase font-mono border-b border-gray-800">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Burn Direction</th>
                    <th className="p-3">Delta-V</th>
                    <th className="p-3">Fuel Cost</th>
                    <th className="p-3">Post Pc</th>
                    <th className="p-3">Risk Reduction</th>
                    <th className="p-3">Score</th>
                    <th className="p-3 text-right">Select</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60">
                  {evalResult.all_candidates.slice(0, 10).map((cand) => {
                    const isSelected = selectedCandidate?.id === cand.id;
                    return (
                      <tr
                        key={cand.id}
                        onClick={() => setSelectedCandidate(cand)}
                        className={`cursor-pointer transition-colors ${
                          isSelected
                            ? 'bg-blue-950/40 border-l-4 border-blue-500'
                            : 'hover:bg-slate-900/50'
                        }`}
                      >
                        <td className="p-3 font-mono font-bold text-gray-200">{cand.id}</td>
                        <td className="p-3 font-semibold text-white">{cand.direction}</td>
                        <td className="p-3 font-mono text-cyan-300">{cand.delta_v_ms} m/s</td>
                        <td className="p-3 font-mono text-gray-400">{cand.estimated_fuel_cost_kg} kg</td>
                        <td className="p-3 font-mono text-amber-400">{cand.risk_after.toExponential(2)}</td>
                        <td className="p-3 font-mono font-bold text-emerald-400">+{cand.risk_reduction_pct}%</td>
                        <td className="p-3 font-mono font-bold text-blue-400">{cand.score}</td>
                        <td className="p-3 text-right">
                          <button className={`px-2.5 py-1 rounded text-xs font-semibold ${isSelected ? 'bg-blue-600 text-white' : 'bg-slate-800 text-gray-400'}`}>
                            {isSelected ? 'Selected' : 'Choose'}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Selected Candidate Detailed View & Approval Modal */}
          {selectedCandidate && (
            <div className="p-6 rounded-xl glass-panel space-y-6 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center space-x-2 text-white font-bold text-base border-b border-gray-800 pb-3">
                  <Navigation className="w-5 h-5 text-blue-400" />
                  <span>Maneuver Detail ({selectedCandidate.id})</span>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="flex justify-between p-2.5 rounded bg-slate-900">
                    <span className="text-gray-400">Direction:</span>
                    <span className="font-bold text-white font-mono">{selectedCandidate.direction}</span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded bg-slate-900">
                    <span className="text-gray-400">Magnitude ($\Delta v$):</span>
                    <span className="font-bold text-cyan-400 font-mono">{selectedCandidate.delta_v_ms} m/s</span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded bg-slate-900">
                    <span className="text-gray-400">Risk Before:</span>
                    <span className="font-bold text-orange-400 font-mono">{selectedCandidate.risk_before.toExponential(2)}</span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded bg-slate-900">
                    <span className="text-gray-400">Risk After:</span>
                    <span className="font-bold text-emerald-400 font-mono">{selectedCandidate.risk_after.toExponential(2)}</span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded bg-slate-900">
                    <span className="text-gray-400">Risk Reduction:</span>
                    <span className="font-bold text-emerald-400 font-mono">+{selectedCandidate.risk_reduction_pct}%</span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded bg-slate-900">
                    <span className="text-gray-400">Post Miss Distance:</span>
                    <span className="font-bold text-white font-mono">{selectedCandidate.post_maneuver_miss_distance_km} km</span>
                  </div>
                </div>
              </div>

              {/* Approval Box */}
              <div className="space-y-3 pt-4 border-t border-gray-800">
                <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-200">
                  ⚠️ Human Operator Approval Required before digital command payload generation.
                </div>

                {!signedPayload ? (
                  <button
                    onClick={handleApproveAndSign}
                    disabled={isApproving}
                    className="w-full py-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-lg shadow-emerald-900/50"
                  >
                    <FileSignature className="w-4 h-4" />
                    <span>{isApproving ? 'Signing Command...' : 'Approve & Digitally Sign Command'}</span>
                  </button>
                ) : (
                  <div className="space-y-2">
                    <div className="p-3 rounded-lg bg-emerald-950/80 border border-emerald-700/60 text-emerald-300 text-xs font-semibold flex items-center space-x-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>COMMAND DIGITALLY SIGNED</span>
                    </div>
                    <button
                      onClick={() => onNavigate('security')}
                      className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center justify-center space-x-1.5"
                    >
                      <span>Open Security Subsystem & Verify</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
