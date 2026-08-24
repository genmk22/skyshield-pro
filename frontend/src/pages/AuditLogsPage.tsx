import React, { useState, useEffect } from 'react';
import { fetchAuditLogs } from '../services/api';
import type { AuditLogEvent } from '../types';
import { FileText, RefreshCw } from 'lucide-react';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogEvent[]>([]);
  const [loading, setLoading] = useState(false);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await fetchAuditLogs();
      setLogs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-xl glass-panel border border-blue-900/40 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <FileText className="w-6 h-6 text-blue-400" />
          <div>
            <h2 className="text-xl font-bold text-white tracking-wide">System Operations Audit Log</h2>
            <p className="text-xs text-gray-400">Immutable trace of all TLE imports, risk calculations, signature events, and security alerts</p>
          </div>
        </div>

        <button
          onClick={loadLogs}
          className="px-3.5 py-1.5 rounded-lg bg-slate-900 border border-gray-800 text-gray-300 text-xs font-semibold flex items-center space-x-1.5 hover:bg-slate-800"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="p-6 rounded-xl glass-panel space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/90 text-gray-400 uppercase border-b border-gray-800">
              <tr>
                <th className="p-3">Event ID</th>
                <th className="p-3">Timestamp (UTC)</th>
                <th className="p-3">Event Type</th>
                <th className="p-3">Object / Asset</th>
                <th className="p-3">Status</th>
                <th className="p-3">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 text-gray-300">
              {logs.map((evt) => (
                <tr key={evt.id} className="hover:bg-slate-900/50 transition-colors">
                  <td className="p-3 text-blue-400 font-bold">{evt.id}</td>
                  <td className="p-3 text-gray-400">{new Date(evt.timestamp).toISOString().replace('T', ' ').slice(0, 19)}</td>
                  <td className="p-3 font-semibold text-white">{evt.event_type}</td>
                  <td className="p-3 text-gray-300">{evt.object_id}</td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        evt.status === 'SUCCESS'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : 'bg-rose-950 text-rose-400 border border-rose-800'
                      }`}
                    >
                      {evt.status}
                    </span>
                  </td>
                  <td className="p-3 text-gray-400 max-w-xs truncate">
                    {JSON.stringify(evt.details)}
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
