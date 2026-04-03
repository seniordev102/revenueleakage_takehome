import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import * as api from "../services/api";
import { UploadPage } from "./UploadPage";

const queryClient = new QueryClient();

function renderWithClient(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("UploadPage", () => {
  it("renders upload form and calls API on submit", async () => {
    const mockUpload = vi.spyOn(api, "uploadBillingFile").mockResolvedValue({
      upload: { upload_id: "u_001", record_count: 1 },
      record_count: 1,
      sample_records: [
        {
          record_id: "r_0001",
          contract_id: "contract-1",
          customer_id: "customer-1",
          product_id: "product-1",
          leakage_amount: 10,
          severity: "HIGH"
        }
      ]
    });

    renderWithClient(<UploadPage />);

    const input = screen.getByLabelText(/choose csv or json file/i) as HTMLInputElement;
    const file = new File(["test"], "sample.csv", { type: "text/csv" });

    // jsdom doesn't fully implement FileList, but React will pick up the first file
    Object.defineProperty(input, "files", {
      value: [file],
      writable: false
    });

    fireEvent.change(input);

    const button = screen.getByRole("button", { name: /upload and analyze/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockUpload).toHaveBeenCalledTimes(1);
      expect(screen.getByText(/upload successful/i)).toBeInTheDocument();
      expect(screen.getByText(/processed sample records/i)).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /view dashboard/i })).toHaveAttribute(
        "href",
        "/dashboard"
      );
    });
  });
});

