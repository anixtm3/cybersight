// ============================================================
// API Layer — CyberSight
// Functions return data matching the real API contract.
// Swap to live endpoints by changing only the fetch body.
// =============================================================

import { HEATMAP_ENDPOINT, COMPLAINT_FULL_ENDPOINT, API_BASE_URL } from '@/config';

// --- Types (match real API contract) ---

export type RiskLevel = 'HIGH' | 'MEDIUM' | 'LOW';
export type FraudType =
  | 'UPI Fraud'
  | 'Loan App Scam'
  | 'Investment Scam'
  | 'Job Fraud'
  | 'Phishing'
  | 'Identity Theft';

// Dispatch status — separate endpoint (/api/alerts/dispatch-log)
export type ChannelStatus = 'PENDING' | 'SENT' | 'DELIVERED' | 'FAILED';
export type OverallDispatchStatus = 'PENDING' | 'PARTIAL' | 'SUCCESS' | 'FAILED';

export interface DispatchStatus {
  alert_id: string;
  dispatch_status: OverallDispatchStatus;
  sms_status: ChannelStatus;
  email_status: ChannelStatus;
  webhook_status: ChannelStatus;
  dashboard_status: ChannelStatus;
}

// Real WebSocket broadcast payload (confirmed contract)
export interface PredictionEvent {
  complaint_id: string;
  tracking_number: string;
  alert_level: 'MEDIUM' | 'HIGH';
  atm_id: string;
  atm_lat: number;
  atm_lon: number;
  recommended_action: string;
  freezable_amount: number;
  timestamp: string;
  // Dispatch status comes from a separate endpoint — this flag marks the pending state.
  dispatch_pending: boolean;
}

export interface HeatmapFilters {
  dateRange: { start: string; end: string };
  district: string | 'all';
  fraudType: FraudType | 'all';
  riskLevel: RiskLevel[]; // empty = all
}

export interface RiskZoneFeature {
  type: 'Feature';
  geometry: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  properties: {
    zoneId: string;
    zoneName: string;
    district: string;
    state: string;
    riskLevel: RiskLevel;
    riskScore: number;
    fraudType: FraudType;
    complaintCount: number;
    atmCount: number;
  };
}

export interface HeatmapGeoJSON {
  type: 'FeatureCollection';
  features: RiskZoneFeature[];
}

export interface ATMEntry {
  atmId: string;
  bankName: string;
  lat: number;
  lng: number;
  rank: number;
  riskContribution: number;
  riskLevel: RiskLevel;
}

// --- Confirmed demo cities ---

interface DemoCity {
  name: string;
  district: string;
  state: string;
  lat: number;
  lng: number;
  bbox: { minLat: number; maxLat: number; minLng: number; maxLng: number };
  atmCount: number;
  atmPrefix: string;
  complaintWeight: number; // relative probability for alert generation
}

const demoCities: DemoCity[] = [
  {
    name: 'Delhi',
    district: 'Delhi',
    state: 'Delhi',
    lat: 28.65,
    lng: 77.23,
    bbox: { minLat: 28.4, maxLat: 28.9, minLng: 76.8, maxLng: 77.4 },
    atmCount: 797,
    atmPrefix: 'DEL',
    complaintWeight: 0.40,
  },
  {
    name: 'Delhi NCR',
    district: 'Delhi NCR',
    state: 'Haryana',
    lat: 28.65,
    lng: 77.15,
    bbox: { minLat: 28.3, maxLat: 29.0, minLng: 76.5, maxLng: 77.8 },
    atmCount: 869,
    atmPrefix: 'NCR',
    complaintWeight: 0.25,
  },
  {
    name: 'Mumbai',
    district: 'Mumbai',
    state: 'Maharashtra',
    lat: 19.07,
    lng: 72.87,
    bbox: { minLat: 18.8, maxLat: 19.3, minLng: 72.7, maxLng: 73.1 },
    atmCount: 300,
    atmPrefix: 'MUM',
    complaintWeight: 0.25,
  },
  {
    name: 'Jamtara',
    district: 'Jamtara',
    state: 'Jharkhand',
    lat: 24.0,
    lng: 86.99,
    bbox: { minLat: 23.8, maxLat: 24.2, minLng: 86.8, maxLng: 87.2 },
    atmCount: 300,
    atmPrefix: 'JAM',
    complaintWeight: 0.10,
  },
  // --- PLACEHOLDER_PENDING_CONFIRMATION: coordinates are approximate city centers, not confirmed bounding boxes ---
  {
    name: 'Bengaluru',
    district: 'Bengaluru',
    state: 'Karnataka',
    lat: 12.97,
    lng: 77.59,
    bbox: { minLat: 12.77, maxLat: 13.17, minLng: 77.39, maxLng: 77.79 },
    atmCount: 400,
    atmPrefix: 'BLR',
    complaintWeight: 0.15,
  },
  // --- PLACEHOLDER_PENDING_CONFIRMATION ---
  {
    name: 'Hyderabad',
    district: 'Hyderabad',
    state: 'Telangana',
    lat: 17.38,
    lng: 78.49,
    bbox: { minLat: 17.18, maxLat: 17.58, minLng: 78.29, maxLng: 78.69 },
    atmCount: 350,
    atmPrefix: 'HYD',
    complaintWeight: 0.12,
  },
  // --- PLACEHOLDER_PENDING_CONFIRMATION ---
  {
    name: 'Agra',
    district: 'Agra',
    state: 'Uttar Pradesh',
    lat: 27.18,
    lng: 78.02,
    bbox: { minLat: 26.98, maxLat: 27.38, minLng: 77.82, maxLng: 78.22 },
    atmCount: 200,
    atmPrefix: 'AGR',
    complaintWeight: 0.08,
  },
  // --- PLACEHOLDER_PENDING_CONFIRMATION ---
  {
    name: 'Patna',
    district: 'Patna',
    state: 'Bihar',
    lat: 25.59,
    lng: 85.14,
    bbox: { minLat: 25.39, maxLat: 25.79, minLng: 84.94, maxLng: 85.34 },
    atmCount: 250,
    atmPrefix: 'PAT',
    complaintWeight: 0.10,
  },
  // --- PLACEHOLDER_PENDING_CONFIRMATION ---
  {
    name: 'Pune',
    district: 'Pune',
    state: 'Maharashtra',
    lat: 18.52,
    lng: 73.86,
    bbox: { minLat: 18.32, maxLat: 18.72, minLng: 73.66, maxLng: 74.06 },
    atmCount: 300,
    atmPrefix: 'PUN',
    complaintWeight: 0.12,
  },
  // --- PLACEHOLDER_PENDING_CONFIRMATION ---
  {
    name: 'Lucknow',
    district: 'Lucknow',
    state: 'Uttar Pradesh',
    lat: 26.85,
    lng: 80.95,
    bbox: { minLat: 26.65, maxLat: 27.05, minLng: 80.75, maxLng: 81.15 },
    atmCount: 280,
    atmPrefix: 'LKO',
    complaintWeight: 0.10,
  },
];

const fraudTypes: FraudType[] = [
  'UPI Fraud', 'Loan App Scam', 'Investment Scam', 'Job Fraud', 'Phishing', 'Identity Theft',
];

const banks = [
  'State Bank of India', 'HDFC Bank', 'ICICI Bank', 'Axis Bank', 'Punjab National Bank',
  'Bank of Baroda', 'Canara Bank', 'Kotak Mahindra',
];

const riskLevelFromScore = (s: number): RiskLevel =>
  s >= 70 ? 'HIGH' : s >= 40 ? 'MEDIUM' : 'LOW';

const randomItem = <T,>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];

// Weighted random city selection based on complaint distribution
const weightedCity = (): DemoCity => {
  const r = Math.random();
  let acc = 0;
  for (const c of demoCities) {
    acc += c.complaintWeight;
    if (r <= acc) return c;
  }
  return demoCities[0];
};

let complaintCounter = 20240800;
const nextComplaintId = () => `NCCT-${String(++complaintCounter).padStart(9, '0')}`;
let trackingCounter = 0;
const nextTrackingNumber = () => `TRK${String(++trackingCounter).padStart(6, '0')}`;

const recommendedActions = [
  'Freeze ATM immediately and dispatch field team',
  'Alert bank nodal officer and monitor withdrawals',
  'Coordinate with local police for ATM surveillance',
  'Block associated UPI IDs and freeze accounts',
  'Dispatch cyber cell team to ATM location',
];

export function generatePredictionEvent(): PredictionEvent {
  const city = weightedCity();
  const isHigh = Math.random() > 0.45;
  const atmId = `${city.atmPrefix}${String(Math.floor(Math.random() * 99999) + 1).padStart(5, '0')}`;
  return {
    complaint_id: nextComplaintId(),
    tracking_number: nextTrackingNumber(),
    alert_level: isHigh ? 'HIGH' : 'MEDIUM',
    atm_id: atmId,
    atm_lat: city.lat + (Math.random() - 0.5) * 0.1,
    atm_lon: city.lng + (Math.random() - 0.5) * 0.1,
    recommended_action: randomItem(recommendedActions),
    freezable_amount: Math.floor(Math.random() * 500000) + 10000,
    timestamp: new Date().toISOString(),
    dispatch_pending: true,
  };
}

export function generateInitialEvents(count: number): PredictionEvent[] {
  const events: PredictionEvent[] = [];
  for (let i = 0; i < count; i++) {
    const e = generatePredictionEvent();
    e.timestamp = new Date(Date.now() - i * 120000).toISOString();
    events.push(e);
  }
  return events;
}

// --- Heatmap GeoJSON ---

// Zones per city — Jamtara gets fewer zones (sparse density)
interface ZoneDef {
  zoneId: string;
  zoneName: string;
  city: DemoCity;
  riskLevel: RiskLevel;
  riskScore: number;
  complaintCount: number;
}

function buildZonesForCity(city: DemoCity, zoneCount: number, startIndex: number): ZoneDef[] {
  const prefix = city.atmPrefix;
  const zones: ZoneDef[] = [];
  for (let i = 0; i < zoneCount; i++) {
    const idx = startIndex + i;
    const score = Math.floor(Math.random() * 70) + 20;
    zones.push({
      zoneId: `Z-${prefix}-${String(idx).padStart(2, '0')}`,
      zoneName: `${city.name} — Zone ${idx}`,
      city,
      riskLevel: riskLevelFromScore(score),
      riskScore: score,
      complaintCount: Math.floor(Math.random() * 150) + 10,
    });
  }
  return zones;
}

// Delhi: 4 zones, Delhi NCR: 3 zones, Mumbai: 3 zones, Jamtara: 2 zones (sparse),
// New placeholder districts: 2 zones each (will adjust once real data arrives)
const allZones: ZoneDef[] = [
  ...buildZonesForCity(demoCities[0], 4, 1),  // Delhi
  ...buildZonesForCity(demoCities[1], 3, 1),  // Delhi NCR
  ...buildZonesForCity(demoCities[2], 3, 1),  // Mumbai
  ...buildZonesForCity(demoCities[3], 2, 1),  // Jamtara
  ...buildZonesForCity(demoCities[4], 2, 1),  // Bengaluru (PLACEHOLDER_PENDING_CONFIRMATION)
  ...buildZonesForCity(demoCities[5], 2, 1),  // Hyderabad (PLACEHOLDER_PENDING_CONFIRMATION)
  ...buildZonesForCity(demoCities[6], 2, 1),  // Agra (PLACEHOLDER_PENDING_CONFIRMATION)
  ...buildZonesForCity(demoCities[7], 2, 1),  // Patna (PLACEHOLDER_PENDING_CONFIRMATION)
  ...buildZonesForCity(demoCities[8], 2, 1),  // Pune (PLACEHOLDER_PENDING_CONFIRMATION)
  ...buildZonesForCity(demoCities[9], 2, 1),  // Lucknow (PLACEHOLDER_PENDING_CONFIRMATION)
];

// Assign fraud types deterministically per zone
const zoneFraudTypes: Record<string, FraudType> = {};
allZones.forEach((z, i) => {
  zoneFraudTypes[z.zoneId] = fraudTypes[i % fraudTypes.length];
});

// Generate a polygon covering most of a city's bounding box for each zone.
// Each zone gets a slightly offset/scaled rectangle within the bbox so
// multiple zones in the same city are visually distinct but still
// district-sized (not tiny grid cells).
function polygonForZone(city: DemoCity, zoneIndex: number, totalZones: number): number[][][] {
  const { minLat, maxLat, minLng, maxLng } = city.bbox;
  const latSpan = maxLat - minLat;
  const lngSpan = maxLng - minLng;

  // For single-zone cities, use the full bbox
  if (totalZones === 1) {
    return [[[minLng, minLat], [maxLng, minLat], [maxLng, maxLat], [minLng, maxLat], [minLng, minLat]]];
  }

  // For multi-zone cities, split the bbox into a grid (2 columns max)
  // so each cell is still a large, visible rectangle.
  const cols = totalZones <= 2 ? totalZones : 2;
  const rows = Math.ceil(totalZones / cols);
  const cellW = lngSpan / cols;
  const cellH = latSpan / rows;
  const row = Math.floor(zoneIndex / cols);
  const col = zoneIndex % cols;

  // Each cell covers a full grid slot — with a small inset for visual separation
  const inset = 0.01; // ~1km gap between zones
  const south = minLat + row * cellH + inset;
  const north = minLat + (row + 1) * cellH - inset;
  const west = minLng + col * cellW + inset;
  const east = minLng + (col + 1) * cellW - inset;

  return [[[west, south], [east, south], [east, north], [west, north], [west, south]]];
}

const zonePolygons: Record<string, number[][][]> = {};
allZones.forEach((z, i) => {
  const totalForCity = allZones.filter((zz) => zz.city.name === z.city.name).length;
  const indexInCity = allZones.filter((zz) => zz.city.name === z.city.name).indexOf(z);
  zonePolygons[z.zoneId] = polygonForZone(z.city, indexInCity, totalForCity);
});

// Mock heatmap generator (fallback when backend is down)
function generateMockHeatmap(filters: HeatmapFilters): HeatmapGeoJSON {
  let features = allZones.map((zone): RiskZoneFeature => ({
    type: 'Feature',
    geometry: { type: 'Polygon', coordinates: zonePolygons[zone.zoneId] },
    properties: {
      zoneId: zone.zoneId,
      zoneName: zone.zoneName,
      district: zone.city.district,
      state: zone.city.state,
      riskLevel: zone.riskLevel,
      riskScore: zone.riskScore,
      fraudType: zoneFraudTypes[zone.zoneId],
      complaintCount: zone.complaintCount,
      atmCount: zone.city.atmCount,
    },
  }));

  if (filters.district !== 'all') {
    features = features.filter((f) => f.properties.district === filters.district);
  }
  if (filters.fraudType !== 'all') {
    features = features.filter((f) => f.properties.fraudType === filters.fraudType);
  }
  if (filters.riskLevel.length > 0) {
    features = features.filter((f) => filters.riskLevel.includes(f.properties.riskLevel));
  }

  return { type: 'FeatureCollection', features };
}

export async function fetchHeatmapData(filters: HeatmapFilters): Promise<HeatmapGeoJSON> {
  const params = new URLSearchParams();
  if (filters.dateRange.start) params.set('date_from', filters.dateRange.start);
  if (filters.dateRange.end) params.set('date_to', filters.dateRange.end);
  if (filters.district !== 'all') params.set('district', filters.district);
  if (filters.fraudType !== 'all') params.set('fraud_type', filters.fraudType);
  if (filters.riskLevel.length > 0) params.set('risk_level', filters.riskLevel.join(','));

  try {
    const resp = await fetch(`${HEATMAP_ENDPOINT}?${params.toString()}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json() as HeatmapGeoJSON;
    if (!data || !data.features || data.features.length === 0) throw new Error('Empty or invalid GeoJSON');
    return data;
  } catch {
    // Fallback to mock data if backend is unreachable
    return new Promise((resolve) => {
      setTimeout(() => resolve(generateMockHeatmap(filters)), 400);
    });
  }
}

// --- ATM drill-down ---

const atmDataByZone: Record<string, ATMEntry[]> = {};

function generateATMsForZone(zoneId: string): ATMEntry[] {
  if (atmDataByZone[zoneId]) return atmDataByZone[zoneId];

  const zone = allZones.find((z) => z.zoneId === zoneId);
  if (!zone) return [];

  const city = zone.city;
  const polygon = zonePolygons[zoneId]?.[0] ?? [];
  const baseLng = polygon[0]?.[0] ?? city.lng;
  const baseLat = polygon[0]?.[1] ?? city.lat;

  // ATM count per zone: Jamtara gets fewer (sparse), Delhi/NCR get more
  let count: number;
  if (city.atmPrefix === 'JAM') {
    count = 5; // sparse — always minimum
  } else if (city.atmPrefix === 'MUM') {
    count = 6 + Math.floor(Math.random() * 3); // 6-8
  } else {
    count = 7 + Math.floor(Math.random() * 2); // 7-8 for Delhi/NCR
  }

  const atms: ATMEntry[] = [];
  for (let i = 0; i < count; i++) {
    const score = Math.floor(Math.random() * 80) + 10;
    atms.push({
      atmId: `${city.atmPrefix}${String(i + 1).padStart(5, '0')}`,
      bankName: randomItem(banks),
      lat: baseLat + (Math.random() - 0.5) * 0.06,
      lng: baseLng + (Math.random() - 0.5) * 0.06,
      rank: 0,
      riskContribution: score,
      riskLevel: riskLevelFromScore(score),
    });
  }

  atms.sort((a, b) => b.riskContribution - a.riskContribution);
  atms.forEach((a, i) => { a.rank = i + 1; });

  atmDataByZone[zoneId] = atms;
  return atms;
}

export function fetchATMsForZone(zoneId: string): Promise<ATMEntry[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(generateATMsForZone(zoneId)), 300);
  });
}

// --- Top ATM predictions (ATM-level risk display) ---
// Real endpoint: POST /api/predict — returns predicted_locations array
// with top-level risk_level/confidence applied to all markers.
export interface AtmPrediction {
  atm_id: string;
  bank_name: string | null;
  lat: number;
  lng: number;
  risk_level: RiskLevel;
  confidence: number;
}

interface PredictResponse {
  predicted_locations: { lat: number; lng: number; atm_id: string; bank_name: string | null }[];
  predicted_district?: string;
  risk_level?: RiskLevel;
  confidence?: number;
  novel_pattern?: boolean;
  recommended_action?: string;
  withdrawal_window_minutes?: number;
  freezable_amount?: number;
  shap_values?: Record<string, number>;
  model?: string;
  message?: string;
}

function generateTopAtmsForDistrict(city: DemoCity): AtmPrediction[] {
  const atms: AtmPrediction[] = [];
  for (let i = 0; i < 5; i++) {
    atms.push({
      atm_id: `${city.atmPrefix}${String(Math.floor(Math.random() * 99999) + 1).padStart(5, '0')}`,
      bank_name: randomItem(banks),
      lat: city.lat + (Math.random() - 0.5) * 0.08,
      lng: city.lng + (Math.random() - 0.5) * 0.08,
      risk_level: riskLevelFromScore(Math.floor(Math.random() * 50) + 45),
      confidence: Math.round((Math.random() * 0.4 + 0.55) * 100) / 100,
    });
  }
  return atms;
}

let cachedTopAtms: AtmPrediction[] | null = null;

function generateAllTopAtms(): AtmPrediction[] {
  if (cachedTopAtms) return cachedTopAtms;
  const all = demoCities.flatMap((city) => generateTopAtmsForDistrict(city));
  cachedTopAtms = all.slice(0, 5);
  return cachedTopAtms;
}

export async function fetchTopAtmPredictions(): Promise<AtmPrediction[]> {
  // Build request from representative case context
  const city = demoCities[0];
  const requestBody = {
    victim_district: city.district,
    victim_lat: city.lat,
    victim_lon: city.lng,
    amount_lost: 150000,
    beneficiary_bank: randomItem(banks),
    number_of_hops: 3,
    beneficiary_account: 'XXXX1234',
  };

  try {
    const resp = await fetch(`${API_BASE_URL}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json() as PredictResponse;
    if (!data || !Array.isArray(data.predicted_locations) || data.predicted_locations.length === 0) {
      throw new Error('Missing predicted_locations');
    }
    const riskLevel: RiskLevel = data.risk_level ?? 'MEDIUM';
    const confidence: number = typeof data.confidence === 'number' ? data.confidence : 0.5;
    return data.predicted_locations.map((loc) => ({
      atm_id: loc.atm_id ?? 'Unknown',
      bank_name: loc.bank_name ?? null,
      lat: typeof loc.lat === 'number' ? loc.lat : 0,
      lng: typeof loc.lng === 'number' ? loc.lng : 0,
      risk_level: riskLevel,
      confidence,
    }));
  } catch {
    return new Promise((resolve) => {
      setTimeout(() => resolve(generateAllTopAtms()), 400);
    });
  }
}

// --- Filter dropdown options ---

export const districtOptions = ['all', 'Delhi', 'Delhi NCR', 'Mumbai', 'Jamtara', 'Bengaluru', 'Hyderabad', 'Agra', 'Patna', 'Pune', 'Lucknow'];
export const fraudTypeOptions: (FraudType | 'all')[] = ['all', 'UPI Fraud', 'Loan App Scam', 'Investment Scam', 'Job Fraud', 'Phishing', 'Identity Theft'];
export const riskLevelOptions: RiskLevel[] = ['HIGH', 'MEDIUM', 'LOW'];

// ============================================================
// SHAP EXPLANATION — location prediction model
// ============================================================

export interface ShapFeatureRow {
  feature: string;
  shap_impact_lat: number;
  shap_impact_lon: number;
  combined_importance: number;
}

export interface ShapExplanation {
  case_id: string;
  shap_values: ShapFeatureRow[];
}

const featureLabels: Record<string, string> = {
  victim_lat: "Victim's Location",
  victim_lon: "Victim's Location",
  victim_district_enc: "Victim's District",
  beneficiary_bank_enc: "Beneficiary's Bank",
  number_of_hops: 'Number of Transaction Hops',
  amount_lost: 'Amount Lost',
  is_insider_case_enc: 'Insider Involvement',
  fraud_type_enc: 'Fraud Type',
  is_weekend_enc: 'Weekend Timing',
  hour: 'Time of Day',
};

export const featureLabel = (key: string): string => featureLabels[key] ?? key.replace(/_enc$/, '').replace(/_/g, ' ');

const shapDataByCase: Record<string, ShapFeatureRow[]> = {
  'ALR-2026-001': [
    { feature: 'victim_lat', shap_impact_lat: 3.26, shap_impact_lon: -0.03, combined_importance: 3.29 },
    { feature: 'victim_district_enc', shap_impact_lat: 1.84, shap_impact_lon: 0.42, combined_importance: 2.26 },
    { feature: 'beneficiary_bank_enc', shap_impact_lat: -0.21, shap_impact_lon: 0.88, combined_importance: 1.09 },
    { feature: 'number_of_hops', shap_impact_lat: 0.12, shap_impact_lon: -0.31, combined_importance: 0.43 },
    { feature: 'amount_lost', shap_impact_lat: 0.08, shap_impact_lon: 0.06, combined_importance: 0.14 },
  ],
  'ALR-2026-002': [
    { feature: 'victim_lat', shap_impact_lat: 2.91, shap_impact_lon: 0.15, combined_importance: 3.06 },
    { feature: 'beneficiary_bank_enc', shap_impact_lat: -0.44, shap_impact_lon: 1.12, combined_importance: 1.56 },
    { feature: 'fraud_type_enc', shap_impact_lat: 0.67, shap_impact_lon: -0.22, combined_importance: 0.89 },
    { feature: 'hour', shap_impact_lat: 0.19, shap_impact_lon: 0.11, combined_importance: 0.30 },
  ],
  'ALR-2026-003': [
    { feature: 'victim_district_enc', shap_impact_lat: 2.14, shap_impact_lon: 0.38, combined_importance: 2.52 },
    { feature: 'victim_lat', shap_impact_lat: 1.77, shap_impact_lon: -0.51, combined_importance: 2.28 },
    { feature: 'is_insider_case_enc', shap_impact_lat: -0.33, shap_impact_lon: 0.74, combined_importance: 1.07 },
    { feature: 'is_weekend_enc', shap_impact_lat: 0.09, shap_impact_lon: -0.18, combined_importance: 0.27 },
  ],
};

function generateMockShap(caseId: string): ShapFeatureRow[] {
  if (shapDataByCase[caseId]) return shapDataByCase[caseId];
  const allFeatures = Object.keys(featureLabels);
  const count = 5 + Math.floor(Math.random() * 2);
  const shuffled = [...allFeatures].sort(() => Math.random() - 0.5);
  const selected = shuffled.slice(0, count);
  return selected.map((feature) => {
    const lat = Math.round((Math.random() * 3 - 0.5) * 100) / 100;
    const lon = Math.round((Math.random() * 2 - 1) * 100) / 100;
    return {
      feature,
      shap_impact_lat: lat,
      shap_impact_lon: lon,
      combined_importance: Math.round((Math.abs(lat) + Math.abs(lon)) * 100) / 100,
    };
  }).sort((a, b) => b.combined_importance - a.combined_importance);
}

export async function fetchShapExplanation(caseId: string): Promise<ShapExplanation> {
  try {
    const resp = await fetch(COMPLAINT_FULL_ENDPOINT(caseId));
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json() as ShapFeatureRow[];
    return {
      case_id: caseId,
      shap_values: data.sort((a, b) => b.combined_importance - a.combined_importance),
    };
  } catch {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          case_id: caseId,
          shap_values: generateMockShap(caseId),
        });
      }, 400);
    });
  }
}

export function generateShapSummary(shapValues: ShapFeatureRow[]): string {
  const sorted = [...shapValues].sort((a, b) => b.combined_importance - a.combined_importance);
  const top = sorted.slice(0, 3);
  if (top.length === 0) return 'No significant factors identified for this location prediction.';
  const labels = top.map((s) => featureLabel(s.feature));
  if (labels.length === 1) {
    return `This predicted withdrawal location was determined primarily by ${labels[0].toLowerCase()}.`;
  }
  if (labels.length === 2) {
    return `This predicted withdrawal location was determined mainly by ${labels[0].toLowerCase()} and ${labels[1].toLowerCase()}.`;
  }
  const main = labels.slice(0, -1).map((l) => l.toLowerCase()).join(', ');
  return `This predicted withdrawal location was determined mainly by ${main}, with some influence from ${labels[labels.length - 1].toLowerCase()}.`;
}

// ============================================================
// MULE REGISTRY (Day 3)
// ============================================================

export type EvidenceBasis = 'INVESTIGATION_VERIFIED' | 'MONITORING_SUSPECTED';

export interface MuleAccount {
  flag_id: string;
  account_hash: string;
  tx_hash: string;
  flagging_authority: string;
  evidence_basis: EvidenceBasis;
  risk_score: number;
  block_timestamp: string;
  flag_reason: string;
}

const flagReasons = [
  'Rapid fund dispersal pattern',
  'Multiple incoming UPI transfers from flagged zones',
  'Cash withdrawal spike at flagged ATM cluster',
  'Account linked to known mule network',
  'Off-hours transaction velocity anomaly',
  'Cross-district fund movement pattern',
];

const flaggingAuthorities = [
  'SBI-FRAUD-CELL-04',
  'HDFC-CYBER-OPS-02',
  'ICICI-RISK-UNIT-01',
  'DELHI-CYBER-CELL-03',
  'MUMBAI-CYBER-CELL-01',
  'I4C-CENTRAL-07',
];

function generateHash(): string {
  const chars = '0123456789abcdef';
  const head = Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * 16)]).join('');
  const tail = Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * 16)]).join('');
  return `0x${head}...${tail}`;
}

function generateTxHash(): string {
  const chars = '0123456789abcdef';
  return '0x' + Array.from({ length: 64 }, () => chars[Math.floor(Math.random() * 16)]).join('');
}

function generateMuleAccounts(): MuleAccount[] {
  const accounts: MuleAccount[] = [];
  const total = 24;
  for (let i = 0; i < total; i++) {
    const score = Math.floor(Math.random() * 50) + 40;
    const verified = Math.random() > 0.45;
    const daysAgo = Math.floor(Math.random() * 30);
    accounts.push({
      flag_id: `FLAG-${String(i + 1).padStart(3, '0')}`,
      account_hash: generateHash(),
      tx_hash: generateTxHash(),
      flagging_authority: flaggingAuthorities[i % flaggingAuthorities.length],
      evidence_basis: verified ? 'INVESTIGATION_VERIFIED' : 'MONITORING_SUSPECTED',
      risk_score: score,
      block_timestamp: new Date(Date.now() - daysAgo * 86400000).toISOString(),
      flag_reason: flagReasons[i % flagReasons.length],
    });
  }
  return accounts.sort((a, b) => b.risk_score - a.risk_score);
}

const muleAccounts = generateMuleAccounts();

export function fetchMuleRegistry(): Promise<MuleAccount[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(muleAccounts), 400);
  });
}

export function fetchMuleAccount(flagId: string): Promise<MuleAccount | undefined> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(muleAccounts.find((a) => a.flag_id === flagId)), 300);
  });
}

// ============================================================
// REPORTS (Day 3)
// ============================================================

export interface DistrictReportRow {
  district: string;
  state: string;
  complaints: number;
  highRisk: number;
  mediumRisk: number;
  lowRisk: number;
  totalAmount: number;
}

export interface BankReportRow {
  bank: string;
  flaggedAccounts: number;
  totalAmount: number;
  highRisk: number;
  mediumRisk: number;
  lowRisk: number;
}

export interface FraudTypeReportRow {
  fraudType: string;
  complaints: number;
  totalAmount: number;
  highRisk: number;
  mediumRisk: number;
  lowRisk: number;
}

export type ReportType = 'district' | 'bank' | 'fraudType';

// Generate district-wise report using confirmed complaint distribution
const districtReportData: DistrictReportRow[] = [
  { district: 'Delhi', state: 'Delhi', complaints: 1840, highRisk: 42, mediumRisk: 68, lowRisk: 24, totalAmount: 28400000 },
  { district: 'Delhi NCR', state: 'Haryana', complaints: 1150, highRisk: 28, mediumRisk: 45, lowRisk: 18, totalAmount: 16700000 },
  { district: 'Mumbai', state: 'Maharashtra', complaints: 1150, highRisk: 22, mediumRisk: 38, lowRisk: 15, totalAmount: 14200000 },
  { district: 'Jamtara', state: 'Jharkhand', complaints: 460, highRisk: 31, mediumRisk: 12, lowRisk: 4, totalAmount: 5800000 },
];

const bankReportData: BankReportRow[] = [
  { bank: 'State Bank of India', flaggedAccounts: 18, totalAmount: 8400000, highRisk: 8, mediumRisk: 7, lowRisk: 3 },
  { bank: 'HDFC Bank', flaggedAccounts: 14, totalAmount: 6200000, highRisk: 5, mediumRisk: 6, lowRisk: 3 },
  { bank: 'ICICI Bank', flaggedAccounts: 11, totalAmount: 4800000, highRisk: 4, mediumRisk: 5, lowRisk: 2 },
  { bank: 'Axis Bank', flaggedAccounts: 9, totalAmount: 3900000, highRisk: 3, mediumRisk: 4, lowRisk: 2 },
  { bank: 'Punjab National Bank', flaggedAccounts: 7, totalAmount: 2800000, highRisk: 2, mediumRisk: 3, lowRisk: 2 },
  { bank: 'Bank of Baroda', flaggedAccounts: 6, totalAmount: 2100000, highRisk: 2, mediumRisk: 3, lowRisk: 1 },
  { bank: 'Canara Bank', flaggedAccounts: 5, totalAmount: 1700000, highRisk: 1, mediumRisk: 3, lowRisk: 1 },
  { bank: 'Kotak Mahindra', flaggedAccounts: 4, totalAmount: 1300000, highRisk: 1, mediumRisk: 2, lowRisk: 1 },
];

const fraudTypeReportData: FraudTypeReportRow[] = [
  { fraudType: 'UPI Fraud', complaints: 1820, totalAmount: 22400000, highRisk: 48, mediumRisk: 62, lowRisk: 22 },
  { fraudType: 'Loan App Scam', complaints: 980, totalAmount: 11800000, highRisk: 32, mediumRisk: 41, lowRisk: 15 },
  { fraudType: 'Investment Scam', complaints: 740, totalAmount: 15600000, highRisk: 24, mediumRisk: 35, lowRisk: 12 },
  { fraudType: 'Job Fraud', complaints: 520, totalAmount: 4200000, highRisk: 12, mediumRisk: 28, lowRisk: 10 },
  { fraudType: 'Phishing', complaints: 410, totalAmount: 2800000, highRisk: 8, mediumRisk: 22, lowRisk: 14 },
  { fraudType: 'Identity Theft', complaints: 350, totalAmount: 6500000, highRisk: 14, mediumRisk: 18, lowRisk: 8 },
];

export function fetchDistrictReport(): Promise<DistrictReportRow[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(districtReportData), 400);
  });
}

export function fetchBankReport(): Promise<BankReportRow[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(bankReportData), 400);
  });
}

export function fetchFraudTypeReport(): Promise<FraudTypeReportRow[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(fraudTypeReportData), 400);
  });
}
