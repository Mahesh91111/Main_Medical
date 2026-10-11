
import { Link } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  Clock3,
  FileText,
  FlaskConical,
  ShieldCheck,
  Sparkles,
  Users
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import StatCard from "../components/common/StatCard";
import SectionHeader from "../components/common/SectionHeader";

const stats = [
  {
    title: "Total patients",
    value: "—",
    description: "Connect the patient API to load data",
    icon: Users,
    tone: "blue"
  },
  {
    title: "Medical documents",
    value: "—",
    description: "Connect document ingestion",
    icon: FileText,
    tone: "purple"
  },
  {
    title: "AI interactions",
    value: "—",
    description: "Connect assistant activity",
    icon: BrainCircuit,
    tone: "green"
  },
  {
    title: "Research resources",
    value: "—",
    description: "Connect research resources",
    icon: FlaskConical,
    tone: "orange"
  }
];

const quickActions = [
  {
    title: "Patient management",
    description: "View and manage authorized patient records.",
    path: "/patients",
    icon: Users,
    tone: "blue"
  },
  {
    title: "Medical documents",
    description: "Upload and review clinical documents.",
    path: "/documents",
    icon: FileText,
    tone: "purple"
  },
  {
    title: "AI medical assistant",
    description: "Explore AI-assisted clinical information.",
    path: "/ai-assistant",
    icon: BrainCircuit,
    tone: "green"
  },
  {
    title: "Research workspace",
    description: "Access your authorized research tools.",
    path: "/research",
    icon: FlaskConical,
    tone: "orange"
  }
];

const activities = [
  {
    icon: CheckCircle2,
    title: "Workspace initialized",
    description: "The frontend workspace is ready for integration.",
    time: "Setup"
  },
  {
    icon: ShieldCheck,
    title: "Authentication configured",
    description: "Session handling is managed through AuthContext.",
    time: "Setup"
  },
  {
    icon: Clock3,
    title: "Backend integration pending",
    description: "Live metrics will appear when API integration is added.",
    time: "Pending"
  }
];

export default function Dashboard() {
  const { user } = useAuth();

  const name =
    user?.full_name ||
    user?.name ||
    user?.email?.split("@")[0] ||
    "there";

  return (
    <div className="dashboard-page">
      <section className="dashboard-welcome">
        <div className="welcome-copy">
          <span className="welcome-label">
            <Sparkles size={15} />
            YOUR CLINICAL WORKSPACE
          </span>

          <h1>Welcome back, {name}</h1>

          <p>
            Your workspace is ready. Use the tools below to
            continue your authorized clinical or research tasks.
          </p>
        </div>

        <div className="welcome-illustration" aria-hidden="true">
          <div className="illustration-ring ring-one" />
          <div className="illustration-ring ring-two" />
          <div className="illustration-cross">
            <Activity size={50} />
          </div>
          <span className="illustration-dot dot-one" />
          <span className="illustration-dot dot-two" />
        </div>
      </section>

      <section className="dashboard-stats">
        {stats.map((stat) => (
          <StatCard key={stat.title} {...stat} />
        ))}
      </section>

      <section className="dashboard-section">
        <SectionHeader
          title="Quick access"
          description="Jump directly into a workspace."
        />

        <div className="quick-actions-grid">
          {quickActions.map((action) => {
            const Icon = action.icon;

            return (
              <Link
                to={action.path}
                key={action.path}
                className="quick-action-card"
              >
                <div className={`quick-action-icon stat-icon-${action.tone}`}>
                  <Icon size={22} />
                </div>

                <h4>{action.title}</h4>
                <p>{action.description}</p>

                <span className="quick-action-link">
                  Open workspace <ArrowRight size={15} />
                </span>
              </Link>
            );
          })}
        </div>
      </section>

      <div className="dashboard-bottom-grid">
        <section className="dashboard-panel">
          <SectionHeader
            title="Workspace activity"
            description="Platform setup and integration status."
          />

          <div className="activity-list">
            {activities.map((activity) => {
              const Icon = activity.icon;

              return (
                <div className="activity-item" key={activity.title}>
                  <div className="activity-icon">
                    <Icon size={18} />
                  </div>

                  <div className="activity-copy">
                    <strong>{activity.title}</strong>
                    <p>{activity.description}</p>
                  </div>

                  <span className="activity-time">{activity.time}</span>
                </div>
              );
            })}
          </div>
        </section>

        <section className="dashboard-panel safety-panel">
          <div className="safety-icon">
            <ShieldCheck size={23} />
          </div>

          <h3>Clinical safety</h3>

          <p>
            AI-generated information is intended to support
            authorized professional workflows, not replace
            clinical judgment.
          </p>

          <div className="safety-divider" />

          <div className="safety-note">
            <ShieldCheck size={16} />
            <span>
              Follow your organization's privacy, access, and
              clinical review procedures.
            </span>
          </div>
        </section>
      </div>
    </div>
  );
}
