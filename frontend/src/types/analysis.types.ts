// ─── Mirror of backend Pydantic schemas ──────────────────────────────────────
// Keep in sync with:
//   backend/app/schemas/resume_schema.py
//   backend/app/schemas/scoring_schema.py

export type AnalysisMode = "job_title" | "ats";
export type FeedbackPriority = "high" | "medium" | "low";
export type FeedbackCategory = "sections" | "keywords" | "structure";

export interface ScoreBreakdown {
  keyword_score: number;
  section_score: number;
  structure_score: number;
}

export interface FeedbackItem {
  priority: FeedbackPriority;
  category: FeedbackCategory;
  message: string;
}

export interface DetectedSections {
  summary: string | null;
  education: string | null;
  experience: string | null;
  projects: string | null;
  skills: string | null;
  certifications: string | null;
}

export interface SectionCounts {
  experience_entries: number;
  project_entries: number;
  education_entries: number;
  certification_entries: number;
}

export interface ResumeAnalysisResponse {
  // Request echo
  job_title: string;
  company_name: string | null;

  // Scoring
  mode: AnalysisMode;
  total_score: number;
  score_breakdown: ScoreBreakdown;
  matched_keywords: string[];
  missing_keywords: string[];

  // Feedback
  feedback: FeedbackItem[];

  // Parser output
  detected_sections: DetectedSections;
  section_counts: SectionCounts;
  raw_text: string;

  // Transparency
  parser_warnings: string[];
}

// ─── Form / UI types ──────────────────────────────────────────────────────────

export interface AnalysisFormValues {
  file: File;
  job_title: string;
  company_name: string;
  job_description: string;
}

export interface ApiError {
  detail: string | { msg: string; type: string }[];
}
