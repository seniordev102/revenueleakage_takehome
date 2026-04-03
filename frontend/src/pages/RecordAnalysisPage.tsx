import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { fetchRecordAnalysis } from "../services/api";

function getSeverityBadgeClass(severity: string) {
  return (
    "inline-flex items-center justify-center rounded-full px-2 py-0.5 text-[11px] font-medium " +
    (severity === "HIGH"
      ? "bg-rose-500/15 text-rose-300 border border-rose-500/40"
      : severity === "MEDIUM"
      ? "bg-amber-500/15 text-amber-300 border border-amber-500/40"
      : severity === "LOW"
      ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/40"
      : "bg-slate-700/40 text-slate-200 border border-slate-600/60")
  );
}

function formatAmount(value?: number) {
  return value == null ? "—" : `$${value.toFixed(2)}`;
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[24px] border border-white/10 bg-slate-900/70 p-5 shadow-xl shadow-slate-950/30">
      <p className="text-xs uppercase tracking-[0.22em] text-slate-400">{label}</p>
      <p className="mt-3 text-2xl font-semibold tracking-tight text-white">{value}</p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-sm font-medium text-slate-100">{value}</p>
    </div>
  );
}

export function RecordAnalysisPage() {
  const { recordId = "" } = useParams();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["record-analysis", recordId],
    queryFn: () => fetchRecordAnalysis(recordId),
    enabled: Boolean(recordId)
  });

  const latest = data?.[0];

  return (
    <section className="mx-auto max-w-5xl space-y-6">
      <div className="rounded-[28px] border border-white/10 bg-gradient-to-br from-slate-900/85 via-slate-900/70 to-indigo-950/30 p-7 shadow-2xl shadow-slate-950/40">
        <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-sky-200">
              Investigation view
            </div>
            <h1 className="text-3xl font-semibold tracking-tight text-white">Record analysis</h1>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Detailed leakage reasoning for <span className="font-mono text-slate-100">{recordId}</span>.
            </p>
          </div>
          <Link
            to="/dashboard"
            className="inline-flex items-center rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-white/10"
          >
            Back to dashboard
          </Link>
        </div>
      </div>

      {isLoading ? (
        <div className="rounded-2xl border border-white/10 bg-slate-900/60 px-5 py-6 text-sm text-slate-400">
          Loading analysis…
        </div>
      ) : null}
      {isError ? (
        <div className="rounded-2xl border border-rose-400/20 bg-rose-500/10 px-5 py-6 text-sm text-rose-300">
          Failed to load analysis.
        </div>
      ) : null}
      {!isLoading && !isError && !latest ? (
        <div className="rounded-2xl border border-white/10 bg-slate-900/60 px-5 py-6 text-sm text-slate-400">
          No analysis is available for this record yet.
        </div>
      ) : null}

      {latest ? (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <SummaryCard label="Analyzer" value={latest.analyzer_type} />
            <SummaryCard label="Status" value={latest.analysis_status} />
            <SummaryCard label="Total leakage" value={formatAmount(latest.total_leakage_amount)} />
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-slate-100">Detected incidents</h2>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
                {latest.issues.length} issue{latest.issues.length === 1 ? "" : "s"}
              </span>
            </div>
            {latest.issues.map((issue, index) => (
              <article
                key={`${issue.id ?? recordId}-${issue.issue}-${index}`}
                className="overflow-hidden rounded-[24px] border border-white/10 bg-slate-900/70 shadow-xl shadow-slate-950/30"
              >
                <div className="h-1 w-full bg-gradient-to-r from-sky-400/80 via-cyan-400/70 to-transparent" />
                <div className="space-y-4 p-5">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-100">{issue.issue}</p>
                      <p className="text-xs text-slate-400">Incident ID: {issue.id ?? recordId}</p>
                    </div>
                    <span className={getSeverityBadgeClass(issue.severity)}>{issue.severity}</span>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <Metric label="Expected" value={formatAmount(issue.expected_amount)} />
                    <Metric label="Billed" value={formatAmount(issue.billed_amount)} />
                    <Metric label="Leakage" value={formatAmount(issue.leakage)} />
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">Reasoning</p>
                    <p className="mt-1 text-sm leading-6 text-slate-200">{issue.reasoning}</p>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">Suggested action</p>
                    <p className="mt-1 text-sm leading-6 text-slate-200">
                      {issue.suggestion ?? "No suggestion provided."}
                    </p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}
