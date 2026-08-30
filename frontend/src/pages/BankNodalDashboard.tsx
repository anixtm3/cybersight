import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import LiveStatusStrip from '@/components/LiveStatusStrip';
import StatCard from '@/components/StatCard';
import { useAuth } from '@/context/AuthContext';
import { IndianRupee, UserX, Clock } from 'lucide-react';

export default function BankNodalDashboard() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen bg-white bg-grid animate-fade-in">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <LiveStatusStrip />
        <div className="mb-6 mt-4">
          <h1 className="text-xl font-bold text-navy">Bank Nodal Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">
            ATM-linked fraud alerts and freeze-action interface
          </p>
        </div>
        <div className="tac-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="label">Officer</span>
            <span className="text-sm font-medium text-navy">{user?.name}</span>
          </div>
          <div className="flex items-center gap-2 mb-6">
            <span className="label">Institution</span>
            <span className="text-sm font-medium text-navy data-mono">{user?.jurisdiction}</span>
          </div>
          <div className="border-t border-gray-100 pt-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <StatCard label="Total Freezable Amount Today" value="₹12,40,000" icon={IndianRupee} accent="alert" />
              <StatCard label="Accounts Flagged" value={14} icon={UserX} accent="danger" />
              <StatCard label="Pending Freeze Actions" value={3} icon={Clock} accent="navy" />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
