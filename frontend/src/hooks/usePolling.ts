import { useEffect, useRef } from "react";

/**
 * Calls `fn` immediately and then every `intervalMs` milliseconds.
 * Stops automatically when `active` is false.
 *
 * Use this to poll a run's status until it reaches a terminal state.
 *
 * @param fn          Async function to call on each tick
 * @param intervalMs  Polling interval in milliseconds (default: 2000)
 * @param active      Whether polling is currently active (default: true)
 */
export function usePolling(
  fn: () => Promise<void> | void,
  intervalMs: number = 2000,
  active: boolean = true
): void {
  const fnRef = useRef(fn);

  // Keep the ref up-to-date without restarting the interval
  useEffect(() => {
    fnRef.current = fn;
  }, [fn]);

  useEffect(() => {
    if (!active) return;

    let cancelled = false;

    async function tick() {
      if (!cancelled) await fnRef.current();
    }

    // Fire immediately, then on interval
    tick();
    const id = setInterval(tick, intervalMs);

    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [intervalMs, active]);
}
