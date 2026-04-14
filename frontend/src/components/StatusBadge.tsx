import type { RunStatus } from "@/api/types";
import styles from "./StatusBadge.module.css";

const CONFIG: Record<RunStatus, { label: string; className: string }> = {
  pending: { label: "Pending",  className: styles.pending  },
  running: { label: "Running",  className: styles.running  },
  done:    { label: "Done",     className: styles.done     },
  failed:  { label: "Failed",   className: styles.failed   },
};

export default function StatusBadge({ status }: { status: RunStatus }) {
  const { label, className } = CONFIG[status] ?? {
    label: status,
    className: styles.pending,
  };

  return (
    <span className={`${styles.badge} ${className}`}>
      <span className={styles.dot} />
      {label}
    </span>
  );
}
