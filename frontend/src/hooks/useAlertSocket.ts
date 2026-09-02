import { useEffect, useRef, useState, useCallback } from 'react';
import type { PredictionEvent } from '@/services/mockApi';
import { API_BASE_URL } from '@/config';

type ConnState = 'connecting' | 'connected' | 'reconnecting' | 'auth_failed';

interface UseAlertSocket {
  events: PredictionEvent[];
  connState: ConnState;
  isLive: boolean;
  authFailReason: string | null;
}

export function useAlertSocket(url: string | null, token: string | null): UseAlertSocket {
  const [events, setEvents] = useState<PredictionEvent[]>([]);
  const [connState, setConnState] = useState<ConnState>('connecting');
  const [authFailReason, setAuthFailReason] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);

  const fetchRecentAlerts = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/alerts/recent?limit=20`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = await res.json();
      if (data.alerts && data.alerts.length > 0) {
        setEvents(data.alerts as PredictionEvent[]);
      }
    } catch {
      // silent fail
    }
  }, [token]);

  const connect = useCallback(() => {
    if (!url || !token) return;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      setConnState('connecting');
      setAuthFailReason(null);

      ws.onopen = () => {
        ws.send(JSON.stringify({ token }));
        setConnState('connected');
        reconnectAttempts.current = 0;
        fetchRecentAlerts();
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data) as Partial<PredictionEvent>;
          if (data.type === 'ping') return;
          setEvents((prev) => [data as PredictionEvent, ...prev].slice(0, 100));
        } catch {
          // ignore malformed
        }
      };

      ws.onclose = (ev) => {
        if (ev.code === 4001) {
          setConnState('auth_failed');
          setAuthFailReason(ev.reason || 'Token required');
          return;
        }
        if (reconnectAttempts.current < 5) {
          setConnState('reconnecting');
          const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 15000);
          reconnectAttempts.current += 1;
          reconnectTimer.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      setConnState('reconnecting');
    }
  }, [url, token, fetchRecentAlerts]);

  useEffect(() => {
    if (!url || !token) {
      setConnState('reconnecting');
      return;
    }
    connect();

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [url, token]);

  return {
    events,
    connState,
    isLive: connState === 'connected',
    authFailReason,
  };
}