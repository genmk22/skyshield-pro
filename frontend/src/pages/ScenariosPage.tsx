import React, { useState, useEffect } from 'react';
import { fetchScenarios, runScenario } from '../services/api';
import { PlayCircle, CheckCircle2, ArrowRight } from 'lucide-react';
import type { SignedCommandPayload } from '../types';

interface ScenariosPageProps {
  onNavigate: (tab: any) => void;
  setConjunctions: (conjs: any) => void;
  setSignedCommand: (cmd: SignedCommandPayload) => void;
}

export const ScenariosPage: React.FC<ScenariosPageProps> = ({ onNavigate, setConjunctions, setSignedCommand }) => {
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchScenarios().then(setScenarios).catch(console.error);
  }, []);

  const handleRunScenario = async (id: string) => {
    setLoading(true);
    try {
      const res = await runScenario(id);
      setActiveScenario(id);

      if (res.conjunctions) {
        setConjunctions(res.conjunctions);
      }
      if (res.original_signed_command) {
        setSignedCommand(res.original_signed_command);
      }

      if (id === 'scenario-3' || id === 'scenario-4' || id === 'scenario-5') {
        onNavigate('maneuvers');
      } else if (id === 'scenario-7') {
        onNavigate('security');
      } else {
        onNavigate('overview');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-xl glass-panel border border-blue-900/40">
        <div className="flex items-center space-x-2">
          <PlayCircle className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-bold text-white tracking-wide">Offline Presentation Scenarios</h2>
        </div>
        <p className="text-xs text-gray-400 mt-1">
          Pre-packaged demonstration test cases for judging presentations without internet dependencies.
        </p>
      </div>

      {/* Scenarios Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {scenarios.map((sc) => {
          const isActive = activeScenario === sc.id;
          return (
            <div
              key={sc.id}
              className={`p-5 rounded-xl glass-panel space-y-4 border transition-all flex flex-col justify-between ${
                isActive ? 'border-blue-500 bg-blue-950/20' : 'border-gray-800'
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800/50">
                    {sc.category}
                  </span>
                  {isActive && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                </div>
                <h3 className="text-sm font-bold text-white tracking-wide">{sc.name}</h3>
                <p className="text-xs text-gray-400 leading-relaxed">{sc.description}</p>
              </div>

              <button
                onClick={() => handleRunScenario(sc.id)}
                disabled={loading}
                className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center justify-center space-x-1.5 shadow-lg shadow-blue-950/40"
              >
                <span>Run Scenario</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
