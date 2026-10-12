
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, CalendarDays, Mail, Phone, UserRound } from "lucide-react";

import { getPatientById } from "../api/patients";
import { getApiErrorMessage } from "../utils/apiErrors";

function display(value) {
  if (value === null || value === undefined || value === "") {
    return "Not provided";
  }

  return String(value);
}

function formatDate(value) {
  if (!value) return "Not provided";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleDateString();
}

export default function PatientDetails() {
  const { patientId } = useParams();

  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadPatient() {
      setLoading(true);
      setError("");
      setPatient(null);

      try {
        const data = await getPatientById(patientId);

        if (active) setPatient(data);
      } catch (error) {
        if (!active) return;

        setError(getApiErrorMessage(error));
      } finally {
        if (active) setLoading(false);
      }
    }

    loadPatient();

    return () => {
      active = false;
    };
  }, [patientId]);

  const name = patient
    ? [
        patient.first_name,
        patient.middle_name,
        patient.last_name
      ].filter(Boolean).join(" ") || patient.full_name || patient.name
    : "";

  return (
    <div className="patient-details-page">
      <Link to="/patients" className="patient-back-link">
        <ArrowLeft size={17} />
        Back to patients
      </Link>

      {loading ? (
        <div className="patient-state">
          <div className="loading-spinner" />
          <p>Loading patient details...</p>
        </div>
      ) : error ? (
        <div className="patient-state patient-error-state" role="alert">
          <h3>Unable to open patient</h3>
          <p>{error}</p>
          <Link to="/patients" className="patient-primary-button">
            Return to patient list
          </Link>
        </div>
      ) : patient ? (
        <>
          <section className="patient-details-hero">
            <div className="patient-details-avatar">
              <UserRound size={28} />
            </div>

            <div className="patient-details-title">
              <p className="eyebrow">PATIENT RECORD</p>
              <h1>{name || "Patient details"}</h1>
              <p>
                Patient ID: {display(patient.id ?? patient.patient_id ?? patientId)}
              </p>
            </div>
          </section>

          <section className="patient-details-panel">
            <h2>Personal information</h2>

            <div className="patient-details-grid">
              <div className="patient-detail-item">
                <span><UserRound size={16} /> Full name</span>
                <strong>{display(name)}</strong>
              </div>

              <div className="patient-detail-item">
                <span><CalendarDays size={16} /> Date of birth</span>
                <strong>{formatDate(patient.date_of_birth)}</strong>
              </div>

              <div className="patient-detail-item">
                <span><UserRound size={16} /> Gender</span>
                <strong>{display(patient.gender)}</strong>
              </div>

              <div className="patient-detail-item">
                <span><Mail size={16} /> Email</span>
                <strong>{display(patient.email)}</strong>
              </div>

              <div className="patient-detail-item">
                <span><Phone size={16} /> Phone</span>
                <strong>{display(patient.phone)}</strong>
              </div>

              <div className="patient-detail-item">
                <span>Medical record number</span>
                <strong>{display(patient.medical_record_number)}</strong>
              </div>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
