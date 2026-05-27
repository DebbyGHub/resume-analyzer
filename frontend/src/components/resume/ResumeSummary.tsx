import { Card } from "../ui/Card";
import type {
  DetectedSections,
  SectionCounts,
} from "../../types/analysis.types";

interface ResumeSummaryProps {
  detectedSections: DetectedSections;
  sectionCounts: SectionCounts;
  rawText: string;
  parserWarnings: string[];
}

const SECTION_META: { key: keyof DetectedSections; label: string }[] = [
  { key: "summary", label: "Summary" },
  { key: "experience", label: "Experience" },
  { key: "education", label: "Education" },
  { key: "projects", label: "Projects" },
  { key: "skills", label: "Skills" },
  { key: "certifications", label: "Certifications" },
];

function countLabel(
  key: keyof DetectedSections,
  counts: SectionCounts,
): string | null {
  if (key === "experience" && counts.experience_entries > 0)
    return `${counts.experience_entries} entr${counts.experience_entries === 1 ? "y" : "ies"}`;
  if (key === "projects" && counts.project_entries > 0)
    return `${counts.project_entries} project${counts.project_entries === 1 ? "" : "s"}`;
  if (key === "education" && counts.education_entries > 0)
    return `${counts.education_entries} degree${counts.education_entries === 1 ? "" : "s"}`;
  if (key === "certifications" && counts.certification_entries > 0)
    return `${counts.certification_entries} cert${counts.certification_entries === 1 ? "" : "s"}`;
  if (key === "skills" && counts.skills_count > 0)
    return `${counts.skills_count} skill${counts.skills_count === 1 ? "" : "s"}`;
  return null;
}

export function ResumeSummary({
  detectedSections,
  sectionCounts,
  rawText,
  parserWarnings,
}: ResumeSummaryProps) {
  const detectedCount = SECTION_META.filter(
    ({ key }) => detectedSections[key] !== null,
  ).length;

  return (
    <div className="flex flex-col gap-3">
      {/* Parser warnings — shown only when present */}
      {parserWarnings.length > 0 && (
        <div className="rounded-lg border border-score-mid/30 bg-score-mid/5 px-4 py-3 flex flex-col gap-1.5">
          <p className="text-xs font-display font-semibold text-score-mid uppercase tracking-widest">
            Parser Notes
          </p>
          {parserWarnings.map((w, i) => (
            <p key={i} className="text-xs text-score-mid/80 leading-relaxed">
              {w}
            </p>
          ))}
        </div>
      )}

      {/* Section map */}
      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-display font-semibold text-text-muted uppercase tracking-widest">
            Parsed Sections
          </h3>
          <span className="font-mono text-xs text-text-secondary">
            <span className="text-text-primary">{detectedCount}</span>
            <span className="text-text-muted">/6 found</span>
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {SECTION_META.map(({ key, label }) => {
            const present = detectedSections[key] !== null;
            const detail = countLabel(key, sectionCounts);
            return (
              <div
                key={key}
                className={
                  "flex items-center gap-2 rounded-lg px-3 py-2 " +
                  (present
                    ? "bg-score-high/5 border border-score-high/15"
                    : "bg-surface-raised border border-surface-border opacity-50")
                }
              >
                
                <div className="min-w-0">
                  <p
                    className={
                      "text-xs font-medium leading-none " +
                      (present ? "text-text-primary" : "text-text-muted")
                    }
                  >
                    {label}
                  </p>
                  {detail && (
                    <p className="text-xs text-text-muted mt-0.5 leading-none">
                      {detail}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Extracted text — collapsible, explicit transparency feature */}
      <details className="group">
        <summary className="cursor-pointer list-none">
          <Card
            className={
              "px-4 py-3 flex items-center justify-between " +
              "hover:border-surface-border/80 transition-colors group-open:rounded-b-none"
            }
          >
            <div className="flex items-center gap-2">
              <svg
                className="h-3 w-3 text-text-muted transition-transform group-open:rotate-90 shrink-0"
                viewBox="0 0 12 12"
                fill="none"
              >
                <path
                  d="M4 2l4 4-4 4"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span className="text-xs font-mono text-text-muted">
                Extracted text
              </span>
            </div>
            <span className="font-mono text-xs text-text-muted">
              {rawText.length.toLocaleString()} chars
            </span>
          </Card>
        </summary>

        {/* Body — seamlessly connected to summary card */}
        <div className="bg-surface-card border border-surface-border border-t-0 rounded-b-xl px-4 pb-4 pt-3">
          <pre className="text-xs font-mono text-text-secondary whitespace-pre-wrap leading-relaxed max-h-72 overflow-y-auto">
            {rawText || "— No text extracted —"}
          </pre>
        </div>
      </details>
    </div>
  );
}
