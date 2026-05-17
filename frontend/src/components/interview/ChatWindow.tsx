/**
 * ChatWindow.tsx
 *
 * Main layout container for the interview session.
 * Structural shell only — no API calls, no state management.
 *
 * Slot layout (top → bottom):
 *   SessionHeader   — topic, progress, timer
 *   QuestionCard    — current question display
 *   Message area    — scrollable conversation history
 *   TypingIndicator — AI composing state
 *   InterviewInput  — candidate answer input
 *   InterviewFeedback — evaluation result (inline, appears after submit)
 */

interface ChatWindowProps {
  /** Slot: SessionHeader component */
  header?: React.ReactNode;
  /** Slot: QuestionCard component */
  questionCard?: React.ReactNode;
  /** Slot: list of ChatMessage components */
  messages?: React.ReactNode;
  /** Slot: TypingIndicator component */
  typingIndicator?: React.ReactNode;
  /** Slot: InterviewInput component */
  input?: React.ReactNode;
  /** Slot: InterviewFeedback component — shown after answer is evaluated */
  feedback?: React.ReactNode;
}

// ─── Placeholder sub-components ──────────────────────────────────────────────
// Removed once real components are wired in.

function PlaceholderHeader() {
  return (
    <div className="flex items-center justify-between px-6 py-4 border-b border-surface-border">
      <div className="flex items-center gap-3">
        <div className="h-2 w-2 rounded-full bg-score-high animate-pulse" />
        <span className="font-mono text-xs text-text-muted uppercase tracking-widest">
          Interview Session
        </span>
      </div>
      <div className="flex items-center gap-4">
        <span className="font-mono text-xs text-text-muted">Topic: OOP</span>
        <span className="font-display text-xs font-semibold text-accent">
          Q 1 / 5
        </span>
      </div>
    </div>
  );
}

function PlaceholderQuestion() {
  return (
    <div className="px-6 py-5 border-b border-surface-border bg-surface-raised/50">
      <p className="text-xs font-mono text-text-muted uppercase tracking-widest mb-2">
        Current Question
      </p>
      <p className="text-base font-display font-semibold text-text-primary leading-snug">
        How does encapsulation improve software maintainability?
      </p>
    </div>
  );
}

function PlaceholderMessages() {
  return (
    <div className="flex flex-col gap-4 px-6 py-6">
      {/* Interviewer message */}
      <div className="flex items-start gap-3 max-w-[80%]">
        <div className="h-7 w-7 rounded-full bg-accent/20 border border-accent/30 flex items-center justify-center shrink-0 mt-0.5">
          <span className="font-mono text-[10px] text-accent font-semibold">
            AI
          </span>
        </div>
        <div className="rounded-2xl rounded-tl-sm bg-surface-raised border border-surface-border px-4 py-3">
          <p className="text-sm text-text-secondary leading-relaxed">
            Welcome to your technical interview. I'll be evaluating your answers
            semantically — focus on clarity and completeness. Ready to begin?
          </p>
        </div>
      </div>

      {/* Candidate message */}
      <div className="flex items-start gap-3 max-w-[80%] self-end flex-row-reverse">
        <div className="h-7 w-7 rounded-full bg-surface-border flex items-center justify-center shrink-0 mt-0.5">
          <span className="font-mono text-[10px] text-text-muted font-semibold">
            You
          </span>
        </div>
        <div className="rounded-2xl rounded-tr-sm bg-accent/10 border border-accent/20 px-4 py-3">
          <p className="text-sm text-text-primary leading-relaxed">
            Yes, I'm ready. Let's start.
          </p>
        </div>
      </div>
    </div>
  );
}

function PlaceholderInput() {
  return (
    <div className="px-6 py-4 border-t border-surface-border bg-surface-base">
      <div className="flex items-end gap-3">
        <textarea
          rows={3}
          placeholder="Type your answer here…"
          disabled
          className="flex-1 resize-none rounded-xl bg-surface-raised border border-surface-border
                     px-4 py-3 text-sm text-text-primary placeholder-text-muted font-sans
                     focus:outline-none focus:border-accent/60 leading-relaxed
                     disabled:opacity-40 disabled:cursor-not-allowed"
        />
        <button
          disabled
          className="h-10 w-10 rounded-xl bg-accent/20 border border-accent/30
                     flex items-center justify-center shrink-0 mb-0.5
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <svg className="h-4 w-4 text-accent" viewBox="0 0 16 16" fill="none">
            <path
              d="M14 8L2 2l3 6-3 6 12-6z"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
      <p className="mt-2 text-xs text-text-muted font-mono">
        Press Enter to submit · Shift+Enter for new line
      </p>
    </div>
  );
}

// ─── ChatWindow ───────────────────────────────────────────────────────────────

export function ChatWindow({
  header,
  questionCard,
  messages,
  typingIndicator,
  input,
  feedback,
}: ChatWindowProps) {
  return (
    <div className="min-h-screen bg-surface-base flex items-center justify-center px-4 py-10">
      <div
        className="w-full max-w-2xl flex flex-col rounded-2xl overflow-hidden
                      bg-surface-card border border-surface-border
                      shadow-[0_8px_48px_rgba(0,0,0,0.5)]"
        style={{ minHeight: "600px", maxHeight: "90vh" }}
      >
        {/* ── Header ────────────────────────────────────────────── */}
        {header ?? <PlaceholderHeader />}

        {/* ── Question card ─────────────────────────────────────── */}
        {questionCard}

        {/* ── Scrollable message area ───────────────────────────── */}
        <div className="flex-1 overflow-y-auto">
          {messages ?? <PlaceholderMessages />}

          {/* Typing indicator slot */}
          {typingIndicator && (
            <div className="px-6 pb-3">{typingIndicator}</div>
          )}
        </div>

        {/* ── Feedback slot (appears after evaluation) ──────────── */}
        {feedback && (
          <div className="px-6 py-4 border-t border-surface-border bg-surface-raised/30">
            {feedback}
          </div>
        )}

        {/* ── Input ─────────────────────────────────────────────── */}
        {input ?? <PlaceholderInput />}
      </div>
    </div>
  );
}
