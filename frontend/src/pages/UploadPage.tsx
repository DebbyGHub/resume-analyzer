import { useState } from "react";
import { UploadBox } from "../components/resume/UploadBox";
import { Button } from "../components/ui/Button";
import { analyzeResume } from "../api/resume.api";
import { extractErrorMessage } from "../api/client";
import type { ResumeAnalysisResponse } from "../types/analysis.types";

interface UploadPageProps {
  onResult: (result: ResumeAnalysisResponse) => void;
}

interface FormErrors {
  file?: string;
  job_title?: string;
}

export function UploadPage({ onResult }: UploadPageProps) {
  const [file, setFile] = useState<File | null>(null);
  const [jobTitle, setJobTitle] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function validate(): boolean {
    const next: FormErrors = {};
    if (!file) next.file = "Please upload a PDF resume.";
    else if (file.type !== "application/pdf")
      next.file = "Only PDF files are accepted.";
    if (!jobTitle.trim()) next.job_title = "Job title is required.";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit() {
    if (!validate() || !file) return;
    setApiError(null);
    setLoading(true);
    try {
      const result = await analyzeResume({
        file,
        job_title: jobTitle,
        company_name: companyName,
        job_description: jobDescription,
      });
      onResult(result);
    } catch (err) {
      setApiError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  const inputClass =
    "w-full rounded-lg bg-surface-raised border border-surface-border px-4 py-2.5 " +
    "text-sm text-text-primary placeholder-text-muted font-sans " +
    "focus:outline-none focus:border-accent/60 focus:ring-1 focus:ring-accent/30 " +
    "transition-colors duration-150";

  const labelClass =
    "block text-xs font-display font-semibold text-text-secondary uppercase tracking-widest mb-1.5";

  return (
    <div className="min-h-screen bg-surface-base flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <div className="h-px flex-1 bg-surface-border" />
            <span className="font-mono text-xs text-text-muted tracking-widest uppercase">
              Resume Analyzer
            </span>
            <div className="h-px flex-1 bg-surface-border" />
          </div>
          <h1 className="font-display text-4xl font-bold text-text-primary tracking-tight leading-tight">
            Analyze your
            <br />
            <span className="text-accent">resume.</span>
          </h1>
          <p className="mt-3 text-sm text-text-secondary leading-relaxed">
            Upload your PDF and get a deterministic, rule-based score — no AI
            hallucinations.
          </p>
        </div>

        {/* Form */}
        <div className="flex flex-col gap-6">
          {/* Upload */}
          <div>
            <UploadBox
              file={file}
              onFileSelect={(f) => {
                setFile(f);
                if (errors.file) setErrors((e) => ({ ...e, file: undefined }));
              }}
              error={errors.file}
            />
          </div>

          {/* Job title */}
          <div className="mt-4">
            <label className={labelClass}>
              Target Job Title{" "}
              <span className="text-accent normal-case font-sans font-normal">
                *
              </span>
            </label>
            <input
              type="text"
              placeholder="e.g. Backend Developer"
              value={jobTitle}
              onChange={(e) => {
                setJobTitle(e.target.value);
                if (errors.job_title)
                  setErrors((er) => ({ ...er, job_title: undefined }));
              }}
              className={
                inputClass + (errors.job_title ? " border-score-low" : "")
              }
            />
            {errors.job_title && (
              <p className="mt-1 text-xs text-score-low">{errors.job_title}</p>
            )}
          </div>

          {/* Company name */}
          <div>
            <label className={labelClass}>
              Company Name{" "}
              <span className="text-text-muted normal-case font-sans font-normal">
                (optional)
              </span>
            </label>
            <input
              type="text"
              placeholder="e.g. Google"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className={inputClass}
            />
          </div>

          {/* Job description */}
          <div>
            <label className={labelClass}>
              Job Description{" "}
              <span className="text-text-muted normal-case font-sans font-normal">
                (optional · enables ATS mode)
              </span>
            </label>
            <textarea
              rows={5}
              placeholder="Paste the job description here to unlock ATS keyword analysis..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              className={inputClass + " resize-none leading-relaxed"}
            />
            {jobDescription.trim() && (
              <p className="mt-1 text-xs text-accent font-mono">
                ATS mode will be activated
              </p>
            )}
          </div>

          {/* API error */}
          {apiError && (
            <div className="rounded-lg bg-score-low/10 border border-score-low/30 px-4 py-3">
              <p className="text-sm text-score-low">{apiError}</p>
            </div>
          )}

          {/* Submit */}
          <Button
            onClick={handleSubmit}
            loading={loading}
            disabled={loading}
            className="w-full py-3 text-base"
          >
            {loading ? "Analyzing resume…" : "Analyze Resume"}
          </Button>
        </div>
      </div>
    </div>
  );
}
