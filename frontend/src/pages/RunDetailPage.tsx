import { useParams, Link } from "react-router-dom";
import { api } from "@/api/client";
import { useRunStatus } from "@/hooks/useRunStatus";
import StatusBadge from "@/components/StatusBadge";
import styles from "./RunDetailPage.module.css";

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "long",
    timeStyle: "medium",
  }).format(new Date(iso));
}

function duration(start: string | null, end: string | null): string {
  if (!start || !end) return "—";
  const ms = new Date(end).getTime() - new Date(start).getTime();
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export default function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>();
  const { run, error, loading } = useRunStatus(runId);

  if (loading) return <PageSkeleton />;
  if (error || !run) return (
    <div className={styles.errorState}>
      <span>⚠️</span>
      <p>{error ?? "Run not found"}</p>
    </div>
  );

  const isActive = run.status === "pending" || run.status === "running";
  const isDone = run.status === "done";
  const isFailed = run.status === "failed";

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <Link to={-1 as unknown as string} className={styles.backLink}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"/>
              <polyline points="12 19 5 12 12 5"/>
            </svg>
            Back
          </Link>
          <div className={styles.titleRow}>
            <h1 className={styles.title}>Run Detail</h1>
            <StatusBadge status={run.status} />
          </div>
          <p className={styles.runIdLabel}>
            <span className={styles.runIdValue}>{run.id}</span>
          </p>
        </div>

        {isDone && run.result_path && (
          <a
            href={api.runs.downloadUrl(run.id)}
            download={run.result_path}
            className={styles.downloadBtn}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Download Report
          </a>
        )}
      </div>

      {/* Live indicator */}
      {isActive && (
        <div className={styles.liveBar}>
          <span className={styles.liveDot} />
          <span>Generating report — this page updates automatically</span>
        </div>
      )}

      {/* Timeline cards */}
      <div className={styles.cards}>
        <InfoCard label="Status" value={<StatusBadge status={run.status} />} />
        <InfoCard label="Created" value={formatDate(run.created_at)} />
        <InfoCard label="Started" value={formatDate(run.started_at)} />
        <InfoCard label="Finished" value={formatDate(run.finished_at)} />
        <InfoCard
          label="Duration"
          value={duration(run.started_at, run.finished_at)}
        />
        <InfoCard
          label="Output File"
          value={run.result_path ?? "—"}
          mono
        />
      </div>

      {/* Error details */}
      {isFailed && run.error_message && (
        <div className={styles.errorBox}>
          <div className={styles.errorBoxHeader}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            Error Details
          </div>
          <pre className={styles.errorMessage}>{run.error_message}</pre>
        </div>
      )}
    </div>
  );
}

function InfoCard({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <div className={styles.card}>
      <p className={styles.cardLabel}>{label}</p>
      <div className={`${styles.cardValue} ${mono ? styles.mono : ""}`}>
        {value}
      </div>
    </div>
  );
}

function PageSkeleton() {
  return (
    <div className={styles.page}>
      <div className={styles.skeletonHeader} />
      <div className={styles.skeletonCards}>
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className={styles.skeletonCard} />
        ))}
      </div>
    </div>
  );
}
