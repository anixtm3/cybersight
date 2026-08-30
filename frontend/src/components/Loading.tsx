import { AlertCircle, Inbox, RefreshCw } from 'lucide-react';

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <div className="w-8 h-8 border-[3px] border-surface border-t-navy rounded-full animate-spin" />
      {label && <p className="label data-mono">{label}</p>}
    </div>
  );
}

export function Skeleton({ className = '', style }: { className?: string; style?: React.CSSProperties }) {
  return <div className={`animate-pulse bg-surface rounded ${className}`} style={style} />;
}

// Skeleton shaped like a table with N rows
export function SkeletonTable({ rows = 6, cols = 6 }: { rows?: number; cols?: number }) {
  return (
    <div className="p-4 space-y-3">
      {/* Header row */}
      <div className="flex gap-3">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      {/* Body rows */}
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex gap-3">
          {Array.from({ length: cols }).map((_, i) => (
            <Skeleton key={i} className="h-5 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

// Skeleton shaped like alert cards
export function SkeletonAlertCards({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="tac-card p-4 border-l-4 border-l-surface">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex-1 space-y-2">
              <div className="flex items-center gap-2">
                <Skeleton className="h-5 w-16 rounded" />
                <Skeleton className="h-3 w-20" />
              </div>
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-3 w-32" />
            </div>
            <div className="space-y-2 text-right">
              <Skeleton className="h-3 w-16" />
              <Skeleton className="h-3 w-20" />
            </div>
          </div>
          <div className="flex gap-4 mb-3">
            <Skeleton className="h-3 w-28" />
            <Skeleton className="h-3 w-32" />
          </div>
          <Skeleton className="h-12 w-full rounded-lg" />
          <div className="border-t border-gray-100 pt-3 mt-3">
            <Skeleton className="h-3 w-24 mb-2" />
            <div className="grid grid-cols-4 gap-2">
              {Array.from({ length: 4 }).map((_, j) => (
                <div key={j} className="flex flex-col items-center gap-1">
                  <Skeleton className="h-4 w-4 rounded" />
                  <Skeleton className="h-2 w-10" />
                  <Skeleton className="h-4 w-12 rounded-full" />
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Skeleton for chart areas
export function SkeletonChart({ height = 260 }: { height?: number }) {
  return (
    <div className="space-y-3">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="w-full rounded" style={{ height }} />
    </div>
  );
}

// Friendly empty state with icon
export function EmptyState({
  icon: Icon = Inbox,
  message,
  hint,
}: {
  icon?: typeof Inbox;
  message: string;
  hint?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-2">
      <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center mb-1">
        <Icon size={20} className="text-gray-300" />
      </div>
      <p className="text-sm text-gray-500 text-center max-w-xs">{message}</p>
      {hint && <p className="text-xs text-gray-400 text-center max-w-xs">{hint}</p>}
    </div>
  );
}

// Error state with retry button
export function RetryErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="border-2 border-danger rounded-lg bg-red-50 px-4 py-4 flex flex-col items-center gap-3">
      <div className="flex items-center gap-2">
        <AlertCircle size={18} className="text-danger" />
        <p className="text-danger font-medium text-sm">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn-touch bg-danger text-white px-4 hover:bg-red-700 text-sm"
        >
          <RefreshCw size={14} />
          Retry
        </button>
      )}
    </div>
  );
}

// Keep the old name for backward compat (no retry button)
export function ErrorState({ message }: { message: string }) {
  return (
    <div className="border-2 border-danger rounded-lg bg-red-50 px-4 py-3">
      <p className="text-danger font-medium text-sm">{message}</p>
    </div>
  );
}

// Persistent reconnecting banner for WebSocket drops
export function ReconnectingBanner() {
  return (
    <div className="flex items-center justify-center gap-2 py-1.5 px-3 bg-alert/10 border-b border-alert/20 rounded-md">
      <RefreshCw size={12} className="text-alert animate-spin" />
      <span className="text-xs text-alert font-medium">Reconnecting to live feed…</span>
    </div>
  );
}

// Cached/mock data indicator
export function CachedDataIndicator() {
  return (
    <span className="inline-flex items-center gap-1 text-[10px] text-gray-400 italic">
      <RefreshCw size={10} />
      showing cached data
    </span>
  );
}
