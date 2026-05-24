import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";

import { AppLayout } from "./layouts/AppLayout";

import { UploadPage } from "./pages/UploadPage";
import { ResultsPage } from "./pages/ResultsPage";
import { InterviewPage } from "./pages/InterviewPage";

import { PrivacyPage } from "./pages/PrivacyPage";
import { TermsPage } from "./pages/TermsPage";
import { DisclaimerPage } from "./pages/DisclaimerPage";

import type { ResumeAnalysisResponse } from "./types/analysis.types";

function App() {
  const [result, setResult] = useState<ResumeAnalysisResponse | null>(null);

  return (
    <BrowserRouter>
      <Routes>
        {/* Default route */}
        <Route path="/" element={<Navigate to="/resume" replace />} />

        {/* Resume Analyzer */}
        <Route
          path="/resume"
          element={
            <AppLayout activeNav="Resume Analyzer">
              {result ? (
                <ResultsPage result={result} onReset={() => setResult(null)} />
              ) : (
                <UploadPage
                  onResult={(analysisResult) => setResult(analysisResult)}
                />
              )}
            </AppLayout>
          }
        />

        {/* AI Interview */}
        <Route
          path="/interview"
          element={
            <AppLayout activeNav="AI Interview" fullWidth>
              <InterviewPage extractedSkills={result?.extracted_skills ?? []} />
            </AppLayout>
          }
        />

        {/* Privacy Policy */}
        <Route
          path="/privacy"
          element={
            <AppLayout>
              <PrivacyPage />
            </AppLayout>
          }
        />

        {/* Terms */}
        <Route
          path="/terms"
          element={
            <AppLayout>
              <TermsPage />
            </AppLayout>
          }
        />

        {/* AI Disclaimer */}
        <Route
          path="/disclaimer"
          element={
            <AppLayout>
              <DisclaimerPage />
            </AppLayout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
