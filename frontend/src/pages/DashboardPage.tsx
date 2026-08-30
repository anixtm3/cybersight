import { Bell, AlertTriangle, MessageSquareWarning, ShieldCheck } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import StatCard from '@/components/StatCard';
import CommandCentre from '@/components/CommandCentre';
import BlockchainTable from '@/components/BlockchainTable';
import ShapChart from '@/components/ShapChart';
import LiveStatusStrip from '@/components/LiveStatusStrip';
import { dashboardStats, blockchainLogs } from '@/mockData';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-white bg-grid animate-fade-in">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <LiveStatusStrip />
        <div className="mb-6 mt-4">
          <h1 className="text-xl font-bold text-navy">Dashboard Overview</h1>
          <p className="text-sm text-gray-500 mt-1">
            Real-time cybercrime intelligence across Indian districts
          </p>
        </div>

        {/* Stat cards — primary stat anchored wider for visual hierarchy */}
        <div className="grid grid-cols-12 gap-4 mb-6">
          <div className="col-span-5">
            <StatCard label="Total Alerts Today" value={dashboardStats.totalAlertsToday} icon={Bell} accent="navy" primary />
          </div>
          <div className="col-span-2">
            <StatCard label="High Risk Districts" value={dashboardStats.highRiskDistricts} icon={AlertTriangle} accent="alert" />
          </div>
          <div className="col-span-2">
            <StatCard label="Complaints Last Hour" value={dashboardStats.complaintsLastHour} icon={MessageSquareWarning} accent="danger" />
          </div>
          <div className="col-span-3">
            <StatCard label="Interceptions" value={dashboardStats.interceptions} icon={ShieldCheck} accent="success" />
          </div>
        </div>

        {/* Middle row — Command Centre + SHAP */}
        <div className="grid grid-cols-10 gap-4 mb-6">
          <div className="col-span-7">
            <CommandCentre />
          </div>
          <div className="col-span-3">
            <ShapChart />
          </div>
        </div>

        {/* Bottom row */}
        <div className="grid grid-cols-10 gap-4">
          <div className="col-span-10">
            <BlockchainTable logs={blockchainLogs} compact />
          </div>
        </div>
      </main>
    </div>
  );
}
