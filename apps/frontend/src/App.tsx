import { Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import DashboardLayout from './components/layout/DashboardLayout';
import LoadingSpinner from './components/ui/LoadingSpinner';

// Lazy-loaded pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const CareerProfile = lazy(() => import('./pages/CareerProfile'));
const CVManager = lazy(() => import('./pages/CVManager'));
const JobOpportunities = lazy(() => import('./pages/JobOpportunities'));
const JobApplications = lazy(() => import('./pages/JobApplications'));
const Interviews = lazy(() => import('./pages/Interviews'));
const FollowUps = lazy(() => import('./pages/FollowUps'));
const Documents = lazy(() => import('./pages/Documents'));
const AIAssistant = lazy(() => import('./pages/AIAssistant'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));

function App() {
  return (
    <AuthProvider>
      <Suspense fallback={<LoadingSpinner fullScreen />}>
        <Routes>
          {/* Auth routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected dashboard routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="profile" element={<CareerProfile />} />
            <Route path="cvs" element={<CVManager />} />
            <Route path="jobs" element={<JobOpportunities />} />
            <Route path="applications" element={<JobApplications />} />
            <Route path="interviews" element={<Interviews />} />
            <Route path="follow-ups" element={<FollowUps />} />
            <Route path="documents" element={<Documents />} />
            <Route path="ai-assistant" element={<AIAssistant />} />
            <Route path="analytics" element={<Analytics />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
    </AuthProvider>
  );
}

export default App;
