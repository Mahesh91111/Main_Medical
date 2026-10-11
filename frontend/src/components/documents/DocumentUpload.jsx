import { useRef, useState } from "react";
import {
  AlertCircle,
  Check,
  FileText,
  UploadCloud,
  X
} from "lucide-react";

import { uploadDocument } from "../../api/documents";

const MAX_FILE_SIZE = 20 * 1024 * 1024;

export default function DocumentUpload({
  patients,
  onUploaded,
  onClose
}) {
  const inputRef = useRef(null);
  const abortRef = useRef(null);

  const [file, setFile] = useState(null);
  const [patientId, setPatientId] = useState("");
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [uploadedAny, setUploadedAny] = useState(false);
  const [uploadedName, setUploadedName] = useState("");
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);

  function validateFile(selectedFile) {
    if (!selectedFile) return "Choose a PDF file.";

    const isPdfName = selectedFile.name.toLowerCase().endsWith(".pdf");
    const isPdfType =
      selectedFile.type === "application/pdf" ||
      selectedFile.type === "";

    if (!isPdfName || !isPdfType) {
      return "Only PDF files are supported.";
    }

    if (selectedFile.size <= 0) {
      return "The selected file is empty.";
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      return "The file exceeds the 20 MB upload limit.";
    }

    return "";
  }

  function selectFile(selectedFile) {
    setError("");

    const validationError = validateFile(selectedFile);

    if (validationError) {
      setFile(null);
      setError(validationError);
      return;
    }

    setFile(selectedFile);
    setProgress(0);
  }

  function handleInputChange(event) {
    selectFile(event.target.files?.[0] || null);
    // Allow the same file to be selected again after an error.
    event.target.value = "";
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);
    selectFile(event.dataTransfer.files?.[0] || null);
  }

  // Close the dialog. If something was uploaded, refresh the list as well.
  function closeDialog() {
    if (uploadedAny) {
      onUploaded();
    } else {
      onClose();
    }
  }

  // Stop an upload that is still in progress (for example a wrong file).
  function cancelUpload() {
    if (abortRef.current) {
      abortRef.current.abort();
    }
  }

  function uploadAnother() {
    setFile(null);
    setPatientId("");
    setProgress(0);
    setError("");
    setUploaded(false);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!file) {
      setError("Choose a PDF file before uploading.");
      return;
    }

    const validationError = validateFile(file);

    if (validationError) {
      setError(validationError);
      return;
    }

    const controller = new AbortController();
    abortRef.current = controller;

    setUploading(true);
    setProgress(0);

    try {
      await uploadDocument(
        file,
        patientId || null,
        setProgress,
        controller.signal
      );

      setUploadedName(file.name);
      setUploaded(true);
      setUploadedAny(true);
    } catch (err) {
      if (err.code === "ERR_CANCELED" || err.name === "CanceledError") {
        setProgress(0);
        setError("Upload cancelled. You can choose a different file.");
        return;
      }

      const detail = err.response?.data?.detail;

      setError(
        Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : typeof detail === "string"
            ? detail
            : !err.response
              ? "Cannot connect to the server. Check that FastAPI is running."
              : err.response?.status === 413
                ? "The server rejected this file because it is too large."
                : err.response?.status === 401
                  ? "Your session has expired. Please sign in again."
                  : err.response?.status === 403
                    ? "You do not have permission to upload this document."
                    : "Upload failed. Check the file and try again."
      );
    } finally {
      abortRef.current = null;
      setUploading(false);
    }
  }

  return (
    <div
      className="document-modal-backdrop"
      onMouseDown={() => {
        if (!uploading) closeDialog();
      }}
    >
      <section
        className="document-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="document-upload-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="document-modal-header">
          <div>
            <h2 id="document-upload-title">Upload medical document</h2>
            <p>Upload a PDF for the document processing pipeline.</p>
          </div>

          <button
            type="button"
            className="icon-button"
            onClick={closeDialog}
            disabled={uploading}
            aria-label="Close upload form"
          >
            <X size={19} />
          </button>
        </header>

        {uploaded ? (
          <div className="document-upload-success" role="status">
            <span className="document-success-icon">
              <Check size={30} />
            </span>

            <h3>Uploaded successfully</h3>

            <p>
              <strong>{uploadedName}</strong> has been uploaded. It is now
              being processed in the background, and its status in the
              document list will change from Processing to Completed.
            </p>

            <div className="document-form-actions document-success-actions">
              <button
                type="button"
                className="patient-secondary-button"
                onClick={uploadAnother}
              >
                Upload another
              </button>

              <button
                type="button"
                className="patient-primary-button"
                onClick={closeDialog}
              >
                Done
              </button>
            </div>
          </div>
        ) : (
          <form className="document-upload-form" onSubmit={handleSubmit}>
            <button
              type="button"
              className={`document-dropzone ${dragging ? "dragging" : ""}`}
              onClick={() => inputRef.current?.click()}
              onDragOver={(event) => {
                event.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              disabled={uploading}
            >
              <span className="document-upload-icon">
                <UploadCloud size={26} />
              </span>

              <strong>
                {file ? file.name : "Click to choose or drop a PDF"}
              </strong>

              <span>
                PDF documents only · Maximum 20 MB
              </span>

              {file && (
                <span className="document-file-size">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </span>
              )}
            </button>

            <input
              ref={inputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleInputChange}
              hidden
            />

            {file && (
              <div className="selected-document">
                <FileText size={20} />
                <div>
                  <strong>{file.name}</strong>
                  <span>{uploading ? "Uploading..." : "Ready to upload"}</span>
                </div>

                <button
                  type="button"
                  className="search-clear"
                  disabled={uploading}
                  onClick={() => {
                    setFile(null);
                    setProgress(0);
                    setError("");
                  }}
                  aria-label="Remove selected file"
                  title="Remove this file and choose another"
                >
                  <X size={17} />
                </button>
              </div>
            )}

            <div className="document-form-field">
              <label htmlFor="document-patient">
                Associate with patient (optional)
              </label>

              <select
                id="document-patient"
                value={patientId}
                onChange={(event) => setPatientId(event.target.value)}
                disabled={uploading}
              >
                <option value="">No patient association</option>

                {patients.map((patient) => {
                  const id = patient.id ?? patient.patient_id;
                  const name = [
                    patient.first_name,
                    patient.middle_name,
                    patient.last_name
                  ].filter(Boolean).join(" ") ||
                    patient.full_name ||
                    patient.name ||
                    `Patient ${id}`;

                  return (
                    <option key={id} value={id}>
                      {name} · ID {id}
                    </option>
                  );
                })}
              </select>
            </div>

            {uploading && (
              <div className="document-progress">
                <div className="document-progress-label">
                  <span>
                    {progress >= 100
                      ? "Finishing upload..."
                      : "Uploading document"}
                  </span>
                  <strong>{progress}%</strong>
                </div>

                <div
                  className="document-progress-track"
                  role="progressbar"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={progress}
                >
                  <div style={{ width: `${progress}%` }} />
                </div>
              </div>
            )}

            {error && (
              <div className="document-form-error" role="alert">
                <AlertCircle size={17} />
                <span>{error}</span>
              </div>
            )}

            <div className="document-form-actions">
              {uploading ? (
                <button
                  type="button"
                  className="patient-secondary-button document-cancel-upload"
                  onClick={cancelUpload}
                >
                  Cancel upload
                </button>
              ) : (
                <button
                  type="button"
                  className="patient-secondary-button"
                  onClick={closeDialog}
                >
                  Cancel
                </button>
              )}

              <button
                type="submit"
                className="patient-primary-button"
                disabled={uploading || !file}
              >
                {uploading ? "Uploading..." : "Upload PDF"}
              </button>
            </div>
          </form>
        )}
      </section>
    </div>
  );
}
