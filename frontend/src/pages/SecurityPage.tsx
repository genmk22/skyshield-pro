import React, { useState } from 'react';
import type { SignedCommandPayload, VerificationResult } from '../types';
import { verifyCommand, tamperCommandDemo } from '../services/api';
import { ShieldCheck, ShieldAlert, CheckCircle2, XCircle, FileCode, Lock } from 'lucide-react';

interface SecurityPageProps {
  signedCommand: SignedCommandPayload | null;
}

export const SecurityPage: React.FC<SecurityPageProps> = ({ signedCommand }) => {
  const [verification, setVerification] = useState<VerificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [tamperedField, setTamperedField] = useState('delta_v_ms');
  const [tamperedVal, setTamperedVal] = useState('99.9');

  const handleVerifyOriginal = async () => {
    if (!signedCommand) return;
    setLoading(true);
    try {
      const res = await verifyCommand(signedCommand);
      setVerification(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateTamper = async () => {
    if (!signedCommand) return;
    setLoading(true);
    try {
      const val = isNaN(Number(tamperedVal)) ? tamperedVal : Number(tamperedVal);
      const res = await tamperCommandDemo(signedCommand, tamperedField, val);
      setVerification(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (!signedCommand) {
    return (
      <div className="p-12 text-center text-gray-400 glass-panel rounded-xl">
        <Lock className="w-12 h-12 text-blue-400 mx-auto mb-3 opacity-60" />
        <h3 className="text-lg font-bold text-white">No Signed Command Available</h3>
        <p className="text-xs text-gray-500 mt-1">Approve a recommended maneuver in the Maneuver Advisor to generate a signed cryptographic payload.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 rounded-xl glass-panel border border-blue-900/40 flex justify-between items-center">
        <div>
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            <h2 className="text-xl font-bold text-white tracking-wide">Cryptographic Security Subsystem</h2>
          </div>
          <p className="text-xs text-gray-400">RSA-2048 Asymmetric Command Hashing & Tamper-Proof Verification</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleVerifyOriginal}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center space-x-1.5 shadow-lg shadow-emerald-950/50"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Verify Untampered Command</span>
          </button>
        </div>
      </div>

      {/* Verification Status Badge Alert */}
      {verification && (
        <div
          className={`p-5 rounded-xl border space-y-2 transition-all ${
            verification.is_valid
              ? 'bg-emerald-950/80 border-emerald-600 text-emerald-200'
              : 'bg-rose-950/90 border-2 border-rose-600 text-rose-100 animate-pulse'
          }`}
        >
          <div className="flex items-center space-x-2 font-bold text-lg">
            {verification.is_valid ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            ) : (
              <XCircle className="w-6 h-6 text-rose-400" />
            )}
            <span>{verification.status_message}</span>
          </div>
          {verification.tampered_fields && (
            <div className="text-xs font-mono text-rose-300 bg-rose-900/40 p-2.5 rounded border border-rose-800/60">
              {verification.tampered_fields.map((f, i) => (
                <p key={i}>⚠️ {f}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Main Grid: Command Payload vs Tampering Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Original Signed Payload */}
        <div className="p-6 rounded-xl glass-panel space-y-4 font-mono text-xs">
          <div className="flex items-center space-x-2 text-white font-bold text-base border-b border-gray-800 pb-3 font-sans">
            <FileCode className="w-5 h-5 text-blue-400" />
            <span>Canonical Signed Command Payload</span>
          </div>

          <div className="space-y-2">
            <p className="text-gray-400 font-sans font-semibold">Command ID:</p>
            <p className="p-2 rounded bg-slate-900 text-blue-400 font-bold">{signedCommand.command.command_id}</p>
          </div>

          <div className="space-y-2">
            <p className="text-gray-400 font-sans font-semibold">Canonical JSON Payload String:</p>
            <pre className="p-3 rounded bg-slate-950 border border-gray-800 text-emerald-400 text-[11px] overflow-x-auto whitespace-pre-wrap">
              {signedCommand.canonical_json}
            </pre>
          </div>

          <div className="space-y-2">
            <p className="text-gray-400 font-sans font-semibold">SHA-256 Digest Hash:</p>
            <p className="p-2.5 rounded bg-slate-950 border border-gray-800 text-amber-400 text-[10px] break-all">
              {signedCommand.payload_hash_sha256}
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-gray-400 font-sans font-semibold">RSA-2048 Signature (Base64):</p>
            <p className="p-2.5 rounded bg-slate-950 border border-gray-800 text-cyan-400 text-[10px] break-all max-h-24 overflow-y-auto">
              {signedCommand.signature_base64}
            </p>
          </div>
        </div>

        {/* Right: Live Command Tampering Demonstration */}
        <div className="p-6 rounded-xl glass-panel space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-white font-bold text-base border-b border-gray-800 pb-3">
              <ShieldAlert className="w-5 h-5 text-rose-400" />
              <span>Simulate Malicious Command Tampering</span>
            </div>

            <p className="text-xs text-gray-400 leading-relaxed">
              Demonstrates security subsystem protection. Altering even a single parameter (e.g. burn magnitude, execution time, or satellite ID) invalidates the SHA-256 digest hash and causes cryptographic signature verification to fail immediately.
            </p>

            <div className="space-y-3 bg-slate-900 p-4 rounded-lg border border-gray-800 text-xs">
              <div>
                <label className="block text-gray-300 font-semibold mb-1">Target Field to Tamper:</label>
                <select
                  value={tamperedField}
                  onChange={(e) => setTamperedField(e.target.value)}
                  className="w-full bg-slate-950 border border-gray-800 rounded px-3 py-2 text-gray-200 focus:outline-none focus:border-rose-500"
                >
                  <option value="delta_v_ms">delta_v_ms (Burn Delta-V)</option>
                  <option value="direction">direction (Burn Direction)</option>
                  <option value="execution_time">execution_time (Execution Epoch)</option>
                  <option value="satellite_id">satellite_id (Target Satellite)</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-300 font-semibold mb-1">Malicious Tampered Value:</label>
                <input
                  type="text"
                  value={tamperedVal}
                  onChange={(e) => setTamperedVal(e.target.value)}
                  className="w-full bg-slate-950 border border-gray-800 rounded px-3 py-2 text-gray-200 focus:outline-none focus:border-rose-500 font-mono"
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleSimulateTamper}
            disabled={loading}
            className="w-full py-3 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-lg shadow-rose-950/60"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Simulate Tampering & Verify Payload</span>
          </button>
        </div>
      </div>
    </div>
  );
};
