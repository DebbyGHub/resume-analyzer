export function DisclaimerPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <div className="space-y-8">
        <div className="space-y-3">
          <h1 className="text-4xl font-bold tracking-tight">AI Disclaimer</h1>

          <p className="text-text-secondary leading-7">
            ResumeAI uses AI-assisted analysis and semantic evaluation
            techniques to generate resume feedback and interview assessments.
          </p>
        </div>

        <ul className="list-disc pl-6 space-y-3 text-text-secondary leading-7">
          <li>
            AI-generated evaluations may not always be fully accurate or
            complete.
          </li>
          <li>
            Interview scores should be treated as guidance rather than
            definitive judgments.
          </li>
          <li>
            Semantic evaluation systems may occasionally misinterpret nuanced
            responses.
          </li>
          <li>
            Generated recommendations may differ from real-world hiring
            outcomes.
          </li>
          <li>
            ResumeAI does not guarantee interviews, employment, or hiring
            success.
          </li>
          <li>
            Users are encouraged to apply independent judgment and professional
            review.
          </li>
        </ul>
      </div>
    </div>
  );
}
