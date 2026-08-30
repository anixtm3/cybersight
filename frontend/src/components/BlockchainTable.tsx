import { Link } from 'react-router-dom';
import { Link2Off } from 'lucide-react';
import type { BlockchainLog } from '@/mockData';
import { EmptyState } from './Loading';

interface BlockchainTableProps {
  logs: BlockchainLog[];
  compact?: boolean;
}

const statusClass = {
  Confirmed: 'bg-success/10 text-success border-success/30',
  Pending: 'bg-alert/15 text-alert border-alert/40 font-bold',
  Failed: 'bg-danger/10 text-danger border-danger/30',
};

export default function BlockchainTable({ logs, compact }: BlockchainTableProps) {
  const rows = compact ? logs.slice(0, 6) : logs;
  return (
    <div className="tac-card overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h3 className="font-bold text-navy text-sm">Recent Blockchain Logs</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-surface text-left">
              <th className="label px-4 py-2">Alert ID</th>
              <th className="label px-4 py-2">Tx Hash</th>
              <th className="label px-4 py-2">District</th>
              <th className="label px-4 py-2">Risk</th>
              <th className="label px-4 py-2">Timestamp</th>
              <th className="label px-4 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={6}>
                  <EmptyState
                    icon={Link2Off}
                    message="No blockchain logs match your filters"
                    hint="Try clearing the search or switching to 'All' status."
                  />
                </td>
              </tr>
            ) : (
              rows.map((log, i) => (
                <tr key={log.id} className={`transition-colors hover:bg-surface ${i % 2 ? 'bg-surface/50' : 'bg-white'}`}>
                  <td className="px-4 py-2.5 text-sm text-navy font-medium data-mono">
                    <Link to={`/alerts/${log.alertId}`} className="hover:underline">
                      {log.alertId}
                    </Link>
                  </td>
                  <td className="px-4 py-2.5 text-xs font-mono text-gray-500 max-w-[160px] truncate">
                    {log.txHash}
                  </td>
                  <td className="px-4 py-2.5 text-sm text-gray-700">{log.district}</td>
                  <td className="px-4 py-2.5 text-sm text-gray-700 data-mono">{log.riskScore}</td>
                  <td className="px-4 py-2.5 text-xs text-gray-500 data-mono">
                    {new Date(log.timestamp).toLocaleString('en-IN', {
                      hour: '2-digit',
                      minute: '2-digit',
                      day: '2-digit',
                      month: 'short',
                    })}
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className={`inline-flex items-center px-2.5 py-1 rounded-full border text-xs font-medium ${statusClass[log.status]}`}
                    >
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
