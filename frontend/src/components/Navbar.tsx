import React, { useState, useEffect } from 'react';
import { Shield, Clock, Database, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface NavbarProps {
  liveDataMode: boolean;
  setLiveDataMode: (live: boolean) => void;
  activeThreatCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({ liveDataMode, setLiveDataMode, activeThreatCount }) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const update = () => {
      setTimeStr(new Date().toUTCString().replace('GMT', 'UTC'));
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 border-b border-gray-800 bg-slate-950/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-blue-600/20 border border-blue-500/30 text-blue-400">
          <Shield className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold tracking-wider text-white">SKYSHIELD PRO</h1>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800/50 font-mono font-semibold">
              v1.0.0 (LEO)
            </span>
          </div>
          <p className="text-xs text-gray-400">Physics-Based Satellite Collision Risk & Maneuver Advisory</p>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        {/* UTC Clock */}
        <div className="flex items-center space-x-2 text-xs font-mono text-gray-300 bg-slate-900 px-3 py-1.5 rounded-md border border-gray-800">
          <Clock className="w-3.5 h-3.5 text-blue-400" />
          <span>{timeStr || 'UTC 00:00:00'}</span>
        </div>

        {/* Data Mode Selector Badge */}
        <button
          onClick={() => setLiveDataMode(!liveDataMode)}
          className={`flex items-center space-x-2 text-xs font-semibold px-3 py-1.5 rounded-md border transition-all ${
            liveDataMode
              ? 'bg-emerald-950/70 text-emerald-300 border-emerald-700/60 hover:bg-emerald-900/80'
              : 'bg-indigo-950/70 text-indigo-300 border-indigo-700/60 hover:bg-indigo-900/80'
          }`}
        >
          <Database className="w-3.5 h-3.5" />
          <span>{liveDataMode ? 'LIVE CELESTRAK' : 'DEMO TLE DATA'}</span>
        </button>

        {/* Threat Alert Summary */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-slate-900 border border-gray-800 text-xs font-semibold">
          {activeThreatCount > 0 ? (
            <>
              <AlertTriangle className="w-4 h-4 text-amber-400 animate-pulse" />
              <span className="text-amber-300">{activeThreatCount} ACTIVE CONJUNCTION THREATS</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-300 font-normal">ORBITAL SECTOR CLEAR</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
