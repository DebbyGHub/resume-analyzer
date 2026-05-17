/**
 * AppLayout.tsx
 *
 * Shared application shell for all pages.
 * Provides: top navigation header + responsive content container.
 * Presentational only — no routing, no auth, no backend calls.
 */

import { Link } from "react-router-dom";

interface NavItem {
  label: string;
  active?: boolean;
}

// Placeholder nav items — replaced with router links in a future step
const NAV_ITEMS: NavItem[] = [
  { label: "Resume Analyzer" },
  { label: "AI Interview" },
];

interface AppLayoutProps {
  children: React.ReactNode;
  activeNav?: string; // label of the currently active nav item
  /** Full-width mode — disables the centered max-width container */
  fullWidth?: boolean;
}

// ─── Top Navigation ───────────────────────────────────────────────────────────

function TopNav({ activeNav }: { activeNav?: string }) {
  return (
    <header className="sticky top-0 z-10 border-b border-surface-border bg-surface-raised/80 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 h-14">
        {/* Wordmark */}
        <div className="flex items-center gap-2.5">
          <div
            className="h-6 w-6 rounded-md bg-accent/20 border border-accent/40
                          flex items-center justify-center"
          >
            <span className="font-mono text-[10px] font-bold text-accent">
              AI
            </span>
          </div>
          <span className="font-display font-bold text-sm text-text-primary tracking-tight">
            Resume<span className="text-accent">AI</span>
          </span>
        </div>

        {/* Nav items */}
        <nav className="flex items-center gap-1" aria-label="Main navigation">
          {NAV_ITEMS.map((item) => {
            const isActive = item.label === activeNav;
            return (
              <Link
                key={item.label}
                to={item.label === "AI Interview" ? "/interview" : "/resume"}
                className={
                  "px-3 py-1.5 rounded-lg font-display text-xs font-medium transition-colors " +
                  (isActive
                    ? "bg-accent/10 text-accent border border-accent/25"
                    : "text-text-secondary hover:text-text-primary hover:bg-surface-border/60")
                }
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

// ─── AppLayout ────────────────────────────────────────────────────────────────

export function AppLayout({
  children,
  activeNav,
  fullWidth = false,
}: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-surface-base text-text-primary">
      <TopNav activeNav={activeNav} />

      <main className={fullWidth ? "" : "mx-auto max-w-6xl px-6 py-8"}>
        {children}
      </main>
    </div>
  );
}
