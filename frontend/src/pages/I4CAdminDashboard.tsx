import { useEffect, useState } from 'react';
import { AlertTriangle, AlertCircle, ShieldCheck, CalendarDays, MapPin } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import LiveStatusStrip from '@/components/LiveStatusStrip';
import CommandCentre from '@/components/CommandCentre';
import StatCard from '@/components/StatCard';
import CrossJurisdictionOverview from '@/components/CrossJurisdictionOverview';
import { useAuth } from '@/context/AuthContext';
import { API_BASE_URL } from '@/config';

interface DashboardStats {
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  total_this_week: number;
  active_zones: number;
}

const mockStats: DashboardStats = {
  high_alerts: 12,
  medium_alerts: 34,
  low_alerts: 58,
  total_this_week: 104,
  active_zones: 24,
};

export default function I4CAdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>(mockStats);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const resp = await fetch(`${API_BASE_URL}/api/dashboard/stats`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = (await resp.json()) as DashboardStats;
        if (!data || typeof data.high_alerts !== 'number') throw new Error('Invalid stats');
        if (!cancelled) setStats(data);
      } catch {
        // keep mock defaults on failure
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="min-h-screen bg-white bg-grid animate-fade-in">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <LiveStatusStrip />
        <div className="mb-4 mt-4">
          <h1 className="text-xl font-bold text-navy">I4C Admin Console</h1>
          <p className="text-sm text-gray-500 mt-1">
            Administrator: <span className="data-mono">{user?.name}</span> · Control Room:{' '}
            <span className="data-mono">{user?.jurisdiction}</span>
          </p>
        </div>

        {/* Summary stats row */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
          <StatCard
            label="High Alerts"
            value={loading ? '—' : stats.high_alerts}
            icon={AlertTriangle}
            accent="danger"
          />
          <StatCard
            label="Medium Alerts"
            value={loading ? '—' : stats.medium_alerts}
            icon={AlertCircle}
            accent="alert"
          />
          <StatCard
            label="Low Alerts"
            value={loading ? '—' : stats.low_alerts}
            icon={ShieldCheck}
            accent="success"
          />
          <StatCard
            label="Total This Week"
            value={loading ? '—' : stats.total_this_week}
            icon={CalendarDays}
            accent="navy"
          />
          <StatCard
            label="Active Zones"
            value={loading ? '—' : stats.active_zones}
            icon={MapPin}
            accent="navy"
          />
        </div>

        <CommandCentre />

        <CrossJurisdictionOverview />
      </main>
    </div>
  );
}
