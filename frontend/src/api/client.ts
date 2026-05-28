import axios, { AxiosError } from "axios";
import type { ApiError } from "../types/analysis.types";

export const client = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ??
    "https://resume-analyzer-6v9w.onrender.com",
  timeout: 60_000, // PDF parsing can take a moment
});

/**
 * Normalise FastAPI validation errors and generic HTTP errors into a single
 * human-readable string so callers never need to inspect error shape.
 */
export function extractErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiError | undefined;

    if (!data) {
      return error.message ?? "Network error — is the backend running?";
    }

    if (typeof data.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data.detail)) {
      return data.detail.map((e) => e.msg).join("; ");
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred.";
}
