import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { Settings, Bell, Shield, Database, Globe } from 'lucide-react';

function SettingRow({ icon: Icon, title, desc, children }: { icon: typeof Settings; title: string; desc: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-4 border-b border-gray-100">
      <div className="flex items-start gap-3">
        <div className="w-9 h-9 rounded-lg bg-surface flex items-center justify-center shrink-0">
          <Icon size={18} className="text-navy" />
        </div>
        <div>
          <p className="text-sm font-medium text-navy">{title}</p>
          <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
        </div>
      </div>
      {children}
    </div>
  );
}

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-white animate-fade-in">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-navy">Settings</h1>
          <p className="text-sm text-gray-500 mt-1">Configure dashboard preferences and integrations</p>
        </div>
        <div className="max-w-2xl tac-card px-5">
          <SettingRow icon={Bell} title="Real-time Alerts" desc="Receive socket-based push notifications">
            <button className="relative w-11 h-6 rounded-full bg-navy" aria-label="Toggle alerts">
              <span className="absolute right-0.5 top-0.5 w-5 h-5 rounded-full bg-white" />
            </button>
          </SettingRow>
          <SettingRow icon={Shield} title="Threat Threshold" desc="Minimum risk score to trigger alerts">
            <select className="border border-gray-200 rounded-lg px-3 py-2 text-sm text-navy" style={{ minHeight: 36 }}>
              <option>Low (35+)</option>
              <option>Medium (50+)</option>
              <option>High (60+)</option>
              <option>Critical (80+)</option>
            </select>
          </SettingRow>
          <SettingRow icon={Database} title="Data Source" desc="Backend API endpoint for alerts">
            <span className="text-xs font-mono text-gray-500 bg-surface px-3 py-1.5 rounded">http://localhost:8000/api/v1</span>
          </SettingRow>
          <SettingRow icon={Globe} title="Socket Server" desc="Real-time socket connection URL">
            <span className="text-xs font-mono text-gray-500 bg-surface px-3 py-1.5 rounded">http://localhost:8000/api/v1</span>
          </SettingRow>
        </div>
      </main>
    </div>
  );
}
