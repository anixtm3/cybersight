import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer, ReferenceLine } from 'recharts';
import type { ShapFeature } from '@/mockData';
import { defaultShap } from '@/mockData';

interface ShapChartProps {
  data?: ShapFeature[];
  title?: string;
  compact?: boolean;
}

export default function ShapChart({ data = defaultShap, title = 'SHAP Explanation', compact }: ShapChartProps) {
  const chartData = [...data].sort((a, b) => b.contribution - a.contribution);

  return (
    <div className="tac-card p-4 flex flex-col">
      <h3 className="font-bold text-navy text-sm mb-3">{title}</h3>
      <div style={{ height: compact ? 200 : 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 0, right: 16, left: 8, bottom: 0 }}
          >
            <XAxis type="number" domain={[-0.5, 0.5]} tick={{ fontSize: 11, fill: '#6b7280' }} />
            <YAxis
              type="category"
              dataKey="feature"
              tick={{ fontSize: 11, fill: '#374151' }}
              width={compact ? 110 : 140}
            />
            <Tooltip
              cursor={{ fill: '#f3f4f6' }}
              contentStyle={{
                fontSize: '12px',
                borderRadius: '6px',
                border: '1px solid #e5e7eb',
              }}
              formatter={(v: number) => [v.toFixed(3), 'Contribution']}
            />
            <ReferenceLine x={0} stroke="#d1d5db" />
            <Bar dataKey="contribution" radius={[0, 3, 3, 0]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.contribution >= 0 ? '#1a2e5a' : '#94a3b8'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
