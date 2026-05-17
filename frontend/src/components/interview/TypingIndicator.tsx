/**
 * TypingIndicator.tsx
 *
 * Displays an "AI is typing" state inside the interview chat UI.
 * Presentational only — CSS-only animation, no timers, no state.
 * Layout mirrors ChatMessage (left-aligned, AI avatar).
 */

export interface TypingIndicatorProps {
  label?: string;
}

export function TypingIndicator({
  label = "AI is evaluating your response…",
}: TypingIndicatorProps) {
  return (
    <div className="flex items-start gap-2.5 px-6 py-3">
      {/* AI avatar — matches ChatMessage */}
      <div
        className="h-7 w-7 rounded-full bg-accent/15 border border-accent/30
                      flex items-center justify-center shrink-0 mt-0.5"
      >
        <span className="font-mono text-[10px] text-accent font-semibold">
          AI
        </span>
      </div>

      {/* Bubble */}
      <div
        className="rounded-2xl rounded-tl-sm bg-surface-raised border border-surface-border
                      px-4 py-3 flex items-center gap-3"
      >
        {/* Bouncing dots */}
        <span className="flex items-center gap-1" aria-hidden>
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="h-1.5 w-1.5 rounded-full bg-text-muted"
              style={{
                animation: "typing-bounce 1.2s ease-in-out infinite",
                animationDelay: `${i * 0.2}s`,
              }}
            />
          ))}
        </span>

        {/* Label */}
        <span className="font-mono text-[11px] text-text-muted">{label}</span>
      </div>

      {/* Keyframes injected inline — no extra CSS file needed */}
      <style>{`
        @keyframes typing-bounce {
          0%, 60%, 100% { transform: translateY(0);    opacity: 0.4; }
          30%            { transform: translateY(-4px); opacity: 1;   }
        }
      `}</style>
    </div>
  );
}
