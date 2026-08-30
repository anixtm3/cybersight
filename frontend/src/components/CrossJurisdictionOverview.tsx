import { useEffect, useState } from 'react';
import { Building2, Activity, Server, Radio, Link2, BrainCircuit } from 'lucide-react';
import { API_BASE_URL } from '@/config';

interface DistrictAlertCounts {
  district: string;
  high: number;
  medium: number;
  low: number;
}

type HealthStatus = 'healthy' | 'degraded' | 'down';

interface SystemService {
  label: string;
  icon: typeof Server;
  status: HealthStatus;
}

const mockDistrictCounts: DistrictAlertCounts[] = [
  { district: 'Delhi', high: 4, medium: 8, low: 12 },
  { district: 'Delhi NCR', high: 3, medium: 6, low: 9 },
  { district: 'Mumbai', high: 2, medium: 5, low: 9 },
  { district: 'Jamtara', high: 5, medium: 4, low: 3 },
  { district: 'Bengaluru', high: 1, medium: 4, low: 7 },
  { district: 'Hyderabad', high: 1, medium: 3, low: 6 },
  { district: 'Agra', high: 1, medium: 2, low: 5 },
  { district: 'Patna', high: 1, medium: 3, low: 4 },
  { district: 'Pune', high: 1, medium: 2, low: 6 },
  { district: 'Lucknow', high: 1, medium: 2, low: 4 },
];

const mockServices: SystemService[] = [
  { label: 'Backend API', icon: Server, status: 'healthy' },
  { label: 'WebSocket Feed', icon: Radio, status: 'healthy' },
  { label: 'Blockchain Node', icon: Link2, status: 'degraded' },
  { label: 'ML Model', icon: BrainCircuit, status: 'healthy' },
];

const healthDot: Record<HealthStatus, string> = {
  healthy: 'bg-success',
  degraded: 'bg-alert',
  down: 'bg-danger',
};

const healthLabel: Record<HealthStatus, string> = {
  healthy: 'Healthy',
  degraded: 'Degraded',
  down: 'Down',
};

const healthText: Record<HealthStatus, string> = {
  healthy: 'text-success',
  degraded: 'text-alert',
  down: 'text-danger',
};

export default function CrossJurisdictionOverview() {
  const [counts, setCounts] = useState<DistrictAlertCounts[]>(mockDistrictCounts);
  const [services, setServices] = useState<SystemService[]>(mockServices);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const resp = await fetch(`${API_BASE_URL}/api/dashboard/cross-jurisdiction`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json() as {
          districts?: DistrictAlertCounts[];
          services?: { label: string; status: HealthStatus }[];
        };
        if (!data || !Array.isArray(data.districts)) throw new Error('Invalid payload');
        if (!cancelled) {
          setCounts(data.districts);
          if (data.services) {
            setServices(data.services.map((s) => {
              const found = mockServices.find((m) => m.label === s.label);
              return {
                label: s.label,
                icon: found?.icon ?? Activity,
                status: s.status,
              };
            }));
          }
        }
      } catch {
        // keep mock defaults
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const totals = counts.reduce(
    (acc, c) => ({
      high: acc.high + c.high,
      medium: acc.medium + c.medium,
      low: acc.low + c.low,
    }),
    { high: 0, medium: 0, low: 0 },
  );

  return (
    <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* District alert counts table */}
      <div className="tac-card overflow-hidden lg:col-span-2">
        <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
          <Building2 size={16} className="text-navy" />
          <h3 className="font-bold text-navy text-sm">Cross-Jurisdiction Alert Counts</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-surface text-left">
                <th className="label px-4 py-2">District</th>
                <th className="label px-4 py-2 text-right">High</th>
                <th className="label px-4 py-2 text-right">Medium</th>
                <th className="label px-4 py-2 text-right">Low</th>
                <th className="label px-4 py-2 text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {counts.map((row, i) => (
                <tr
                  key={row.district}
                  className={`transition-colors hover:bg-surface ${i % 2 ? 'bg-surface/50' : 'bg-white'}`}
                >
                  <td className="px-4 py-2.5 text-sm text-navy font-medium">{row.district}</td>
                  <td className="px-4 py-2.5 text-sm text-danger font-semibold data-mono text-right">
                    {loading ? '—' : row.high}
                  </td>
                  <td className="px-4 py-2.5 text-sm text-alert font-semibold data-mono text-right">
                    {loading ? '—' : row.medium}
                  </td>
                  <td className="px-4 py-2.5 text-sm text-success font-semibold data-mono text-right">
                    {loading ? '—' : row.low}
                  </td>
                  <td className="px-4 py-2.5 text-sm text-navy font-bold data-mono text-right">
                    {loading ? '—' : row.high + row.medium + row.low}
                  </td>
                </tr>
              ))}
              <tr className="border-t-2 border-gray-200 bg-surface font-bold">
                <td className="px-4 py-2.5 text-sm text-navy">All Districts</td>
                <td className="px-4 py-2.5 text-sm text-danger data-mono text-right">
                  {loading ? '—' : totals.high}
                </td>
                <td className="px-4 py-2.5 text-sm text-alert data-mono text-right">
                  {loading ? '—' : totals.medium}
                </td>
                <td className="px-4 py-2.5 text-sm text-success data-mono text-right">
                  {loading ? '—' : totals.low}
                </td>
                <td className="px-4 py-2.5 text-sm text-navy data-mono text-right">
                  {loading ? '—' : totals.high + totals.medium + totals.low}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* System Health strip */}
      <div className="tac-card">
        <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
          <Activity size={16} className="text-navy" />
          <h3 className="font-bold text-navy text-sm">System Health</h3>
        </div>
        <div className="p-4 space-y-4">
          {services.map((svc) => {
            const Icon = svc.icon;
            return (
              <div key={svc.label} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-surface flex items-center justify-center shrink-0">
                    <Icon size={18} strokeWidth={1.5} className="text-navy" />
                  </div>
                  <span className="text-sm font-medium text-navy">{svc.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${healthDot[svc.status]} ${
                    svc.status === 'degraded' ? 'animate-pulse' : ''
                  }`} />
                  <span className={`text-xs font-medium ${healthText[svc.status]}`}>
                    {healthLabel[svc.status]}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
