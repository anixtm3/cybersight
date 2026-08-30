import { createContext, useContext, useState, type ReactNode } from 'react';

export type UserRole = 'cyber_cell_officer' | 'bank_nodal_officer' | 'i4c_admin';

export interface CurrentUser {
  name: string;
  role: UserRole;
  jurisdiction: string;
}

interface AuthCtx {
  user: CurrentUser | null;
  token: string | null;
  login: (role: UserRole) => void;
  logout: () => void;
}

// Role profiles — shape (user, login, logout) stays stable for API swap.
const mockProfiles: Record<UserRole, CurrentUser> = {
  cyber_cell_officer: {
    name: 'Inspector R. Sharma',
    role: 'cyber_cell_officer',
    jurisdiction: 'New Delhi Cyber Cell',
  },
  bank_nodal_officer: {
    name: 'A. Mehta',
    role: 'bank_nodal_officer',
    jurisdiction: 'State Bank of India — Nodal Operations',
  },
  i4c_admin: {
    name: 'Director V. Krishnan',
    role: 'i4c_admin',
    jurisdiction: 'I4C Control Room',
  },
};

const AuthContext = createContext<AuthCtx>({
  user: null,
  token: null,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const login = (role: UserRole) => {
    setUser(mockProfiles[role]);
    // Simulated JWT — in production this comes from POST /api/auth/login
    setToken(`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${btoa(JSON.stringify({ role, iat: Date.now() }))}.simulated-signature`);
  };
  const logout = () => {
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
