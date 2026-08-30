import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import {
  ArrowLeft,
  Users,
  IndianRupee,
  UserX,
  Clock,
  ChevronRight,
  FileX,
  FolderOpen,
  FileDown,
  Loader2,
} from 'lucide-react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import StatCard from '@/components/StatCard';
import ShapExplanationPanel from '@/components/ShapExplanationPanel';
import { getAlertById, formatCurrency, relativeTime, riskBgClass } from '@/mockData';
import { EmptyState } from '@/components/Loading';
import { generateCasePdf } from '@/services/pdfReport';

export default function AlertDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [action, setAction] = useState<string | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const alert = id ? getAlertById(id) : undefined;

  if (!alert) {
    return (
      <div className="min-h-screen bg-white bg-grid">
        <Navbar />
        <Sidebar />
        <main className="ml-sidebar mt-navbar p-6">
          <button
            onClick={() => navigate('/alerts')}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-navy mb-4 transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Alerts
          </button>
          <div className="tac-card p-6">
            <EmptyState
              icon={FileX}
              message={`Case ${id ?? ''} not found`}
              hint="Case may be resolved or purged. Return to alerts list."
            />
            <div className="flex justify-center mt-4">
              <button
                onClick={() => navigate('/alerts')}
                className="btn-touch bg-navy text-white px-4 hover:bg-navy-dark text-sm"
              >
                <FolderOpen size={14} />
                Browse All Alerts
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const totalAtRisk = alert.linkedComplaints.reduce((s, c) => s + c.amount, 0);

  return (
    <div className="min-h-screen bg-white bg-grid animate-fade-in">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-navy mb-4 transition-colors"
        >
          <ArrowLeft size={16} />
          Back to Dashboard
        </button>

        {/* Alert header */}
        <div className="tac-card p-5 mb-6 border-t-[3px] border-t-navy">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-xl font-bold text-navy">{alert.district}, {alert.state}</h1>
                <span className={`inline-flex items-center px-2.5 py-1 rounded text-xs font-bold data-mono ${riskBgClass(alert.riskLevel)}`}>
                  {alert.riskLevel} · {alert.riskScore}
                </span>
              </div>
              <p className="text-sm text-gray-500 mt-1 data-mono">{alert.id} · {alert.fraudType}</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={async () => {
                  setDownloadingPdf(true);
                  try {
                    await generateCasePdf(alert, action);
                  } finally {
                    setDownloadingPdf(false);
                  }
                }}
                disabled={downloadingPdf}
                className="btn-touch bg-navy text-white px-4 py-2 hover:bg-navy-dark disabled:opacity-50 disabled:cursor-wait transition-colors"
              >
                {downloadingPdf ? <Loader2 size={16} className="animate-spin" /> : <FileDown size={16} />}
                <span className="text-sm font-medium">{downloadingPdf ? 'Generating…' : 'Download Report'}</span>
              </button>
              <div className="flex items-center gap-2 bg-surface px-3 py-2 rounded-lg">
                <Clock size={16} className="text-alert" />
                <div>
                  <p className="label">Predicted Withdrawal Window</p>
                  <p className="text-sm font-medium text-navy data-mono">{alert.predictedWithdrawalWindow}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Left column — linked complaints */}
          <div className="col-span-4">
            <div className="tac-card overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-100">
                <h3 className="font-bold text-navy text-sm">
                  Linked Complaints ({alert.linkedComplaints.length})
                </h3>
              </div>
              <div className="max-h-[500px] overflow-y-auto scroll-thin">
                {alert.linkedComplaints.length === 0 ? (
                  <EmptyState
                    icon={FileX}
                    message="No linked complaints on record"
                    hint="Complaints will appear here as they are filed and linked."
                  />
                ) : (
                  alert.linkedComplaints.map((c) => (
                    <div key={c.id} className="px-4 py-3 border-b border-gray-50 hover:bg-surface transition-colors">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono text-gray-500">{c.id}</span>
                        <span className="text-xs text-gray-400 data-mono">{relativeTime(c.timestamp)}</span>
                      </div>
                      <p className="text-sm font-medium text-navy mt-1">{c.fraudType}</p>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-gray-500">by {c.reporter}</span>
                        <span className="text-sm font-bold text-navy data-mono">{formatCurrency(c.amount)}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right column — main panel */}
          <div className="col-span-8 space-y-6">
            {/* Summary stat cards */}
            <div className="grid grid-cols-3 gap-4">
              <StatCard label="Linked Complaints" value={alert.linkedComplaints.length} icon={Users} accent="navy" />
              <StatCard label="Total Amount at Risk" value={formatCurrency(totalAtRisk)} icon={IndianRupee} accent="alert" />
              <StatCard label="Mule Accounts" value={alert.muleAccounts} icon={UserX} accent="danger" />
            </div>

            {/* SHAP */}
            <ShapExplanationPanel caseId={alert.id} title={`Location Factor Analysis — ${alert.id}`} />

            {/* Action row */}
            <div className="tac-card p-5">
              <h3 className="font-bold text-navy text-sm mb-3">Response Actions</h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => setAction('deploy')}
                  className="btn-touch bg-alert text-white px-5 hover:bg-orange-700 font-bold transition-colors"
                >
                  Deploy Team
                </button>
                <button
                  onClick={() => setAction('alert-bank')}
                  className="btn-touch bg-navy text-white px-5 hover:bg-navy-dark transition-colors"
                >
                  Alert Bank/ATM
                </button>
                <button
                  onClick={() => setAction('resolved')}
                  className="btn-touch border-2 border-success text-success px-5 hover:bg-success/5 transition-colors"
                >
                  Mark Resolved
                </button>
                <button
                  onClick={() => setAction('false-positive')}
                  className="btn-touch border-2 border-gray-300 text-gray-600 px-5 hover:bg-surface transition-colors"
                >
                  False Positive
                </button>
              </div>
              {action && (
                <div className="mt-4 flex items-center gap-2 text-sm text-success animate-fade-in">
                  <ChevronRight size={16} />
                  <span>
                    Action &ldquo;{action}&rdquo; recorded for {alert.id}.
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
