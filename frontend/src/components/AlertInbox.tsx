import { useEffect, useRef, useState } from 'react';
import { io, type Socket } from 'socket.io-client';
import { Bell, Wifi, WifiOff } from 'lucide-react';
import type { AlertItem } from '@/mockData';
import { alerts as initialAlerts, socketAlertPool } from '@/mockData';
import AlertListItem from './AlertListItem';
import { Spinner } from './Loading';

const SOCKET_URL = 'http://localhost:3001';

export default function AlertInbox() {
  const [list, setList] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [newId, setNewId] = useState<string | null>(null);
  const socketRef = useRef<Socket | null>(null);
  const poolIndex = useRef(0);

  useEffect(() => {
    const t = setTimeout(() => {
      setList(initialAlerts);
      setLoading(false);
    }, 600);

    const socket = io(SOCKET_URL, {
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
    });
    socketRef.current = socket;

    socket.on('connect', () => setConnected(true));
    socket.on('disconnect', () => setConnected(false));

    const mockInterval = setInterval(() => {
      const base = socketAlertPool[poolIndex.current % socketAlertPool.length];
      poolIndex.current++;
      const newAlert: AlertItem = {
        ...base,
        id: `ALR-2026-${String(100 + poolIndex.current).padStart(3, '0')}`,
        timestamp: new Date().toISOString(),
        status: 'new',
      };
      setList((prev) => [newAlert, ...prev].slice(0, 50));
      setNewId(newAlert.id);
      setTimeout(() => setNewId(null), 2000);
    }, 15000);

    return () => {
      clearTimeout(t);
      clearInterval(mockInterval);
      socket.disconnect();
    };
  }, []);

  return (
    <div className="tac-card flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <Bell size={16} className="text-navy" />
          <h3 className="font-bold text-navy text-sm">Alert Inbox</h3>
          <span className="text-xs text-gray-400 data-mono">({list.length})</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          {connected ? (
            <>
              <Wifi size={14} className="text-success" />
              <span className="text-success font-medium">Live</span>
            </>
          ) : (
            <>
              <WifiOff size={14} className="text-gray-400" />
              <span className="text-gray-400 font-medium">Offline</span>
            </>
          )}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scroll-thin">
        {loading ? (
          <Spinner label="Establishing alert channel…" />
        ) : list.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 gap-2">
            <Bell size={24} className="text-gray-300" />
            <p className="text-sm text-gray-400 data-mono">No active alerts — all zones nominal</p>
          </div>
        ) : (
          list.map((a) => <AlertListItem key={a.id} alert={a} isNew={a.id === newId} />)
        )}
      </div>
    </div>
  );
}
