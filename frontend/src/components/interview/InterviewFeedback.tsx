/**
 * InterviewFeedback.tsx
 *
 * Displays the structured evaluation result returned by the backend.
 * Presentational only — no API calls, no state management.
 */

export interface InterviewFeedbackProps {
  similarityScore: number;
  confidenceScore: number;
  finalScore:      number;
  quality:         "excellent" | "good" | "average" | "weak";
  flags?:          string[];
}

// ─── Config maps ──────────────────────────────────────────────────────────────

const QUALITY_CONFIG = {
  excellent: { label: "Excellent",  bar: "bg-score-high",  text: "text-score-high",  border: "border-score-high/30",  bg: "bg-score-high/8"  },
  good:      { label: "Good",       bar: "bg-score-high",  text: "text-score-high",  border: "border-score-high/20",  bg: "bg-score-high/5"  },
  average:   { label: "Average",    bar: "bg-score-mid",   text: "text-score-mid",   border: "border-score-mid/30",   bg: "bg-score-mid/8"   },
  weak:      { label: "Weak",       bar: "bg-score-low",   text: "text-score-low",   border: "border-score-low/30",   bg: "bg-score-low/8"   },
} as const;

const FLAG_LABELS: Record<string, string> = {
  answer_brief:     "Answer is brief",
  answer_too_short: "Answer too short",
  vague_answer:     "Vague phrasing detected",
  empty_answer:     "No answer provided",
};

// ─── Score bar ────────────────────────────────────────────────────────────────

function ScoreBar({
  label,
  value,
  barClass,
}: {
  label:    string;
  value:    number;
  barClass: string;
}) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-baseline justify-between">
        <span className="text-xs text-text-muted uppercase tracking-widest font-mono">
          {label}
        </span>
        <span className="font-mono text-sm text-text-primary tabular-nums">
          {pct}<span className="text-text-muted text-xs">%</span>
        </span>
      </div>
      <div className="h-1 w-full rounded-full bg-surface-border overflow-hidden">
        <div
          className={`h-full rounded-full ${barClass}`}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}

// ─── InterviewFeedback ────────────────────────────────────────────────────────

export function InterviewFeedback({
  similarityScore,
  confidenceScore,
  finalScore,
  quality,
  flags = [],
}: InterviewFeedbackProps) {
  const cfg = QUALITY_CONFIG[quality];

  return (
    <div className={`rounded-xl border ${cfg.border} ${cfg.bg} p-4 flex flex-col gap-4`}>

      {/* Header row — quality badge + final score */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`h-1.5 w-1.5 rounded-full ${cfg.bar}`} />
          <span className={`font-display font-semibold text-sm ${cfg.text}`}>
            {cfg.label}
          </span>
        </div>
        <div className="flex items-baseline gap-0.5">
          <span className={`font-mono text-xl font-semibold ${cfg.text}`}>
            {Math.round(finalScore * 100)}
          </span>
          <span className="font-mono text-xs text-text-muted">/100</span>
        </div>
      </div>

      {/* Score breakdown */}
      <div className="flex flex-col gap-3">
        <ScoreBar label="Similarity"  value={similarityScore} barClass={cfg.bar} />
        <ScoreBar label="Confidence"  value={confidenceScore} barClass={cfg.bar} />
      </div>

      {/* Flags */}
      {flags.length > 0 && (
        <div className="flex flex-col gap-1.5 pt-1 border-t border-surface-border/60">
          <p className="font-mono text-[10px] text-text-muted uppercase tracking-widest">
            Notes
          </p>
          <div className="flex flex-wrap gap-1.5">
            {flags.map(flag => (
              <span
                key={flag}
                className="inline-flex items-center gap-1 rounded-md bg-surface-raised
                           border border-surface-border px-2 py-0.5
                           font-mono text-[10px] text-text-secondary"
              >
                <span className="text-score-mid">!</span>
                {FLAG_LABELS[flag] ?? flag.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}