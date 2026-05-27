import type { AnalysisMode } from "../../types/analysis.types";

interface ScoreCardProps {
  totalScore: number;
  mode: AnalysisMode;
  jobTitle: string;
  companyName: string | null;
}

function scoreColor(score: number): string {
  if (score >= 75) return "#34d399"; // score-high
  if (score >= 45) return "#fbbf24"; // score-mid
  return "#f87171"; // score-low
}

function scoreLabel(score: number): string {
  if (score >= 85) return "Excellent";
  if (score >= 70) return "Strong";
  if (score >= 55) return "Good";
  if (score >= 40) return "Fair";
  return "Needs Work";
}

const RADIUS = 40;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS; // ≈ 251.2

export function ScoreCard({
  totalScore,
  mode,
  jobTitle,
  companyName,
}: ScoreCardProps) {
  const color = scoreColor(totalScore);
  const dashOffset = CIRCUMFERENCE - (CIRCUMFERENCE * totalScore) / 100;

  return (
    <div className="flex flex-col items-center gap-4 py-6">
      {/* SVG ring */}
      <div className="relative">
        <svg width="120" height="120" viewBox="0 0 100 100">
          {/* Track */}
          <circle
            cx="50"
            cy="50"
            r={RADIUS}
            fill="none"
            stroke="#252a35"
            strokeWidth="8"
          />
          {/* Progress */}
          <circle
            cx="50"
            cy="50"
            r={RADIUS}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={dashOffset}
            transform="rotate(-90 50 50)"
            style={{
              transition:
                "stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1), stroke 0.4s",
            }}
          />
        </svg>
        {/* Score number centered */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="font-mono text-3xl font-semibold leading-none"
            style={{ color }}
          >
            {totalScore}
          </span>
          <span className="text-xs text-text-muted font-mono">/100</span>
        </div>
      </div>

      {/* Label */}
      <div className="text-center">
        <p className="font-display font-semibold text-lg text-text-primary leading-tight">
          {scoreLabel(totalScore)}
        </p>
        <p className="text-xs text-text-secondary mt-0.5">
          {jobTitle}
          {companyName ? ` · ${companyName}` : ""}
        </p>
      </div>

      {/* Mode badge */}
      <span
        className={
          "inline-flex items-center rounded-full px-3 py-1 text-xs font-mono font-medium border " +
          (mode === "ats"
            ? "bg-accent/10 text-accent border-accent/30"
            : "bg-surface-border text-text-secondary border-surface-border")
        }
      >
        <span
          className={
            "font-mono uppercase tracking-[0.2em] " +
            (mode === "ats" ? "text-accent" : "text-text-muted")
          }
        >
          {mode === "ats" ? "ATS Mode" : "Job Title Mode"}
        </span>
      </span>
    </div>
  );
}
