
import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { useAuth } from "../context/useAuth";
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
      <div className="auth-loading" role="status">
        Verifying your session...
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles) {
    const role = String(user.role || "").toLowerCase();
    const permittedRoles = allowedRoles.map((value) =>
      String(value).toLowerCase()
    );

    if (!permittedRoles.includes(role)) {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return <Outlet />;
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
