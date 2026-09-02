import { useState, useMemo, useEffect } from 'react';
import { Search, BellOff } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import AlertListItem from '@/components/AlertListItem';
import { Skeleton, EmptyState } from '@/components/Loading';
import { API_BASE_URL } from '@/config';
import { useAuth } from '@/context/AuthContext';

export default function AlertsPage() {
  const { token } = useAuth();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE_URL}/api/alerts/recent?limit=50`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => {
        const mapped = (data.alerts || []).map((a: any) => ({
          id: a.complaint_id,
          district: a.district || a.complaint_id,
          state: a.state || '',
          fraudType: a.fraud_type || '',
          riskScore: a.risk_score || 80,
          riskLevel: a.alert_level,
          timestamp: a.timestamp,
        }));
        setAlerts(mapped);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const filtered = useMemo(() => {
    if (!query.trim()) return alerts;
    const q = query.toLowerCase();
    return alerts.filter(
      (a) =>
        a.id.toLowerCase().includes(q) ||
        a.district.toLowerCase().includes(q) ||
        a.fraudType.toLowerCase().includes(q)
    );
  }, [query, alerts]);

  return (
    <div className="min-h-screen bg-white bg-grid">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-navy">All Alerts</h1>
          <p className="text-sm text-gray-500 mt-1">
            {alerts.length} active alerts across all districts
          </p>
        </div>
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by alert ID, district, or fraud type..."
              className="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-navy/20 focus:border-navy transition-colors"
            />
          </div>
        </div>
        <div className="max-w-2xl tac-card overflow-hidden">
          {loading ? (
            <div className="p-4 space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3 py-3 border-b border-gray-50">
                  <Skeleton className="h-5 w-16 rounded" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                </div>
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState
              icon={BellOff}
              message="No active alerts"
              hint="New predictions will appear here."
            />
          ) : (
            <div>
              {filtered.map((a) => (
                <AlertListItem key={a.id} alert={a} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}