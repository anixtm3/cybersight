import { useEffect, useState, useCallback } from 'react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { Search, ShieldCheck, Lock, Users } from 'lucide-react';
import { type EvidenceBasis, type MuleAccount } from '@/services/mockApi';
import { API_BASE_URL } from '@/config';
import { SkeletonTable, EmptyState, RetryErrorState, Spinner } from '@/components/Loading';

const evidenceBadge: Record<EvidenceBasis, { label: string; className: string }> = {
  INVESTIGATION_VERIFIED: {
    label: 'INVESTIGATION VERIFIED',
    className: 'bg-success text-white border-success',
  },
  MONITORING_SUSPECTED: {
    label: 'MONITORING SUSPECTED',
    className: 'bg-white text-gray-500 border-gray-300',
  },
};

const riskBadgeClass = (score: number): string => {
  if (score >= 70) return 'bg-danger text-white';
  if (score >= 50) return 'bg-alert text-white';
  return 'bg-amber-500 text-white';
};

export default function MuleRegistryPage() {
  const [accounts, setAccounts] = useState<MuleAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [query, setQuery] = useState('');
  const [evidenceFilter, setEvidenceFilter] = useState<string>('all');
  const [selectedFlagId, setSelectedFlagId] = useState<string | null>(null);
  const [detail, setDetail] = useState<MuleAccount | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState(false);
  const [copied, setCopied] = useState(false);

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
      .then((data) => {
        const mapped = (Array.isArray(data) ? data : []).map((m: any, i: number) => ({
          flag_id: `FLAG-${String(i + 1).padStart(3, '0')}`,
          account_hash: m.account_number
            ? `0x${m.account_number.slice(0, 4)}...${m.account_number.slice(-4)}`
            : '0x????...????',
          tx_hash: m.blockchain_tx_hash ?? '0x' + '0'.repeat(64),
          flagging_authority: m.bank_name ?? 'CyberSight-AutoDispatch',
          evidence_basis: (m.is_red_flagged
            ? 'INVESTIGATION_VERIFIED'
            : 'MONITORING_SUSPECTED') as EvidenceBasis,
          risk_score: Math.round((m.risk_score ?? 0.5) * 100),
          block_timestamp: m.red_flagged_at ?? new Date().toISOString(),
          flag_reason: `Fraud complaint auto-flagged by CyberSight ML`,
        }));
        setAccounts(mapped);
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

  const loadDetail = useCallback(() => {
    if (!selectedFlagId) return;
    setDetailLoading(true);
    setDetailError(false);
    setCopied(false);
    const found = accounts.find((a) => a.flag_id === selectedFlagId);
    if (found) {
      setDetail(found);
      setDetailLoading(false);
    } else {
      setDetailError(true);
      setDetailLoading(false);
    }
  }, [selectedFlagId, accounts]);

  useEffect(() => {
    if (selectedFlagId) loadDetail();
  }, [selectedFlagId, loadDetail]);

  const filtered = accounts.filter((a) => {
    const matchesQuery =
      a.flag_id.toLowerCase().includes(query.toLowerCase()) ||
      a.account_hash.toLowerCase().includes(query.toLowerCase()) ||
      a.flagging_authority.toLowerCase().includes(query.toLowerCase());
    const matchesEvidence =
      evidenceFilter === 'all' || a.evidence_basis === evidenceFilter;
    return matchesQuery && matchesEvidence;
  });

  const copyTxHash = (txHash: string) => {
    navigator.clipboard.writeText(txHash).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="min-h-screen bg-white bg-grid">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-navy">Mule Account Registry</h1>
          <p className="text-sm text-gray-500 mt-1">
            Flagged accounts with on-chain proof — read-only, immutable records
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
              placeholder="Search by Flag ID, account hash, or authority..."
              className="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-navy/20 focus:border-navy transition-colors"
              aria-label="Search mule registry"
            />
          </div>
          <div className="inline-flex rounded-lg overflow-hidden border border-gray-200">
            {['all', 'INVESTIGATION_VERIFIED', 'MONITORING_SUSPECTED'].map((s) => (
              <button
                key={s}
                onClick={() => setEvidenceFilter(s)}
                className={`px-3 text-xs font-medium transition-colors ${
                  evidenceFilter === s
                    ? 'bg-navy text-white'
                    : 'bg-white text-gray-500 hover:bg-surface'
                }`}
                style={{ minHeight: 36 }}
              >
                {s === 'all'
                  ? 'All'
                  : s === 'INVESTIGATION_VERIFIED'
                  ? 'Verified'
                  : 'Suspected'}
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
                message="Registry unavailable — retry connection."
                onRetry={load}
              />
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState
              icon={Users}
              message="No flagged accounts match current filters"
              hint="Clear the search field or switch to 'All' evidence types."
            />
          ) : (
            <div className="overflow-x-auto transition-opacity duration-200">
              <table className="w-full">
                <thead>
                  <tr className="bg-surface text-left">
                    <th className="label px-4 py-2">Flag ID</th>
                    <th className="label px-4 py-2">Account Hash</th>
                    <th className="label px-4 py-2">Risk Score</th>
                    <th className="label px-4 py-2">Flag Reason</th>
                    <th className="label px-4 py-2">Evidence</th>
                    <th className="label px-4 py-2">Flagged Date</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((a, i) => (
                    <tr
                      key={a.flag_id}
                      onClick={() => setSelectedFlagId(a.flag_id)}
                      className={`cursor-pointer hover-transition hover:bg-surface ${
                        i % 2 ? 'bg-surface/50' : 'bg-white'
                      } ${selectedFlagId === a.flag_id ? 'ring-2 ring-navy/30' : ''}`}
                    >
                      <td className="px-4 py-2 text-sm text-navy font-medium data-mono">
                        {a.flag_id}
                      </td>
                      <td className="px-4 py-2 text-xs font-mono text-gray-500">
                        {a.account_hash}
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold data-mono ${riskBadgeClass(
                            a.risk_score
                          )}`}
                        >
                          {a.risk_score}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-600 max-w-[200px] truncate">
                        {a.flag_reason}
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full border text-[10px] font-bold ${
                            evidenceBadge[a.evidence_basis].className
                          }`}
                        >
                          {evidenceBadge[a.evidence_basis].label}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-xs text-gray-500 data-mono">
                        {new Date(a.block_timestamp).toLocaleDateString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Detail panel */}
        {selectedFlagId && (
          <>
            <div
              className="fixed inset-0 bg-navy/30 z-[500] animate-fade-in"
              onClick={() => setSelectedFlagId(null)}
            />
            <div className="fixed right-0 top-navbar bottom-0 w-[480px] bg-white border-l border-navy/15 z-[600] flex flex-col shadow-xl animate-slide-in-right">
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <ShieldCheck size={18} className="text-navy" />
                  <h3 className="font-bold text-navy text-sm">On-Chain Proof</h3>
                </div>
                <button
                  onClick={() => setSelectedFlagId(null)}
                  className="btn-touch bg-surface text-gray-500 hover:bg-gray-200 px-2"
                  aria-label="Close detail panel"
                >
                  <Lock size={16} />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto scroll-thin p-5">
                {detailLoading ? (
                  <Spinner label="Retrieving on-chain proof…" />
                ) : detailError ? (
                  <RetryErrorState
                    message="On-chain proof retrieval failed."
                    onRetry={loadDetail}
                  />
                ) : detail ? (
                  <div className="space-y-4 transition-opacity duration-200">
                    <div>
                      <p className="label mb-1">Flag ID</p>
                      <p className="text-sm font-medium text-navy data-mono">{detail.flag_id}</p>
                    </div>
                    <div>
                      <p className="label mb-1">Account Hash</p>
                      <p className="text-sm font-mono text-gray-600">{detail.account_hash}</p>
                    </div>
                    <div>
                      <p className="label mb-1">Transaction Hash</p>
                      <div className="flex items-center gap-2">
                        <code className="flex-1 text-xs font-mono text-gray-600 bg-surface px-3 py-2 rounded break-all">
                          {detail.tx_hash}
                        </code>
                        <button
                          onClick={() => copyTxHash(detail.tx_hash)}
                          className="btn-touch bg-navy text-white px-3 hover:bg-navy-dark shrink-0"
                          aria-label="Copy transaction hash"
                        >
                          {copied ? 'Copied!' : 'Copy'}
                        </button>
                      </div>
                    </div>
                    <div>
                      <p className="label mb-1">Flagging Authority</p>
                      <p className="text-sm font-medium text-navy data-mono">
                        {detail.flagging_authority}
                      </p>
                    </div>
                    <div>
                      <p className="label mb-1">Evidence Basis</p>
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full border text-xs font-bold ${
                          evidenceBadge[detail.evidence_basis].className
                        }`}
                      >
                        {evidenceBadge[detail.evidence_basis].label}
                      </span>
                    </div>
                    <div>
                      <p className="label mb-1">Risk Score</p>
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded text-sm font-bold data-mono ${riskBadgeClass(
                          detail.risk_score
                        )}`}
                      >
                        {detail.risk_score}
                      </span>
                    </div>
                    <div>
                      <p className="label mb-1">Flag Reason</p>
                      <p className="text-sm text-gray-600">{detail.flag_reason}</p>
                    </div>
                    <div className="border-t border-gray-100 pt-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Lock size={12} className="text-gray-400" />
                        <p className="label">Block Timestamp (immutable)</p>
                      </div>
                      <p className="text-sm text-gray-600 data-mono">
                        {new Date(detail.block_timestamp).toLocaleString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                        })}
                      </p>
                    </div>
                  </div>
                ) : (
                  <RetryErrorState
                    message="On-chain proof for this account unavailable."
                    onRetry={loadDetail}
                  />
                )}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}