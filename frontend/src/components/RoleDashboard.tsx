import { useAuth } from '@/context/AuthContext';
import CyberCellDashboard from '@/pages/CyberCellDashboard';
import BankNodalDashboard from '@/pages/BankNodalDashboard';
import I4CAdminDashboard from '@/pages/I4CAdminDashboard';

export default function RoleDashboard() {
  const { user } = useAuth();

  switch (user?.role) {
    case 'cyber_cell_officer':
      return <CyberCellDashboard />;
    case 'bank_nodal_officer':
      return <BankNodalDashboard />;
    case 'i4c_admin':
      return <I4CAdminDashboard />;
    default:
      return <CyberCellDashboard />;
  }
}
