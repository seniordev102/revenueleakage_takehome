import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { fetchDashboardSummary, fetchRecords, type DashboardRecord } from "../services/api";

const SEVERITY_LEVELS = ["HIGH", "MEDIUM", "LOW", "INFO"] as const;

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

export function DashboardPage() {
  const [page, setPage] = useState(1);
  const [severity, setSeverity] = useState("");
  const [search, setSearch] = useState("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: fetchDashboardSummary
  });

  const {
    data: recordsResponse,
    isLoading: isLoadingRecords,
    isError: isErrorRecords
  } = useQuery({
    queryKey: ["records", page, severity, search.trim()],
    queryFn: () =>
      fetchRecords({
        page,
        page_size: 10,
        severity: severity || undefined,
        search: search.trim() || undefined
      })
  });

  const normalizedSearch = search.trim();

  const severityCounts = useMemo(() => {
    const counts = Object.fromEntries(SEVERITY_LEVELS.map((level) => [level, 0])) as Record<
      (typeof SEVERITY_LEVELS)[number],
      number
    >;

    for (const record of recordsResponse?.items ?? []) {
      if (record.severity && record.severity in counts) {
        counts[record.severity as keyof typeof counts] += 1;
      }
    }

    return counts;
  }, [recordsResponse]);

  return (
    <section className="mx-auto max-w-6xl space-y-6">
      <div className="rounded-[28px] border border-white/10 bg-gradient-to-br from-slate-900/85 via-slate-900/70 to-cyan-950/35 p-7 shadow-2xl shadow-slate-950/40">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-sky-200">
              Risk overview
            </div>
            <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">Dashboard</h1>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Overview of processed billing records, flagged leakage, and overall risk. Data is loaded
              from the FastAPI backend.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Data source</p>
              <p className="mt-2 text-sm font-medium capitalize text-white">{data?.data_source ?? "memory"}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Active view</p>
              <p className="mt-2 text-sm font-medium text-white">
                {severity || normalizedSearch ? "Filtered results" : "All visible records"}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard
          label="Total records"
          value={data?.total_records}
          isLoading={isLoading}
          isError={isError}
        />
        <SummaryCard
          label="Flagged records"
          value={data?.flagged_records}
          isLoading={isLoading}
          isError={isError}
        />
        <SummaryCard
          label="Estimated leakage"
          value={data ? `$${data.total_leakage_amount.toFixed(2)}` : undefined}
          isLoading={isLoading}
          isError={isError}
        />
        <SummaryCard
          label="High severity"
          value={data?.high_severity_count}
          isLoading={isLoading}
          isError={isError}
        />
      </div>

      <section className="space-y-4">
        <div className="rounded-[24px] border border-white/10 bg-slate-900/65 p-4 shadow-xl shadow-slate-950/30 backdrop-blur-xl md:p-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-medium uppercase tracking-wide text-slate-300">
                Severity
              </label>
              <div className="relative min-w-[190px]">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <span className="h-2.5 w-2.5 rounded-full bg-gradient-to-br from-rose-400 via-amber-300 to-emerald-400 shadow-[0_0_14px_rgba(56,189,248,0.3)]" />
                </div>
                <select
                  value={severity}
                  onChange={(event) => {
                    setSeverity(event.target.value);
                    setPage(1);
                  }}
                  className="w-full appearance-none rounded-2xl border border-white/10 bg-gradient-to-r from-slate-950/95 via-slate-900/90 to-slate-950/95 py-2.5 pl-8 pr-11 text-sm font-medium text-slate-100 shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_12px_30px_rgba(2,6,23,0.28)] transition hover:border-sky-400/30 focus:border-sky-400/40 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
                >
                  <option value="">All severities</option>
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                  <option value="INFO">Info</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400">
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 20 20"
                    className="h-4 w-4"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M5 7.5 10 12.5 15 7.5"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              </div>
            </div>

            <div className="flex flex-1 md:max-w-sm items-center gap-2">
              <input
                type="search"
                value={search}
                onChange={(event) => {
                  setSearch(event.target.value);
                  setPage(1);
                }}
                placeholder="Search by contract, customer, or product…"
                className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-4 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 shadow-inner shadow-slate-950/30 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-400">
            <span className="uppercase tracking-[0.22em] text-slate-500">Filters</span>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
              Severity: {severity || "All"}
            </span>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
              Search: {normalizedSearch || "None"}
            </span>
          </div>
        </div>

        <RecordsTable
          response={recordsResponse}
          isLoading={isLoadingRecords}
          isError={isErrorRecords}
          page={page}
          onPageChange={setPage}
          hasActiveFilters={Boolean(severity || normalizedSearch)}
        />

        <div className="rounded-[24px] border border-white/10 bg-slate-900/65 p-5 shadow-xl shadow-slate-950/30 backdrop-blur-xl">
          <h2 className="mb-2 text-sm font-semibold text-slate-100">Severity distribution</h2>
          <p className="mb-4 text-xs text-slate-400">
            Distribution of HIGH, MEDIUM, LOW, and INFO records in the current table results.
          </p>
          <SeverityDistributionChart
            counts={severityCounts}
            isLoading={isLoadingRecords}
            isError={isErrorRecords}
            severityFilter={severity}
            searchFilter={search}
          />
        </div>
      </section>
    </section>
  );
}

type SummaryCardProps = {
  label: string;
  value?: string | number;
  isLoading: boolean;
  isError: boolean;
};

function SummaryCard({ label, value, isLoading, isError }: SummaryCardProps) {
  let content: string | number | JSX.Element = "—";

  if (isLoading) {
    content = <span className="text-slate-500 text-sm">Loading...</span>;
  } else if (isError) {
    content = <span className="text-rose-400 text-sm">Error</span>;
  } else if (value !== undefined) {
    content = value;
  }

  return (
    <div className="group relative overflow-hidden rounded-[24px] border border-white/10 bg-slate-900/70 p-5 shadow-xl shadow-slate-950/30">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-400/50 to-transparent opacity-80" />
      <div className="absolute right-0 top-0 h-20 w-20 rounded-full bg-sky-400/10 blur-2xl transition group-hover:bg-sky-400/15" />
      <p className="text-xs uppercase tracking-[0.22em] text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-white">{content}</p>
    </div>
  );
}

type RecordsTableProps = {
  response:
    | {
        total: number;
        page: number;
        page_size: number;
        items: DashboardRecord[];
      }
    | undefined;
  isLoading: boolean;
  isError: boolean;
  page: number;
  onPageChange: (page: number) => void;
  hasActiveFilters: boolean;
};

function RecordsTable({
  response,
  isLoading,
  isError,
  page,
  onPageChange,
  hasActiveFilters
}: RecordsTableProps) {
  const total = response?.total ?? 0;
  const visibleCount = response?.items.length ?? 0;
  const pageSize = response?.page_size ?? 10;
  const totalPages = total > 0 ? Math.ceil(total / pageSize) : 1;

  return (
    <div className="overflow-hidden rounded-[24px] border border-white/10 bg-slate-900/65 shadow-xl shadow-slate-950/30 backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-4 text-xs text-slate-400">
        <span>
          Records{" "}
          {total > 0 && (
            <span className="ml-1 text-[11px] text-slate-500">
              ({total} total, showing {visibleCount})
            </span>
          )}
        </span>
      </div>

      {isLoading ? (
        <div className="px-4 py-10 text-sm text-slate-400">Loading records…</div>
      ) : isError ? (
        <div className="px-4 py-10 text-sm text-rose-400">Failed to load records.</div>
      ) : total === 0 ? (
        <div className="px-4 py-10 text-sm text-slate-400">No records available yet.</div>
      ) : visibleCount === 0 ? (
        <div className="px-4 py-10 text-sm text-slate-400">
          {hasActiveFilters ? "No records match the current filters." : "No records available yet."}
        </div>
      ) : (
        <div className="overflow-x-auto px-4 py-4">
          <table className="min-w-full text-sm text-left">
            <thead className="border-b border-white/10 text-xs uppercase tracking-wide text-slate-400">
              <tr>
                <th className="py-2 pr-4">Contract</th>
                <th className="py-2 pr-4">Customer</th>
                <th className="py-2 pr-4">Product</th>
                <th className="py-2 pr-4 text-right">Expected</th>
                <th className="py-2 pr-4 text-right">Billed</th>
                <th className="py-2 pr-4 text-right">Leakage</th>
                <th className="py-2 pr-4 text-right">Severity</th>
                <th className="py-2">Analysis</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {response?.items.map((r) => (
                <tr
                  key={r.record_id ?? `${r.contract_id}-${r.customer_id}-${r.product_id}`}
                  className="transition hover:bg-white/5"
                >
                  <td className="py-3 pr-4 font-mono text-xs text-slate-300">{r.contract_id}</td>
                  <td className="py-3 pr-4 text-slate-200">{r.customer_id}</td>
                  <td className="py-3 pr-4 text-slate-200">{r.product_id}</td>
                  <td className="py-3 pr-4 text-right text-slate-200">
                    {r.expected_amount != null ? `$${r.expected_amount.toFixed(2)}` : "—"}
                  </td>
                  <td className="py-3 pr-4 text-right text-slate-200">
                    {r.billed_amount != null ? `$${r.billed_amount.toFixed(2)}` : "—"}
                  </td>
                  <td className="py-3 pr-4 text-right text-slate-100">
                    {r.leakage_amount != null ? `$${r.leakage_amount.toFixed(2)}` : "—"}
                  </td>
                  <td className="py-3 pr-4 text-right">
                    {r.severity ? (
                      <span className={getSeverityBadgeClass(r.severity)}>
                        {r.severity}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="py-3">
                    {r.record_id ? (
                      <Link
                        to={`/records/${r.record_id}`}
                        className="inline-flex items-center rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-100 transition hover:bg-white/10"
                      >
                        View analysis
                      </Link>
                    ) : (
                      <span className="text-xs text-slate-500">Unavailable</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-between border-t border-white/10 px-4 py-4 text-xs text-slate-400">
        <span>
          Page {page} of {totalPages}
        </span>
        <div className="flex items-center gap-1">
          <button
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-slate-200 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
            disabled={page <= 1}
            onClick={() => onPageChange(Math.max(1, page - 1))}
          >
            ‹ Prev
          </button>
          <button
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-slate-200 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
            disabled={page >= totalPages}
            onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          >
            Next ›
          </button>
        </div>
      </div>
    </div>
  );
}

type SeverityDistributionChartProps = {
  counts: Record<(typeof SEVERITY_LEVELS)[number], number>;
  isLoading: boolean;
  isError: boolean;
  severityFilter: string;
  searchFilter: string;
};

function SeverityDistributionChart({
  counts,
  isLoading,
  isError,
  severityFilter,
  searchFilter
}: SeverityDistributionChartProps) {
  const total = Object.values(counts).reduce((sum, value) => sum + value, 0);
  const maxCount = Math.max(...Object.values(counts), 1);

  if (isLoading) {
    return <div className="h-32 flex items-center justify-center text-xs text-slate-500">Loading chart…</div>;
  }

  if (isError) {
    return (
      <div className="h-32 flex items-center justify-center text-xs text-rose-400">
        Failed to load severity distribution.
      </div>
    );
  }

  if (total === 0) {
    return (
      <div className="h-32 flex items-center justify-center text-xs text-slate-500">
        {severityFilter
          ? `No ${severityFilter.toLowerCase()} records in the current results.`
          : searchFilter.trim()
          ? "No records match the current search."
          : "No records available for charting."}
      </div>
    );
  }

  return (
    <div className="space-y-3" aria-label="Severity distribution chart">
      {SEVERITY_LEVELS.map((level) => {
        const count = counts[level];
        const width = `${(count / maxCount) * 100}%`;
        const percentage = Math.round((count / total) * 100);

        return (
          <div key={level} className="grid grid-cols-[64px_1fr_52px] items-center gap-3">
            <span className={getSeverityBadgeClass(level)}>{level}</span>
            <div className="h-3 overflow-hidden rounded-full bg-slate-800/90">
              <div
                className={
                  "h-full rounded-full transition-all " +
                  (level === "HIGH"
                    ? "bg-rose-400/80"
                    : level === "MEDIUM"
                    ? "bg-amber-400/80"
                    : level === "LOW"
                    ? "bg-emerald-400/80"
                    : "bg-slate-400/80")
                }
                style={{ width }}
                aria-label={`${level} count ${count}`}
              />
            </div>
            <span className="text-right text-xs text-slate-400">
              {count} ({percentage}%)
            </span>
          </div>
        );
      })}
    </div>
  );
}

