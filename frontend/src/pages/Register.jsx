import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import {
  Activity,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  User
} from "lucide-react";

import { registerUser } from "../api/auth";
import { useAuth } from "../context/useAuth";

const MIN_PASSWORD_LENGTH = 12;

export default function Register() {
  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (loading) {
    return <div className="auth-loading">Checking session...</div>;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const cleanName = fullName.trim();
    const cleanEmail = email.trim();

    if (cleanName.length < 2) {
      setError("Enter your full name (at least 2 characters).");
      return;
    }

    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(`Your password must be at least ${MIN_PASSWORD_LENGTH} characters long.`);
      return;
    }

    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }

    setSubmitting(true);

    try {
      await registerUser({
        email: cleanEmail,
        full_name: cleanName,
        password
      });

      // Registration worked, so send the user to the login page.
      navigate("/login", {
        replace: true,
        state: { registered: true, email: cleanEmail }
      });
    } catch (err) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;

      if (!err.response) {
        setError(
          "Cannot connect to the server. Check that the FastAPI backend is running."
        );
      } else if (status === 409) {
        setError(
          typeof detail === "string"
            ? detail
            : "An account with this email already exists."
        );
      } else if (Array.isArray(detail)) {
        setError(detail.map((item) => item.msg).join(", "));
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("Unable to create your account. Please try again.");
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
          <h1>Create your<br />clinical workspace.</h1>
          <p>
            Register once to manage patients, upload medical documents,
            and use AI-assisted tools from one secure application.
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

          <p className="eyebrow">GET STARTED</p>
          <h2>Create your account</h2>
          <p className="auth-subtitle">
            Enter your details below to register. You will sign in on the next step.
          </p>

          <form onSubmit={handleSubmit} className="auth-form">
            <label htmlFor="full_name">Full name</label>
            <div className="auth-input-wrap">
              <User size={18} aria-hidden="true" />
              <input
                id="full_name"
                type="text"
                autoComplete="name"
                placeholder="Your full name"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                maxLength={150}
                required
              />
            </div>

            <label htmlFor="register_email">Email address</label>
            <div className="auth-input-wrap">
              <Mail size={18} aria-hidden="true" />
              <input
                id="register_email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <label htmlFor="register_password">Password</label>
            <div className="auth-input-wrap">
              <LockKeyhole size={18} aria-hidden="true" />
              <input
                id="register_password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder={`At least ${MIN_PASSWORD_LENGTH} characters`}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                maxLength={128}
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

            <label htmlFor="confirm_password">Confirm password</label>
            <div className="auth-input-wrap">
              <LockKeyhole size={18} aria-hidden="true" />
              <input
                id="confirm_password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder="Re-enter your password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                maxLength={128}
                required
              />
            </div>

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
              {submitting ? "Creating account..." : "Create account"}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account? <Link to="/login">Sign in</Link>
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
