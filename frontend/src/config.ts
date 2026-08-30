// Centralized API configuration — single source of truth for endpoints.
// Override via Vite env vars: VITE_API_BASE_URL, VITE_WS_BASE_URL
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const WS_BASE = import.meta.env.VITE_WS_BASE_URL ?? 'ws://localhost:8000';

export const WS_ALERTS_URL = `${WS_BASE}/ws/alerts`;
export const API_BASE_URL = API_BASE;
export const HEATMAP_ENDPOINT = `${API_BASE}/api/heatmap`;
export const COMPLAINT_FULL_ENDPOINT = (caseId: string) =>
  `${API_BASE}/api/complaints/${caseId}/full`;
