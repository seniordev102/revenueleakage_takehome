import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import * as api from "../services/api";
import { DashboardPage } from "./DashboardPage";

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("DashboardPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders summary cards with data from API", async () => {
    vi.spyOn(api, "fetchRecords").mockResolvedValue({
      total: 0,
      page: 1,
      page_size: 10,
      items: [],
      source: "memory"
    });
    vi.spyOn(api, "fetchDashboardSummary").mockResolvedValue({
      total_records: 10,
      flagged_records: 4,
      total_leakage_amount: 123.45,
      high_severity_count: 2,
      data_source: "memory"
    });

    renderWithClient(<DashboardPage />);

    expect(screen.getByText(/total records/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("10")).toBeInTheDocument();
      expect(screen.getByText("4")).toBeInTheDocument();
      expect(screen.getByText("$123.45")).toBeInTheDocument();
      expect(screen.getByText("2")).toBeInTheDocument();
    });
  });

  it("filters records by severity", async () => {
    vi.spyOn(api, "fetchDashboardSummary").mockResolvedValue({
      total_records: 10,
      flagged_records: 4,
      total_leakage_amount: 123.45,
      high_severity_count: 2
    });

    const fetchRecordsMock = vi.spyOn(api, "fetchRecords").mockResolvedValue({
      total: 1,
      page: 1,
      page_size: 10,
      items: [
        {
          record_id: "rec_1",
          contract_id: "contract-1",
          customer_id: "customer-1",
          product_id: "product-1",
          expected_amount: 10,
          billed_amount: 20,
          leakage_amount: 10,
          severity: "HIGH"
        }
      ]
    });

    renderWithClient(<DashboardPage />);

    await waitFor(() => {
      expect(fetchRecordsMock).toHaveBeenCalledWith({
        page: 1,
        page_size: 10,
        severity: undefined,
        search: undefined
      });
      expect(screen.getByRole("link", { name: /view analysis/i })).toHaveAttribute("href", "/records/rec_1");
    });

    fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "HIGH" }
    });

    await waitFor(() => {
      expect(fetchRecordsMock).toHaveBeenLastCalledWith({
        page: 1,
        page_size: 10,
        severity: "HIGH",
        search: undefined
      });
    });
  });

  it("renders severity distribution for the current records", async () => {
    vi.spyOn(api, "fetchDashboardSummary").mockResolvedValue({
      total_records: 10,
      flagged_records: 4,
      total_leakage_amount: 123.45,
      high_severity_count: 2
    });

    vi.spyOn(api, "fetchRecords").mockResolvedValue({
      total: 4,
      page: 1,
      page_size: 10,
      items: [
        { record_id: "rec_1", severity: "HIGH" },
        { record_id: "rec_2", severity: "HIGH" },
        { record_id: "rec_3", severity: "MEDIUM" },
        { record_id: "rec_4", severity: "LOW" }
      ]
    });

    renderWithClient(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByLabelText("Severity distribution chart")).toBeInTheDocument();
      expect(screen.getByLabelText("HIGH count 2")).toBeInTheDocument();
      expect(screen.getByLabelText("MEDIUM count 1")).toBeInTheDocument();
      expect(screen.getByLabelText("LOW count 1")).toBeInTheDocument();
      expect(screen.getByLabelText("INFO count 0")).toBeInTheDocument();
      expect(screen.getByText("2 (50%)")).toBeInTheDocument();
      expect(screen.getByText("0 (0%)")).toBeInTheDocument();
    });
  });

  it("filters the current records by search term", async () => {
    vi.spyOn(api, "fetchDashboardSummary").mockResolvedValue({
      total_records: 10,
      flagged_records: 4,
      total_leakage_amount: 123.45,
      high_severity_count: 2
    });

    const fetchRecordsMock = vi
      .spyOn(api, "fetchRecords")
      .mockResolvedValueOnce({
        total: 3,
        page: 1,
        page_size: 10,
        items: [
          {
            record_id: "rec_1",
            contract_id: "contract-alpha",
            customer_id: "customer-a",
            product_id: "product-x",
            severity: "HIGH"
          },
          {
            record_id: "rec_2",
            contract_id: "contract-beta",
            customer_id: "customer-b",
            product_id: "product-y",
            severity: "LOW"
          },
          {
            record_id: "rec_3",
            contract_id: "contract-gamma",
            customer_id: "customer-c",
            product_id: "product-z",
            severity: "INFO"
          }
        ]
      })
      .mockResolvedValueOnce({
        total: 1,
        page: 1,
        page_size: 10,
        items: [
          {
            record_id: "rec_2",
            contract_id: "contract-beta",
            customer_id: "customer-b",
            product_id: "product-y",
            severity: "LOW"
          }
        ]
      });

    renderWithClient(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("contract-alpha")).toBeInTheDocument();
      expect(screen.getByText("contract-beta")).toBeInTheDocument();
      expect(screen.getByText("contract-gamma")).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText(/search by contract, customer, or product/i), {
      target: { value: "beta" }
    });

    await waitFor(() => {
      expect(fetchRecordsMock).toHaveBeenLastCalledWith({
        page: 1,
        page_size: 10,
        severity: undefined,
        search: "beta"
      });
      expect(screen.queryByText("contract-alpha")).not.toBeInTheDocument();
      expect(screen.getByText("contract-beta")).toBeInTheDocument();
      expect(screen.queryByText("contract-gamma")).not.toBeInTheDocument();
      expect(screen.getByText(/\(1 total, showing 1\)/i)).toBeInTheDocument();
      expect(screen.getByLabelText("LOW count 1")).toBeInTheDocument();
      expect(screen.getByLabelText("HIGH count 0")).toBeInTheDocument();
    });
  });
});

