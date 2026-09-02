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

const roleCredentials: Record<UserRole, { username: string; password: string }> = {
  cyber_cell_officer: { username: 'cyber_delhi', password: 'password123' },
  bank_nodal_officer: { username: 'bank_sbi', password: 'password123' },
  i4c_admin: { username: 'i4c_admin', password: 'password123' },
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

  const login = async (role: UserRole) => {
    try {
      const creds = roleCredentials[role];
      const resp = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: creds.username, password: creds.password }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setToken(data.access_token);
        sessionStorage.setItem('cybersight_token', data.access_token);
      } else {
        // fallback — simulated token
        const sim = `sim-${role}-${Date.now()}`;
        setToken(sim);
        sessionStorage.setItem('cybersight_token', sim);
      }
    } catch {
      const sim = `sim-${role}-${Date.now()}`;
      setToken(sim);
      sessionStorage.setItem('cybersight_token', sim);
    }
    setUser(mockProfiles[role]);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    sessionStorage.removeItem('cybersight_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);