
import { NavLink } from "react-router-dom";
import {
  Activity,
  BrainCircuit,
  FileText,
  FlaskConical,
  LayoutDashboard,
  Users,
  X
} from "lucide-react";

import { useAuth } from "../../context/AuthContext";

const navigation = [
  {
    label: "Overview",
    path: "/dashboard",
    icon: LayoutDashboard,
    roles: ["clinician", "researcher", "admin"]
  },
  {
    label: "Patients",
    path: "/patients",
    icon: Users,
    roles: ["clinician", "admin"]
  },
  {
    label: "Medical documents",
    path: "/documents",
    icon: FileText,
    roles: ["clinician", "researcher", "admin"]
  },
  {
    label: "AI assistant",
    path: "/ai-assistant",
    icon: BrainCircuit,
    roles: ["clinician", "admin"]
  },
  {
    label: "Research",
    path: "/research",
    icon: FlaskConical,
    roles: ["researcher", "admin"]
  }
];

export default function Sidebar({ open, onClose }) {
  const { user } = useAuth();
  const role = String(user?.role || "").toLowerCase();

  const items = navigation.filter((item) =>
    item.roles.includes(role)
  );

  return (
    <>
      {open && (
        <button
          className="sidebar-overlay"
          aria-label="Close navigation"
          onClick={onClose}
        />
      )}

      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Activity size={23} />
          </div>
          <div>
            <strong>Clinica</strong>
            <span>Medical intelligence</span>
          </div>

          <button
            className="sidebar-close"
            aria-label="Close navigation"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-section-label">WORKSPACE</div>

        <nav className="sidebar-nav">
          {items.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end
              onClick={onClose}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={19} strokeWidth={1.9} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-security">
            <div className="security-indicator" />
            <div>
              <strong>Clinical workspace</strong>
              <span>Authorized access only</span>
            </div>
          </div>
          <p className="sidebar-version">CLINICA · PHASE 3</p>
        </div>
      </aside>
    </>
  );
}
