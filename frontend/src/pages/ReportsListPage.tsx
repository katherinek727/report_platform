import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/api/client";
import type { Report } from "@/api/types";
import { routes } from "@/routes";
import styles from "./ReportsListPage.module.css";

const FORMAT_LABELS: Record<string, string> = {
  xlsx: "XLSX",
  pdf: "PDF",
};

const FORMAT_ICONS: Record<string, string> = {
  xlsx: "📊",
  pdf: "📄",
};

export default function ReportsListPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.reports
      .list()
      .then((res) => setReports(res.items))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Reports</h1>
          <p className={styles.subtitle}>
            {reports.length} report{reports.length !== 1 ? "s" : ""} available on the platform
          </p>
        </div>
      </div>

      {reports.length === 0 ? (
        <EmptyState />
      ) : (
        <div className={styles.grid}>
          {reports.map((report) => (
            <ReportCard
              key={report.id}
              report={report}
              onClick={() => navigate(routes.reports.runs(report.slug))}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ReportCard({
  report,
  onClick,
}: {
  report: Report;
  onClick: () => void;
}) {
  return (
    <article className={styles.card} onClick={onClick} role="button" tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick()}>
      <div className={styles.cardHeader}>
        <div className={styles.cardIcon}>
          {FORMAT_ICONS[report.output_format] ?? "📁"}
        </div>
        <span className={`${styles.formatBadge} ${styles[`format_${report.output_format}`]}`}>
          {FORMAT_LABELS[report.output_format] ?? report.output_format.toUpperCase()}
        </span>
      </div>

      <div className={styles.cardBody}>
        <h2 className={styles.cardTitle}>{report.name}</h2>
        <p className={styles.cardDesc}>{report.description}</p>
      </div>

      <div className={styles.cardFooter}>
        <span className={styles.cardSlug}>{report.slug}</span>
        <span className={styles.cardArrow}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
        </span>
      </div>
    </article>
  );
}

function PageSkeleton() {
  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.skeletonTitle} />
        <div className={styles.skeletonSubtitle} />
      </div>
      <div className={styles.grid}>
        {[1, 2, 3].map((i) => (
          <div key={i} className={styles.skeletonCard} />
        ))}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className={styles.empty}>
      <div className={styles.emptyIcon}>📭</div>
      <h3 className={styles.emptyTitle}>No reports yet</h3>
      <p className={styles.emptyDesc}>
        Reports will appear here once they are registered on the platform.
      </p>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className={styles.errorState}>
      <span className={styles.errorIcon}>⚠️</span>
      <p>{message}</p>
    </div>
  );
}
