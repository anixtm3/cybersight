import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import LiveStatusStrip from '@/components/LiveStatusStrip';
import HeatmapPanel from '@/components/HeatmapPanel';

export default function HeatmapPage() {
  return (
    <div className="min-h-screen bg-white bg-grid animate-fade-in">
      <Navbar />
      <Sidebar />
      <main className="ml-sidebar mt-navbar p-6">
        <LiveStatusStrip />
        <div className="mb-4 mt-4">
          <h1 className="text-xl font-bold text-navy">GIS Risk Heatmap</h1>
          <p className="text-sm text-gray-500 mt-1">
            Choropleth risk zones with top 5 highest-risk ATM markers — click any zone to drill down to ranked ATMs
          </p>
        </div>
        <HeatmapPanel />
      </main>
    </div>
  );
}
