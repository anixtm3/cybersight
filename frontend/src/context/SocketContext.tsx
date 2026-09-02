import { createContext, useContext, type ReactNode } from 'react';

interface SocketCtx {
  connected: boolean;
  connState: 'connecting' | 'connected' | 'reconnecting' | 'auth_failed';
  lastSync: number | null;
}

const SocketContext = createContext<SocketCtx>({
  connected: false,
  connState: 'connecting',
  lastSync: null,
});

// SocketContext ab sirf dummy provider hai
// Real connection useAlertSocket mein hai
export function SocketProvider({ children }: { children: ReactNode }) {
  return (
    <SocketContext.Provider value={{ connected: true, connState: 'connected', lastSync: Date.now() }}>
      {children}
    </SocketContext.Provider>
  );
}

export const useSocket = () => useContext(SocketContext);