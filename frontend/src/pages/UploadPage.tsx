import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { uploadBillingFile } from "../services/api";

function getSeverityBadgeClass(severity?: string) {
  const value = severity ?? "INFO";
  return (
    "inline-flex items-center justify-center rounded-full border px-2.5 py-1 text-[11px] font-medium " +
    (value === "HIGH"
      ? "border-rose-400/30 bg-rose-500/10 text-rose-200"
      : value === "MEDIUM"
      ? "border-amber-400/30 bg-amber-500/10 text-amber-200"
      : value === "LOW"
      ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-200"
      : "border-slate-500/40 bg-slate-700/30 text-slate-200")
  );
}

export function UploadPage() {
  const [file, setFile] = useState<File | null>(null);

  const mutation = useMutation({
    mutationFn: uploadBillingFile
  });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    mutation.mutate(file);
  };

  return (
    <section className="mx-auto max-w-5xl space-y-8">
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[28px] border border-white/10 bg-gradient-to-br from-slate-900/90 via-slate-900/70 to-sky-950/40 p-8 shadow-2xl shadow-slate-950/40">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-sky-200">
            Ingestion
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
            Upload billing data
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
            CSV or JSON files containing pricing and billing records. Files are sent to the FastAPI
            backend for ingestion, leakage analysis, and dashboard-ready enrichment.
          </p>
          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Formats</p>
              <p className="mt-2 text-sm font-medium text-white">CSV and JSON</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Pipeline</p>
              <p className="mt-2 text-sm font-medium text-white">Normalize and analyze</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Output</p>
              <p className="mt-2 text-sm font-medium text-white">Dashboard-ready records</p>
            </div>
          </div>
        </div>

        <div className="rounded-[28px] border border-white/10 bg-slate-900/70 p-6 shadow-2xl shadow-slate-950/40 backdrop-blur-xl">
          <form onSubmit={onSubmit} className="flex h-full flex-col gap-5">
            <div>
              <p className="text-sm font-semibold text-white">Submit a dataset</p>
              <p className="mt-1 text-sm text-slate-400">
                Choose a file and send it through the ingestion and analysis workflow.
              </p>
            </div>

            <label className="flex flex-col gap-3 rounded-2xl border border-dashed border-slate-600 bg-slate-950/40 p-5 text-sm text-slate-200 transition hover:border-sky-400/40 hover:bg-slate-900/70">
              <span className="font-medium">Choose CSV or JSON file</span>
              <input
                type="file"
                accept=".csv,application/json,.json,text/csv"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="block w-full text-sm text-slate-200 file:mr-4 file:rounded-full file:border-0 file:bg-sky-500/90 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-sky-400"
              />
              <span className="text-xs text-slate-500">
                Best results come from normalized billing exports with pricing, quantity, and billed amounts.
              </span>
            </label>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Selected file</p>
              <p className="mt-2 truncate text-sm font-medium text-white">
                {file ? file.name : "No file selected yet"}
              </p>
            </div>

            <button
              type="submit"
              disabled={!file || mutation.isPending}
              className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-sky-500 to-cyan-400 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-500/20 transition hover:from-sky-400 hover:to-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {mutation.isPending ? "Uploading..." : "Upload and analyze"}
            </button>

            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Analysis mode</p>
                <p className="mt-2 text-sm text-slate-200">Deterministic checks with optional AI reasoning</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Next step</p>
                <p className="mt-2 text-sm text-slate-200">Review processed records in the dashboard</p>
              </div>
            </div>

            {mutation.isError && (
              <p className="rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
                {(mutation.error as Error).message || "Upload failed, please try again."}
              </p>
            )}
          </form>
        </div>
      </div>

      {mutation.isSuccess && (
        <div className="rounded-[28px] border border-emerald-400/20 bg-gradient-to-br from-emerald-500/10 via-slate-900/80 to-slate-900/80 p-6 shadow-2xl shadow-slate-950/40">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div className="space-y-2">
              <div className="inline-flex items-center rounded-full border border-emerald-400/25 bg-emerald-500/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.22em] text-emerald-200">
                Completed
              </div>
              <p className="text-sm text-emerald-100">
                Upload successful. Processed {mutation.data.record_count} records (upload id{" "}
                <span className="font-mono">{mutation.data.upload.upload_id}</span>).
              </p>
            </div>
            <Link
              to="/dashboard"
              className="inline-flex items-center justify-center rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10"
            >
              View dashboard
            </Link>
          </div>

          {mutation.data.sample_records.length > 0 ? (
            <div className="mt-6 space-y-3">
              <p className="text-xs font-medium uppercase tracking-[0.24em] text-slate-300">
                Processed sample records
              </p>
              <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/35">
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm text-left">
                    <thead className="bg-white/5 text-xs uppercase tracking-wide text-slate-400">
                      <tr>
                        <th className="px-4 py-3">Contract</th>
                        <th className="px-4 py-3">Customer</th>
                        <th className="px-4 py-3">Product</th>
                        <th className="px-4 py-3 text-right">Leakage</th>
                        <th className="px-4 py-3 text-right">Severity</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {mutation.data.sample_records.map((record, index) => (
                        <tr
                          key={
                            record.record_id ??
                            `${record.contract_id}-${record.customer_id}-${record.product_id}-${index}`
                          }
                          className="transition hover:bg-white/5"
                        >
                          <td className="px-4 py-3 text-slate-200">{record.contract_id ?? "—"}</td>
                          <td className="px-4 py-3 text-slate-200">{record.customer_id ?? "—"}</td>
                          <td className="px-4 py-3 text-slate-200">{record.product_id ?? "—"}</td>
                          <td className="px-4 py-3 text-right text-slate-100">
                            {record.leakage_amount != null ? `$${record.leakage_amount.toFixed(2)}` : "—"}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <span className={getSeverityBadgeClass(record.severity)}>
                              {record.severity ?? "INFO"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}

