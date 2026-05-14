import { client } from "./client";
import type {
  AnalysisFormValues,
  ResumeAnalysisResponse,
} from "../types/analysis.types";

/**
 * POST /api/resume/parse
 *
 * Sends the PDF and metadata as multipart/form-data.
 * Returns the typed backend response.
 */
export async function analyzeResume(
  values: AnalysisFormValues,
): Promise<ResumeAnalysisResponse> {
  const form = new FormData();
  form.append("file", values.file);
  form.append("job_title", values.job_title.trim());

  if (values.company_name.trim()) {
    form.append("company_name", values.company_name.trim());
  }
  if (values.job_description.trim()) {
    form.append("job_description", values.job_description.trim());
  }

  const { data } = await client.post<ResumeAnalysisResponse>(
    "/api/resume/parse",
    form,
    { headers: { "Content-Type": "multipart/form-data" } },
  );

  return data;
}
