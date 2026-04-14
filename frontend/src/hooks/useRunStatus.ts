import { useState, useCallback } from "react";
import { api } from "@/api/client";
import type { ReportRun, RunStatus } from "@/api/types";
import { usePolling } from "./usePolling";

const TERMINAL_STATUSES: RunStatus[] = ["done", "failed"];

/**
 * Fetches and live-polls a single ReportRun until it reaches a terminal state.
 *
 * Polling stops automatically when status is "done" or "failed".
 *
 * @param runId  The UUID of the run to track
 */
export function useRunStatus(runId: string | undefined) {
  const [run, setRun] = useState<ReportRun | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const isTerminal = run ? TERMINAL_STATUSES.includes(run.status) : false;

  const fetchRun = useCallback(async () => {
    if (!runId) return;
    try {
      const data = await api.runs.get(runId);
      setRun(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch run");
    } finally {
      setLoading(false);
    }
  }, [runId]);

  // Poll every 2s while run is active; stop when terminal
  usePolling(fetchRun, 2000, !!runId && !isTerminal);

  // Also fetch once immediately even if terminal (first load)
  usePolling(fetchRun, 2000, !!runId && loading);

  return { run, error, loading, isTerminal };
}
