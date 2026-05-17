/**
 * QuestionCard.tsx
 *
 * Displays the current interview question with optional metadata.
 * Presentational only — no API calls, no state management.
 */

export interface QuestionCardProps {
  question: string;
  topic?: string;
  difficulty?: "easy" | "medium" | "hard";
  questionNumber?: number;
  totalQuestions?: number;
}

// ─── Config ───────────────────────────────────────────────────────────────────

const DIFFICULTY_CONFIG = {
  easy: {
    label: "Easy",
    classes: "text-score-high bg-score-high/10 border-score-high/25",
  },
  medium: {
    label: "Medium",
    classes: "text-score-mid  bg-score-mid/10  border-score-mid/25",
  },
  hard: {
    label: "Hard",
    classes: "text-score-low  bg-score-low/10  border-score-low/25",
  },
} as const;

// ─── QuestionCard ─────────────────────────────────────────────────────────────

export function QuestionCard({
  question,
  topic,
  difficulty,
  questionNumber,
  totalQuestions,
}: QuestionCardProps) {
  const diffCfg = difficulty ? DIFFICULTY_CONFIG[difficulty] : null;
  const showProgress =
    questionNumber !== undefined && totalQuestions !== undefined;

  return (
    <div className="px-5 py-4 border-b border-surface-border bg-surface-raised/40">
      {/* Metadata row */}
      {(topic || diffCfg || showProgress) && (
        <div className="flex items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            {/* Topic badge */}
            {topic && (
              <span
                className="font-mono text-[10px] uppercase tracking-widest
                               text-text-muted bg-surface-border/60
                               border border-surface-border rounded-md px-2 py-0.5"
              >
                {topic}
              </span>
            )}

            {/* Difficulty badge */}
            {diffCfg && (
              <span
                className={`font-mono text-[10px] uppercase tracking-widest
                                border rounded-md px-2 py-0.5 ${diffCfg.classes}`}
              >
                {diffCfg.label}
              </span>
            )}
          </div>

          {/* Progress indicator */}
          {showProgress && (
            <span className="font-mono text-xs text-text-muted shrink-0 tabular-nums">
              <span className="text-text-secondary font-semibold">
                {questionNumber}
              </span>
              <span className="mx-0.5">/</span>
              {totalQuestions}
            </span>
          )}
        </div>
      )}

      {/* Question text */}
      <p className="font-display font-semibold text-base text-text-primary leading-snug">
        {question}
      </p>
    </div>
  );
}
