
import { Link } from "react-router-dom";
import { Eye, Users } from "lucide-react";

function patientName(patient) {
  const fullName = [
    patient.first_name,
    patient.middle_name,
    patient.last_name
  ].filter(Boolean).join(" ");

  return fullName || patient.full_name || patient.name || "Unnamed patient";
}

function patientId(patient) {
  return patient.id ?? patient.patient_id;
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return String(value);

  return date.toLocaleDateString();
}

export default function PatientTable({
  patients,
  loading,
  error,
  onRetry
}) {
  if (loading) {
    return (
      <div className="patient-state" role="status">
        <div className="loading-spinner" />
        <p>Loading patient records...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="patient-state patient-error-state" role="alert">
        <h3>Unable to load patients</h3>
        <p>{error}</p>
        <button className="patient-primary-button" onClick={onRetry}>
          Try again
        </button>
      </div>
    );
  }

  if (patients.length === 0) {
    return (
      <div className="patient-state">
        <div className="patient-empty-icon">
          <Users size={25} />
        </div>
        <h3>No patients found</h3>
        <p>Try changing your search or register a new patient.</p>
      </div>
    );
  }

  return (
    <div className="patient-table-wrapper">
      <table className="patient-table">
        <thead>
          <tr>
            <th>Patient</th>
            <th>Patient ID</th>
            <th>Date of birth</th>
            <th>Gender</th>
            <th>Email</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {patients.map((patient, index) => {
            const id = patientId(patient);

            return (
              <tr key={id ?? `${patientName(patient)}-${index}`}>
                <td>
                  <div className="patient-name-cell">
                    <span className="patient-avatar">
                      {patientName(patient).charAt(0).toUpperCase()}
                    </span>

                    <strong>{patientName(patient)}</strong>
                  </div>
                </td>

                <td>{id ?? "—"}</td>
                <td>{formatDate(patient.date_of_birth)}</td>
                <td className="capitalize">
                  {patient.gender || "Not specified"}
                </td>
                <td>{patient.email || "—"}</td>

                <td>
                  {id != null ? (
                    <Link
                      className="patient-view-link"
                      to={`/patients/${encodeURIComponent(id)}`}
                      aria-label={`View ${patientName(patient)}`}
                    >
                      <Eye size={16} />
                      View
                    </Link>
                  ) : (
                    <span className="patient-muted">No ID</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
