import { Calendar, MapPin, Tag, AlertTriangle } from 'lucide-react';
import {
  districtOptions,
  fraudTypeOptions,
  riskLevelOptions,
  type HeatmapFilters,
  type RiskLevel,
  type FraudType,
} from '@/services/mockApi';

interface HeatmapFiltersBarProps {
  filters: HeatmapFilters;
  onChange: (filters: HeatmapFilters) => void;
}

const riskColors: Record<RiskLevel, string> = {
  HIGH: 'bg-danger text-white',
  MEDIUM: 'bg-alert text-white',
  LOW: 'bg-success text-white',
};

export default function HeatmapFiltersBar({ filters, onChange }: HeatmapFiltersBarProps) {
  const toggleRiskLevel = (level: RiskLevel) => {
    const current = filters.riskLevel;
    const next = current.includes(level)
      ? current.filter((l) => l !== level)
      : [...current, level];
    onChange({ ...filters, riskLevel: next });
  };

  return (
    <div className="tac-card p-4 mb-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Date range */}
        <div>
          <label className="label flex items-center gap-1.5 mb-1.5">
            <Calendar size={12} /> Date Range
          </label>
          <div className="flex items-center gap-2">
            <input
              type="date"
              value={filters.dateRange.start}
              onChange={(e) =>
                onChange({ ...filters, dateRange: { ...filters.dateRange, start: e.target.value } })
              }
              className="border border-navy/15 rounded-[3px] px-2 py-1.5 text-xs text-navy data-mono w-full"
              style={{ minHeight: 36 }}
            />
            <span className="text-gray-400 text-xs">→</span>
            <input
              type="date"
              value={filters.dateRange.end}
              onChange={(e) =>
                onChange({ ...filters, dateRange: { ...filters.dateRange, end: e.target.value } })
              }
              className="border border-navy/15 rounded-[3px] px-2 py-1.5 text-xs text-navy data-mono w-full"
              style={{ minHeight: 36 }}
            />
          </div>
        </div>

        {/* District dropdown */}
        <div>
          <label className="label flex items-center gap-1.5 mb-1.5">
            <MapPin size={12} /> District
          </label>
          <select
            value={filters.district}
            onChange={(e) => onChange({ ...filters, district: e.target.value })}
            className="border border-navy/15 rounded-[3px] px-3 py-1.5 text-xs text-navy w-full"
            style={{ minHeight: 36 }}
          >
            {districtOptions.map((d) => (
              <option key={d} value={d}>
                {d === 'all' ? 'All Districts' : d}
              </option>
            ))}
          </select>
        </div>

        {/* Fraud type dropdown */}
        <div>
          <label className="label flex items-center gap-1.5 mb-1.5">
            <Tag size={12} /> Fraud Type
          </label>
          <select
            value={filters.fraudType}
            onChange={(e) => onChange({ ...filters, fraudType: e.target.value as FraudType | 'all' })}
            className="border border-navy/15 rounded-[3px] px-3 py-1.5 text-xs text-navy w-full"
            style={{ minHeight: 36 }}
          >
            {fraudTypeOptions.map((f) => (
              <option key={f} value={f}>
                {f === 'all' ? 'All Fraud Types' : f}
              </option>
            ))}
          </select>
        </div>

        {/* Risk level multi-select */}
        <div>
          <label className="label flex items-center gap-1.5 mb-1.5">
            <AlertTriangle size={12} /> Risk Level
          </label>
          <div className="flex items-center gap-2" style={{ minHeight: 36 }}>
            {riskLevelOptions.map((level) => {
              const active = filters.riskLevel.includes(level);
              return (
                <button
                  key={level}
                  onClick={() => toggleRiskLevel(level)}
                  className={`px-2.5 py-1 rounded-[3px] text-xs font-bold border transition-colors ${
                    active
                      ? `${riskColors[level]} border-transparent`
                      : 'bg-white text-gray-400 border-navy/15 hover:border-navy/30'
                  }`}
                  style={{ minHeight: 32 }}
                >
                  {level}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
