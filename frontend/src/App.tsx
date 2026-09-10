import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import DashboardShell from "./components/DashboardShell";
import { AuthProvider, useAuth } from "./store/AuthContext";
import LiveMap from "./pages/LiveMap";
import Forecast from "./pages/Forecast";
import SafeRoutes from "./pages/SafeRoutes";
import Reports from "./pages/Reports";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";

function ProtectedRoute({ children }: { children: React.ReactNode }) { const { user, loading } = useAuth(); if (loading) return <div className="auth-loading">Loading FloodFlow…</div>; return user ? <>{children}</> : <Navigate to="/login" replace />; }
function AdminRoute({ children }: { children: React.ReactNode }) { const { user } = useAuth(); const location = useLocation(); if (user?.role !== "ADMIN") return <Navigate to="/" state={{ from: location.pathname }} replace />; return <>{children}</>; }

function AppRoutes() { return <Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />
  <Route element={<ProtectedRoute><DashboardShell /></ProtectedRoute>}>
    <Route path="/" element={<LiveMap />} /><Route path="/forecast" element={<Forecast />} /><Route path="/routes" element={<SafeRoutes />} /><Route path="/reports" element={<Reports />} /><Route path="/profile" element={<Profile />} /><Route path="/admin" element={<AdminRoute><Reports /></AdminRoute>} />
  </Route>
  <Route path="*" element={<Navigate to="/" replace />} />
</Routes>; }

export default function App() { return <AuthProvider><BrowserRouter><AppRoutes /></BrowserRouter></AuthProvider>; }
