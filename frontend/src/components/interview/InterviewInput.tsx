/**
 * InterviewInput.tsx
 *
 * Candidate answer input area for the interview interface.
 * Handles textarea, submit button, keyboard shortcuts, and char count.
 * Presentational + interaction only — no API calls, no global state.
 */

import { useRef, useEffect, type KeyboardEvent } from "react";

export interface InterviewInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  loading?: boolean;
  placeholder?: string;
  maxLength?: number;
}

// ─── Submit icon ──────────────────────────────────────────────────────────────

function SendIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none" aria-hidden>
      <path
        d="M14 8L2 2l3 6-3 6 12-6z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function SpinnerIcon({ className }: { className?: string }) {
  return (
    <svg
      className={`animate-spin ${className}`}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="3"
        className="opacity-20"
      />
      <path
        d="M12 2a10 10 0 0110 10"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        className="opacity-80"
      />
    </svg>
  );
}

// ─── InterviewInput ───────────────────────────────────────────────────────────

export function InterviewInput({
  value,
  onChange,
  onSubmit,
  disabled = false,
  loading = false,
  placeholder = "Type your answer… (Enter to submit, Shift+Enter for new line)",
  maxLength,
}: InterviewInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // ── Auto-resize textarea height ──────────────────────────────
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [value]);

  useEffect(() => {
    if (!disabled && !loading) {
      textareaRef.current?.focus();
    }
  }, [disabled, loading]);

  // ── Submission guard ─────────────────────────────────────────
  const canSubmit = !disabled && !loading && value.trim().length > 0;

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (canSubmit) onSubmit();
    }
  }

  // ── Character count state ────────────────────────────────────
  const charCount = value.length;
  const nearLimit = maxLength && charCount >= maxLength * 0.9;
  const atLimit = maxLength && charCount >= maxLength;

  return (
    <div className="px-4 py-3 border-t border-surface-border bg-surface-base">
      {/* Input row */}
      <div
        className={
          "flex items-end gap-2 rounded-xl border px-3 py-2.5 transition-colors duration-150 " +
          (disabled
            ? "border-surface-border opacity-50"
            : "border-surface-border focus-within:border-accent/50 focus-within:bg-surface-raised/40")
        }
      >
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || loading}
          placeholder={placeholder}
          maxLength={maxLength}
          rows={1}
          className="flex-1 resize-none overflow-hidden bg-transparent text-sm
                     text-text-primary placeholder-text-muted font-sans leading-relaxed
                     focus:outline-none disabled:cursor-not-allowed"
          style={{ minHeight: "24px", maxHeight: "200px" }}
          aria-label="Your answer"
        />

        {/* Submit button */}
        <button
          onClick={onSubmit}
          disabled={!canSubmit}
          aria-label="Submit answer"
          className={
            "h-8 w-8 rounded-lg flex items-center justify-center shrink-0 mb-0.5 transition-all duration-150 " +
            (canSubmit
              ? "bg-accent text-surface-base hover:bg-accent-dim active:scale-95"
              : "bg-surface-border text-text-muted cursor-not-allowed")
          }
        >
          {loading ? (
            <SpinnerIcon className="h-3.5 w-3.5" />
          ) : (
            <SendIcon className="h-3.5 w-3.5" />
          )}
        </button>
      </div>

      {/* Footer row: hint + char count */}
      <div className="flex items-center justify-between mt-1.5 px-1">
        <span className="font-mono text-[10px] text-text-muted">
          {loading ? "Evaluating your answer…" : "Shift+Enter for new line"}
        </span>

        {maxLength && (
          <span
            className={
              "font-mono text-[10px] tabular-nums " +
              (atLimit
                ? "text-score-low"
                : nearLimit
                  ? "text-score-mid"
                  : "text-text-muted")
            }
          >
            {charCount}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
}
