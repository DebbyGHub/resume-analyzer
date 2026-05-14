import type {
  DetectedSections,
  SectionCounts,
} from "../../types/analysis.types";

interface FeedbackListProps {
  detectedSections: DetectedSections;
  sectionCounts: SectionCounts;
}

interface SectionStatus {
  key: keyof DetectedSections;
  label: string;
  detail: (sections: DetectedSections, counts: SectionCounts) => string;
}

const SECTION_STATUSES: SectionStatus[] = [
  {
    key: "experience",
    label: "Work Experience",
    detail: (_, c) =>
      c.experience_entries > 0
        ? `${c.experience_entries} entr${c.experience_entries === 1 ? "y" : "ies"} detected`
        : "Section present",
  },
  {
    key: "education",
    label: "Education",
    detail: (_, c) =>
      c.education_entries > 0
        ? `${c.education_entries} degree${c.education_entries === 1 ? "" : "s"} detected`
        : "Section present",
  },
  {
    key: "skills",
    label: "Skills",
    detail: (s) => {
      const count = s.skills?.split(",").length ?? 0;
      return count > 1 ? `~${count} skills listed` : "Section present";
    },
  },
  {
    key: "projects",
    label: "Projects",
    detail: (_, c) =>
      c.project_entries > 0
        ? `${c.project_entries} project${c.project_entries === 1 ? "" : "s"} detected`
        : "Section present",
  },
  {
    key: "summary",
    label: "Summary / Objective",
    detail: () => "Professional summary found",
  },
  {
    key: "certifications",
    label: "Certifications",
    detail: (_, c) =>
      c.certification_entries > 0
        ? `${c.certification_entries} certification${c.certification_entries === 1 ? "" : "s"}`
        : "Section present",
  },
];

export function FeedbackList({
  detectedSections,
  sectionCounts,
}: FeedbackListProps) {
  const present = SECTION_STATUSES.filter(
    (s) => detectedSections[s.key] !== null,
  );
  const absent = SECTION_STATUSES.filter(
    (s) => detectedSections[s.key] === null,
  );

  return (
    <div className="flex flex-col gap-4">
      <h3 className="text-xs font-display font-semibold text-text-muted uppercase tracking-widest">
        Detected Sections
      </h3>

      <ul className="flex flex-col gap-2">
        {present.map((s) => (
          <li
            key={s.key}
            className="flex items-start gap-3 py-2 border-b border-surface-border last:border-0"
          >
            <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-score-high/10">
              <svg
                className="h-3 w-3 text-score-high"
                viewBox="0 0 12 12"
                fill="none"
              >
                <path
                  d="M2.5 6l2.5 2.5 4.5-5"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-medium text-text-primary font-display leading-snug">
                {s.label}
              </span>
              <span className="text-xs text-text-secondary">
                {s.detail(detectedSections, sectionCounts)}
              </span>
            </div>
          </li>
        ))}

        {absent.map((s) => (
          <li
            key={s.key}
            className="flex items-start gap-3 py-2 border-b border-surface-border last:border-0 opacity-50"
          >
            <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-surface-border">
              <svg
                className="h-3 w-3 text-text-muted"
                viewBox="0 0 12 12"
                fill="none"
              >
                <path
                  d="M3 9l6-6M3 3l6 6"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </span>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-medium text-text-secondary font-display leading-snug">
                {s.label}
              </span>
              <span className="text-xs text-text-muted">Not detected</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
