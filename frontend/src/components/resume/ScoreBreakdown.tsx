import { ProgressBar } from "../ui/ProgressBar";
import type {
  ScoreBreakdown as ScoreBreakdownType,
  AnalysisMode,
} from "../../types/analysis.types";

interface ScoreBreakdownProps {
  breakdown: ScoreBreakdownType;
  mode: AnalysisMode;
}

// Maximum possible weighted contribution per dimension, per mode.
// These mirror the weight tables in backend/services/scoring/score_calculator.py.
const MODE_MAXES: Record<
  AnalysisMode,
  Record<keyof ScoreBreakdownType, number>
> = {
  job_title: { keyword_score: 30, section_score: 40, structure_score: 30 },
  ats: { keyword_score: 60, section_score: 20, structure_score: 20 },
};

const LABELS: Record<keyof ScoreBreakdownType, string> = {
  keyword_score: "Keywords",
  section_score: "Sections",
  structure_score: "Structure",
};

export function ScoreBreakdown({ breakdown, mode }: ScoreBreakdownProps) {
  const maxes = MODE_MAXES[mode];

  return (
    <div className="flex flex-col gap-4">
      <h3 className="text-xs font-display font-semibold text-text-muted uppercase tracking-widest">
        Score Breakdown
      </h3>
      {(Object.keys(LABELS) as Array<keyof ScoreBreakdownType>).map((key) => (
        <ProgressBar
          key={key}
          label={LABELS[key]}
          value={breakdown[key]}
          max={maxes[key]}
        />
      ))}
    </div>
  );
}
