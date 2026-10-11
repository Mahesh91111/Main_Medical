
import { useState } from "react";
import { X } from "lucide-react";

import { createPatient } from "../../api/patients";

const initialForm = {
  first_name: "",
  last_name: "",
  date_of_birth: "",
  gender: "",
  email: "",
  phone: ""
};

// The backend needs a unique patient code, so one is generated for each new patient.
function generatePatientCode() {
  const time = Date.now().toString(36);
  const random = Math.random().toString(36).slice(2, 6);
  return `P-${time}${random}`.toUpperCase();
}

export default function PatientForm({ onClose, onCreated }) {
  const [form, setForm] = useState(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function updateField(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const payload = {
        patient_code: generatePatientCode(),
        full_name: `${form.first_name.trim()} ${form.last_name.trim()}`,
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        date_of_birth: form.date_of_birth,
        gender: form.gender,
        email: form.email.trim() || null,
        phone: form.phone.trim() || null
      };

      const created = await createPatient(payload);
      await onCreated(created);
    } catch (err) {
      const detail = err.response?.data?.detail;

      setError(
        Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : typeof detail === "string"
            ? detail
            : "Unable to register patient. Check the required fields and try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="patient-modal-backdrop" onMouseDown={onClose}>
      <section
        className="patient-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="patient-form-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="patient-modal-header">
          <div>
            <h2 id="patient-form-title">Register patient</h2>
            <p>Add a new patient record to your workspace.</p>
          </div>

          <button
            type="button"
            className="icon-button"
            onClick={onClose}
            aria-label="Close registration form"
          >
            <X size={19} />
          </button>
        </header>

        <form className="patient-form" onSubmit={handleSubmit}>
          <div className="patient-form-grid">
            <div className="patient-field">
              <label htmlFor="first_name">First name *</label>
              <input
                id="first_name"
                name="first_name"
                value={form.first_name}
                onChange={updateField}
                maxLength={100}
                autoComplete="given-name"
                required
              />
            </div>

            <div className="patient-field">
              <label htmlFor="last_name">Last name *</label>
              <input
                id="last_name"
                name="last_name"
                value={form.last_name}
                onChange={updateField}
                maxLength={100}
                autoComplete="family-name"
                required
              />
            </div>

            <div className="patient-field">
              <label htmlFor="date_of_birth">Date of birth *</label>
              <input
                id="date_of_birth"
                type="date"
                name="date_of_birth"
                value={form.date_of_birth}
                onChange={updateField}
                max={new Date().toISOString().slice(0, 10)}
                required
              />
            </div>

            <div className="patient-field">
              <label htmlFor="gender">Gender *</label>
              <select
                id="gender"
                name="gender"
                value={form.gender}
                onChange={updateField}
                required
              >
                <option value="">Select gender</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
                <option value="unknown">Prefer not to specify</option>
              </select>
            </div>

            <div className="patient-field">
              <label htmlFor="patient_email">Email address</label>
              <input
                id="patient_email"
                type="email"
                name="email"
                value={form.email}
                onChange={updateField}
                autoComplete="email"
                maxLength={254}
              />
            </div>

            <div className="patient-field">
              <label htmlFor="phone">Phone number</label>
              <input
                id="phone"
                type="tel"
                name="phone"
                value={form.phone}
                onChange={updateField}
                autoComplete="tel"
                maxLength={30}
              />
            </div>
          </div>

          {error && (
            <div className="patient-form-error" role="alert">
              {error}
            </div>
          )}

          <div className="patient-form-actions">
            <button
              type="button"
              className="patient-secondary-button"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="patient-primary-button"
              disabled={submitting}
            >
              {submitting ? "Registering..." : "Register patient"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
