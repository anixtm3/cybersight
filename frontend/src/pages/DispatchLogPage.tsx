import { useEffect, useState, useCallback } from 'react';
import { Search, Send } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { fetchDispatchLog, type DispatchLogRow, type DispatchChannel, type DeliveryStatus } from '@/services/api';
import { SkeletonTable, EmptyState, RetryErrorState } from '@/components/Loading';
import { Database } from 'lucide-react';

const channelOptions: { value: DispatchChannel | 'all'; label: string }[] = [
  { value: 'all', label: 'All Channels' },
  { value: 'sms', label: 'SMS' },
  { value: 'email', label: 'Email' },
  { value: 'webhook', label: 'Webhook' },
  { value: 'websocket', label: 'Dashboard' },
];

const channelLabel: Record<DispatchChannel, string> = {
  sms: 'SMS',
  email: 'Email',
  webhook: 'Webhook',
  websocket: 'Dashboard',
};

const statusBadge: Record<DeliveryStatus, string> = {
  sent: 'bg-success text-white',
  failed: 'bg-danger text-white',
  pending: 'bg-gray-100 text-gray-500 border border-gray-300',
};

const statusLabel: Record<DeliveryStatus, string> = {
  sent: 'SENT',
  failed: 'FAILED',
  pending: 'PENDING',
};

export default function DispatchLogPage() {
  const [rows, setRows] = useState<DispatchLogRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [isDemo, setIsDemo] = useState(false);
  const [query, setQuery] = useState('');
  const [channelFilter, setChannelFilter] = useState<DispatchChannel | 'all'>('all');

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    fetchDispatchLog(query || undefined, channelFilter === 'all' ? undefined : channelFilter)
      .then((result) => {
        setRows(result.data);
        setIsDemo(result.isDemo);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [query, channelFilter]);

  useEffect(() => {
    const t = setTimeout(() => load(), 300);
    return () => clearTimeout(t);
  }, [load]);

  return (
    <div className="min-h-screen bg-white bg-grid animate-fade-in">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <div className="mb-6">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-navy">Alert Dispatch Log</h1>
            {isDemo && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 text-gray-400 text-[10px] font-medium" title="Live API unreachable — showing cached demo data">
                <Database size={10} />
                cached data
              </span>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Channel-level delivery status for all alert dispatches
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by complaint ID..."
              className="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-navy/20 focus:border-navy transition-colors"
              aria-label="Search by complaint ID"
            />
          </div>
          <div className="inline-flex rounded-lg overflow-hidden border border-gray-200">
            {channelOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setChannelFilter(opt.value)}
                className={`px-3 text-xs font-medium transition-colors ${
                  channelFilter === opt.value
                    ? 'bg-navy text-white'
                    : 'bg-white text-gray-500 hover:bg-surface'
                }`}
                style={{ minHeight: 36 }}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="tac-card overflow-hidden">
          {loading ? (
            <SkeletonTable rows={8} cols={6} />
          ) : error ? (
            <div className="p-6">
              <RetryErrorState
                message="Dispatch log unavailable — retry query."
                onRetry={load}
              />
            </div>
          ) : rows.length === 0 ? (
            <EmptyState
              icon={Send}
              message="No dispatch log entries match current filters"
              hint="Clear the search or switch channel filter."
            />
          ) : (
            <div className="overflow-x-auto transition-opacity duration-200">
              <table className="w-full">
                <thead>
                  <tr className="bg-surface text-left">
                    <th className="label px-4 py-2">Complaint ID</th>
                    <th className="label px-4 py-2">Channel</th>
                    <th className="label px-4 py-2">Recipient</th>
                    <th className="label px-4 py-2">Dispatched At</th>
                    <th className="label px-4 py-2">Status</th>
                    <th className="label px-4 py-2">Response</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, i) => (
                    <tr
                      key={`${row.complaint_id}-${row.channel}-${row.dispatched_at}-${i}`}
                      className={`hover-transition hover:bg-surface ${i % 2 ? 'bg-surface/50' : 'bg-white'}`}
                    >
                      <td className="px-4 py-2 text-sm text-navy font-medium data-mono">
                        {row.complaint_id}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-600">
                        {channelLabel[row.channel]}
                      </td>
                      <td className="px-4 py-2 text-xs font-mono text-gray-500 max-w-[200px] truncate">
                        {row.recipient}
                      </td>
                      <td className="px-4 py-2 text-xs text-gray-500 data-mono">
                        {new Date(row.dispatched_at).toLocaleString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                        })}
                      </td>
                      <td className="px-4 py-2">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold data-mono ${statusBadge[row.delivery_status]}`}>
                          {statusLabel[row.delivery_status]}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-xs font-mono text-gray-400 max-w-[240px] truncate">
                        {row.raw_response ?? '—'}
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
