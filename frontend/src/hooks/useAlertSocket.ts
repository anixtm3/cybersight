import { useEffect, useRef, useState, useCallback } from 'react';
import { generatePredictionEvent, generateInitialEvents, type PredictionEvent } from '@/services/mockApi';
import { WS_ALERTS_URL } from '@/config';

type ConnState = 'connecting' | 'connected' | 'reconnecting' | 'mock' | 'auth_failed';

interface UseAlertSocket {
  events: PredictionEvent[];
  connState: ConnState;
  isLive: boolean;
  authFailReason: string | null;
}

// Wraps native WebSocket. Connects to real backend endpoint by default.
// Sends JWT auth token as first message on open. If token is missing,
// does not connect at all. Handles 4001 close as auth failure.
// If URL is unreachable, falls back to a mock generator that pushes a
// new alert every 5-8 seconds so the UI is demonstrable standalone.
export function useAlertSocket(url: string | null, token: string | null): UseAlertSocket {
  const [events, setEvents] = useState<PredictionEvent[]>([]);
  const [connState, setConnState] = useState<ConnState>('connecting');
  const [authFailReason, setAuthFailReason] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mockTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const scheduleMockAlert = useCallback(() => {
    const delay = 5000 + Math.random() * 3000; // 5-8 seconds
    mockTimer.current = setTimeout(() => {
      setEvents((prev) => [generatePredictionEvent(), ...prev].slice(0, 100));
      scheduleMockAlert();
    }, delay);
  }, []);

  const startMockMode = useCallback(() => {
    setConnState('mock');
    setEvents((prev) => (prev.length === 0 ? generateInitialEvents(6) : prev));
    if (mockTimer.current) clearTimeout(mockTimer.current);
    scheduleMockAlert();
  }, [scheduleMockAlert]);

  const connect = useCallback(() => {
    if (!url) {
      startMockMode();
      return;
    }

    // Do not connect without a token — backend will reject with 4001
    if (!token) {
      startMockMode();
      return;
    }

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      setConnState('connecting');
      setAuthFailReason(null);

      ws.onopen = () => {
        // Send auth token as the very first message
        ws.send(JSON.stringify({ token }));
        setConnState('connected');
        if (mockTimer.current) clearTimeout(mockTimer.current);
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data) as Partial<PredictionEvent>;
          // Ensure dispatch_pending flag is set (WS payload doesn't include dispatch status)
          if (data.dispatch_pending === undefined) {
            data.dispatch_pending = true;
          }
          setEvents((prev) => [data as PredictionEvent, ...prev].slice(0, 100));
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = (ev) => {
        if (ev.code === 4001) {
          // Auth failure — don't retry, won't resolve with same token
          console.error(`WebSocket auth failed (4001): ${ev.reason}`);
          setConnState('auth_failed');
          setAuthFailReason(ev.reason || 'Token required');
          if (mockTimer.current) clearTimeout(mockTimer.current);
          return;
        }

        // Other close codes — normal disconnect or network issue, retry
        setConnState('reconnecting');
        if (!mockTimer.current) scheduleMockAlert();
        reconnectTimer.current = setTimeout(() => connect(), 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      startMockMode();
    }
  }, [url, token, scheduleMockAlert, startMockMode]);

  useEffect(() => {
    // Seed initial events immediately so UI isn't empty
    setEvents(generateInitialEvents(6));

    if (!url || !token) {
      startMockMode();
      return () => {
        if (mockTimer.current) clearTimeout(mockTimer.current);
      };
    }

    // Try connecting with a short timeout — if it fails, go mock
    const fallbackTimer = setTimeout(() => {
      if (connState !== 'connected') startMockMode();
    }, 2000);

    connect();

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (mockTimer.current) clearTimeout(mockTimer.current);
      if (fallbackTimer) clearTimeout(fallbackTimer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, token]);

  return { events, connState, isLive: connState === 'connected', authFailReason };
}
