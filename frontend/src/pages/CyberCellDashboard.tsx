import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import LiveStatusStrip from '@/components/LiveStatusStrip';
import CommandCentre from '@/components/CommandCentre';
import { useAuth } from '@/context/AuthContext';

export default function CyberCellDashboard() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen bg-white bg-grid animate-fade-in">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <LiveStatusStrip />
        <div className="mb-4 mt-4">
          <h1 className="text-xl font-bold text-navy">Cyber Cell Command Centre</h1>
          <p className="text-sm text-gray-500 mt-1">
            Officer: <span className="data-mono">{user?.name}</span> · Jurisdiction:{' '}
            <span className="data-mono">{user?.jurisdiction}</span>
          </p>
        </div>
        <CommandCentre />
      </main>
    </div>
  );
}
