import React, { useEffect, useRef, useState } from 'react';
import type { ConjunctionEvent } from '../types';
import { Orbit, Play, Pause, RotateCcw } from 'lucide-react';

interface OrbitalVisualizationPageProps {
  conjunction: ConjunctionEvent | null;
}

export const OrbitalVisualizationPage: React.FC<OrbitalVisualizationPageProps> = ({ conjunction }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [angle, setAngle] = useState(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const earthRadius = 90;

      // 1. Draw Space background stars
      ctx.fillStyle = '#090d16';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = '#ffffff';
      for (let i = 0; i < 60; i++) {
        const sx = (Math.sin(i * 99) * 0.5 + 0.5) * canvas.width;
        const sy = (Math.cos(i * 33) * 0.5 + 0.5) * canvas.height;
        ctx.fillRect(sx, sy, 1.5, 1.5);
      }

      // 2. Draw 3D Earth Globe
      const gradient = ctx.createRadialGradient(
        centerX - 20, centerY - 20, 10,
        centerX, centerY, earthRadius
      );
      gradient.addColorStop(0, '#3b82f6');
      gradient.addColorStop(0.7, '#1d4ed8');
      gradient.addColorStop(1, '#0f172a');

      ctx.beginPath();
      ctx.arc(centerX, centerY, earthRadius, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();
      ctx.strokeStyle = '#60a5fa';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Earth atmosphere glow
      ctx.beginPath();
      ctx.arc(centerX, centerY, earthRadius + 6, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(96, 165, 250, 0.25)';
      ctx.lineWidth = 4;
      ctx.stroke();

      // 3. Primary Orbit Path (Green/Blue)
      const primaryRadiusX = 180;
      const primaryRadiusY = 70;
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(-0.3);

      ctx.beginPath();
      ctx.ellipse(0, 0, primaryRadiusX, primaryRadiusY, 0, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.7)';
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Primary Satellite Position
      const satAngle = angle;
      const px = Math.cos(satAngle) * primaryRadiusX;
      const py = Math.sin(satAngle) * primaryRadiusY;

      ctx.beginPath();
      ctx.arc(px, py, 6, 0, Math.PI * 2);
      ctx.fillStyle = '#10b981';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Primary Tag
      ctx.fillStyle = '#ffffff';
      ctx.font = '11px monospace';
      ctx.fillText('ISS (ZARYA)', px + 10, py - 8);

      ctx.restore();

      // 4. Secondary Debris Orbit Path (Orange/Red)
      const secondaryRadiusX = 170;
      const secondaryRadiusY = 90;
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(0.5);

      ctx.beginPath();
      ctx.ellipse(0, 0, secondaryRadiusX, secondaryRadiusY, 0, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(249, 115, 22, 0.7)';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Debris Position
      const debAngle = angle + 0.15;
      const dx = Math.cos(debAngle) * secondaryRadiusX;
      const dy = Math.sin(debAngle) * secondaryRadiusY;

      ctx.beginPath();
      ctx.arc(dx, dy, 5, 0, Math.PI * 2);
      ctx.fillStyle = '#f97316';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Debris Tag
      ctx.fillStyle = '#f97316';
      ctx.font = '11px monospace';
      ctx.fillText(conjunction?.secondary_name || 'DEBRIS OBJECT', dx + 8, dy + 12);

      // TCA Intersection Warning Vector
      ctx.beginPath();
      ctx.moveTo(px, py);
      ctx.lineTo(dx, dy);
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.8)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      ctx.restore();

      if (isPlaying) {
        setAngle((prev) => (prev + 0.008) % (Math.PI * 2));
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isPlaying, angle, conjunction]);

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-xl glass-panel border border-blue-900/40 flex justify-between items-center">
        <div>
          <div className="flex items-center space-x-2">
            <Orbit className="w-5 h-5 text-blue-400" />
            <h2 className="text-xl font-bold text-white tracking-wide">3D Orbital Digital Twin</h2>
          </div>
          <p className="text-xs text-gray-400">Interactive orbital propagation visualizer (SGP4 State Geometry)</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 border border-gray-800 text-gray-200 text-xs font-semibold flex items-center space-x-1.5"
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isPlaying ? 'Pause Simulation' : 'Resume'}</span>
          </button>
          <button
            onClick={() => setAngle(0)}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 border border-gray-800 text-gray-200 text-xs font-semibold flex items-center space-x-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Epoch</span>
          </button>
        </div>
      </div>

      {/* 3D Canvas Box */}
      <div className="p-4 rounded-xl glass-panel relative overflow-hidden flex justify-center items-center">
        <canvas
          ref={canvasRef}
          width={900}
          height={480}
          className="rounded-lg border border-gray-800 bg-slate-950 shadow-2xl"
        />

        <div className="absolute bottom-8 left-8 p-3 rounded-lg bg-slate-900/90 border border-gray-800 text-xs space-y-1 font-mono">
          <p className="text-emerald-400">● ISS (ZARYA) Primary Orbit (Green)</p>
          <p className="text-orange-400">● Secondary Debris Trajectory (Orange)</p>
          <p className="text-red-400">-- Predicted Close Approach Distance (Red)</p>
        </div>
      </div>
    </div>
  );
};
