import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react';
import { io, type Socket } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:3001';

type ConnState = 'connecting' | 'connected' | 'reconnecting' | 'disconnected';

interface SocketCtx {
  connected: boolean;
  connState: ConnState;
  lastSync: number | null;
}

const SocketContext = createContext<SocketCtx>({
  connected: false,
  connState: 'connecting',
  lastSync: null,
});

export function SocketProvider({ children }: { children: ReactNode }) {
  const [connState, setConnState] = useState<ConnState>('connecting');
  const [lastSync, setLastSync] = useState<number | null>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    const socket = io(SOCKET_URL, {
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
    });
    socketRef.current = socket;

    socket.on('connect', () => {
      setConnState('connected');
      setLastSync(Date.now());
    });
    socket.on('disconnect', () => setConnState('reconnecting'));
    socket.on('reconnect_attempt', () => setConnState('reconnecting'));
    socket.on('reconnect_failed', () => setConnState('disconnected'));

    const syncInterval = setInterval(() => {
      if (socket.connected) setLastSync(Date.now());
    }, 2000);

    return () => {
      clearInterval(syncInterval);
      socket.disconnect();
    };
  }, []);

  return (
    <SocketContext.Provider value={{ connected: connState === 'connected', connState, lastSync }}>
      {children}
    </SocketContext.Provider>
  );
}

export const useSocket = () => useContext(SocketContext);
