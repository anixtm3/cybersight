import { useEffect, useState } from 'react';
import { MessageSquare, Mail, Webhook, LayoutDashboard, MapPin, IndianRupee, Clock } from 'lucide-react';
import type { PredictionEvent } from '@/services/mockApi';
import { fetchDispatchLog, type DeliveryStatus } from '@/services/api';

const riskBorder: Record<string, string> = {
  HIGH: 'border-l-danger',
  MEDIUM: 'border-l-alert',
  LOW: 'border-l-success',
};

const riskBadge: Record<string, string> = {
  HIGH: 'bg-danger text-white',
  MEDIUM: 'bg-alert text-white',
  LOW: 'bg-success text-white',
};

const formatCurrency = (n: number): string => '₹' + n.toLocaleString('en-IN');

const channelConfig = [
  { icon: MessageSquare, label: 'SMS', channel: 'sms' as const },
  { icon: Mail, label: 'Email', channel: 'email' as const },
  { icon: Webhook, label: 'Webhook', channel: 'webhook' as const },
  { icon: LayoutDashboard, label: 'Dashboard', channel: 'websocket' as const },
];

const statusBadge: Record<DeliveryStatus, string> = {
  sent: 'bg-success text-white border-success',
  failed: 'bg-danger text-white border-danger',
  pending: 'bg-gray-100 text-gray-500 border-gray-300',
};

const statusLabel: Record<DeliveryStatus, string> = {
  sent: 'SENT',
  failed: 'FAILED',
  pending: 'PENDING',
};

export default function AlertEventCard({ event }: { event: PredictionEvent }) {
  const [channelStatuses, setChannelStatuses] = useState<Record<string, DeliveryStatus>>({
    sms: 'pending',
    email: 'pending',
    webhook: 'pending',
    websocket: 'pending',
  });
  const [loadingDispatch, setLoadingDispatch] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchDispatchLog(event.complaint_id)
      .then((result) => {
        if (cancelled) return;
        const map: Record<string, DeliveryStatus> = {
          sms: 'pending',
          email: 'pending',
          webhook: 'pending',
          websocket: 'pending',
        };
        for (const row of result.data) {
          map[row.channel] = row.delivery_status;
        }
        setChannelStatuses(map);
        setLoadingDispatch(false);
      })
      .catch(() => {
        if (cancelled) return;
        setLoadingDispatch(false);
      });
    return () => { cancelled = true; };
  }, [event.complaint_id]);

  const time = new Date(event.timestamp).toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  return (
    <div className={`tac-card p-4 border-l-4 ${riskBorder[event.alert_level] ?? 'border-l-gray-300'}`}>
      {/* Header row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold data-mono ${riskBadge[event.alert_level] ?? 'bg-gray-400 text-white'}`}>
              {event.alert_level}
            </span>
            <span className="text-xs text-gray-400 data-mono">{time}</span>
          </div>
          <p className="text-sm font-bold text-navy truncate data-mono">{event.complaint_id}</p>
          <p className="text-xs text-gray-500 mt-0.5 data-mono">Tracking: {event.tracking_number}</p>
        </div>
        <div className="text-right shrink-0">
          <p className="text-xs text-gray-400">ATM ID</p>
          <p className="text-xs font-medium text-navy data-mono">{event.atm_id}</p>
        </div>
      </div>

      {/* ATM location + freezable amount */}
      <div className="flex items-center gap-4 mb-3 text-xs">
        <span className="flex items-center gap-1 text-gray-500 data-mono">
          <MapPin size={12} />
          {event.atm_lat.toFixed(4)}, {event.atm_lon.toFixed(4)}
        </span>
        <span className="flex items-center gap-1 text-navy font-medium data-mono">
          <IndianRupee size={12} />
          {formatCurrency(event.freezable_amount)} freezable
        </span>
      </div>

      {/* Recommended action */}
      <div className="bg-surface rounded-lg px-3 py-2 mb-3">
        <p className="label mb-0.5">Recommended Action</p>
        <p className="text-sm text-navy">{event.recommended_action}</p>
      </div>

      {/* Dispatch channels */}
      <div className="border-t border-gray-100 pt-3">
        <div className="flex items-center justify-between mb-2">
          <p className="label">Dispatch Status</p>
          {loadingDispatch && (
            <span className="inline-flex items-center gap-1 text-[10px] text-gray-400 italic">
              <Clock size={10} />
              querying dispatch log…
            </span>
          )}
        </div>
        <div className="grid grid-cols-4 gap-2">
          {channelConfig.map(({ icon: ChannelIcon, label, channel }) => {
            const status = channelStatuses[channel] ?? 'pending';
            return (
              <div key={label} className="flex flex-col items-center gap-1">
                <ChannelIcon size={16} className="text-gray-400" />
                <span className="text-[10px] text-gray-400">{label}</span>
                <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full border text-[10px] font-medium ${statusBadge[status]}`}>
                  {statusLabel[status]}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
