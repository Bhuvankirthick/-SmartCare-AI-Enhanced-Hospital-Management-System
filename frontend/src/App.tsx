import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProtectedRoute from './routes/ProtectedRoute';
import Login from './pages/Login';
import AdminDashboard from './pages/admin/AdminDashboard';
import DoctorDashboard from './pages/doctor/DoctorDashboard';
import PatientDashboard from './pages/patient/PatientDashboard';
import ReceptionistDashboard from './pages/receptionist/ReceptionistDashboard';
import PharmacistDashboard from './pages/pharmacist/PharmacistDashboard';
import { useAuthStore } from './store/authStore';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30000 } },
});

function RootRedirect() {
  const { isAuthenticated, user } = useAuthStore();
  if (!isAuthenticated || !user) return <Navigate to="/login" replace />;
  return <Navigate to={`/${user.role}`} replace />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<Login />} />

          <Route path="/admin/*" element={
            <ProtectedRoute roles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          } />

          <Route path="/doctor/*" element={
            <ProtectedRoute roles={['doctor', 'admin']}>
              <DoctorDashboard />
            </ProtectedRoute>
          } />

          <Route path="/patient/*" element={
            <ProtectedRoute roles={['patient', 'admin']}>
              <PatientDashboard />
            </ProtectedRoute>
          } />

          <Route path="/receptionist/*" element={
            <ProtectedRoute roles={['receptionist', 'admin']}>
              <ReceptionistDashboard />
            </ProtectedRoute>
          } />

          <Route path="/pharmacist/*" element={
            <ProtectedRoute roles={['pharmacist', 'admin']}>
              <PharmacistDashboard />
            </ProtectedRoute>
          } />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
