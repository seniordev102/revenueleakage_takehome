export const API_BASE_URL = "http://localhost:8000";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed with status ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function uploadBillingFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/uploads`, {
    method: "POST",
    body: formData
  });

  return handleResponse<{
    upload: { upload_id: string; record_count: number };
    record_count: number;
    sample_records: DashboardRecord[];
  }>(res);
}

export async function fetchDashboardSummary() {
  const res = await fetch(`${API_BASE_URL}/dashboard/summary`);
  return handleResponse<{
    total_records: number;
    flagged_records: number;
    total_leakage_amount: number;
    high_severity_count: number;
    data_source?: "memory" | "dynamodb";
  }>(res);
}

export type DashboardRecord = {
  record_id?: string;
  contract_id?: string;
  customer_id?: string;
  product_id?: string;
  expected_amount?: number;
  billed_amount?: number;
  leakage_amount?: number;
  severity?: string;
  has_leakage?: boolean;
};

export async function fetchRecords(params: {
  page?: number;
  page_size?: number;
  severity?: string;
  search?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", String(params.page));
  if (params.page_size) searchParams.set("page_size", String(params.page_size));
  if (params.severity) searchParams.set("severity", params.severity);
  if (params.search) searchParams.set("search", params.search);

  const res = await fetch(`${API_BASE_URL}/records?${searchParams.toString()}`);
  return handleResponse<{
    total: number;
    page: number;
    page_size: number;
    items: DashboardRecord[];
  }>(res);
}

export type AnalysisIssue = {
  id?: string;
  issue: string;
  expected_amount?: number;
  billed_amount?: number;
  leakage?: number;
  reasoning: string;
  severity: string;
  suggestion?: string;
  confidence_score?: number;
};

export type AnalysisResult = {
  record_id: string;
  issues: AnalysisIssue[];
  has_leakage: boolean;
  total_leakage_amount: number;
  analysis_status: string;
  analyzer_type: string;
  analysis_version: number;
};

export async function fetchRecordAnalysis(recordId: string) {
  const res = await fetch(`${API_BASE_URL}/records/${recordId}/analysis`);
  return handleResponse<AnalysisResult[]>(res);
}
