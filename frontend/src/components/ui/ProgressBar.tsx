interface ProgressBarProps {
  label: string;
  value: number; // 0–100 (weighted contribution, not raw sub-score)
  max: number; // maximum possible contribution for this dimension
  className?: string;
}

function barColor(value: number, max: number): string {
  const pct = max > 0 ? value / max : 0;
  if (pct >= 0.75) return "bg-score-high";
  if (pct >= 0.4) return "bg-score-mid";
  return "bg-score-low";
}

export function ProgressBar({
  label,
  value,
  max,
  className = "",
}: ProgressBarProps) {
  const widthPct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  const color = barColor(value, max);

  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      <div className="flex justify-between items-baseline">
        <span className="text-xs font-medium text-text-secondary uppercase tracking-widest">
          {label}
        </span>
        <span className="font-mono text-sm text-text-primary">
          {value}
          <span className="text-text-muted">/{max}</span>
        </span>
      </div>

      <div className="h-1.5 w-full rounded-full bg-surface-border overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${color}`}
          style={{ width: `${widthPct}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
}
