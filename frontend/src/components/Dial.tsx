import React from 'react';

type DialProps = {
  value: number;
  max: number;
  unit: string;
  label: string;
  color: string;
  size?: number;
  valueColor?: string;
  main?: boolean; // If true, use larger text for center dial
};

const Dial = ({
  value,
  max,
  unit,
  label,
  color,
  size = 200,
  valueColor,
  main = false,
}: DialProps) => {
  const radius = (size / 2) - 22;
  const circumference = 2 * Math.PI * radius;
  const percent = Math.min(Math.abs(value) / max, 1);
  const dashoffset = circumference * (1 - percent);
  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#e5e7eb"
          className="dark:stroke-zinc-900"
          strokeWidth="22"
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth="18"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={dashoffset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.5s' }}
          transform={`rotate(90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="absolute top-0 left-0 w-full h-full flex flex-col items-center justify-center">
        <span className={`font-bold ${main ? 'text-8xl' : 'text-5xl'} ${valueColor || 'text-black dark:text-white'}`}>{value}</span>
        <span className={`font-semibold ${main ? 'text-3xl' : 'text-xl'} text-gray-500 dark:text-gray-400`}>{unit}</span>
      </div>
    </div>
  );
};

export default Dial; 