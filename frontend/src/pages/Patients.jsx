
import { useCallback, useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw, Users } from "lucide-react";

import { getPatients } from "../api/patients";
import PatientSearch from "../components/patients/PatientSearch";
import PatientTable from "../components/patients/PatientTable";
import PatientForm from "../components/patients/PatientForm";
import SectionHeader from "../components/common/SectionHeader";
import { getApiErrorMessage } from "../utils/apiErrors";

function normalize(value) {
  return String(value ?? "").trim().toLowerCase();
}

function getPatientName(patient) {
  return [
    patient.first_name,
    patient.middle_name,
    patient.last_name
  ].filter(Boolean).join(" ") || patient.full_name || patient.name || "";
}

export default function Patients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [gender, setGender] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const loadPatients = useCallback(async () => {
    try {
      const data = await getPatients();
      setPatients(data);
      setError("");
    } catch (error) {
      setError(getApiErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    queueMicrotask(() => {
      void loadPatients();
    });
  }, [loadPatients, refreshKey]);

  function refreshPatients() {
    setLoading(true);
    setError("");
    setRefreshKey((current) => current + 1);
  }

  const filteredPatients = useMemo(() => {
    return patients.filter((patient) => {
      const searchableText = [
        getPatientName(patient),
        patient.id,
        patient.patient_id,
        patient.email,
        patient.medical_record_number
      ].map(normalize).join(" ");

      const matchesQuery =
        !normalize(query) || searchableText.includes(normalize(query));

      const patientGender = normalize(patient.gender);
      const matchesGender =
        !gender ||
        (gender === "unknown"
          ? !patientGender || patientGender === "unknown" ||
            patientGender === "unspecified"
          : patientGender === gender);

      return matchesQuery && matchesGender;
    });
  }, [patients, query, gender]);

  async function handleCreated() {
    setShowForm(false);
    setQuery("");
    setGender("");
    setRefreshKey((current) => current + 1);
  }

  return (
    <div className="patients-page">
      <div className="patients-page-heading">
        <div>
          <p className="eyebrow">CLINICAL WORKSPACE</p>
          <h1>Patient management</h1>
          <p className="patients-page-description">
            Search, register, and view patient records you are authorized to access.
          </p>
        </div>

        <button
          className="patient-primary-button"
          onClick={() => setShowForm(true)}
        >
          <Plus size={18} />
          Register patient
        </button>
      </div>

      <div className="patient-summary-card">
        <div className="patient-summary-icon">
          <Users size={22} />
        </div>

        <div>
          <span>Total loaded patients</span>
          <strong>{loading ? "…" : patients.length}</strong>
        </div>

        <div className="patient-summary-divider" />

        <div>
          <span>Matching records</span>
          <strong>{loading ? "…" : filteredPatients.length}</strong>
        </div>

        <button
          className="patient-refresh-button"
          onClick={refreshPatients}
          disabled={loading}
          aria-label="Refresh patients"
          title="Refresh patients"
        >
          <RefreshCw size={17} />
        </button>
      </div>

      <section className="patient-list-panel">
        <SectionHeader
          title="Patient records"
          description="Search by name, email, or patient identifier."
        />

        <PatientSearch
          query={query}
          onQueryChange={setQuery}
          gender={gender}
          onGenderChange={setGender}
        />

        <PatientTable
          patients={filteredPatients}
          loading={loading}
          error={error}
          onRetry={refreshPatients}
        />
      </section>

      {showForm && (
        <PatientForm
          onClose={() => setShowForm(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}
