import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Map, Bell, Link2, Users, FileText, Settings, ShieldCheck, Send } from 'lucide-react';
import { useAuth, type UserRole } from '@/context/AuthContext';

const allNavItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['cyber_cell_officer', 'bank_nodal_officer', 'i4c_admin'] as UserRole[] },
  { to: '/heatmap', label: 'Heatmap', icon: Map, roles: ['cyber_cell_officer', 'i4c_admin'] as UserRole[] },
  { to: '/alerts', label: 'Alerts', icon: Bell, roles: ['cyber_cell_officer', 'bank_nodal_officer', 'i4c_admin'] as UserRole[] },
  { to: '/blockchain', label: 'Blockchain Log', icon: Link2, roles: ['cyber_cell_officer', 'i4c_admin'] as UserRole[] },
  { to: '/dispatch-log', label: 'Dispatch Log', icon: Send, roles: ['cyber_cell_officer', 'bank_nodal_officer', 'i4c_admin'] as UserRole[] },
  { to: '/registry', label: 'Mule Registry', icon: Users, roles: ['cyber_cell_officer', 'i4c_admin'] as UserRole[] },
  { to: '/reports', label: 'Reports', icon: FileText, roles: ['cyber_cell_officer', 'bank_nodal_officer', 'i4c_admin'] as UserRole[] },
  { to: '/settings', label: 'Settings', icon: Settings, roles: ['cyber_cell_officer', 'bank_nodal_officer', 'i4c_admin'] as UserRole[] },
];

export default function Sidebar() {
  const { pathname } = useLocation();
  const { user } = useAuth();
  const role = user?.role ?? 'cyber_cell_officer';
  const navItems = allNavItems.filter((item) => item.roles.includes(role));

  return (
    <aside className="fixed left-0 top-navbar w-sidebar h-[calc(100vh-60px)] bg-navy z-30 flex flex-col">
      <nav className="flex-1 py-4">
        {navItems.map((item) => {
          const active = pathname === item.to;
          const Icon = item.icon;
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`nav-item ${active ? 'nav-item-active' : ''}`}
            >
              <Icon size={18} className={active ? 'text-info' : 'text-white/60'} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="px-5 py-4 border-t border-white/10">
        <div className="flex items-center gap-2 text-white/50 text-xs">
          <ShieldCheck size={14} />
          <span>Secure Channel · v2.1</span>
        </div>
      </div>
    </aside>
  );
}
