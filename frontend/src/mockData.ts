// Centralized mock data for CyberSight.
// Structured so it can be swapped for real API calls later.

export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type FraudType =
  | 'UPI Fraud'
  | 'Loan App Scam'
  | 'Investment Scam'
  | 'Job Fraud'
  | 'Phishing'
  | 'Identity Theft';

export interface DistrictRisk {
  id: string;
  name: string;
  state: string;
  // approximate centroid for map markers
  lat: number;
  lng: number;
  riskScore: number; // 0-100
  riskLevel: RiskLevel;
  predicted: boolean;
  complaints: number;
  interceptions: number;
}

export interface AlertItem {
  id: string;
  district: string;
  state: string;
  riskScore: number;
  riskLevel: RiskLevel;
  fraudType: FraudType;
  timestamp: string; // ISO
  predictedWithdrawalWindow: string;
  linkedComplaints: LinkedComplaint[];
  muleAccounts: number;
  status: 'new' | 'deployed' | 'resolved' | 'false-positive';
}

export interface LinkedComplaint {
  id: string;
  fraudType: FraudType;
  amount: number;
  timestamp: string;
  reporter: string;
}

export interface BlockchainLog {
  id: string;
  alertId: string;
  txHash: string;
  district: string;
  riskScore: number;
  timestamp: string;
  status: 'Confirmed' | 'Pending' | 'Failed';
}

export interface ShapFeature {
  feature: string;
  contribution: number; // -1 to 1
}

const riskLevelFromScore = (s: number): RiskLevel =>
  s >= 80 ? 'CRITICAL' : s >= 60 ? 'HIGH' : s >= 35 ? 'MEDIUM' : 'LOW';

// --- Districts (representative centroids across India) ---
export const districts: DistrictRisk[] = [
  { id: 'd1', name: 'Jaipur', state: 'Rajasthan', lat: 26.9124, lng: 75.7873, riskScore: 92, predicted: false, complaints: 148, interceptions: 12 },
  { id: 'd2', name: 'Gurugram', state: 'Haryana', lat: 28.4595, lng: 77.0266, riskScore: 88, predicted: false, complaints: 131, interceptions: 9 },
  { id: 'd3', name: 'Noida', state: 'Uttar Pradesh', lat: 28.5355, lng: 77.391, riskScore: 85, predicted: true, complaints: 119, interceptions: 7 },
  { id: 'd4', name: 'Hyderabad', state: 'Telangana', lat: 17.385, lng: 78.4867, riskScore: 79, predicted: false, complaints: 104, interceptions: 15 },
  { id: 'd5', name: 'Bengaluru', state: 'Karnataka', lat: 12.9716, lng: 77.5946, riskScore: 73, predicted: true, complaints: 97, interceptions: 11 },
  { id: 'd6', name: 'Pune', state: 'Maharashtra', lat: 18.5204, lng: 73.8567, riskScore: 68, predicted: false, complaints: 88, interceptions: 8 },
  { id: 'd7', name: 'Mumbai', state: 'Maharashtra', lat: 19.076, lng: 72.8777, riskScore: 64, predicted: true, complaints: 81, interceptions: 14 },
  { id: 'd8', name: 'Chennai', state: 'Tamil Nadu', lat: 13.0827, lng: 80.2707, riskScore: 58, predicted: false, complaints: 72, interceptions: 6 },
  { id: 'd9', name: 'Kolkata', state: 'West Bengal', lat: 22.5726, lng: 88.3639, riskScore: 52, predicted: true, complaints: 65, interceptions: 5 },
  { id: 'd10', name: 'Bhopal', state: 'Madhya Pradesh', lat: 23.2599, lng: 77.4126, riskScore: 47, predicted: false, complaints: 54, interceptions: 4 },
  { id: 'd11', name: 'Patna', state: 'Bihar', lat: 25.5941, lng: 85.1376, riskScore: 41, predicted: true, complaints: 43, interceptions: 3 },
  { id: 'd12', name: 'Lucknow', state: 'Uttar Pradesh', lat: 26.8467, lng: 80.9462, riskScore: 36, predicted: false, complaints: 38, interceptions: 2 },
  { id: 'd13', name: 'Surat', state: 'Gujarat', lat: 21.1702, lng: 72.8311, riskScore: 29, predicted: true, complaints: 27, interceptions: 1 },
  { id: 'd14', name: 'Kochi', state: 'Kerala', lat: 9.9312, lng: 76.2673, riskScore: 22, predicted: false, complaints: 19, interceptions: 0 },
  { id: 'd15', name: 'Bhubaneswar', state: 'Odisha', lat: 20.2961, lng: 85.8245, riskScore: 16, predicted: true, complaints: 11, interceptions: 0 },
].map((d) => ({ ...d, riskLevel: riskLevelFromScore(d.riskScore) }));

// --- Alerts ---
const now = Date.now();
const minsAgo = (m: number) => new Date(now - m * 60000).toISOString();

const complaint = (i: number, fraudType: FraudType, amount: number, mins: number, reporter: string): LinkedComplaint => ({
  id: `NCCT-${String(20240800 + i).padStart(9, '0')}`,
  fraudType,
  amount,
  timestamp: minsAgo(mins),
  reporter,
});

export const alerts: AlertItem[] = [
  {
    id: 'ALR-2026-001',
    district: 'Jaipur',
    state: 'Rajasthan',
    riskScore: 92,
    riskLevel: 'CRITICAL',
    fraudType: 'UPI Fraud',
    timestamp: minsAgo(3),
    predictedWithdrawalWindow: 'Next 4 hours (14:00–18:00 IST)',
    muleAccounts: 7,
    status: 'new',
    linkedComplaints: [
      complaint(1, 'UPI Fraud', 45000, 4, 'Ramesh K.'),
      complaint(2, 'UPI Fraud', 82000, 7, 'Sunita P.'),
      complaint(3, 'UPI Fraud', 12500, 12, 'Arjun M.'),
      complaint(4, 'Phishing', 6700, 18, 'Deepak S.'),
      complaint(5, 'UPI Fraud', 210000, 25, 'Priya R.'),
    ],
  },
  {
    id: 'ALR-2026-002',
    district: 'Gurugram',
    state: 'Haryana',
    riskScore: 88,
    riskLevel: 'CRITICAL',
    fraudType: 'Loan App Scam',
    timestamp: minsAgo(9),
    predictedWithdrawalWindow: 'Next 2 hours (12:00–14:00 IST)',
    muleAccounts: 5,
    status: 'new',
    linkedComplaints: [
      complaint(6, 'Loan App Scam', 15000, 10, 'Vikas T.'),
      complaint(7, 'Loan App Scam', 35000, 16, 'Anita G.'),
      complaint(8, 'Loan App Scam', 9500, 22, 'Manoj B.'),
    ],
  },
  {
    id: 'ALR-2026-003',
    district: 'Noida',
    state: 'Uttar Pradesh',
    riskScore: 85,
    riskLevel: 'HIGH',
    fraudType: 'Investment Scam',
    timestamp: minsAgo(15),
    predictedWithdrawalWindow: 'Next 6 hours (16:00–22:00 IST)',
    muleAccounts: 4,
    status: 'new',
    linkedComplaints: [
      complaint(9, 'Investment Scam', 120000, 17, 'Sahil V.'),
      complaint(10, 'Investment Scam', 75000, 24, 'Neha A.'),
      complaint(11, 'Investment Scam', 48000, 31, 'Rohit K.'),
    ],
  },
  {
    id: 'ALR-2026-004',
    district: 'Hyderabad',
    state: 'Telangana',
    riskScore: 79,
    riskLevel: 'HIGH',
    fraudType: 'Job Fraud',
    timestamp: minsAgo(22),
    predictedWithdrawalWindow: 'Next 3 hours (15:00–18:00 IST)',
    muleAccounts: 3,
    status: 'deployed',
    linkedComplaints: [
      complaint(12, 'Job Fraud', 18000, 24, 'Karthik N.'),
      complaint(13, 'Job Fraud', 22000, 30, 'Sneha R.'),
    ],
  },
  {
    id: 'ALR-2026-005',
    district: 'Bengaluru',
    state: 'Karnataka',
    riskScore: 73,
    riskLevel: 'HIGH',
    fraudType: 'UPI Fraud',
    timestamp: minsAgo(35),
    predictedWithdrawalWindow: 'Next 5 hours (17:00–22:00 IST)',
    muleAccounts: 2,
    status: 'new',
    linkedComplaints: [
      complaint(14, 'UPI Fraud', 33000, 36, 'Faisal A.'),
      complaint(15, 'UPI Fraud', 51000, 42, 'Lakshmi D.'),
    ],
  },
  {
    id: 'ALR-2026-006',
    district: 'Pune',
    state: 'Maharashtra',
    riskScore: 68,
    riskLevel: 'MEDIUM',
    fraudType: 'Phishing',
    timestamp: minsAgo(48),
    predictedWithdrawalWindow: 'Next 8 hours (19:00–03:00 IST)',
    muleAccounts: 1,
    status: 'new',
    linkedComplaints: [
      complaint(16, 'Phishing', 9800, 50, 'Gaurav P.'),
      complaint(17, 'Phishing', 14500, 55, 'Meera J.'),
    ],
  },
  {
    id: 'ALR-2026-007',
    district: 'Mumbai',
    state: 'Maharashtra',
    riskScore: 64,
    riskLevel: 'MEDIUM',
    fraudType: 'Identity Theft',
    timestamp: minsAgo(61),
    predictedWithdrawalWindow: 'Next 4 hours (16:00–20:00 IST)',
    muleAccounts: 2,
    status: 'resolved',
    linkedComplaints: [
      complaint(18, 'Identity Theft', 67000, 62, 'Aditya S.'),
    ],
  },
  {
    id: 'ALR-2026-008',
    district: 'Chennai',
    state: 'Tamil Nadu',
    riskScore: 58,
    riskLevel: 'MEDIUM',
    fraudType: 'Loan App Scam',
    timestamp: minsAgo(74),
    predictedWithdrawalWindow: 'Next 6 hours (18:00–00:00 IST)',
    muleAccounts: 1,
    status: 'new',
    linkedComplaints: [
      complaint(19, 'Loan App Scam', 12000, 75, 'Bharath M.'),
    ],
  },
];

// --- Blockchain logs ---
const randomHash = () => '0x' + [...Array(64)].map(() =>
  Math.floor(Math.random() * 16).toString(16)).join('');

export const blockchainLogs: BlockchainLog[] = alerts.map((a, i) => ({
  id: `BLK-${String(i + 1).padStart(4, '0')}`,
  alertId: a.id,
  txHash: randomHash(),
  district: a.district,
  riskScore: a.riskScore,
  timestamp: a.timestamp,
  status: i % 5 === 0 ? 'Failed' : i % 3 === 0 ? 'Pending' : 'Confirmed',
}));

// --- SHAP explanations per alert ---
export const shapExplanations: Record<string, ShapFeature[]> = {
  'ALR-2026-001': [
    { feature: 'UPI txn velocity', contribution: 0.42 },
    { feature: 'Mule account clustering', contribution: 0.31 },
    { feature: 'Off-hours activity', contribution: 0.18 },
    { feature: 'Repeat device fingerprint', contribution: 0.15 },
    { feature: 'Geographic spread', contribution: 0.09 },
    { feature: 'Avg complaint amount', contribution: -0.07 },
  ],
  'ALR-2026-002': [
    { feature: 'Loan app install spike', contribution: 0.38 },
    { feature: 'SMS campaign overlap', contribution: 0.27 },
    { feature: 'Mule account clustering', contribution: 0.21 },
    { feature: 'Off-hours activity', contribution: 0.12 },
    { feature: 'Repeat device fingerprint', contribution: 0.06 },
  ],
  'ALR-2026-003': [
    { feature: 'Investment ad clicks', contribution: 0.35 },
    { feature: 'Telegram group linkage', contribution: 0.29 },
    { feature: 'Mule account clustering', contribution: 0.17 },
    { feature: 'Avg complaint amount', contribution: 0.14 },
    { feature: 'Off-hours activity', contribution: -0.05 },
  ],
};

// Default SHAP for dashboard overview
export const defaultShap: ShapFeature[] = [
  { feature: 'UPI txn velocity', contribution: 0.38 },
  { feature: 'Mule account clustering', contribution: 0.29 },
  { feature: 'Loan app install spike', contribution: 0.22 },
  { feature: 'Off-hours activity', contribution: 0.16 },
  { feature: 'Investment ad clicks', contribution: 0.11 },
  { feature: 'Repeat device fingerprint', contribution: 0.08 },
];

// --- Dashboard stat values ---
export const dashboardStats = {
  totalAlertsToday: 47,
  highRiskDistricts: 12,
  complaintsLastHour: 23,
  interceptions: 9,
};

// --- Socket mock: pool of alerts to emit ---
export const socketAlertPool: Omit<AlertItem, 'status'>[] = [
  {
    id: 'ALR-2026-009',
    district: 'Kolkata',
    state: 'West Bengal',
    riskScore: 71,
    riskLevel: 'HIGH',
    fraudType: 'UPI Fraud',
    timestamp: minsAgo(0),
    predictedWithdrawalWindow: 'Next 3 hours (15:00–18:00 IST)',
    muleAccounts: 3,
    linkedComplaints: [
      complaint(20, 'UPI Fraud', 41000, 1, 'Soumita R.'),
      complaint(21, 'UPI Fraud', 28000, 3, 'Anirban H.'),
    ],
  },
  {
    id: 'ALR-2026-010',
    district: 'Patna',
    state: 'Bihar',
    riskScore: 84,
    riskLevel: 'HIGH',
    fraudType: 'Job Fraud',
    timestamp: minsAgo(0),
    predictedWithdrawalWindow: 'Next 2 hours (12:00–14:00 IST)',
    muleAccounts: 2,
    linkedComplaints: [
      complaint(22, 'Job Fraud', 16000, 1, 'Rahul V.'),
    ],
  },
  {
    id: 'ALR-2026-011',
    district: 'Bhopal',
    state: 'Madhya Pradesh',
    riskScore: 63,
    riskLevel: 'MEDIUM',
    fraudType: 'Phishing',
    timestamp: minsAgo(0),
    predictedWithdrawalWindow: 'Next 5 hours (17:00–22:00 IST)',
    muleAccounts: 1,
    linkedComplaints: [
      complaint(23, 'Phishing', 8900, 1, 'Shreya P.'),
    ],
  },
];

export const getAlertById = (id: string) => alerts.find((a) => a.id === id);

export const relativeTime = (iso: string): string => {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
};

export const riskColor = (level: RiskLevel): string => {
  switch (level) {
    case 'CRITICAL': return '#dc2626';
    case 'HIGH': return '#ea580c';
    case 'MEDIUM': return '#f59e0b';
    case 'LOW': return '#15803d';
  }
};

export const riskBgClass = (level: RiskLevel): string => {
  switch (level) {
    case 'CRITICAL': return 'bg-danger text-white';
    case 'HIGH': return 'bg-alert text-white';
    case 'MEDIUM': return 'bg-amber-500 text-white';
    case 'LOW': return 'bg-success text-white';
  }
};

export const formatCurrency = (n: number): string =>
  '₹' + n.toLocaleString('en-IN');
