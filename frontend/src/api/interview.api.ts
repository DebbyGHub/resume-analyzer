/**
 * interview.api.ts
 *
 * Service layer for all interview-related backend communication.
 * Framework-agnostic — no React, no JSX, no hooks.
 * Import and call from any page or hook.
 */

const BASE_URL = "http://127.0.0.1:8000/api/interview";

// ─── Types ────────────────────────────────────────────────────────────────────

export type AnswerQuality = "excellent" | "good" | "average" | "weak";

export type Difficulty = "easy" | "medium" | "hard";

export interface InterviewQuestion {
  id: number;
  topic: string;
  difficulty: Difficulty;
  question: string;
  ideal_answer: string;
}

export interface EvaluateAnswerRequest {
  ideal_answer: string;
  candidate_answer: string;
}

export interface EvaluateAnswerResponse {
  similarity_score: number;
  confidence_score: number;
  final_score: number;
  quality: AnswerQuality;
  flags: string[];
}

// ─── Wrapped result types ─────────────────────────────────────────────────────

export type EvaluateAnswerResult =
  | { ok: true; data: EvaluateAnswerResponse }
  | { ok: false; error: string };

export type InterviewQuestionsResult =
  | { ok: true; data: InterviewQuestion[] }
  | { ok: false; error: string };

// ─── API: Evaluate answer ─────────────────────────────────────────────────────

/**
 * POST /api/interview/evaluate-answer
 *
 * Evaluates a candidate answer against the ideal answer using
 * the backend semantic similarity pipeline.
 */
export async function evaluateInterviewAnswer(
  payload: EvaluateAnswerRequest,
): Promise<EvaluateAnswerResult> {
  try {
    const response = await fetch(`${BASE_URL}/evaluate-answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const detail = await response.text().catch(() => "Unknown server error");

      return {
        ok: false,
        error: `Server error ${response.status}: ${detail}`,
      };
    }

    const data: EvaluateAnswerResponse = await response.json();

    return {
      ok: true,
      data,
    };
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Network request failed";

    return {
      ok: false,
      error: message,
    };
  }
}

// ─── API: Get interview questions ─────────────────────────────────────────────

/**
 * GET /api/interview/questions
 *
 * Fetches the interview question set from the backend.
 * Backend owns question selection and dataset management.
 */
export async function getInterviewQuestions(
  skills?: string[],
): Promise<InterviewQuestionsResult> {
  try {
    let url = `${BASE_URL}/questions`;

    if (skills && skills.length > 0) {
      const query = encodeURIComponent(skills.join(","));
      url += `?skills=${query}`;
    }

    const response = await fetch(url);

    if (!response.ok) {
      const detail = await response.text().catch(() => "Unknown server error");

      return {
        ok: false,
        error: `Server error ${response.status}: ${detail}`,
      };
    }

    const data: InterviewQuestion[] = await response.json();

    return {
      ok: true,
      data,
    };
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Network request failed";

    return {
      ok: false,
      error: message,
    };
  }
}