
import { useCallback, useEffect, useState } from "react";
import {
  FileText,
  Files,
  RefreshCw,
  UploadCloud
} from "lucide-react";

import { getDocuments } from "../api/documents";
import { getPatients } from "../api/patients";
import SectionHeader from "../components/common/SectionHeader";
import DocumentUpload from "../components/documents/DocumentUpload";
import DocumentTable from "../components/documents/DocumentTable";
import DocumentDeleteDialog from "../components/documents/DocumentDeleteDialog";

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [patientError, setPatientError] = useState("");
  const [showUpload, setShowUpload] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const loadDocuments = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    setError("");

    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      const status = err.response?.status;

      if (status === 401) {
        setError("Your session has expired. Please sign in again.");
      } else if (status === 403) {
        setError("You do not have permission to view these documents.");
      } else if (!err.response) {
        setError("Cannot connect to the API. Check that FastAPI is running.");
      } else {
        setError(
          err.response?.data?.detail ||
          "Unable to load documents."
        );
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments, refreshKey]);

  useEffect(() => {
    let active = true;

    async function loadPatients() {
      setPatientError("");

      try {
        const data = await getPatients();

        if (active) setPatients(data);
      } catch (err) {
        if (!active) return;

        setPatientError(
          err.response?.status === 403
            ? "You cannot access the patient list. Documents can still be uploaded without a patient association."
            : "Patient options could not be loaded. You can still upload without associating a patient."
        );
      }
    }

    loadPatients();

    return () => {
      active = false;
    };
  }, []);

  const processingCount = documents.filter((document) => {
    const status = String(
      document.processing_status ||
      document.status ||
      document.ingestion_status ||
      ""
    ).toLowerCase();

    return ["pending", "queued", "processing"].includes(status);
  }).length;

  const completedCount = documents.filter((document) => {
    const status = String(
      document.processing_status ||
      document.status ||
      document.ingestion_status ||
      ""
    ).toLowerCase();

    return ["completed", "processed"].includes(status);
  }).length;

  const failedCount = documents.filter((document) => {
    const status = String(
      document.processing_status ||
      document.status ||
      document.ingestion_status ||
      ""
    ).toLowerCase();

    return ["failed", "error"].includes(status);
  }).length;

  // While any document is still processing, check for updates every few seconds.
  useEffect(() => {
    if (processingCount === 0) return undefined;

    const timer = setInterval(() => {
      loadDocuments(true);
    }, 4000);

    return () => clearInterval(timer);
  }, [processingCount, loadDocuments]);

  async function handleUploaded() {
    setShowUpload(false);
    setRefreshKey((current) => current + 1);
  }

  return (
    <div className="documents-page">
      <div className="documents-page-heading">
        <div>
          <p className="eyebrow">CLINICAL WORKSPACE</p>
          <h1>Medical documents</h1>
          <p className="documents-page-description">
            Upload, associate, and monitor clinical PDF documents.
          </p>
        </div>

        <button
          className="patient-primary-button"
          onClick={() => setShowUpload(true)}
        >
          <UploadCloud size={18} />
          Upload PDF
        </button>
      </div>

      <div className="document-metrics">
        <div className="document-metric-card">
          <span className="document-metric-icon metric-blue">
            <Files size={20} />
          </span>
          <div>
            <span>Total documents</span>
            <strong>{loading ? "…" : documents.length}</strong>
          </div>
        </div>

        <div className="document-metric-card">
          <span className="document-metric-icon metric-orange">
            <RefreshCw size={20} />
          </span>
          <div>
            <span>Processing</span>
            <strong>{loading ? "…" : processingCount}</strong>
          </div>
        </div>

        <div className="document-metric-card">
          <span className="document-metric-icon metric-green">
            <FileText size={20} />
          </span>
          <div>
            <span>Completed</span>
            <strong>{loading ? "…" : completedCount}</strong>
          </div>
        </div>

        <div className="document-metric-card">
          <span className="document-metric-icon metric-red">
            <Files size={20} />
          </span>
          <div>
            <span>Failed</span>
            <strong>{loading ? "…" : failedCount}</strong>
          </div>
        </div>
      </div>

      <section className="document-list-panel">
        <SectionHeader
          title="Document library"
          description="Processing status reflects the latest state returned by the backend."
          action={
            <button
              type="button"
              className="document-refresh-button"
              onClick={() => setRefreshKey((current) => current + 1)}
              disabled={loading}
              aria-label="Refresh documents"
            >
              <RefreshCw size={17} />
            </button>
          }
        />

        {patientError && (
          <p className="document-inline-notice" role="status">
            {patientError}
          </p>
        )}

        <DocumentTable
          documents={documents}
          patients={patients}
          loading={loading}
          error={error}
          onRetry={() => loadDocuments()}
          onDelete={setDocumentToDelete}
        />
      </section>

      {documentToDelete && (
        <DocumentDeleteDialog
          document={documentToDelete}
          onClose={() => setDocumentToDelete(null)}
          onDeleted={() => {
            setDocumentToDelete(null);
            setRefreshKey((current) => current + 1);
          }}
        />
      )}

      {showUpload && (
        <DocumentUpload
          patients={patients}
          onClose={() => setShowUpload(false)}
          onUploaded={handleUploaded}
        />
      )}
    </div>
  );
}
