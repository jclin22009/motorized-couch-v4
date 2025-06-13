import { useState } from 'react';
import { Helmet } from 'react-helmet-async';

const SPEED_MODES = [
  { label: 'Chill' },
  { label: 'Standard' },
  { label: 'Sport' },
  { label: 'Insane' },
  { label: 'Ludicrous' },
];
const GEAR_MODES = ['P', 'R', 'N', 'D'];

export default function HomePage() {
  const [speed, setSpeed] = useState(42); // km/h
  const [battery, setBattery] = useState(76); // % 
  const [speedMode, setSpeedMode] = useState(2); // index
  const [gear, setGear] = useState(3); // index
  const [wattage, setWattage] = useState(1200); // W, demo value
  const [range, setRange] = useState(24); // mi, demo value (38 km ≈ 24 mi)

  // For demo: cycle speed and battery
  // ... existing code ...

  return (
    <>
      <Helmet>
        <title>Motorized Couch Dashboard</title>
      </Helmet>
      <div className="min-h-screen bg-white dark:bg-black flex flex-col items-center justify-center transition-colors">
        {/* Spedometer Gauge */}
        <div className="relative flex flex-col items-center justify-center mb-8">
          <svg width="260" height="260" viewBox="0 0 260 260">
            <circle
              cx="130"
              cy="130"
              r="110"
              stroke="#e5e7eb" // zinc-200 for light
              className="dark:stroke-zinc-900"
              strokeWidth="24"
              fill="none"
            />
            <circle
              cx="130"
              cy="130"
              r="110"
              className="stroke-black dark:stroke-white"
              strokeWidth="18"
              fill="none"
              strokeDasharray={2 * Math.PI * 110}
              strokeDashoffset={2 * Math.PI * 110 * (1 - speed / 160)}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 0.5s' }}
            />
          </svg>
          <div className="absolute top-0 left-0 w-full h-full flex flex-col items-center justify-center">
            <span className="text-7xl font-bold text-black dark:text-white drop-shadow-lg">{speed}</span>
            <span className="text-2xl text-gray-500 dark:text-gray-400">km/h</span>
          </div>
        </div>

        {/* Live Wattage */}
        <div className="mb-8 flex flex-col items-center">
          <span className="text-lg font-semibold text-black dark:text-white">{wattage} W</span>
          <span className="text-xs text-gray-500 dark:text-gray-400">Live Power</span>
        </div>

        {/* Battery and Modes */}
        <div className="flex flex-row items-center gap-12 mb-8">
          {/* Battery */}
          <div className="flex flex-col items-center">
            {/* Estimated Range */}
            <span className="text-sm font-semibold text-black dark:text-white mb-1">{range} mi</span>
            <div className="w-16 h-8 bg-zinc-200 dark:bg-zinc-900 rounded-lg flex items-center justify-center relative border border-zinc-300 dark:border-zinc-700">
              <div
                className="absolute left-0 top-0 h-full rounded-lg bg-green-500 dark:bg-green-700"
                style={{ width: `${battery}%`, transition: 'width 0.5s' }}
              />
              <span className="relative z-10 text-lg font-semibold text-white dark:text-white">{battery}%</span>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">Battery</span>
          </div>

          {/* Speed Modes */}
          <div className="flex flex-col items-center">
            <div className="flex flex-row gap-2">
              {SPEED_MODES.map((mode, idx) => (
                <button
                  key={mode.label}
                  className={`px-3 py-1 rounded-full text-xs font-bold shadow transition-all duration-200 border border-zinc-300 dark:border-zinc-700 focus:outline-none focus:ring-2 focus:ring-black/80 dark:focus:ring-white/80 ${
                    idx === speedMode
                      ? 'bg-black text-white dark:bg-white dark:text-black scale-110'
                      : 'bg-zinc-200 text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400 opacity-60'
                  }`}
                  onClick={() => setSpeedMode(idx)}
                >
                  {mode.label}
                </button>
              ))}
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">Speed Mode</span>
          </div>

          {/* Gear Modes */}
          <div className="flex flex-col items-center">
            <div className="flex flex-row gap-1">
              {GEAR_MODES.map((g, idx) => (
                <button
                  key={g}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-lg font-bold transition-all duration-200 border border-zinc-300 dark:border-zinc-700 focus:outline-none focus:ring-2 focus:ring-black/80 dark:focus:ring-white/80 ${
                    idx === gear
                      ? 'bg-black text-white dark:bg-white dark:text-black scale-110 shadow-lg'
                      : 'bg-zinc-200 text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400'
                  }`}
                  onClick={() => setGear(idx)}
                >
                  {g}
                </button>
              ))}
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">Gear</span>
          </div>
        </div>
      </div>
    </>
  );
}
