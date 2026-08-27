import { Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { CurriculumPage } from "./pages/CurriculumPage";
import { LearningPage } from "./pages/LearningPage";
import { PYQPage } from "./pages/PYQPage";
import { TeachBackPage } from "./pages/TeachBackPage";

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<CurriculumPage />} />
        <Route path="/concept/:conceptId" element={<LearningPage />} />
        <Route path="/session/:sessionId" element={<TeachBackPage />} />
        <Route path="/pyq/:pyqId" element={<PYQPage />} />
        <Route
          path="*"
          element={
            <div>
              <h1 className="text-[22px] font-semibold">Page not found</h1>
              <p className="mt-2 text-[15px] text-ink-soft">
                That page doesn't exist. Head back to the learning path.
              </p>
            </div>
          }
        />
      </Route>
    </Routes>
  );
}
