import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import * as api from "../services/api";
import { RecordAnalysisPage } from "./RecordAnalysisPage";

function renderWithClient(initialEntry = "/records/r_0001") {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/records/:recordId" element={<RecordAnalysisPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("RecordAnalysisPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the latest analysis incidents for a record", async () => {
    vi.spyOn(api, "fetchRecordAnalysis").mockResolvedValue([
      {
        record_id: "r_0001",
        has_leakage: true,
        total_leakage_amount: 80,
        analysis_status: "COMPLETED",
        analyzer_type: "RULE_PLUS_LLM",
        analysis_version: 1,
        issues: [
          {
            id: "r_0001",
            issue: "RATE_MISMATCH",
            expected_amount: 1000,
            billed_amount: 920,
            leakage: 80,
            reasoning: "Contract rate exceeds the billed rate, causing underbilling.",
            severity: "HIGH",
            suggestion: "Update the invoice rate to match the contract and recover the shortfall."
          }
        ]
      }
    ]);

    renderWithClient();

    await waitFor(() => {
      expect(screen.getByText(/record analysis/i)).toBeInTheDocument();
      expect(screen.getByText("RULE_PLUS_LLM")).toBeInTheDocument();
      expect(screen.getAllByText("$80.00")).toHaveLength(2);
      expect(screen.getByText("RATE_MISMATCH")).toBeInTheDocument();
      expect(
        screen.getByText(/contract rate exceeds the billed rate, causing underbilling/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/update the invoice rate to match the contract and recover the shortfall/i)
      ).toBeInTheDocument();
    });
  });
});
