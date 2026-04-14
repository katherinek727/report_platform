/**
 * TypeScript types mirroring the backend Pydantic schemas.
 * Keep in sync with backend/app/api/schemas.py
 */

export type OutputFormat = "xlsx" | "pdf";

export type RunStatus = "pending" | "running" | "done" | "failed";

export interface Report {
  id: string;
  slug: string;
  name: string;
  description: string;
  output_format: OutputFormat;
  created_at: string;
}

export interface ReportListResponse {
  items: Report[];
  total: number;
}

export interface ReportRun {
  id: string;
  report_id: string;
  status: RunStatus;
  result_path: string | null;
  error_message: string | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
}

export interface RunListResponse {
  items: ReportRun[];
  total: number;
}

export interface TriggerRunResponse {
  run_id: string;
  status: RunStatus;
}

export interface ApiError {
  detail: string;
}
