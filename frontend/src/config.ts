/**
 * Runtime configuration sourced from environment variables.
 *
 * All VITE_* variables are inlined at build time by Vite.
 * Provide defaults so the app works out-of-the-box in development
 * without requiring a .env file.
 */
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "/api/v1",
} as const;
