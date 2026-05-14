import { useState } from "react";
import { UploadPage } from "./pages/UploadPage";
import { ResultsPage } from "./pages/ResultsPage";
import type { ResumeAnalysisResponse } from "./types/analysis.types";

function App() {
  const [result, setResult] = useState<ResumeAnalysisResponse | null>(null);

  return (
    <main className="min-h-screen bg-[#0a0c10] text-white">
      {result ? (
        <ResultsPage result={result} onReset={() => setResult(null)} />
      ) : (
        <UploadPage
          onResult={(analysisResult) => setResult(analysisResult)}
        />
      )}
    </main>
  );
}

export default App;
