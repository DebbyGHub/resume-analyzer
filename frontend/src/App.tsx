import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";

import { AppLayout } from "./layouts/AppLayout";

import { UploadPage } from "./pages/UploadPage";
import { ResultsPage } from "./pages/ResultsPage";
import { InterviewPage } from "./pages/InterviewPage";

import type { ResumeAnalysisResponse } from "./types/analysis.types";

function ResumeFlow() {
  const [result, setResult] = useState<ResumeAnalysisResponse | null>(null);

  return (
    <AppLayout activeNav="Resume Analyzer">
      {result ? (
        <ResultsPage result={result} onReset={() => setResult(null)} />
      ) : (
        <UploadPage onResult={(analysisResult) => setResult(analysisResult)} />
      )}
    </AppLayout>
  );
}

function InterviewFlow() {
  return (
    <AppLayout activeNav="AI Interview" fullWidth>
      <InterviewPage />
    </AppLayout>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Default route */}
        <Route path="/" element={<Navigate to="/resume" replace />} />

        {/* Resume analyzer */}
        <Route path="/resume" element={<ResumeFlow />} />

        {/* AI interview */}
        <Route path="/interview" element={<InterviewFlow />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
