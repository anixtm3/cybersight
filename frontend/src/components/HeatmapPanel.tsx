import { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMap } from 'react-leaflet';
import type { PathOptions, DivIcon } from 'leaflet';
import { MapPinOff } from 'lucide-react';
import {
  fetchHeatmapData,
  fetchTopAtmPredictions,
  type HeatmapFilters,
  type HeatmapGeoJSON,
  type RiskZoneFeature,
  type AtmPrediction,
  type RiskLevel,
} from '@/services/mockApi';
import HeatmapFiltersBar from './HeatmapFiltersBar';
import ZoneDrillDown from './ZoneDrillDown';
import { Spinner, EmptyState, RetryErrorState } from './Loading';

const riskFillColor: Record<string, string> = {
  HIGH: '#dc2626',
  MEDIUM: '#ea580c',
  LOW: '#15803d',
};

const riskFillOpacity: Record<string, number> = {
  HIGH: 0.55,
  MEDIUM: 0.45,
  LOW: 0.35,
};

function atmMarkerColor(level: RiskLevel): string {
  return riskFillColor[level] ?? '#94a3b8';
}

function atmMarkerIcon(level: RiskLevel): DivIcon {
  const color = atmMarkerColor(level);
  const size = level === 'HIGH' ? 18 : level === 'MEDIUM' ? 16 : 14;
  return window.L?.divIcon({
    className: 'atm-marker-icon',
    html: `<div style="
      width:${size}px;height:${size}px;border-radius:50% 50% 50% 0;
      background:${color};transform:rotate(-45deg);
      border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.4);
    "></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size],
  }) ?? window.L.divIcon({ className: 'atm-marker-icon', html: '' });
}

function InvalidateMapSize({ onReady }: { onReady: () => void }) {
  const map = useMap();
  useEffect(() => {
    const t = setTimeout(() => {
      map.invalidateSize();
      onReady();
    }, 200);
    return () => clearTimeout(t);
  }, [map, onReady]);
  return null;
}

const defaultFilters: HeatmapFilters = {
  dateRange: {
    start: new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10),
    end: new Date().toISOString().slice(0, 10),
  },
  district: 'all',
  fraudType: 'all',
  riskLevel: [],
};

export default function HeatmapPanel() {
  const [filters, setFilters] = useState<HeatmapFilters>(defaultFilters);
  const [geoData, setGeoData] = useState<HeatmapGeoJSON | null>(null);
  const [topAtms, setTopAtms] = useState<AtmPrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [selectedZone, setSelectedZone] = useState<{ zoneId: string; zoneName: string } | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const [data, atms] = await Promise.all([
        fetchHeatmapData(filters),
        fetchTopAtmPredictions(),
      ]);
      setGeoData(data);
      setTopAtms(atms);
      setLoading(false);
    } catch {
      setError(true);
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    load();
  }, [load]);

  const styleFor = (feature: { properties: Record<string, unknown> } | undefined): PathOptions => {
    if (!feature || !feature.properties) return {};
    const level = (feature.properties.riskLevel as string) || 'LOW';
    return {
      fillColor: riskFillColor[level] || '#94a3b8',
      fillOpacity: riskFillOpacity[level] || 0.4,
      color: riskFillColor[level] || '#94a3b8',
      weight: 2.5,
      opacity: 0.9,
    };
  };

  return (
    <div className="flex flex-col">
      {/* Filter bar */}
      <HeatmapFiltersBar filters={filters} onChange={setFilters} />

      {/* Map */}
      <div className="tac-card overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
          <h3 className="font-bold text-navy text-sm">GIS Risk Heatmap — Zone + ATM View</h3>
          <span className="text-xs text-gray-400 data-mono">
            {geoData ? `${geoData.features.length} zones · ${topAtms.length} top ATMs` : loading ? 'Loading…' : '—'}
          </span>
        </div>

        <div className="relative" style={{ height: 500 }}>
          {loading && (
            <div className="absolute inset-0 z-[1000] bg-white/80 flex items-center justify-center transition-opacity duration-200">
              <Spinner label="Establishing risk feed…" />
            </div>
          )}
          {error && !loading && (
            <div className="absolute inset-0 z-[1000] bg-white/90 flex items-center justify-center p-6">
              <RetryErrorState
                message="Unable to load heatmap data. The backend may be unreachable."
                onRetry={load}
              />
            </div>
          )}
          {!loading && !error && geoData && geoData.features.length === 0 && (
            <div className="absolute inset-0 z-[1000] bg-white/90 flex items-center justify-center p-6">
              <EmptyState
                icon={MapPinOff}
                message="No zones match these filters"
                hint="Try widening your date range or clearing filter selections."
              />
            </div>
          )}
          <MapContainer
            center={[26.5, 82.0]}
            zoom={6}
            scrollWheelZoom={true}
            className="w-full transition-opacity duration-200"
            style={{ height: 500 }}
          >
            <InvalidateMapSize onReady={() => {}} />
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            {geoData && geoData.features.length > 0 && (
              <GeoJSON
                key={JSON.stringify(filters) + geoData.features.length}
                data={geoData}
                style={styleFor}
                onEachFeature={(feature, layer) => {
                  const props = feature.properties as RiskZoneFeature['properties'] | undefined;
                  if (!props) return;
                  layer.bindTooltip(
                    `<div>
                      <div style="font-weight:bold">${props.zoneName}</div>
                      <div style="font-family:'JetBrains Mono',monospace">Risk: ${props.riskLevel} · ${props.riskScore}</div>
                      <div style="font-family:'JetBrains Mono',monospace">${props.fraudType} · ${props.complaintCount} complaints</div>
                      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;opacity:0.7">${props.atmCount} ATMs in district</div>
                      <div style="font-size:11px;margin-top:4px;opacity:0.7">Click to view ATMs</div>
                    </div>`,
                    { className: 'cybersight-tooltip' }
                  );
                  layer.on('click', () => {
                    setSelectedZone({ zoneId: props.zoneId, zoneName: props.zoneName });
                  });
                }}
              />
            )}
            {/* Top 5 ATM markers — prediction layer on top of choropleth */}
            {topAtms.map((atm) => (
              <Marker
                key={atm.atm_id}
                position={[atm.lat, atm.lng]}
                icon={atmMarkerIcon(atm.risk_level)}
              >
                <Popup>
                  <div style={{ minWidth: 160 }}>
                    <div style={{ fontWeight: 'bold', fontSize: '13px', marginBottom: '4px' }}>
                      {atm.bank_name ?? 'Bank name unavailable'}
                    </div>
                    <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px', color: '#6b7280' }}>
                      ATM: {atm.atm_id}
                    </div>
                    <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px', marginTop: '2px' }}>
                      <span style={{
                        display: 'inline-block',
                        padding: '1px 6px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 'bold',
                        color: '#fff',
                        backgroundColor: atmMarkerColor(atm.risk_level),
                      }}>
                        Risk: {atm.risk_level}
                      </span>
                    </div>
                    <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '4px' }}>
                      Confidence: {(atm.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* Legend */}
        <div className="px-4 py-3 border-t border-gray-100 flex items-center gap-4 flex-wrap">
          <span className="label">Legend</span>
          {(['HIGH', 'MEDIUM', 'LOW'] as const).map((level) => (
            <div key={level} className="flex items-center gap-1.5">
              <span
                className="inline-block w-3 h-3 rounded-sm"
                style={{ backgroundColor: riskFillColor[level] }}
              />
              <span className="text-xs text-gray-500 font-medium">{level}</span>
            </div>
          ))}
          <div className="flex items-center gap-1.5 ml-2">
            <span
              className="inline-block w-3 h-3 rounded-full"
              style={{ backgroundColor: '#dc2626' }}
            />
            <span className="text-xs text-gray-500 font-medium">Top ATM (by risk)</span>
          </div>
          <span className="text-xs text-gray-400 ml-auto data-mono">
            Click a zone to drill down to ranked ATMs
          </span>
        </div>
      </div>

      {/* Drill-down panel */}
      {selectedZone && (
        <ZoneDrillDown
          zoneId={selectedZone.zoneId}
          zoneName={selectedZone.zoneName}
          onClose={() => setSelectedZone(null)}
        />
      )}
    </div>
  );
}
