
import {
  CheckCircle2,
  Clock3,
  LoaderCircle,
  AlertCircle,
  FileText
} from "lucide-react";

const statusConfig = {
  uploaded: {
    label: "Uploaded",
    className: "status-uploaded",
    icon: FileText
  },
  pending: {
    label: "Pending",
    className: "status-pending",
    icon: Clock3
  },
  queued: {
    label: "Queued",
    className: "status-pending",
    icon: Clock3
  },
  processing: {
    label: "Processing",
    className: "status-processing",
    icon: LoaderCircle
  },
  completed: {
    label: "Completed",
    className: "status-completed",
    icon: CheckCircle2
  },
  processed: {
    label: "Processed",
    className: "status-completed",
    icon: CheckCircle2
  },
  failed: {
    label: "Failed",
    className: "status-failed",
    icon: AlertCircle
  },
  error: {
    label: "Error",
    className: "status-failed",
    icon: AlertCircle
  }
};

export default function ProcessingStatus({ status }) {
  const normalized = String(status || "uploaded").toLowerCase();
  const config = statusConfig[normalized] || {
    label: String(status || "Unknown").replaceAll("_", " "),
    className: "status-unknown",
    icon: Clock3
  };

  const Icon = config.icon;

  return (
    <span className={`document-status ${config.className}`}>
      <Icon
        size={14}
        className={normalized === "processing" ? "status-spin" : ""}
      />
      <span>{config.label}</span>
    </span>
  );
}
