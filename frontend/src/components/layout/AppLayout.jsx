
import { useState } from "react";
import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-shell">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="app-main">
        <Navbar onMenuClick={() => setSidebarOpen(true)} />

        <main className="page-content">
          <Outlet />
        </main>

        <footer className="app-footer">
          <span>Clinica Medical Intelligence</span>
          <span>AI-assisted clinical workflows</span>
        </footer>
      </div>
    </div>
  );
}
