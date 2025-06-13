import { Helmet } from 'react-helmet-async';
import Dial from '../components/Dial';
import { useDashboardWebSocket } from '../hooks/useDashboardWebSocket';

const SPEED_MODES = [
  { label: 'Chill' },
  { label: 'Standard' },
  { label: 'Sport' },
  { label: 'Insane' },
  { label: 'Ludicrous' },
];
const GEAR_MODES = ['P', 'R', 'N', 'D'];

export default function HomePage() {
  const {
    speed,
    battery,
    speedMode,
    gear,
    wattage,
    range,
    voltage,
    connected,
  } = useDashboardWebSocket();

  // Color logic for wattage dial
  const wattageColor = wattage < 0 ? '#2563eb' : '#dc2626'; // blue-600 for regen, red-600 for power
  const wattageValueColor = wattage < 0 ? 'text-blue-600' : 'text-red-600';

  return (
    <>
      <Helmet>
        <title>Motorized Couch Dashboard</title>
      </Helmet>
      <div className="fixed left-0 z-10 flex flex-col items-start m-6">
        <div className="w-40 bg-zinc-200 dark:bg-zinc-900 rounded-xl flex items-center justify-center relative border border-zinc-300 dark:border-zinc-700">
          <div
            className="absolute left-0 top-0 h-full rounded-xl bg-green-500 dark:bg-green-700"
            style={{ width: `${battery}%`, transition: 'width 0.5s' }}
          />
          <div className="relative z-10 flex flex-col items-center justify-center w-full gap-2 py-2">
            <span className="text-2xl font-extrabold text-white dark:text-white leading-none">{range} mi</span>
            <span className="text-xs font-semibold text-white dark:text-white leading-none">{battery}%</span>
          </div>
        </div>
        <span className={`mt-2 text-2xl font-semibold ${connected ? 'text-green-600' : 'text-red-600'}`}>{connected ? 'Live' : 'Offline'}</span>
      </div>

      <div className="min-h-screen h-screen w-screen">
        <div className="bg-white dark:bg-black flex flex-col items-stretch transition-colors relative min-h-0 h-full">
          {/* Main three-dial layout */}
          <div className="flex flex-1 flex-row items-center justify-center gap-16 px-8 pt-8 min-h-0">
            {/* Left Dial: Wattage */}
            <div className="flex flex-col items-center justify-center flex-1">
              <Dial
                value={wattage}
                max={2000}
                unit="W"
                label="Live Power"
                color={wattageColor}
                valueColor={wattageValueColor}
                size={260}
                main={false}
              />
            </div>

            {/* Center Dial: Speed (bigger) */}
            <div className="flex flex-col items-center justify-center flex-1">
              <Dial
                value={speed}
                max={160}
                unit="mph"
                label="Speed"
                color="#0ea5e9" // sky-500 for accent
                size={400}
                main={true}
                valueColor={undefined}
              />
            </div>

            {/* Right Dial: Voltage (yellow) */}
            <div className="flex flex-col items-center justify-center flex-1">
              <Dial
                value={voltage}
                max={60}
                unit="V"
                label="Voltage"
                color="#eab308" // yellow-500
                valueColor="text-yellow-600"
                size={260}
                main={false}
              />
            </div>
          </div>

          {/* Bottom Panel: Speed Mode & Gear */}
          <div className="w-full flex flex-row items-end justify-center gap-8 pb-8 pt-8">
            {/* Speed Modes */}
            <div className="flex flex-col items-center">
              <div className="flex flex-row gap-2 mb-2">
                {SPEED_MODES.map((mode, idx) => (
                  <button
                    key={mode.label}
                    className={`px-3 py-1 rounded-full text-xs font-bold shadow transition-all duration-200 border border-zinc-300 dark:border-zinc-700 focus:outline-none focus:ring-2 focus:ring-black/80 dark:focus:ring-white/80 ${
                      idx === speedMode
                        ? 'bg-black text-white dark:bg-white dark:text-black scale-110'
                        : 'bg-zinc-200 text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400 opacity-60'
                    }`}
                    // No-op: dashboard is read-only
                    onClick={() => {}}
                  >
                    {mode.label}
                  </button>
                ))}
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400">Speed Mode</span>
            </div>
            {/* Gear Modes */}
            <div className="flex flex-col items-center">
              <div className="flex flex-row gap-1 mb-2">
                {GEAR_MODES.map((g, idx) => (
                  <button
                    key={g}
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-lg font-bold transition-all duration-200 border border-zinc-300 dark:border-zinc-700 focus:outline-none focus:ring-2 focus:ring-black/80 dark:focus:ring-white/80 ${
                      idx === gear
                        ? 'bg-black text-white dark:bg-white dark:text-black scale-110 shadow-lg'
                        : 'bg-zinc-200 text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400'
                    }`}
                    // No-op: dashboard is read-only
                    onClick={() => {}}
                  >
                    {g}
                  </button>
                ))}
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400">Gear</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
