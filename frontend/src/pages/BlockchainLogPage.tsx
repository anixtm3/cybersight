import { useState } from 'react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import BlockchainTable from '@/components/BlockchainTable';
import { blockchainLogs } from '@/mockData';
import { Search } from 'lucide-react';

export default function BlockchainLogPage() {
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filtered = blockchainLogs.filter((l) => {
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

        {/* Filters */}
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by Alert ID, district, or tx hash..."
              className="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-navy/20 focus:border-navy transition-colors"
              aria-label="Search blockchain logs"
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

        <BlockchainTable logs={filtered} />
      </main>
    </div>
  );
}
