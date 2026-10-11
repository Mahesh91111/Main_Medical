import {
  AlertCircle,
  FileText,
  Files,
  Trash2
} from "lucide-react";

import ProcessingStatus from "./ProcessingStatus";

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleString();
}

function getDocumentName(document) {
  return (
    document.filename ||
    document.file_name ||
    document.original_filename ||
    document.title ||
    "Untitled document"
  );
}

function getDocumentStatus(document) {
  return (
    document.processing_status ||
    document.status ||
    document.ingestion_status ||
    "uploaded"
  );
}

export default function DocumentTable({
  documents,
  patients,
  loading,
  error,
  onRetry,
  onDelete
}) {
  const patientNames = new Map();

  for (const patient of patients) {
    const id = patient.id ?? patient.patient_id;
    const name = [
      patient.first_name,
      patient.middle_name,
      patient.last_name
    ].filter(Boolean).join(" ") ||
      patient.full_name ||
      patient.name;

    if (id != null) {
      patientNames.set(String(id), name || `Patient ${id}`);
    }
  }

  if (loading) {
    return (
      <div className="patient-state" role="status">
        <div className="loading-spinner" />
        <p>Loading documents...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="patient-state patient-error-state" role="alert">
        <AlertCircle size={27} />
        <h3>Unable to load documents</h3>
        <p>{error}</p>
        <button className="patient-primary-button" onClick={onRetry}>
          Try again
        </button>
      </div>
    );
  }

  if (!documents.length) {
    return (
      <div className="patient-state">
        <div className="patient-empty-icon">
          <Files size={25} />
        </div>
        <h3>No documents yet</h3>
        <p>Upload a PDF to start building your document library.</p>
      </div>
    );
  }

  return (
    <div className="document-table-wrapper">
      <table className="document-table">
        <thead>
          <tr>
            <th>Document</th>
            <th>Patient</th>
            <th>Uploaded</th>
            <th>Processing status</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {documents.map((document, index) => {
            const id = document.id ?? document.document_id;
            const patientId = document.patient_id;
            const status = String(getDocumentStatus(document)).toLowerCase();
            const isProcessing = ["processing", "pending", "queued"].includes(status);

            return (
              <tr key={id ?? `${getDocumentName(document)}-${index}`}>
                <td>
                  <div className="document-name-cell">
                    <span className="document-file-icon">
                      <FileText size={19} />
                    </span>
                    <div>
                      <strong>{getDocumentName(document)}</strong>
                      <span>
                        {document.file_type ||
                          document.content_type ||
                          "PDF document"}
                      </span>
                    </div>
                  </div>
                </td>

                <td>
                  {patientId != null
                    ? patientNames.get(String(patientId)) ||
                      `Patient ID ${patientId}`
                    : "Not associated"}
                </td>

                <td>
                  {formatDate(
                    document.created_at ||
                    document.uploaded_at ||
                    document.created_on
                  )}
                </td>

                <td>
                  <ProcessingStatus status={getDocumentStatus(document)} />
                </td>

                <td>
                  <button
                    type="button"
                    className="document-delete-button"
                    onClick={() => onDelete(document)}
                    disabled={isProcessing}
                    aria-label={`Delete ${getDocumentName(document)}`}
                    title={
                      isProcessing
                        ? "Wait until processing has finished"
                        : "Delete this document"
                    }
                  >
                    <Trash2 size={16} />
                    Delete
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
