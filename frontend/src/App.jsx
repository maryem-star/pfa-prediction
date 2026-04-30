import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import AdminDashboard from "./pages/AdminDashboard";
import StudentsPage from "./pages/StudentsPage";
import PredictionPage from "./pages/PredictionPage";
import BatchPredictionPage from "./pages/BatchPredictionPage";
import StudentProfilePage from "./pages/StudentProfilePage";
import AnalysisPage from "./pages/AnalysisPage";
import StudentDashboard from "./pages/StudentDashboard";
import UsersManagementPage from "./pages/UsersManagementPage";
import AdminPage from "./pages/AdminPage";
import StudentLogin from "./pages/StudentLogin";
import HomePage from "./pages/HomePage";
import api from "./services/api";

function ProtectedRoute({ children, allowedRoles }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/" replace />;
  if (allowedRoles && !allowedRoles.some(r => user.role?.startsWith(r) || user.role === r)) {
    return <Navigate to="/" replace />;
  }
  return children;
}

function RoleRedirect() {
  const { user, getHomeRoute } = useAuth();
  // Si pas connecté → HomePage (choix étudiant/staff)
  if (!user) return <Navigate to="/home" replace />;
  // Si connecté → espace dédié selon le rôle
  return <Navigate to={getHomeRoute(user.role)} replace />;
}

const STAFF_ROLES = ["super_admin", "directeur_adjoint", "chef_departement", "chef_filiere"];

function AppRoutes() {
  return (
    <Routes>

      {/* Page d'accueil */}
      <Route path="/" element={<RoleRedirect />} />
      <Route path="/home" element={<HomePage />} />

      {/* Login staff */}
      <Route path="/login" element={<LoginPage />} />

      {/* Login étudiant */}
      <Route path="/student/login" element={<StudentLogin />} />

      {/* Staff routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute allowedRoles={STAFF_ROLES}>
          <AdminDashboard />
        </ProtectedRoute>
      } />
      <Route path="/students" element={
        <ProtectedRoute allowedRoles={STAFF_ROLES}>
          <StudentsPage />
        </ProtectedRoute>
      } />
      <Route path="/students/:id/stats" element={
        <ProtectedRoute allowedRoles={STAFF_ROLES}>
          <StudentProfilePage />
        </ProtectedRoute>
      } />
      <Route path="/students/:id" element={
        <ProtectedRoute allowedRoles={STAFF_ROLES}>
          <StudentProfilePage />
        </ProtectedRoute>
      } />
      <Route path="/prediction" element={
        <ProtectedRoute allowedRoles={STAFF_ROLES}>
          <PredictionPage />
        </ProtectedRoute>
      } />
      <Route path="/batch" element={
        <ProtectedRoute allowedRoles={STAFF_ROLES}>
          <BatchPredictionPage />
        </ProtectedRoute>
      } />
      <Route path="/analysis" element={
        <ProtectedRoute allowedRoles={STAFF_ROLES}>
          <AnalysisPage />
        </ProtectedRoute>
      } />
      <Route path="/users" element={
        <ProtectedRoute allowedRoles={["super_admin", "directeur_adjoint", "chef_departement"]}>
          <UsersManagementPage />
        </ProtectedRoute>
      } />
      <Route path="/admin" element={
        <ProtectedRoute allowedRoles={STAFF_ROLES}>
          <AdminPage />
        </ProtectedRoute>
      } />

      {/* Espace étudiant */}
      <Route path="/student-dashboard" element={
        <ProtectedRoute allowedRoles={["etudiant"]}>
          <StudentDashboard />
        </ProtectedRoute>
      } />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/home" replace />} />

    </Routes>
  );
}
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // ✅ Redirige vers /home au lieu de /login
      window.location.href = "/home";
    }
    return Promise.reject(error);
  }
);
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}