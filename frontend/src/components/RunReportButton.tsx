import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/api/client";
import { routes } from "@/routes";
import { useToast } from "@/components/Toast";
import styles from "./RunReportButton.module.css";

type State = "idle" | "loading" | "success" | "error";

interface Props {
  reportSlug: string;
  onSuccess?: (runId: string) => void;
}

export default function RunReportButton({ reportSlug, onSuccess }: Props) {
  const [state, setState] = useState<State>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  async function handleClick() {
    if (state === "loading") return;

    setState("loading");
    setErrorMsg(null);

    try {
      const res = await api.runs.trigger(reportSlug);
      setState("success");
      onSuccess?.(res.run_id);
      toast("Report generation started", "success");

      // Navigate to the run detail after a brief success flash
      setTimeout(() => {
        navigate(routes.runs.detail(res.run_id));
      }, 600);
    } catch (err) {
      setState("error");
      const msg = err instanceof Error ? err.message : "Failed to trigger report";
      setErrorMsg(msg);
      toast(msg, "error");
      setTimeout(() => setState("idle"), 3000);
    }
  }

  return (
    <div className={styles.wrapper}>
      <button
        className={`${styles.btn} ${styles[state]}`}
        onClick={handleClick}
        disabled={state === "loading" || state === "success"}
        aria-busy={state === "loading"}
      >
        <span className={styles.btnInner}>
          {state === "loading" && <Spinner />}
          {state === "success" && <CheckIcon />}
          {state === "error" && <ErrorIcon />}
          {state === "idle" && <RunIcon />}
          <span className={styles.btnLabel}>
            {state === "loading" && "Generating…"}
            {state === "success" && "Dispatched"}
            {state === "error" && "Retry"}
            {state === "idle" && "Generate Report"}
          </span>
        </span>
      </button>

      {state === "error" && errorMsg && (
        <p className={styles.errorMsg}>{errorMsg}</p>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <svg className={styles.spinner} width="16" height="16" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2.5">
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
    </svg>
  );
}

function RunIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="5 3 19 12 5 21 5 3"/>
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  );
}

function ErrorIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  );
}
