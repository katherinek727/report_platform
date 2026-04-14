/**
 * Typed route definitions.
 *
 * Use these helpers everywhere instead of hardcoding path strings.
 * This makes refactoring routes a single-file change.
 */
export const routes = {
  reports: {
    list: () => "/reports",
    runs: (slug: string) => `/reports/${slug}/runs`,
  },
  runs: {
    detail: (runId: string) => `/runs/${runId}`,
  },
} as const;
