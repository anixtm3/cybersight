import { useNavigate } from 'react-router-dom';
import { LogOut, ShieldAlert } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const roleLabel = user?.role === 'cyber_cell_officer'
    ? 'Cyber Cell · Tier-1'
    : user?.role === 'bank_nodal_officer'
      ? 'Bank Nodal · Officer'
      : 'I4C · Admin';

  return (
    <header className="fixed top-0 left-0 right-0 h-navbar bg-navy z-40 flex items-center justify-between px-6 border-b border-info/20">
      <div className="flex items-center gap-2.5">
        <div className="w-9 h-9 rounded-lg bg-info/20 flex items-center justify-center">
          <ShieldAlert size={20} className="text-info" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-white font-bold text-lg tracking-tight">CyberSight</span>
          <span className="text-white/40 text-xs font-medium hidden md:inline">
            Cybercrime Intelligence
          </span>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className="inline-flex items-center px-3 py-1.5 rounded-full bg-info text-navy font-medium text-xs">
          {roleLabel}
        </span>
        <button
          onClick={handleLogout}
          className="btn-touch bg-navy-light text-white px-4 hover:bg-navy-dark border border-white/10"
        >
          <LogOut size={16} />
          <span className="text-sm">Logout</span>
        </button>
      </div>
    </header>
  );
}
