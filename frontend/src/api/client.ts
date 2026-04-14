import { config } from "@/config";
import type {
  Report,
  ReportListResponse,
  ReportRun,
  RunListResponse,
  TriggerRunResponse,
} from "./types";

/**
 * Thin fetch wrapper that:
 * - Prefixes all requests with the configured API base URL
 * - Throws a typed ApiError on non-2xx responses
 * - Returns parsed JSON
 */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${config.apiBaseUrl}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

// ── Reports ────────────────────────────────────────────────

export const api = {
  reports: {
    list: (): Promise<ReportListResponse> =>
      request<ReportListResponse>("/reports"),

    get: (slug: string): Promise<Report> =>
      request<Report>(`/reports/${slug}`),
  },

  runs: {
    trigger: (reportSlug: string): Promise<TriggerRunResponse> =>
      request<TriggerRunResponse>(`/reports/${reportSlug}/runs`, {
        method: "POST",
      }),

    listForReport: (reportSlug: string): Promise<RunListResponse> =>
      request<RunListResponse>(`/reports/${reportSlug}/runs`),

    get: (runId: string): Promise<ReportRun> =>
      request<ReportRun>(`/runs/${runId}`),

    downloadUrl: (runId: string): string =>
      `${config.apiBaseUrl}/runs/${runId}/download`,
  },
};
