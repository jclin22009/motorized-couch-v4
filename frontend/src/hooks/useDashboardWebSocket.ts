import { useState, useEffect, useRef } from 'react';
import { z } from 'zod';

const DashboardDataSchema = z.object({
  speed: z.number(),
  battery: z.number(),
  wattage: z.number(),
  range: z.number(),
  voltage: z.number(),
  speedMode: z.number(),
  gear: z.number(),
});

export type DashboardData = z.infer<typeof DashboardDataSchema>;

export function useDashboardWebSocket() {
  const [data, setData] = useState<DashboardData>({
    speed: 0,
    battery: 100,
    wattage: 0,
    range: 0,
    voltage: 0,
    speedMode: 0,
    gear: 0,
  });
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let ws: WebSocket;
    let reconnectTimeout: NodeJS.Timeout;
    const connect = () => {
      ws = new window.WebSocket('ws://localhost:8000/ws/dashboard');
      wsRef.current = ws;
      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        reconnectTimeout = setTimeout(connect, 1000);
      };
      ws.onerror = () => {
        ws.close();
      };
      ws.onmessage = (event) => {
        try {
          const parsed = DashboardDataSchema.parse(JSON.parse(event.data));
          setData(parsed);
        } catch (e) {
          // Ignore parse/validation errors
        }
      };
    };
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      clearTimeout(reconnectTimeout);
    };
  }, []);

  return { ...data, connected };
} 