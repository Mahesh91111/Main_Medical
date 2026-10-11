
import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import AppLayout from "../components/layout/AppLayout";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard";
import Patients from "../pages/Patients";
import PatientDetails from "../pages/PatientDetails";
import Documents from "../pages/Documents";
import MedicalAssistant from "../pages/MedicalAssistant";
import Research from "../pages/Research";

function ProtectedRoute({ allowedRoles }) {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="auth-loading">
        Loading your workspace...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/register" replace />;
  }

  if (
    allowedRoles &&
    !allowedRoles.includes(String(user?.role || "").toLowerCase())
  ) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}

function PlaceholderPage({ title, description }) {
  return (
    <section className="placeholder-page">
      <div className="placeholder-icon">+</div>
      <h1>{title}</h1>
      <p>{description}</p>
      <span>This module will be implemented in a later phase.</span>
    </section>
  );
}

function NotFound() {
  return (
    <section className="placeholder-page">
      <h1>Page not found</h1>
      <p>The requested page does not exist.</p>
    </section>
  );
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />

          <Route path="/dashboard" element={<Dashboard />} />

          <Route element={<ProtectedRoute allowedRoles={["clinician", "admin"]} />}>
            <Route path="/patients" element={<Patients />} />
            <Route path="/patients/:patientId" element={<PatientDetails />} />

            <Route
              path="/ai-assistant"
              element={<MedicalAssistant />}
            />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={["clinician", "researcher", "admin"]} />}>
            <Route path="/documents" element={<Documents />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={["researcher", "admin"]} />}>
            <Route
              path="/research"
              element={<Research />}
            />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
