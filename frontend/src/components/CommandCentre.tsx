import { useRef, useEffect } from 'react';
import { Radio, Wifi, WifiOff, RefreshCw, BellOff, ShieldX } from 'lucide-react';
import { useAlertSocket } from '@/hooks/useAlertSocket';
import { useAuth } from '@/context/AuthContext';
import AlertEventCard from './AlertEventCard';
import { SkeletonAlertCards, EmptyState, ReconnectingBanner, CachedDataIndicator } from './Loading';
import { WS_ALERTS_URL } from '@/config';

const SOCKET_URL: string = WS_ALERTS_URL;

export default function CommandCentre() {
  const { token } = useAuth();
  const { events, connState, isLive, authFailReason } = useAlertSocket(SOCKET_URL, token);
  const scrollRef = useRef<HTMLDivElement>(null);
  const prevCount = useRef(events.length);

  useEffect(() => {
    if (events.length > prevCount.current && scrollRef.current) {
      scrollRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
    prevCount.current = events.length;
  }, [events.length]);

  const connLabel = connState === 'connected' ? 'LIVE'
    : connState === 'reconnecting' ? 'RECONNECTING…'
    : connState === 'auth_failed' ? 'AUTH FAILED'
    : connState === 'mock' ? 'DEMO FEED'
    : 'CONNECTING…';

  const ConnIcon = isLive ? Wifi : connState === 'reconnecting' ? RefreshCw : connState === 'auth_failed' ? ShieldX : WifiOff;
  const connColor = isLive ? 'text-success' : connState === 'reconnecting' ? 'text-alert' : connState === 'auth_failed' ? 'text-danger' : 'text-gray-400';

  const showConnecting = connState === 'connecting' && events.length === 0;
  const showReconnecting = connState === 'reconnecting';
  const showAuthFailed = connState === 'auth_failed';
  const showCached = !isLive;
  const showEmpty = !showConnecting && !showAuthFailed && events.length === 0;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Radio size={18} className="text-navy" />
          <h2 className="text-lg font-bold text-navy">Command Centre</h2>
          <span className="text-xs text-gray-400 data-mono">({events.length} events)</span>
          {showCached && <CachedDataIndicator />}
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          <ConnIcon
            size={14}
            className={`${connColor} ${connState === 'reconnecting' ? 'animate-spin' : ''}`}
          />
          <span className={`${connColor} font-medium data-mono`}>{connLabel}</span>
        </div>
      </div>

      {/* Auth failure banner */}
      {showAuthFailed && (
        <div className="mb-3 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 flex items-start gap-3">
          <ShieldX size={18} className="text-danger shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-bold text-danger">Authentication failed — please log in again</p>
            <p className="text-xs text-gray-600 mt-0.5">
              {authFailReason
                ? `Server reason: ${authFailReason}`
                : 'The alert feed connection was rejected due to an invalid or missing token.'}
            </p>
          </div>
        </div>
      )}

      {/* Reconnecting banner */}
      {showReconnecting && (
        <div className="mb-3">
          <ReconnectingBanner />
        </div>
      )}

      {/* Live feed */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto scroll-thin space-y-3 pr-1 transition-opacity duration-200"
        style={{ maxHeight: 'calc(100vh - 200px)' }}
      >
        {showConnecting ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <div className="w-8 h-8 border-[3px] border-surface border-t-navy rounded-full animate-spin" />
            <p className="label data-mono">Establishing risk feed…</p>
          </div>
        ) : showAuthFailed ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <ShieldX size={32} className="text-danger/60" />
            <p className="text-sm font-medium text-danger">Alert feed disconnected</p>
            <p className="text-xs text-gray-500 text-center max-w-xs">
              Your session token was rejected by the server. Please log out and sign in again to restore the live feed.
            </p>
          </div>
        ) : showEmpty ? (
          <EmptyState
            icon={BellOff}
            message="No active alerts — all zones nominal"
            hint="New predictions will populate this feed in real time."
          />
        ) : (
          events.map((e, i) => <AlertEventCard key={`${e.complaint_id}-${i}`} event={e} />)
        )}
      </div>
    </div>
  );
}
