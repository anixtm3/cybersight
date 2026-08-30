import { useEffect, useState, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from 'recharts';
import { Brain, BarChart3 } from 'lucide-react';
import {
  fetchShapExplanation,
  generateShapSummary,
  featureLabel,
  type ShapExplanation,
  type ShapFeatureRow,
} from '@/services/mockApi';
import { Skeleton, RetryErrorState, EmptyState } from './Loading';

const DIRECTION_THRESHOLD = 0.05;

function directionPhrase(row: ShapFeatureRow): string {
  const latSig = Math.abs(row.shap_impact_lat) >= DIRECTION_THRESHOLD;
  const lonSig = Math.abs(row.shap_impact_lon) >= DIRECTION_THRESHOLD;

  if (latSig || lonSig) {
    // North/north-east = positive impact = increases risk; south/south-west = negative = decreases
    const positive = row.shap_impact_lat > 0 || (row.shap_impact_lat === 0 && row.shap_impact_lon > 0);
    return positive ? 'Increases risk score' : 'Decreases risk score';
  }
  return 'negligible directional impact';
}

const barColor = (index: number, total: number): string => {
  const shades = [
    '#1a2e5a', '#244080', '#3457a8', '#4a72c4', '#6b8fd6', '#94aee8', '#bccdf2', '#dde6f8',
  ];
  return shades[Math.min(index, shades.length - 1)];
};

interface ShapExplanationPanelProps {
  caseId: string;
  title?: string;
}

export default function ShapExplanationPanel({ caseId, title }: ShapExplanationPanelProps) {
  const [explanation, setExplanation] = useState<ShapExplanation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    fetchShapExplanation(caseId)
      .then((data) => {
        setExplanation(data);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [caseId]);

  useEffect(() => {
    load();
  }, [load]);

  const header = (
    <div className="flex items-center gap-2 mb-3">
      <Brain size={16} className="text-navy" />
      <h3 className="font-bold text-navy text-sm">{title ?? 'Location Factor Analysis'}</h3>
    </div>
  );

  if (loading) {
    return (
      <div className="tac-card p-4 flex flex-col">
        {header}
        <div className="space-y-3">
          <div className="animate-pulse bg-surface rounded h-4 w-48" />
          <div className="animate-pulse bg-surface rounded w-full" style={{ height: 260 }} />
        </div>
      </div>
    );
  }

  if (error || !explanation) {
    return (
      <div className="tac-card p-4 flex flex-col">
        {header}
        <RetryErrorState
          message="Location factor analysis unavailable — retry fetch."
          onRetry={load}
        />
      </div>
    );
  }

  if (explanation.shap_values.length === 0) {
    return (
      <div className="tac-card p-4 flex flex-col">
        {header}
        <EmptyState
          icon={BarChart3}
          message="No location factor data for this case"
          hint="The model has not generated a factor breakdown for this alert."
        />
      </div>
    );
  }

  const chartData = explanation.shap_values.map((s) => ({
    feature: featureLabel(s.feature),
    combined_importance: s.combined_importance,
    direction: directionPhrase(s),
  }));

  const summary = generateShapSummary(explanation.shap_values);

  return (
    <div className="tac-card p-4 flex flex-col transition-opacity duration-200">
      {header}

      {/* Plain-language summary */}
      <div className="mb-4">
        <p className="label mb-1.5">Summary</p>
        <p className="text-sm text-gray-700 leading-relaxed">{summary}</p>
      </div>

      {/* Main chart — ranked by combined_importance */}
      <div style={{ height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 0, right: 16, left: 8, bottom: 0 }}
          >
            <XAxis type="number" tick={{ fontSize: 11, fill: '#6b7280' }} />
            <YAxis
              type="category"
              dataKey="feature"
              tick={{ fontSize: 11, fill: '#374151' }}
              width={150}
            />
            <Tooltip
              cursor={{ fill: '#f3f4f6' }}
              contentStyle={{
                fontSize: '12px',
                borderRadius: '6px',
                border: '1px solid #e5e7eb',
              }}
              formatter={(v: number) => [v.toFixed(4), 'Combined Importance']}
            />
            <Bar dataKey="combined_importance" radius={[0, 3, 3, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={barColor(i, chartData.length)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Per-feature direction indicators */}
      <div className="border-t border-gray-100 pt-3 mt-2">
        <p className="label mb-2">Directional Influence</p>
        <div className="space-y-1.5">
          {explanation.shap_values.map((row, i) => (
            <div key={row.feature} className="flex items-center justify-between text-xs">
              <span className="text-gray-600 font-medium">
                {featureLabel(row.feature)}
              </span>
              <span className="text-gray-500 italic">
                {directionPhrase(row)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
