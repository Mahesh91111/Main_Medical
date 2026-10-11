import { useState } from "react";
import { AlertCircle, Trash2, X } from "lucide-react";

import { deleteDocument } from "../../api/documents";

export default function DocumentDeleteDialog({
  document,
  onClose,
  onDeleted
}) {
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");

  const documentId = document.id ?? document.document_id;
  const documentName =
    document.filename ||
    document.file_name ||
    document.original_filename ||
    document.title ||
    "this document";

  async function handleDelete() {
    setError("");
    setDeleting(true);

    try {
      await deleteDocument(documentId);
      await onDeleted();
    } catch (err) {
      const detail = err.response?.data?.detail;
      const status = err.response?.status;

      setError(
        typeof detail === "string"
          ? detail
          : !err.response
            ? "Cannot connect to the server. Check that FastAPI is running."
            : status === 401
              ? "Your session has expired. Please sign in again."
              : status === 403
                ? "You do not have permission to delete this document."
                : status === 404
                  ? "This document no longer exists. Refresh the list."
                  : "Unable to delete the document. Please try again."
      );
      setDeleting(false);
    }
  }

  return (
    <div
      className="document-modal-backdrop"
      onMouseDown={() => {
        if (!deleting) onClose();
      }}
    >
      <section
        className="document-modal document-delete-modal"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="document-delete-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="document-modal-header">
          <div>
            <h2 id="document-delete-title">Delete document?</h2>
            <p>This action cannot be undone.</p>
          </div>

          <button
            type="button"
            className="icon-button"
            onClick={onClose}
            disabled={deleting}
            aria-label="Close"
          >
            <X size={19} />
          </button>
        </header>

        <div className="document-upload-form">
          <div className="document-delete-summary">
            <span className="document-delete-icon">
              <Trash2 size={22} />
            </span>

            <p>
              <strong>{documentName}</strong> will be permanently removed,
              including its stored file and the text the AI assistant uses
              to answer questions.
            </p>
          </div>

          {error && (
            <div className="document-form-error" role="alert">
              <AlertCircle size={17} />
              <span>{error}</span>
            </div>
          )}

          <div className="document-form-actions">
            <button
              type="button"
              className="patient-secondary-button"
              onClick={onClose}
              disabled={deleting}
            >
              Cancel
            </button>

            <button
              type="button"
              className="patient-danger-button"
              onClick={handleDelete}
              disabled={deleting}
            >
              <Trash2 size={16} />
              {deleting ? "Deleting..." : "Delete document"}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
