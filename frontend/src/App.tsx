import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { SocketProvider } from '@/context/SocketContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import RoleDashboard from '@/components/RoleDashboard';
import Login from '@/pages/Login';
import DashboardPage from '@/pages/DashboardPage';
import HeatmapPage from '@/pages/HeatmapPage';
import AlertsPage from '@/pages/AlertsPage';
import AlertDetailPage from '@/pages/AlertDetailPage';
import BlockchainLogPage from '@/pages/BlockchainLogPage';
import MuleRegistryPage from '@/pages/MuleRegistryPage';
import ReportsPage from '@/pages/ReportsPage';
import DispatchLogPage from '@/pages/DispatchLogPage';
import SettingsPage from '@/pages/SettingsPage';

export default function App() {
  return (
    <AuthProvider>
      <SocketProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <RoleDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/heatmap"
              element={
                <ProtectedRoute allowedRoles={['cyber_cell_officer', 'i4c_admin']}>
                  <HeatmapPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/alerts"
              element={
                <ProtectedRoute>
                  <AlertsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/alerts/:id"
              element={
                <ProtectedRoute>
                  <AlertDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/blockchain"
              element={
                <ProtectedRoute allowedRoles={['cyber_cell_officer', 'i4c_admin']}>
                  <BlockchainLogPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/registry"
              element={
                <ProtectedRoute allowedRoles={['cyber_cell_officer', 'i4c_admin']}>
                  <MuleRegistryPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute allowedRoles={['cyber_cell_officer', 'bank_nodal_officer', 'i4c_admin']}>
                  <ReportsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dispatch-log"
              element={
                <ProtectedRoute>
                  <DispatchLogPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </SocketProvider>
    </AuthProvider>
  );
}
