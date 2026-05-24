import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer className="border-t border-surface-border mt-16">
      <div className="mx-auto max-w-6xl px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-text-secondary">
        <p>© 2026 ResumeAI. All rights reserved.</p>

        <div className="flex items-center gap-4">
          <Link
            to="/privacy"
            className="hover:text-text-primary transition-colors"
          >
            Privacy
          </Link>

          <Link
            to="/terms"
            className="hover:text-text-primary transition-colors"
          >
            Terms
          </Link>

          <Link
            to="/disclaimer"
            className="hover:text-text-primary transition-colors"
          >
            AI Disclaimer
          </Link>
        </div>
      </div>
    </footer>
  );
}
