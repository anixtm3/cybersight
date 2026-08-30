import { useSocket } from '@/context/SocketContext';

export default function LiveStatusStrip() {
  const { connState, lastSync } = useSocket();

  const isLive = connState === 'connected';
  const dotColor = isLive ? 'bg-success' : connState === 'disconnected' ? 'bg-danger' : 'bg-alert';
  const label = isLive ? 'LIVE' : connState === 'disconnected' ? 'OFFLINE' : 'RECONNECTING';

  const syncText = isLive && lastSync
    ? `Last sync: ${Math.max(0, Math.floor((Date.now() - lastSync) / 1000))}s ago`
    : connState === 'reconnecting'
      ? 'Attempting to re-establish link…'
      : 'No connection';

  return (
    <div className="flex items-center gap-2.5 px-4 py-1.5 bg-navy-dark border-b border-navy-light/30 text-xs">
      <span className={`inline-block w-2 h-2 rounded-full ${dotColor} ${isLive ? 'status-dot-pulse' : ''}`} />
      <span className="data-mono text-info font-bold tracking-wide">{label}</span>
      <span className="text-white/30">·</span>
      <span className="data-mono text-white/50">{syncText}</span>
    </div>
  );
}
