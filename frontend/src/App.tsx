import { NavLink, Route, Routes } from "react-router-dom";
import { UploadPage } from "./pages/UploadPage";
import { DashboardPage } from "./pages/DashboardPage";
import { RecordAnalysisPage } from "./pages/RecordAnalysisPage";

export default function App() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-8rem] top-[-6rem] h-72 w-72 rounded-full bg-sky-500/15 blur-3xl" />
        <div className="absolute right-[-10rem] top-20 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute bottom-[-10rem] left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-indigo-500/10 blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(56,189,248,0.08),transparent_28%),linear-gradient(180deg,rgba(2,6,23,0.2),rgba(2,6,23,0.95))]" />
      </div>

      <div className="relative z-10 flex min-h-screen flex-col">
        <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/65 backdrop-blur-xl">
          <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-sky-400/30 bg-gradient-to-br from-sky-400/20 to-cyan-300/10 shadow-[0_0_40px_rgba(56,189,248,0.18)]">
                <span className="text-sm font-semibold tracking-[0.24em] text-sky-200">AI</span>
              </div>
              <div>
                <p className="text-[11px] font-medium uppercase tracking-[0.32em] text-sky-300/80">
                  Revenue intelligence
                </p>
                <span className="text-lg font-semibold tracking-tight text-white">
                  Revenue Leakage Detection
                </span>
              </div>
            </div>

            <nav className="flex gap-2 rounded-full border border-white/10 bg-white/5 p-1.5 text-sm shadow-lg shadow-slate-950/30">
            <NavLink
              to="/upload"
              className={({ isActive }) =>
                `rounded-full px-4 py-2 transition ${
                  isActive
                    ? "bg-gradient-to-r from-sky-500 to-cyan-400 text-white shadow-lg shadow-sky-500/20"
                    : "text-slate-300 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              Upload
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `rounded-full px-4 py-2 transition ${
                  isActive
                    ? "bg-gradient-to-r from-sky-500 to-cyan-400 text-white shadow-lg shadow-sky-500/20"
                    : "text-slate-300 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              Dashboard
            </NavLink>
          </nav>
          </div>
        </header>

        <main className="mx-auto flex-1 w-full max-w-6xl px-4 py-8 md:py-10">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/records/:recordId" element={<RecordAnalysisPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

