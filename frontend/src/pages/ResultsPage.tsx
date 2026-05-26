import { ScoreCard } from "../components/resume/ScoreCard";
import { ScoreBreakdown } from "../components/resume/ScoreBreakdown";
import { MissingKeywords } from "../components/resume/MissingKeywords";
import { FeedbackList } from "../components/resume/FeedbackList";
import { ResumeSummary } from "../components/resume/ResumeSummary";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { useNavigate } from "react-router-dom";
import type {
  ResumeAnalysisResponse,
  FeedbackItem,
} from "../types/analysis.types";

interface ResultsPageProps {
  result: ResumeAnalysisResponse;
  onReset: () => void;
}

const PRIORITY_ICON: Record<string, { icon: string; color: string }> = {
  high: { icon: "●", color: "text-score-low" },
  medium: { icon: "●", color: "text-score-mid" },
  low: { icon: "●", color: "text-score-high" },
};

function FeedbackPanel({ feedback }: { feedback: FeedbackItem[] }) {
  if (feedback.length === 0) return null;

  return (
    <Card className="p-5">
      <h3 className="text-xs font-display font-semibold text-text-muted uppercase tracking-widest mb-4">
        Recommendations
      </h3>
      <ul className="flex flex-col gap-3">
        {feedback.map((item, i) => {
          const meta = PRIORITY_ICON[item.priority];
          return (
            <li key={i} className="flex items-start gap-3">
              <span
                className={`mt-1 text-xs shrink-0 ${meta.color}`}
                aria-hidden
              >
                {meta.icon}
              </span>
              <div className="flex flex-col gap-0.5">
                <div className="flex items-center gap-2">
                  <span
                    className={`font-mono text-[10px] uppercase tracking-wider ${meta.color}`}
                  >
                    {item.priority}
                  </span>
                  <span className="text-text-muted text-[10px] font-mono">
                    {item.category}
                  </span>
                </div>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {item.message}
                </p>
              </div>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}

export function ResultsPage({ result, onReset }: ResultsPageProps) {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-surface-base px-4 py-12">
      <div className="mx-auto max-w-4xl">
        {/* Top bar */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-accent" />

            <span className="font-mono text-xs text-text-muted tracking-widest uppercase">
              Analysis Complete
            </span>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              onClick={onReset}
              className="text-xs px-4 py-2"
            >
              ← New Analysis
            </Button>

            <Button
              className="text-xs px-5 py-2"
              onClick={() => {
                navigate("/interview", {
                  state: {
                    extractedSkills: result.extracted_skills,
                    jobTitle: result.job_title,
                    companyName: result.company_name,
                    matchedKeywords: result.matched_keywords,
                    missingKeywords: result.missing_keywords,
                  },
                });
              }}
            >
              Practice Resume-Based Interview
            </Button>
          </div>
        </div>

        {/* Main grid — 3 columns on desktop */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* ── Left column ── Score + Breakdown */}
          <div className="md:col-span-1 flex flex-col gap-4">
            <Card accent className="px-4 pb-6">
              <ScoreCard
                totalScore={result.total_score}
                mode={result.mode}
                jobTitle={result.job_title}
                companyName={result.company_name}
              />
            </Card>

            <Card className="p-5">
              <ScoreBreakdown
                breakdown={result.score_breakdown}
                mode={result.mode}
              />
            </Card>
          </div>

          {/* ── Right column ── Keywords + Section feedback */}
          <div className="md:col-span-2 flex flex-col gap-4">
            <Card className="p-5">
              <MissingKeywords
                missing={result.missing_keywords}
                matched={result.matched_keywords}
              />
            </Card>

            <Card className="p-5">
              <FeedbackList
                detectedSections={result.detected_sections}
                sectionCounts={result.section_counts}
              />
            </Card>
          </div>
        </div>

        <Card className="p-6 mt-4 border border-white/10 bg-white/5">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">
                Personalized AI Interview
              </h2>

              <p className="text-text-muted text-sm leading-relaxed max-w-2xl">
                Interview questions are tailored using your resume skills,
                target role, and technical background.
              </p>

              {result.job_title && (
                <div className="mt-4 text-sm text-text-muted">
                  Target Role:
                  <span className="ml-2 text-text-primary font-medium">
                    {result.job_title}
                  </span>
                </div>
              )}

              {result.extracted_skills?.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {result.extracted_skills.slice(0, 8).map((skill) => (
                    <div
                      key={skill}
                      className="px-3 py-1.5 rounded-full bg-white/10 border border-white/10 text-sm"
                    >
                      {skill}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <Button
              onClick={() => {
                navigate("/interview", {
                  state: {
                    extractedSkills: result.extracted_skills,
                    jobTitle: result.job_title,
                    companyName: result.company_name,
                    matchedKeywords: result.matched_keywords,
                    missingKeywords: result.missing_keywords,
                  },
                });
              }}
              className="shrink-0"
            >
              Start AI Interview
            </Button>
          </div>
        </Card>

        {/* ── Full-width: Recommendations ── */}
        {result.feedback.length > 0 && (
          <div className="mt-4">
            <FeedbackPanel feedback={result.feedback} />
          </div>
        )}

        {/* ── Full-width: Parser transparency ── */}
        <div className="mt-4">
          <ResumeSummary
            detectedSections={result.detected_sections}
            sectionCounts={result.section_counts}
            rawText={result.raw_text}
            parserWarnings={result.parser_warnings ?? []}
          />
        </div>
      </div>
    </div>
  );
}
