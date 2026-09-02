import { useState, useEffect, useCallback } from 'react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { Search, Link } from 'lucide-react';
import { API_BASE_URL } from '@/config';
import { SkeletonTable, EmptyState, RetryErrorState } from '@/components/Loading';

interface BlockchainEntry {
  alertId: string;
  txHash: string;
  district: string;
  risk: number;
  timestamp: string;
  status: 'Confirmed' | 'Pending' | 'Failed';
}

export default function BlockchainLogPage() {
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [logs, setLogs] = useState<BlockchainEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    const token = sessionStorage.getItem('cybersight_token') ?? '';
    fetch(`${API_BASE_URL}/api/mule-accounts`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: any[]) => {
        const mapped: BlockchainEntry[] = data.map((m, i) => ({
          alertId: `ALR-2026-${String(i + 1).padStart(3, '0')}`,
          txHash: m.blockchain_tx_hash ?? '0x' + '0'.repeat(64),
          district: m.bank_name ?? 'Unknown',
          risk: Math.round((m.risk_score ?? 0.5) * 100),
          timestamp: m.red_flagged_at ?? new Date().toISOString(),
          status: m.blockchain_tx_hash
            ? 'Confirmed'
            : m.is_red_flagged
            ? 'Pending'
            : 'Failed',
        }));
        setLogs(mapped);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = logs.filter((l) => {
    const matchesQuery =
      l.alertId.toLowerCase().includes(query.toLowerCase()) ||
      l.district.toLowerCase().includes(query.toLowerCase()) ||
      l.txHash.toLowerCase().includes(query.toLowerCase());
    const matchesStatus = statusFilter === 'all' || l.status === statusFilter;
    return matchesQuery && matchesStatus;
  });

  return (
    <div className="min-h-screen bg-white bg-grid animate-fade-in">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-navy">Blockchain Log</h1>
          <p className="text-sm text-gray-500 mt-1">
            Immutable audit trail of all alert transactions
          </p>
        </div>

        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by Alert ID, district, or tx hash..."
              className="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-navy/20 focus:border-navy transition-colors"
            />
          </div>
          <div className="inline-flex rounded-lg overflow-hidden border border-gray-200">
            {['all', 'Confirmed', 'Pending', 'Failed'].map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-3 text-xs font-medium transition-colors ${
                  statusFilter === s
                    ? 'bg-navy text-white'
                    : 'bg-white text-gray-500 hover:bg-surface'
                }`}
                style={{ minHeight: 36 }}
              >
                {s === 'all' ? 'All' : s}
              </button>
            ))}
          </div>
        </div>

        <div className="tac-card overflow-hidden">
          {loading ? (
            <SkeletonTable rows={8} cols={6} />
          ) : error ? (
            <div className="p-6">
              <RetryErrorState message="Blockchain log unavailable." onRetry={load} />
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState
              icon={Link}
              message="No blockchain logs match current filters"
              hint="Clear search or switch status filter."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-surface text-left">
                    <th className="label px-4 py-2">Alert ID</th>
                    <th className="label px-4 py-2">Tx Hash</th>
                    <th className="label px-4 py-2">Bank</th>
                    <th className="label px-4 py-2">Risk</th>
                    <th className="label px-4 py-2">Timestamp</th>
                    <th className="label px-4 py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((l, i) => (
                    <tr
                      key={l.alertId}
                      className={`hover-transition hover:bg-surface ${
                        i % 2 ? 'bg-surface/50' : 'bg-white'
                      }`}
                    >
                      <td className="px-4 py-2 text-sm text-navy font-medium data-mono">
                        {l.alertId}
                      </td>
                      <td className="px-4 py-2 text-xs font-mono text-gray-500 max-w-[200px] truncate">
                        {l.txHash}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-600">{l.district}</td>
                      <td className="px-4 py-2">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold data-mono ${
                            l.risk >= 70
                              ? 'bg-danger text-white'
                              : l.risk >= 50
                              ? 'bg-alert text-white'
                              : 'bg-amber-500 text-white'
                          }`}
                        >
                          {l.risk}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-xs text-gray-500 data-mono">
                        {new Date(l.timestamp).toLocaleString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${
                            l.status === 'Confirmed'
                              ? 'bg-success/10 text-success border border-success/30'
                              : l.status === 'Failed'
                              ? 'bg-danger/10 text-danger border border-danger/30'
                              : 'bg-alert/10 text-alert border border-alert/30'
                          }`}
                        >
                          {l.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}