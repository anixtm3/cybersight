import axios from 'axios';
import { API_BASE_URL } from '@/config';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export interface ApiAlert {
  id: string;
  district: string;
  state: string;
  riskScore: number;
  riskLevel: string;
  fraudType: string;
  timestamp: string;
}

export const fetchAlerts = async (): Promise<ApiAlert[]> => {
  const { data } = await apiClient.get<ApiAlert[]>('/alerts');
  return data;
};

export const fetchAlertById = async (id: string): Promise<ApiAlert | null> => {
  const { data } = await apiClient.get<ApiAlert>(`/alerts/${id}`);
  return data;
};

export const fetchBlockchainLogs = async () => {
  const { data } = await apiClient.get('/blockchain/logs');
  return data;
};

export const postAlertAction = async (alertId: string, action: string) => {
  const { data } = await apiClient.post(`/alerts/${alertId}/action`, { action });
  return data;
};

// ============================================================
// REPORTS
// ============================================================

export type ReportType = 'district' | 'bank' | 'fraudType';

export interface ReportRow {
  group_label: string;
  complaint_count: number;
  total_amount_lost: number;
  avg_amount_lost: number;
  high_alert_count: number;
  medium_alert_count: number;
  low_alert_count: number;
}

export interface FetchResult<T> {
  data: T;
  isDemo: boolean;
}

// --- Mock fallback data (used when API fails or returns empty) ---

const mockDispatchLog: DispatchLogRow[] = [
  { complaint_id: 'NCCT-202409001', channel: 'sms', recipient: '+91-98xxx-xxx42', dispatched_at: '2026-08-29T09:14:22Z', delivery_status: 'sent', raw_response: 'ACK msg_id=DLV44820' },
  { complaint_id: 'NCCT-202409002', channel: 'email', recipient: 'cybercell.delhi@nic.in', dispatched_at: '2026-08-29T09:15:10Z', delivery_status: 'sent', raw_response: 'SMTP 250 OK queued' },
  { complaint_id: 'NCCT-202409003', channel: 'webhook', recipient: 'https://api.sbi.co.in/fraud-alert', dispatched_at: '2026-08-29T09:16:45Z', delivery_status: 'sent', raw_response: 'HTTP 200 {"ack":"yes"}' },
  { complaint_id: 'NCCT-202409004', channel: 'websocket', recipient: 'dashboard:cyber-cell-mumbai', dispatched_at: '2026-08-29T09:17:30Z', delivery_status: 'sent', raw_response: 'ws push ok' },
  { complaint_id: 'NCCT-202409005', channel: 'sms', recipient: '+91-70xxx-xxx18', dispatched_at: '2026-08-29T09:18:05Z', delivery_status: 'failed', raw_response: 'ERR carrier timeout' },
  { complaint_id: 'NCCT-202409006', channel: 'email', recipient: 'nodal.hdfc@hdfcbank.net', dispatched_at: '2026-08-29T09:19:12Z', delivery_status: 'sent', raw_response: 'SMTP 250 OK queued' },
  { complaint_id: 'NCCT-202409007', channel: 'webhook', recipient: 'https://api.icici.co.in/alert-ingest', dispatched_at: '2026-08-29T09:20:33Z', delivery_status: 'sent', raw_response: 'HTTP 200 {"status":"received"}' },
  { complaint_id: 'NCCT-202409008', channel: 'websocket', recipient: 'dashboard:i4c-central-ops', dispatched_at: '2026-08-29T09:21:50Z', delivery_status: 'pending', raw_response: null },
  { complaint_id: 'NCCT-202409009', channel: 'sms', recipient: '+91-99xxx-xxx77', dispatched_at: '2026-08-29T09:22:15Z', delivery_status: 'sent', raw_response: 'ACK msg_id=DLV44891' },
  { complaint_id: 'NCCT-202409010', channel: 'email', recipient: 'sp.jamtara@jhpol.gov.in', dispatched_at: '2026-08-29T09:23:40Z', delivery_status: 'sent', raw_response: 'SMTP 250 OK queued' },
];

const mockReportDistrict: ReportRow[] = [
  { group_label: 'Delhi', complaint_count: 1840, total_amount_lost: 28400000, avg_amount_lost: 15435, high_alert_count: 42, medium_alert_count: 68, low_alert_count: 24 },
  { group_label: 'Delhi NCR', complaint_count: 1150, total_amount_lost: 16700000, avg_amount_lost: 14522, high_alert_count: 28, medium_alert_count: 45, low_alert_count: 18 },
  { group_label: 'Mumbai', complaint_count: 1150, total_amount_lost: 14200000, avg_amount_lost: 12348, high_alert_count: 22, medium_alert_count: 38, low_alert_count: 15 },
  { group_label: 'Jamtara', complaint_count: 460, total_amount_lost: 5800000, avg_amount_lost: 12609, high_alert_count: 31, medium_alert_count: 12, low_alert_count: 4 },
  { group_label: 'Bengaluru', complaint_count: 820, total_amount_lost: 9800000, avg_amount_lost: 11951, high_alert_count: 18, medium_alert_count: 29, low_alert_count: 12 },
  { group_label: 'Hyderabad', complaint_count: 640, total_amount_lost: 7200000, avg_amount_lost: 11250, high_alert_count: 14, medium_alert_count: 22, low_alert_count: 9 },
  { group_label: 'Agra', complaint_count: 310, total_amount_lost: 3400000, avg_amount_lost: 10968, high_alert_count: 9, medium_alert_count: 14, low_alert_count: 6 },
  { group_label: 'Patna', complaint_count: 480, total_amount_lost: 5100000, avg_amount_lost: 10625, high_alert_count: 12, medium_alert_count: 18, low_alert_count: 7 },
  { group_label: 'Pune', complaint_count: 590, total_amount_lost: 6600000, avg_amount_lost: 11186, high_alert_count: 11, medium_alert_count: 20, low_alert_count: 8 },
  { group_label: 'Lucknow', complaint_count: 430, total_amount_lost: 4700000, avg_amount_lost: 10930, high_alert_count: 10, medium_alert_count: 16, low_alert_count: 6 },
];

const mockReportBank: ReportRow[] = [
  { group_label: 'State Bank of India', complaint_count: 840, total_amount_lost: 11200000, avg_amount_lost: 13333, high_alert_count: 28, medium_alert_count: 42, low_alert_count: 15 },
  { group_label: 'HDFC Bank', complaint_count: 620, total_amount_lost: 8400000, avg_amount_lost: 13548, high_alert_count: 20, medium_alert_count: 31, low_alert_count: 12 },
  { group_label: 'ICICI Bank', complaint_count: 510, total_amount_lost: 6800000, avg_amount_lost: 13333, high_alert_count: 16, medium_alert_count: 25, low_alert_count: 10 },
  { group_label: 'Axis Bank', complaint_count: 430, total_amount_lost: 5600000, avg_amount_lost: 13023, high_alert_count: 13, medium_alert_count: 21, low_alert_count: 8 },
  { group_label: 'Punjab National Bank', complaint_count: 350, total_amount_lost: 4200000, avg_amount_lost: 12000, high_alert_count: 10, medium_alert_count: 17, low_alert_count: 7 },
  { group_label: 'Bank of Baroda', complaint_count: 290, total_amount_lost: 3300000, avg_amount_lost: 11379, high_alert_count: 8, medium_alert_count: 14, low_alert_count: 6 },
  { group_label: 'Canara Bank', complaint_count: 240, total_amount_lost: 2700000, avg_amount_lost: 11250, high_alert_count: 6, medium_alert_count: 12, low_alert_count: 5 },
  { group_label: 'Kotak Mahindra', complaint_count: 190, total_amount_lost: 2300000, avg_amount_lost: 12105, high_alert_count: 5, medium_alert_count: 9, low_alert_count: 4 },
];

const mockReportFraudType: ReportRow[] = [
  { group_label: 'UPI Fraud', complaint_count: 1820, total_amount_lost: 22400000, avg_amount_lost: 12308, high_alert_count: 48, medium_alert_count: 62, low_alert_count: 22 },
  { group_label: 'Loan App Scam', complaint_count: 980, total_amount_lost: 11800000, avg_amount_lost: 12041, high_alert_count: 32, medium_alert_count: 41, low_alert_count: 15 },
  { group_label: 'Investment Scam', complaint_count: 740, total_amount_lost: 15600000, avg_amount_lost: 21081, high_alert_count: 24, medium_alert_count: 35, low_alert_count: 12 },
  { group_label: 'Job Fraud', complaint_count: 520, total_amount_lost: 4200000, avg_amount_lost: 8077, high_alert_count: 12, medium_alert_count: 28, low_alert_count: 10 },
  { group_label: 'Phishing', complaint_count: 410, total_amount_lost: 2800000, avg_amount_lost: 6829, high_alert_count: 8, medium_alert_count: 22, low_alert_count: 14 },
  { group_label: 'Identity Theft', complaint_count: 350, total_amount_lost: 6500000, avg_amount_lost: 18571, high_alert_count: 14, medium_alert_count: 18, low_alert_count: 8 },
];

const mockReports: Record<ReportType, ReportRow[]> = {
  district: mockReportDistrict,
  bank: mockReportBank,
  fraudType: mockReportFraudType,
};

function rowsToCsv(rows: ReportRow[]): string {
  const header = 'group_label,complaint_count,total_amount_lost,avg_amount_lost,high_alert_count,medium_alert_count,low_alert_count';
  const body = rows.map((r) =>
    [r.group_label, r.complaint_count, r.total_amount_lost, r.avg_amount_lost, r.high_alert_count, r.medium_alert_count, r.low_alert_count].join(',')
  ).join('\n');
  return `${header}\n${body}`;
}

const reportEndpointMap: Record<ReportType, string> = {
  district: '/api/reports/by-district',
  bank: '/api/reports/by-bank',
  fraudType: '/api/reports/by-fraud-type',
};

export async function fetchReport(
  type: ReportType,
  dateFrom?: string,
  dateTo?: string,
): Promise<FetchResult<ReportRow[]>> {
  const params = new URLSearchParams();
  if (dateFrom) params.set('date_from', dateFrom);
  if (dateTo) params.set('date_to', dateTo);
  const qs = params.toString();
  const url = `${API_BASE_URL}${reportEndpointMap[type]}${qs ? `?${qs}` : ''}`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const rows = (await resp.json()) as ReportRow[];
    if (!rows || rows.length === 0) throw new Error('Empty response');
    return { data: rows, isDemo: false };
  } catch {
    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: mockReports[type], isDemo: true }), 300);
    });
  }
}

const reportTypeParamMap: Record<ReportType, string> = {
  district: 'district',
  bank: 'bank',
  fraudType: 'fraud_type',
};

export async function exportReportCsv(
  type: ReportType,
  fallbackRows?: ReportRow[],
): Promise<Blob> {
  const params = new URLSearchParams();
  params.set('type', reportTypeParamMap[type]);
  params.set('format', 'csv');
  const url = `${API_BASE_URL}/api/reports/export?${params.toString()}`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.blob();
  } catch {
    const rows = fallbackRows ?? mockReports[type];
    return new Blob([rowsToCsv(rows)], { type: 'text/csv' });
  }
}

// ============================================================
// DISPATCH LOG
// ============================================================

export type DispatchChannel = 'sms' | 'email' | 'webhook' | 'websocket';
export type DeliveryStatus = 'sent' | 'failed' | 'pending';

export interface DispatchLogRow {
  complaint_id: string;
  channel: DispatchChannel;
  recipient: string;
  dispatched_at: string;
  delivery_status: DeliveryStatus;
  raw_response: string | null;
}

export async function fetchDispatchLog(
  complaintId?: string,
  channel?: DispatchChannel,
): Promise<FetchResult<DispatchLogRow[]>> {
  const params = new URLSearchParams();
  if (complaintId) params.set('complaint_id', complaintId);
  if (channel) params.set('channel', channel);
  const qs = params.toString();
  const url = `${API_BASE_URL}/api/alerts/dispatch-log${qs ? `?${qs}` : ''}`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const rows = (await resp.json()) as DispatchLogRow[];
    if (!rows || rows.length === 0) throw new Error('Empty response');
    return { data: rows, isDemo: false };
  } catch {
    let rows = mockDispatchLog;
    if (complaintId) rows = rows.filter((r) => r.complaint_id.includes(complaintId));
    if (channel) rows = rows.filter((r) => r.channel === channel);
    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: rows, isDemo: true }), 300);
    });
  }
}

export default apiClient;
