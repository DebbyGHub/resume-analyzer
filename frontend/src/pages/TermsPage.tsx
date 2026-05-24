export function TermsPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <div className="space-y-8">
        <div className="space-y-3">
          <h1 className="text-4xl font-bold tracking-tight">Terms of Use</h1>

          <p className="text-text-secondary leading-7">
            By using ResumeAI, you agree to use the platform responsibly and for
            educational or career preparation purposes.
          </p>
        </div>

        <ul className="list-disc pl-6 space-y-3 text-text-secondary leading-7">
          <li>
            Users are responsible for the accuracy of uploaded resumes and
            submitted responses.
          </li>
          <li>
            Abuse, spam, or malicious usage of the platform is prohibited.
          </li>
          <li>
            Users may not attempt to exploit, disrupt, or overload the system.
          </li>
          <li>
            Uploaded content must comply with applicable laws and regulations.
          </li>
          <li>ResumeAI features and scoring systems may evolve over time.</li>
          <li>
            Platform functionality may change as new AI capabilities are
            introduced.
          </li>
        </ul>
      </div>
    </div>
  );
}
