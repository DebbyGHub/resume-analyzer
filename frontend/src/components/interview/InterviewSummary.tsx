/**
 * InterviewSummary.tsx
 *
 * End-of-session interview performance summary.
 * Presentational only — no API calls, no calculations, no state.
 */

export interface QualityBreakdown {
  excellent?: number;
  good?: number;
  average?: number;
  weak?: number;
}

export interface InterviewSummaryProps {
  totalQuestions: number;
  averageScore: number; // 0–1
  strongestCategory?: string;
  weakestCategory?: string;
  qualityBreakdown?: QualityBreakdown;
  recommendation?: string;
}

// ─── Config ───────────────────────────────────────────────────────────────────

const QUALITY_CONFIG: Record<
  keyof QualityBreakdown,
  { label: string; bar: string; text: string }
> = {
  excellent: {
    label: "Excellent",
    bar: "bg-score-high",
    text: "text-score-high",
  },
  good: { label: "Good", bar: "bg-score-high", text: "text-score-high" },
  average: { label: "Average", bar: "bg-score-mid", text: "text-score-mid" },
  weak: { label: "Weak", bar: "bg-score-low", text: "text-score-low" },
};

function scoreColor(score: number): string {
  if (score >= 0.75) return "text-score-high";
  if (score >= 0.5) return "text-score-mid";
  return "text-score-low";
}

function scoreLabel(score: number): string {
  if (score >= 0.85) return "Excellent";
  if (score >= 0.7) return "Good";
  if (score >= 0.5) return "Average";
  return "Needs Work";
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function StatBlock({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="font-mono text-[10px] uppercase tracking-widest text-text-muted">
        {label}
      </span>
      <span className="font-display font-semibold text-lg text-text-primary leading-none">
        {value}
      </span>
      {sub && (
        <span className="font-mono text-[10px] text-text-muted">{sub}</span>
      )}
    </div>
  );
}

function QualityBar({
  tier,
  count,
  total,
}: {
  tier: keyof QualityBreakdown;
  count: number;
  total: number;
}) {
  const cfg = QUALITY_CONFIG[tier];
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;

  return (
    <div className="flex items-center gap-3">
      <span
        className={`font-mono text-[10px] uppercase tracking-widest w-16 shrink-0 ${cfg.text}`}
      >
        {cfg.label}
      </span>
      <div className="flex-1 h-1.5 rounded-full bg-surface-border overflow-hidden">
        <div
          className={`h-full rounded-full ${cfg.bar}`}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={count}
          aria-valuemax={total}
        />
      </div>
      <span className="font-mono text-xs text-text-secondary tabular-nums w-6 text-right shrink-0">
        {count}
      </span>
    </div>
  );
}

// ─── InterviewSummary ─────────────────────────────────────────────────────────

export function InterviewSummary({
  totalQuestions,
  averageScore,
  strongestCategory,
  weakestCategory,
  qualityBreakdown = {},
  recommendation,
}: InterviewSummaryProps) {
  const pct = Math.round(averageScore * 100);
  const color = scoreColor(averageScore);
  const overallLabel = scoreLabel(averageScore);

  const breakdownTiers = (
    ["excellent", "good", "average", "weak"] as (keyof QualityBreakdown)[]
  ).filter((t) => (qualityBreakdown[t] ?? 0) > 0);

  return (
    <div className="w-full max-w-2xl mx-auto flex flex-col gap-4 px-4 py-6">
      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="mb-1">
        <span className="font-mono text-xs text-accent uppercase tracking-[0.25em]">
          Session Complete
        </span>
      </div>

      {/* ── Score panel ─────────────────────────────────────────── */}
      <div
        className="rounded-2xl border border-surface-border bg-surface-card p-6
                      flex items-center justify-between gap-6"
      >
        {/* Big score */}
        <div className="flex flex-col gap-1">
          <span className="font-mono text-[10px] uppercase tracking-widest text-text-muted">
            Overall Score
          </span>
          <div className="flex items-baseline gap-1">
            <span
              className={`font-display font-bold text-5xl leading-none ${color}`}
            >
              {pct}
            </span>
            <span className="font-mono text-sm text-text-muted self-end mb-1">
              /100
            </span>
          </div>
          <span className={`font-mono text-xs ${color}`}>{overallLabel}</span>
        </div>

        {/* Stat blocks */}
        <div className="flex gap-6 flex-wrap justify-end">
          <StatBlock
            label="Questions"
            value={String(totalQuestions)}
            sub="answered"
          />
          {strongestCategory && (
            <StatBlock
              label="Strongest"
              value={strongestCategory}
              sub="topic area"
            />
          )}
          {weakestCategory && (
            <StatBlock
              label="Weakest"
              value={weakestCategory}
              sub="topic area"
            />
          )}
        </div>
      </div>

      {/* ── Quality breakdown ────────────────────────────────────── */}
      {breakdownTiers.length > 0 && (
        <div
          className="rounded-xl border border-surface-border bg-surface-card p-5
                        flex flex-col gap-4"
        >
          <h3 className="font-mono text-[10px] uppercase tracking-widest text-text-muted">
            Answer Quality Breakdown
          </h3>
          <div className="flex flex-col gap-3">
            {breakdownTiers.map((tier) => (
              <QualityBar
                key={tier}
                tier={tier}
                count={qualityBreakdown[tier] ?? 0}
                total={totalQuestions}
              />
            ))}
          </div>
        </div>
      )}

      {/* ── Recommendation ───────────────────────────────────────── */}
      {recommendation && (
        <div
          className="rounded-xl border border-surface-border bg-surface-raised/40
                        px-5 py-4 flex flex-col gap-2"
        >
          <span className="font-mono text-[10px] uppercase tracking-widest text-text-muted">
            Recommendation
          </span>
          <p className="text-sm text-text-secondary leading-relaxed">
            {recommendation}
          </p>
        </div>
      )}
    </div>
  );
}
