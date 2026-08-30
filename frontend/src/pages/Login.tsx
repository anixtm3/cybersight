import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ShieldCheck, Landmark, Building2, Loader2 } from 'lucide-react';
import { useAuth, type UserRole } from '@/context/AuthContext';

const roleOptions: { role: UserRole; label: string; desc: string; icon: typeof ShieldCheck }[] = [
  {
    role: 'cyber_cell_officer',
    label: 'Cyber Cell Officer',
    desc: 'Jurisdiction-scoped alerts, heatmap, case investigation',
    icon: ShieldCheck,
  },
  {
    role: 'bank_nodal_officer',
    label: 'Bank Nodal Officer',
    desc: 'ATM-linked alerts, freeze-action interface',
    icon: Landmark,
  },
  {
    role: 'i4c_admin',
    label: 'I4C Admin',
    desc: 'Cross-jurisdiction oversight, reports, full registry',
    icon: Building2,
  },
];

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [authenticating, setAuthenticating] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null);

  const handleLogin = (role: UserRole) => {
    setSelectedRole(role);
    setAuthenticating(true);
    // Simulate brief auth delay for smooth UX — no flash
    setTimeout(() => {
      login(role);
      navigate('/dashboard');
    }, 400);
  };

  return (
    <div className="min-h-screen bg-white bg-grid flex items-center justify-center p-6">
      <div className="tac-card w-full max-w-md p-8 animate-fade-in">
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-12 h-12 rounded-lg bg-info/20 flex items-center justify-center mb-4 logo-fade-in">
            <ShieldAlert size={28} className="text-navy" />
          </div>
          <h1 className="text-2xl font-bold text-navy">CyberSight</h1>
          <p className="text-sm text-gray-500 mt-1">Cybercrime Intelligence Platform</p>
        </div>

        <div className="space-y-3">
          <p className="label text-center mb-4">Select your role to continue</p>
          {roleOptions.map(({ role, label, desc, icon: Icon }) => {
            const isThisAuth = authenticating && selectedRole === role;
            return (
              <button
                key={role}
                onClick={() => handleLogin(role)}
                disabled={authenticating}
                className="btn-touch w-full text-left border border-navy/15 bg-white px-4 hover:bg-info/20 hover:border-navy/40 transition-colors group disabled:opacity-50 disabled:cursor-wait"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-surface group-hover:bg-info/30 flex items-center justify-center shrink-0 transition-colors">
                    {isThisAuth ? (
                      <Loader2 size={20} className="text-navy animate-spin" />
                    ) : (
                      <Icon size={20} className="text-navy" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-bold text-navy">{label}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
                  </div>
                  {isThisAuth && (
                    <span className="text-xs text-gray-400 data-mono">Authenticating…</span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
