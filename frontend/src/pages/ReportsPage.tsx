import { useEffect, useState, useCallback } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, Legend,
} from 'recharts';
import { Download, FileBarChart, FileX, Calendar, Database, FileSpreadsheet } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { fetchReport, exportReportCsv, type ReportRow, type ReportType } from '@/services/api';
import { exportCombinedCsv } from '@/services/pdfReport';
import { SkeletonTable, EmptyState, RetryErrorState } from '@/components/Loading';

const reportTabs: { key: ReportType; label: string }[] = [
  { key: 'district', label: 'District-wise' },
  { key: 'bank', label: 'Bank-wise' },
  { key: 'fraudType', label: 'Fraud-typology-wise' },
];

const formatCurrency = (n: number): string => '₹' + n.toLocaleString('en-IN', { maximumFractionDigits: 2 });

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<ReportType>('district');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [data, setData] = useState<ReportRow[]>([]);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [exporting, setExporting] = useState(false);
  const [exportingCombined, setExportingCombined] = useState(false);
  const [isDemo, setIsDemo] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    fetchReport(activeTab, dateFrom || undefined, dateTo || undefined)
      .then((result) => {
        setData(result.data);
        setIsDemo(result.isDemo);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [activeTab, dateFrom, dateTo]);

  useEffect(() => {
    load();
  }, [load]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const blob = await exportReportCsv(activeTab, data);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${activeTab}-report.csv`;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      // surface error silently — button state resets
    } finally {
      setExporting(false);
    }
  };

  const handleCombinedExport = async () => {
    setExportingCombined(true);
    try {
      await exportCombinedCsv(activeTab, data);
    } catch {
      // silent
    } finally {
      setExportingCombined(false);
    }
  };

  const chartColors = ['#1a2e5a', '#ea580c', '#15803d', '#dc2626', '#f59e0b', '#244080', '#94a3b8', '#6366f1'];

  const hasData = data.length > 0;

  const chartData = data.map((r) => ({
    name: r.group_label,
    value: r.total_amount_lost,
    complaints: r.complaint_count,
  }));

  return (
    <div className="min-h-screen bg-white bg-grid">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold text-navy">Reports</h1>
              {isDemo && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 text-gray-400 text-[10px] font-medium" title="Live API unreachable — showing cached data">
                  <Database size={10} />
                  cached data
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Aggregate analytics with CSV export
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCombinedExport}
              disabled={loading || error || !hasData || exportingCombined}
              className="btn-touch border border-navy/20 text-navy px-4 hover:bg-surface disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <FileSpreadsheet size={16} />
              <span className="text-sm font-medium">{exportingCombined ? 'Exporting…' : 'Daily Combined CSV'}</span>
            </button>
            <button
              onClick={handleExport}
              disabled={loading || error || !hasData || exporting}
              className="btn-touch bg-navy text-white px-4 hover:bg-navy-dark disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <Download size={16} />
              <span className="text-sm font-medium">{exporting ? 'Exporting…' : 'Export CSV'}</span>
            </button>
          </div>
        </div>

        {/* Date range filter */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-2">
            <Calendar size={14} className="text-gray-400" />
            <label className="label">From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="border border-navy/15 rounded-[3px] px-2 py-1.5 text-xs text-navy data-mono"
              style={{ minHeight: 36 }}
            />
            <span className="text-gray-400 text-xs">→</span>
            <label className="label">To</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="border border-navy/15 rounded-[3px] px-2 py-1.5 text-xs text-navy data-mono"
              style={{ minHeight: 36 }}
            />
          </div>
        </div>

        {/* Tabs */}
        <div className="inline-flex rounded-lg overflow-hidden border border-gray-200 mb-6">
          {reportTabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-navy text-white'
                  : 'bg-white text-gray-500 hover:bg-surface'
              }`}
              style={{ minHeight: 40 }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-7">
              <div className="tac-card overflow-hidden">
                <SkeletonTable rows={6} cols={7} />
              </div>
            </div>
            <div className="col-span-5">
              <div className="tac-card p-4">
                <div className="animate-pulse bg-surface rounded h-4 w-32 mb-3" />
                <div className="animate-pulse bg-surface rounded w-full" style={{ height: 300 }} />
              </div>
            </div>
          </div>
        ) : error ? (
          <RetryErrorState
            message="Report data unavailable — retry fetch."
            onRetry={load}
          />
        ) : !hasData ? (
          <EmptyState
            icon={FileX}
            message="No report data for current selection"
            hint="Switch report type or adjust date range."
          />
        ) : (
          <div className="grid grid-cols-12 gap-6 animate-fade-in">
            {/* Summary table */}
            <div className="col-span-7">
              <div className="tac-card overflow-hidden">
                <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
                  <FileBarChart size={16} className="text-navy" />
                  <h3 className="font-bold text-navy text-sm">
                    {activeTab === 'district' && 'District-wise Aggregate'}
                    {activeTab === 'bank' && 'Bank-wise Aggregate'}
                    {activeTab === 'fraudType' && 'Fraud-typology-wise Aggregate'}
                  </h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-surface text-left">
                        <th className="label px-4 py-2">
                          {activeTab === 'district' ? 'District' : activeTab === 'bank' ? 'Bank' : 'Fraud Type'}
                        </th>
                        <th className="label px-4 py-2">Complaints</th>
                        <th className="label px-4 py-2">Total Lost</th>
                        <th className="label px-4 py-2">Avg Lost</th>
                        <th className="label px-4 py-2">High</th>
                        <th className="label px-4 py-2">Med</th>
                        <th className="label px-4 py-2">Low</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.map((r, i) => (
                        <tr key={r.group_label} className={`hover-transition hover:bg-surface ${i % 2 ? 'bg-surface/50' : 'bg-white'}`}>
                          <td className="px-4 py-2 text-sm text-navy font-medium">{r.group_label}</td>
                          <td className="px-4 py-2 text-sm text-gray-700 data-mono">{r.complaint_count}</td>
                          <td className="px-4 py-2 text-sm text-navy data-mono">{formatCurrency(r.total_amount_lost)}</td>
                          <td className="px-4 py-2 text-sm text-gray-600 data-mono">{formatCurrency(r.avg_amount_lost)}</td>
                          <td className="px-4 py-2 text-sm text-danger data-mono">{r.high_alert_count}</td>
                          <td className="px-4 py-2 text-sm text-alert data-mono">{r.medium_alert_count}</td>
                          <td className="px-4 py-2 text-sm text-success data-mono">{r.low_alert_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Chart */}
            <div className="col-span-5">
              <div className="tac-card p-4">
                <h3 className="font-bold text-navy text-sm mb-3">
                  {activeTab === 'district' && 'Total Amount Lost by District'}
                  {activeTab === 'bank' && 'Total Amount Lost by Bank'}
                  {activeTab === 'fraudType' && 'Complaints by Fraud Type'}
                </h3>
                <div style={{ height: 300 }}>
                  {activeTab === 'fraudType' ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={data.map((r) => ({ name: r.group_label, value: r.complaint_count }))}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          outerRadius={90}
                        >
                          {data.map((_, i) => (
                            <Cell key={i} fill={chartColors[i % chartColors.length]} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ fontSize: '12px', borderRadius: '6px', border: '1px solid #e5e7eb' }}
                        />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={chartData}
                        margin={{ top: 0, right: 16, left: 0, bottom: 40 }}
                      >
                        <XAxis
                          dataKey="name"
                          tick={{ fontSize: 10, fill: '#6b7280' }}
                          angle={-30}
                          textAnchor="end"
                          height={50}
                          interval={0}
                        />
                        <YAxis tick={{ fontSize: 11, fill: '#6b7280' }} />
                        <Tooltip
                          cursor={{ fill: '#f3f4f6' }}
                          contentStyle={{ fontSize: '12px', borderRadius: '6px', border: '1px solid #e5e7eb' }}
                          formatter={(v: number) => [formatCurrency(v), 'Total Lost']}
                        />
                        <Bar dataKey="value" radius={[3, 3, 0, 0]}>
                          {data.map((_, i) => (
                            <Cell key={i} fill={chartColors[i % chartColors.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
