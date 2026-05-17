/**
 * ChatMessage.tsx
 *
 * Renders a single message in the interview conversation.
 * Presentational only — no API calls, no state.
 */

export interface ChatMessageProps {
  role: "ai" | "user";
  content: string;
  timestamp?: string;
  status?: "sending" | "sent" | "error";
}

// ─── Status indicator ─────────────────────────────────────────────────────────

function StatusDot({ status }: { status: ChatMessageProps["status"] }) {
  if (!status || status === "sent") return null;

  const styles = {
    sending: "text-text-muted",
    error: "text-score-low",
  } as const;

  const labels = {
    sending: "Sending…",
    error: "Failed to send",
  } as const;

  return (
    <span className={`font-mono text-[10px] ${styles[status]}`}>
      {labels[status]}
    </span>
  );
}

// ─── Avatar badge ─────────────────────────────────────────────────────────────

function Avatar({ role }: { role: "ai" | "user" }) {
  const isAI = role === "ai";
  return (
    <div
      className={
        "h-7 w-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 " +
        (isAI
          ? "bg-accent/15 border border-accent/30"
          : "bg-surface-border border border-surface-border")
      }
    >
      <span
        className={
          "font-mono text-[10px] font-semibold " +
          (isAI ? "text-accent" : "text-text-muted")
        }
      >
        {isAI ? "AI" : "You"}
      </span>
    </div>
  );
}

// ─── ChatMessage ──────────────────────────────────────────────────────────────

export function ChatMessage({
  role,
  content,
  timestamp,
  status,
}: ChatMessageProps) {
  const isAI = role === "ai";

  return (
    <div
      className={
        "flex items-start gap-2.5 " +
        (isAI ? "" : "flex-row-reverse self-end max-w-[82%]")
      }
    >
      {/* Avatar */}
      <Avatar role={role} />

      {/* Bubble + meta */}
      <div
        className={
          "flex flex-col gap-1 min-w-0 " +
          (isAI ? "items-start max-w-[82%]" : "items-end")
        }
      >
        {/* Message bubble */}
        <div
          className={
            "rounded-2xl px-4 py-3 " +
            (isAI
              ? "rounded-tl-sm bg-surface-raised border border-surface-border"
              : "rounded-tr-sm bg-accent/10 border border-accent/20")
          }
        >
          <p
            className={
              "text-sm leading-relaxed whitespace-pre-wrap break-words " +
              (isAI ? "text-text-secondary" : "text-text-primary")
            }
          >
            {content}
          </p>
        </div>

        {/* Timestamp + status row */}
        {(timestamp || status) && (
          <div
            className={
              "flex items-center gap-2 px-1 " + (isAI ? "" : "flex-row-reverse")
            }
          >
            {timestamp && (
              <span className="font-mono text-[10px] text-text-muted">
                {timestamp}
              </span>
            )}
            <StatusDot status={status} />
          </div>
        )}
      </div>
    </div>
  );
}
