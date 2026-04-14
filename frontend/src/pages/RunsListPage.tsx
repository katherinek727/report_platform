import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "@/api/client";
import type { Report, ReportRun } from "@/api/types";
import { routes } from "@/routes";
import StatusBadge from "@/components/StatusBadge";
import RunReportButton from "@/components/RunReportButton";
import styles from "./RunsListPage.module.css";

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(iso));
}

export default function RunsListPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();

  const [report, setReport] = useState<Report | null>(null);
  const [runs, setRuns] = useState<ReportRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    if (!slug) return;
    try {
      const [reportData, runsData] = await Promise.all([
        api.reports.get(slug),
        api.runs.listForReport(slug),
      ]);
      setReport(reportData);
      setRuns(runsData.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadData(); }, [slug]);

  if (loading) return <PageSkeleton />;
  if (error || !report) return (
    <div className={styles.errorState}>
      <span>⚠️</span>
      <p>{error ?? "Report not found"}</p>
    </div>
  );

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <Link to={routes.reports.list()} className={styles.backLink}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"/>
              <polyline points="12 19 5 12 12 5"/>
            </svg>
            All Reports
          </Link>
          <h1 className={styles.title}>{report.name}</h1>
          <p className={styles.subtitle}>{report.description}</p>
        </div>
        <RunReportButton reportSlug={report.slug} onSuccess={() => loadData()} />
      </div>

      <div className={styles.tableWrapper}>
        <div className={styles.tableHeader}>
          <h2 className={styles.tableTitle}>Run History</h2>
          <span className={styles.runCount}>{runs.length} run{runs.length !== 1 ? "s" : ""}</span>
        </div>

        {runs.length === 0 ? (
          <div className={styles.empty}>
            <p className={styles.emptyText}>No runs yet. Click "Generate Report" to start.</p>
          </div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Run ID</th>
                <th>Status</th>
                <th>Created</th>
                <th>Started</th>
                <th>Finished</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr
                  key={run.id}
                  className={styles.row}
                  onClick={() => navigate(routes.runs.detail(run.id))}
                >
                  <td>
                    <span className={styles.runId}>
                      {run.id.slice(0, 8)}…
                    </span>
                  </td>
                  <td><StatusBadge status={run.status} /></td>
                  <td className={styles.dateCell}>{formatDate(run.created_at)}</td>
                  <td className={styles.dateCell}>{formatDate(run.started_at)}</td>
                  <td className={styles.dateCell}>{formatDate(run.finished_at)}</td>
                  <td>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                      className={styles.rowArrow}>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                      <polyline points="12 5 19 12 12 19"/>
                    </svg>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function PageSkeleton() {
  return (
    <div className={styles.page}>
      <div className={styles.skeletonHeader} />
      <div className={styles.skeletonTable} />
    </div>
  );
}
