interface MissingKeywordsProps {
  missing: string[];
  matched: string[];
}

export function MissingKeywords({ missing, matched }: MissingKeywordsProps) {
  const total = missing.length + matched.length;

  return (
    <div className="flex flex-col gap-4">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-display font-semibold text-text-muted uppercase tracking-widest">
          Keyword Coverage
        </h3>
        <span className="font-mono text-xs text-text-secondary">
          <span className="text-score-high">{matched.length}</span>
          <span className="text-text-muted">/{total} matched</span>
        </span>
      </div>

      {/* Missing chips */}
      {missing.length > 0 ? (
        <div>
          <p className="text-xs text-text-muted mb-2">Missing from your resume:</p>
          <div className="flex flex-wrap gap-1.5">
            {missing.map((kw) => (
              <span
                key={kw}
                className="inline-block rounded-md bg-score-low/10 border border-score-low/20
                           px-2.5 py-1 font-mono text-xs text-score-low"
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-sm text-score-high font-display">
          ✓ All target keywords are present in your resume.
        </p>
      )}

      {/* Matched chips (collapsed by default — show first 8) */}
      {matched.length > 0 && (
        <div>
          <p className="text-xs text-text-muted mb-2">Matched keywords:</p>
          <div className="flex flex-wrap gap-1.5">
            {matched.slice(0, 12).map((kw) => (
              <span
                key={kw}
                className="inline-block rounded-md bg-score-high/10 border border-score-high/20
                           px-2.5 py-1 font-mono text-xs text-score-high"
              >
                {kw}
              </span>
            ))}
            {matched.length > 12 && (
              <span className="inline-block rounded-md bg-surface-border px-2.5 py-1
                               font-mono text-xs text-text-muted">
                +{matched.length - 12} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}