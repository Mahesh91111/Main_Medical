import { useEffect, useState } from "react";
import { Activity, AlertCircle, CheckCircle2 } from "lucide-react";
import { checkBackendHealth } from "../../api/health";

export default function ApiStatus() {
  const [status, setStatus] = useState({
    loading: true,
    online: false,
    message: "Checking backend...",
  });

  useEffect(() => {
    let active = true;

    async function check() {
      const result = await checkBackendHealth();

      if (active) {
        setStatus({
          loading: false,
          ...result,
        });
      }
    }

    check();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div
      className={`api-status ${
        status.loading
          ? "api-status-loading"
          : status.online
            ? "api-status-online"
            : "api-status-offline"
      }`}
      role="status"
      title={status.message}
    >
      {status.loading ? (
        <Activity size={15} />
      ) : status.online ? (
        <CheckCircle2 size={15} />
      ) : (
        <AlertCircle size={15} />
      )}

      <span>
        {status.loading
          ? "Checking API"
          : status.online
            ? "API connected"
            : "API unavailable"}
      </span>
    </div>
  );
}