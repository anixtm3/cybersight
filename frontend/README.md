\# CyberSight AI — Frontend



Cybercrime Intelligence Platform — Investigator Dashboard

Built for SIH 2026, PS 26184 (MHA / I4C, Blockchain \& Cybersecurity theme)



\## Tech Stack

\- React 18 + TypeScript, Vite

\- TailwindCSS

\- React Router

\- Leaflet.js (GIS heatmap)

\- Recharts (SHAP charts, reports)

\- Lucide React (icons)



\## Features Built



\### Day 1 — Foundation

\- Design system (palette, type scale, spacing, component primitives)

\- App shell — login, sidebar, routing

\- 3 role-based views: Cyber Cell Officer, Bank Nodal Officer, I4C Admin



\### Day 2 — Command Centre, Heatmap, Drill-down

\- Command Centre — live WebSocket alert feed, severity-coded, 4-channel dispatch status (SMS/Email/Webhook/Dashboard)

\- GIS Risk Heatmap — Leaflet map, choropleth district zones (HIGH/MEDIUM/LOW), filter bar (date range, district, fraud type, risk level)

\- Zone drill-down — click a zone to see ranked ATMs (bank, coordinates, risk score)

\- Top-5 ATM prediction markers wired to `/api/predict`



\### Day 3 — SHAP, Registry, Reports

\- SHAP Explanation Panel — per-prediction location factor analysis (directional influence, redesigned for the real lat/lon-based model output)

\- Mule Registry — flagged accounts table + on-chain proof detail (tx hash, flagging authority, evidence basis, block timestamp)

\- Reports — District-wise / Bank-wise / Fraud-typology-wise tabs + CSV export

\- Alert Dispatch Log screen



\### Day 4 — Polish \& Integration

\- Loading / empty / error states across all screens (no blank/crash pages)

\- Page/panel transitions

\- WebSocket JWT auth (token sent on connect, 4001 close-code handling)

\- 3 genuinely distinct role dashboards (Cyber Cell — investigation view; Bank Nodal — freeze-action view; I4C Admin — oversight view with stats + cross-jurisdiction overview)

\- Mock-data fallback for all screens when backend is unreachable (with a "cached data" indicator that hides automatically once live)



\## Known Open Items (backend-dependent, not frontend-blocking)

\- Mule Registry `tx\_hash` — pending Aniket's smart contract update (Keccak-256 hashing decision made; contract-level storage still pending)

\- Full live end-to-end backend integration test — pending Kartike's backend being consistently live

\- `beneficiary\_bank` field mapping — model only accepts 8 short bank-name codes (Axis, BOB, Canara, HDFC, ICICI, Kotak, PNB, SBI); needs confirmation on whether frontend needs a bank-selection form or if this is backend-only



\## Setup



```bash

npm install

npm run dev

```



Runs on `http://localhost:5173` by default.



\## Environment

Backend API base URL and WebSocket URL are configured in `src/config.ts` — update there if the backend host/port changes.



\## Demo Roles

Login screen offers 3 mock roles (JWT-based auth once backend is connected):

\- Cyber Cell Officer

\- Bank Nodal Officer

\- I4C Admin

