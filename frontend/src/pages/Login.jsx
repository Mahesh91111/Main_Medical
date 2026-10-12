
import { useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import {
  Activity,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail
} from "lucide-react";

import { useAuth } from "../context/useAuth";

export default function Login() {
  const { login, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  const [email, setEmail] = useState(location.state?.email || "");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const destination = location.state?.from?.pathname || "/dashboard";

  if (loading) {
    return <div className="auth-loading">Checking session...</div>;
  }

  if (isAuthenticated) {
    return <Navigate to={destination} replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!email.trim() || !password) {
      setError("Enter your email address and password.");
      return;
    }

    setSubmitting(true);

    try {
      await login({
        email: email.trim(),
        password
      });
    } catch (err) {
      const status = err.response?.status;

      if (status === 401 || status === 400) {
        setError("Invalid email or password.");
      } else if (!err.response) {
        setError(
          "Cannot connect to the server. Check that the FastAPI backend is running."
        );
      } else {
        setError(
          err.response?.data?.detail ||
          "Unable to sign in. Please try again."
        );
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-brand-panel">
        <div className="auth-brand">
          <span className="auth-brand-icon">
            <Activity size={25} />
          </span>
          <span>Clinica</span>
        </div>

        <div className="auth-brand-copy">
          <p className="eyebrow">CLINICAL INTELLIGENCE PLATFORM</p>
          <h1>Better insights.<br />More informed care.</h1>
          <p>
            Access your clinical workspace, medical documents,
            and AI-assisted tools from one secure application.
          </p>
        </div>

        <p className="auth-brand-footer">
          AI Medical Assistant & Clinical Intelligence
        </p>
      </section>

      <section className="auth-form-panel">
        <div className="auth-form-container">
          <div className="auth-mobile-brand">
            <Activity size={24} />
            <span>Clinica</span>
          </div>

          <p className="eyebrow">WELCOME BACK</p>
          <h2>Sign in to your account</h2>
          <p className="auth-subtitle">
            Enter your credentials to access your workspace.
          </p>

          <form onSubmit={handleSubmit} className="auth-form">
            <label htmlFor="email">Email address</label>
            <div className="auth-input-wrap">
              <Mail size={18} aria-hidden="true" />
              <input
                id="email"
                type="email"
                autoComplete="username"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <label htmlFor="password">Password</label>
            <div className="auth-input-wrap">
              <LockKeyhole size={18} aria-hidden="true" />
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((visible) => !visible)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            {location.state?.registered && !error && (
              <div className="auth-success" role="status">
                Account created successfully. Please sign in to continue.
              </div>
            )}

            {error && (
              <div className="auth-error" role="alert">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="auth-submit"
              disabled={submitting}
            >
              {submitting ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account?{" "}
            <Link to="/register">Create an account</Link>
          </p>

          <p className="auth-security-note">
            <LockKeyhole size={14} />
            Secure access for authorized users
          </p>
        </div>
      </section>
    </main>
  );
}
