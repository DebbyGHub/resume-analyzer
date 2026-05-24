export function PrivacyPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <div className="space-y-8">
        <div className="space-y-3">
          <h1 className="text-4xl font-bold tracking-tight">Privacy Policy</h1>

          <p className="text-text-secondary leading-7">
            ResumeAI processes resumes and interview responses to provide
            AI-powered analysis and interview functionality.
          </p>
        </div>

        <ul className="list-disc pl-6 space-y-3 text-text-secondary leading-7">
          <li>
            Uploaded resumes are processed to generate resume analysis and
            interview questions.
          </li>
          <li>
            Interview responses may be analyzed using semantic evaluation
            techniques.
          </li>
          <li>
            Uploaded files may be temporarily processed during active sessions.
          </li>
          <li>
            Users should avoid uploading highly sensitive personal information.
          </li>

        </ul>
      </div>
    </div>
  );
}
