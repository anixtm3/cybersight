import { useNavigate } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import type { AlertItem } from '@/mockData';
import { relativeTime, riskBgClass } from '@/mockData';

interface AlertListItemProps {
  alert: AlertItem;
  isNew?: boolean;
}

export default function AlertListItem({ alert, isNew }: AlertListItemProps) {
  const navigate = useNavigate();
  return (
    <button
      onClick={() => navigate(`/alerts/${alert.id}`)}
      className={`w-full text-left px-4 py-2.5 border-b border-gray-100 hover:bg-surface hover-transition flex items-center gap-3 ${
        isNew ? 'bg-info/30 animate-pulse' : ''
      }`}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-bold text-navy text-sm truncate">{alert.district}</span>
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold data-mono ${riskBgClass(
              alert.riskLevel
            )}`}
          >
            {alert.riskLevel} · {alert.riskScore}
          </span>
          <span className="text-xs text-gray-500 truncate">{alert.fraudType}</span>
        </div>
        <p className="text-xs text-gray-400 mt-0.5 data-mono">{relativeTime(alert.timestamp)}</p>
      </div>
      <ChevronRight size={16} className="text-gray-300 shrink-0" />
    </button>
  );
}
