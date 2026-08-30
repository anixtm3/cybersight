import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
  accent?: 'navy' | 'alert' | 'success' | 'danger';
  subtitle?: string;
  primary?: boolean;
}

const accentClass = {
  navy: 'border-t-navy',
  alert: 'border-t-alert',
  success: 'border-t-success',
  danger: 'border-t-danger',
};

export default function StatCard({ label, value, icon: Icon, accent = 'navy', subtitle, primary = false }: StatCardProps) {
  return (
    <div
      className={`tac-card ${primary ? 'p-6 tac-card-accent' : 'p-5'} flex items-start justify-between ${accent === 'alert' ? 'tac-card-accent' : ''}`}
    >
      <div>
        <p className={`${primary ? 'text-4xl' : 'text-3xl'} font-bold text-navy leading-none data-mono`}>{value}</p>
        <p className="label mt-2">{label}</p>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
      <div className={`${primary ? 'w-11 h-11' : 'w-10 h-10'} rounded-lg bg-surface flex items-center justify-center shrink-0`}>
        <Icon size={primary ? 22 : 20} strokeWidth={1.5} className="text-navy" />
      </div>
    </div>
  );
}
