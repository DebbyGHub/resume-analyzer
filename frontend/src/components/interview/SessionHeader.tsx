/**
 * SessionHeader.tsx
 *
 * Top-level interview session metadata bar.
 * Presentational only — no timer logic, no API calls, no state.
 */

export interface SessionHeaderProps {
  title?: string;
  currentQuestion?: number;
  totalQuestions?: number;
  topic?: string;
  elapsedTime?: string;
  status?: "active" | "paused" | "completed";
}

// ─── Config ───────────────────────────────────────────────────────────────────

const STATUS_CONFIG = {
  active: {
    label: "Active",
    text: "text-score-high",
  },
  paused: { label: "Paused", text: "text-score-mid" },
  completed: {
    label: "Completed",
    text: "text-text-secondary",
  },
} as const;

// ─── Divider ─────────────────────────────────────────────────────────────────

function Divider() {
  return <span className="h-3 w-px bg-surface-border shrink-0" aria-hidden />;
}

// ─── SessionHeader ────────────────────────────────────────────────────────────

export function SessionHeader({
  title = "Technical Interview",
  currentQuestion,
  totalQuestions,
  topic,
  elapsedTime,
  status = "active",
}: SessionHeaderProps) {
  const cfg = STATUS_CONFIG[status];
  const showProgress =
    currentQuestion !== undefined && totalQuestions !== undefined;

  return (
    <div
      className="flex items-center justify-between gap-4
                    px-5 py-3 border-b border-surface-border
                    bg-surface-raised/60"
    >
      {/* Left — title + status */}
      <div className="flex items-center gap-3 min-w-0">

        {/* Title */}
        <span className="font-display font-semibold text-sm text-text-primary truncate">
          {title}
        </span>

        {/* Status label — hidden on very small viewports */}
        <span
          className={`hidden sm:inline font-mono text-[10px] uppercase
                          tracking-widest ${cfg.text}`}
        >
          {cfg.label}
        </span>
      </div>

      {/* Right — metadata pills */}
      <div className="flex items-center gap-2.5 shrink-0">
        {/* Topic */}
        {topic && (
          <>
            <span className="font-mono text-[10px] uppercase tracking-widest text-text-muted">
              {topic}
            </span>
            <Divider />
          </>
        )}

        {/* Progress */}
        {showProgress && (
          <>
            <span className="font-mono text-xs tabular-nums text-text-secondary">
              <span className="text-text-primary font-semibold">
                {currentQuestion}
              </span>
              <span className="text-text-muted mx-0.5">/</span>
              {totalQuestions}
            </span>
            {elapsedTime && <Divider />}
          </>
        )}

        {/* Elapsed time */}
        {elapsedTime && (
          <span className="font-mono text-xs tabular-nums text-text-muted">
            {elapsedTime}
          </span>
        )}
      </div>
    </div>
  );
}
