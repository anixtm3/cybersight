import { useEffect, useState, useCallback } from 'react';
import { X, MapPin, Building, AlertCircle, RefreshCw } from 'lucide-react';
import { fetchATMsForZone, type ATMEntry, type RiskLevel } from '@/services/mockApi';
import { Spinner, EmptyState, RetryErrorState } from './Loading';

interface ZoneDrillDownProps {
  zoneId: string;
  zoneName: string;
  onClose: () => void;
}

const riskBadge: Record<RiskLevel, string> = {
  HIGH: 'bg-danger text-white',
  MEDIUM: 'bg-alert text-white',
  LOW: 'bg-success text-white',
};

export default function ZoneDrillDown({ zoneId, zoneName, onClose }: ZoneDrillDownProps) {
  const [atms, setATMs] = useState<ATMEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    fetchATMsForZone(zoneId)
      .then((data) => {
        setATMs(data);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [zoneId]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-navy/30 z-[500] animate-fade-in"
        onClick={onClose}
      />
      {/* Side panel */}
      <div className="fixed right-0 top-navbar bottom-0 w-[420px] bg-white border-l border-navy/15 z-[600] flex flex-col shadow-xl animate-slide-in-right">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div>
            <h3 className="font-bold text-navy text-sm">{zoneName}</h3>
            <p className="text-xs text-gray-400 mt-0.5 data-mono">{zoneId}</p>
          </div>
          <button
            onClick={onClose}
            className="btn-touch bg-surface text-gray-500 hover:bg-gray-200 px-2"
            aria-label="Close drill-down panel"
          >
            <X size={18} />
          </button>
        </div>

        {/* ATM list */}
        <div className="flex-1 overflow-y-auto scroll-thin p-4">
          {loading ? (
            <Spinner label="Querying ATM registry…" />
          ) : error ? (
            <RetryErrorState
              message="ATM registry unreachable — retry query."
              onRetry={load}
            />
          ) : atms.length === 0 ? (
            <EmptyState
              icon={Building}
              message="No ATMs registered in this zone"
              hint="ATM locations have not been mapped for this district."
            />
          ) : (
            <>
              <p className="label mb-3">
                {atms.length} ATMs — ranked by risk contribution
              </p>
              <div className="space-y-2">
                {atms.map((atm) => (
                  <div
                    key={atm.atmId}
                    className="tac-card p-3 flex items-center gap-3 transition-colors hover:bg-surface"
                  >
                    {/* Rank */}
                    <div className="w-8 h-8 rounded-lg bg-navy text-white flex items-center justify-center shrink-0">
                      <span className="text-sm font-bold data-mono">{atm.rank}</span>
                    </div>

                    {/* Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-bold text-navy data-mono">{atm.atmId}</span>
                        <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold ${riskBadge[atm.riskLevel]}`}>
                          {atm.riskLevel}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 truncate">{atm.bankName}</p>
                      <p className="text-xs text-gray-400 data-mono mt-0.5 flex items-center gap-1">
                        <MapPin size={10} />
                        {atm.lat.toFixed(4)}, {atm.lng.toFixed(4)}
                      </p>
                    </div>

                    {/* Risk contribution */}
                    <div className="text-right shrink-0">
                      <p className="text-[10px] text-gray-400">Risk Score</p>
                      <p className="text-sm font-bold text-navy data-mono">{atm.riskContribution}</p>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
