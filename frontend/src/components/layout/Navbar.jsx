
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Bell,
  ChevronDown,
  LogOut,
  Menu,
  UserRound
} from "lucide-react";

import { useAuth } from "../../context/useAuth";

const pageTitles = {
  "/dashboard": "Overview",
  "/patients": "Patients",
  "/documents": "Medical documents",
  "/ai-assistant": "AI assistant",
  "/research": "Research"
};

export default function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const title =
    location.pathname.startsWith("/patients/") && location.pathname !== "/patients"
      ? "Patient details"
      : pageTitles[location.pathname] || "Workspace";

  const displayName =
    user?.full_name || user?.name || user?.email || "User";

  const initials = displayName
    .split(/[\s@._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button
          className="icon-button mobile-menu-button"
          onClick={onMenuClick}
          aria-label="Open navigation"
        >
          <Menu size={21} />
        </button>

        <div>
          <h2>{title}</h2>
          <p>Clinical Intelligence Platform</p>
        </div>
      </div>

      <div className="topbar-actions">
        <button
          className="icon-button notification-button"
          aria-label="Notifications"
          title="Notifications are not implemented yet"
        >
          <Bell size={19} />
        </button>

        <div className="profile-menu-wrapper">
          <button
            className="profile-trigger"
            onClick={() => setMenuOpen((value) => !value)}
            aria-expanded={menuOpen}
          >
            <span className="avatar">{initials || <UserRound size={18} />}</span>

            <span className="profile-copy">
              <strong>{displayName}</strong>
              <small>{user?.role || "User"}</small>
            </span>

            <ChevronDown size={16} />
          </button>

          {menuOpen && (
            <>
              <button
                className="profile-dismiss"
                aria-label="Close profile menu"
                onClick={() => setMenuOpen(false)}
              />

              <div className="profile-dropdown">
                <div className="profile-dropdown-info">
                  <strong>{displayName}</strong>
                  <span>{user?.email || ""}</span>
                </div>

                <button
                  className="dropdown-logout"
                  onClick={handleLogout}
                >
                  <LogOut size={17} />
                  Sign out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
