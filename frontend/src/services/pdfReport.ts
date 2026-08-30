import {
  fetchShapExplanation,
  fetchTopAtmPredictions,
  featureLabel,
  generateShapSummary,
  type ShapFeatureRow,
  type AtmPrediction,
} from '@/services/mockApi';
import { type AlertItem, formatCurrency } from '@/mockData';
import {
  fetchDispatchLog,
  exportReportCsv,
  type ReportRow,
  type ReportType,
  type DispatchLogRow,
} from '@/services/api';

interface DispatchEntry {
  channel: string;
  recipient: string;
  status: string;
  dispatchedAt: string;
}

function esc(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function atmRowsHtml(atms: AtmPrediction[]): string {
  if (atms.length === 0) {
    return '<tr><td colspan="5" style="text-align:center;padding:16px;color:#666;">No ATM predictions available</td></tr>';
  }
  return atms
    .map(
      (a, i) => `
      <tr>
        <td>${i + 1}</td>
        <td style="font-family:monospace;">${esc(a.atm_id)}</td>
        <td>${esc(a.bank_name)}</td>
        <td>${a.lat.toFixed(4)}, ${a.lon.toFixed(4)}</td>
        <td style="text-align:right;font-weight:bold;">${a.risk_score.toFixed(1)}</td>
      </tr>`,
    )
    .join('');
}

function shapRowsHtml(rows: ShapFeatureRow[]): string {
  if (rows.length === 0) {
    return '<tr><td colspan="4" style="text-align:center;padding:16px;color:#666;">No SHAP data available</td></tr>';
  }
  return rows
    .map(
      (r) => `
      <tr>
        <td>${esc(featureLabel(r.feature))}</td>
        <td style="text-align:right;">${r.shap_impact_lat.toFixed(2)}</td>
        <td style="text-align:right;">${r.shap_impact_lon.toFixed(2)}</td>
        <td style="text-align:right;font-weight:bold;">${r.combined_importance.toFixed(2)}</td>
      </tr>`,
    )
    .join('');
}

function dispatchRowsHtml(entries: DispatchEntry[]): string {
  if (entries.length === 0) {
    return '<tr><td colspan="4" style="text-align:center;padding:16px;color:#666;">No dispatch records</td></tr>';
  }
  const statusColor: Record<string, string> = {
    sent: '#15803d',
    failed: '#dc2626',
    pending: '#ea580c',
  };
  return entries
    .map(
      (e) => `
      <tr>
        <td>${esc(e.channel.toUpperCase())}</td>
        <td style="font-family:monospace;font-size:11px;">${esc(e.recipient)}</td>
        <td style="font-weight:bold;color:${statusColor[e.status] ?? '#666'};">${esc(e.status.toUpperCase())}</td>
        <td style="font-family:monospace;font-size:11px;">${formatDate(e.dispatchedAt)}</td>
      </tr>`,
    )
    .join('');
}

function complaintRowsHtml(alert: AlertItem): string {
  if (alert.linkedComplaints.length === 0) {
    return '<tr><td colspan="5" style="text-align:center;padding:16px;color:#666;">No linked complaints</td></tr>';
  }
  return alert.linkedComplaints
    .map(
      (c) => `
      <tr>
        <td style="font-family:monospace;">${esc(c.id)}</td>
        <td>${esc(c.fraudType)}</td>
        <td>${esc(c.reporter)}</td>
        <td style="text-align:right;font-weight:bold;">${formatCurrency(c.amount)}</td>
        <td style="font-family:monospace;font-size:11px;">${formatDate(c.timestamp)}</td>
      </tr>`,
    )
    .join('');
}

export async function generateCasePdf(
  alert: AlertItem,
  investigatorAction: string | null,
): Promise<void> {
  const [shapData, topAtms, dispatchResult] = await Promise.all([
    fetchShapExplanation(alert.id).catch(() => null),
    fetchTopAtmPredictions().catch(() => [] as AtmPrediction[]),
    fetchDispatchLog(alert.id).catch(() => ({ data: [], isDemo: true })),
  ]);

  const shapRows = shapData?.shap_values ?? [];
  const shapSummary = shapRows.length > 0 ? generateShapSummary(shapRows) : 'No SHAP summary available.';
  const dispatchEntries: DispatchEntry[] = (dispatchResult as { data: DispatchLogRow[] }).data.map((d) => ({
    channel: d.channel,
    recipient: d.recipient,
    status: d.delivery_status,
    dispatchedAt: d.dispatched_at,
  }));

  const totalAtRisk = alert.linkedComplaints.reduce((s, c) => s + c.amount, 0);
  const generatedAt = new Date().toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Case Report — ${esc(alert.id)}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1a2e5a; padding: 32px; background: #fff; }
  .header { border-bottom: 3px solid #1a2e5a; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-start; }
  .header h1 { font-size: 22px; font-weight: 800; }
  .header .meta { text-align: right; font-size: 12px; color: #6b7280; }
  .section { margin-bottom: 24px; }
  .section h2 { font-size: 14px; font-weight: 700; color: #1a2e5a; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
  .case-info { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 24px; font-size: 13px; }
  .case-info .label { color: #6b7280; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
  .case-info .value { font-weight: 600; }
  .risk-badge { display: inline-block; padding: 3px 12px; border-radius: 4px; font-size: 12px; font-weight: 700; color: #fff; }
  .risk-CRITICAL { background: #dc2626; }
  .risk-HIGH { background: #ea580c; }
  .risk-MEDIUM { background: #f59e0b; }
  .risk-LOW { background: #15803d; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  thead th { background: #f3f4f6; text-align: left; padding: 8px 10px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.3px; color: #6b7280; border-bottom: 2px solid #e5e7eb; }
  tbody td { padding: 8px 10px; border-bottom: 1px solid #f3f4f6; color: #374151; }
  tbody tr:nth-child(even) { background: #fafafa; }
  .summary-box { background: #f3f4f6; border-radius: 6px; padding: 14px; font-size: 13px; color: #374151; line-height: 1.6; }
  .action-box { background: #dbeafe; border-left: 4px solid #1a2e5a; border-radius: 4px; padding: 12px 16px; font-size: 13px; }
  .footer { margin-top: 32px; border-top: 1px solid #e5e7eb; padding-top: 12px; font-size: 11px; color: #9ca3af; text-align: center; }
  @media print { body { padding: 16px; } .no-print { display: none; } }
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>CyberSight — Case Investigation Report</h1>
      <p style="font-size:13px;color:#6b7280;margin-top:4px;">Indian Cybercrime Coordination Centre (I4C)</p>
    </div>
    <div class="meta">
      <div>Generated: ${generatedAt}</div>
      <div style="margin-top:4px;">Case ID: ${esc(alert.id)}</div>
    </div>
  </div>

  <div class="section">
    <h2>Case Overview</h2>
    <div class="case-info">
      <div>
        <div class="label">Case ID</div>
        <div class="value" style="font-family:monospace;">${esc(alert.id)}</div>
      </div>
      <div>
        <div class="label">District</div>
        <div class="value">${esc(alert.district)}, ${esc(alert.state)}</div>
      </div>
      <div>
        <div class="label">Risk Score</div>
        <div class="value">
          <span class="risk-badge risk-${esc(alert.riskLevel)}">${esc(alert.riskLevel)} · ${alert.riskScore}</span>
        </div>
      </div>
      <div>
        <div class="label">Fraud Type</div>
        <div class="value">${esc(alert.fraudType)}</div>
      </div>
      <div>
        <div class="label">Predicted Withdrawal Window</div>
        <div class="value">${esc(alert.predictedWithdrawalWindow)}</div>
      </div>
      <div>
        <div class="label">Alert Timestamp</div>
        <div class="value" style="font-family:monospace;font-size:12px;">${formatDate(alert.timestamp)}</div>
      </div>
      <div>
        <div class="label">Mule Accounts</div>
        <div class="value">${alert.muleAccounts}</div>
      </div>
      <div>
        <div class="label">Total Amount at Risk</div>
        <div class="value" style="font-weight:800;">${formatCurrency(totalAtRisk)}</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Predicted ATMs — Withdrawal Hotspots</h2>
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>ATM ID</th>
          <th>Bank</th>
          <th>Coordinates (Lat, Lon)</th>
          <th style="text-align:right;">Risk Score</th>
        </tr>
      </thead>
      <tbody>${atmRowsHtml(topAtms)}</tbody>
    </table>
  </div>

  <div class="section">
    <h2>SHAP Feature Attribution — ML Model Explanation</h2>
    <div class="summary-box" style="margin-bottom:12px;">${esc(shapSummary)}</div>
    <table>
      <thead>
        <tr>
          <th>Feature</th>
          <th style="text-align:right;">Lat Impact</th>
          <th style="text-align:right;">Lon Impact</th>
          <th style="text-align:right;">Combined Importance</th>
        </tr>
      </thead>
      <tbody>${shapRowsHtml(shapRows)}</tbody>
    </table>
  </div>

  <div class="section">
    <h2>Dispatch Status — Alert Notifications</h2>
    <table>
      <thead>
        <tr>
          <th>Channel</th>
          <th>Recipient</th>
          <th>Status</th>
          <th>Dispatched At</th>
        </tr>
      </thead>
      <tbody>${dispatchRowsHtml(dispatchEntries)}</tbody>
    </table>
  </div>

  <div class="section">
    <h2>Linked Complaints</h2>
    <table>
      <thead>
        <tr>
          <th>Complaint ID</th>
          <th>Fraud Type</th>
          <th>Reporter</th>
          <th style="text-align:right;">Amount</th>
          <th>Timestamp</th>
        </tr>
      </thead>
      <tbody>${complaintRowsHtml(alert)}</tbody>
    </table>
  </div>

  <div class="section">
    <h2>Investigator Action Taken</h2>
    <div class="action-box">
      ${investigatorAction
        ? `<strong>Action:</strong> ${esc(investigatorAction)}<br/><strong>Recorded at:</strong> ${generatedAt}`
        : '<em>No action recorded yet for this case.</em>'
      }
    </div>
  </div>

  <div class="footer">
    CyberSight — Cybercrime Intelligence Platform · I4C Control Room<br/>
    This report is auto-generated and intended for authorized investigative use only.
  </div>

  <div class="no-print" style="margin-top:24px;text-align:center;">
    <button onclick="window.print()" style="background:#1a2e5a;color:#fff;border:none;padding:10px 24px;border-radius:6px;font-size:14px;cursor:pointer;font-weight:600;">Print / Save as PDF</button>
  </div>
</body>
</html>`;

  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const win = window.open(url, '_blank');
  if (!win) {
    // Popup blocked — fallback: create a download link
    const link = document.createElement('a');
    link.href = url;
    link.download = `case-report-${alert.id}.html`;
    link.click();
  }
  // Clean up after a delay to allow the new window to load
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}

export async function exportCombinedCsv(
  type: ReportType,
  rows: ReportRow[],
): Promise<void> {
  const blob = await exportReportCsv(type, rows);
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  const dateStr = new Date().toISOString().split('T')[0];
  link.download = `cybersight-combined-report-${dateStr}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}
