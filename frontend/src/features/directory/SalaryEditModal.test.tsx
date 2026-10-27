import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { Employee } from "../../api/types";
import { renderWithProviders } from "../../test/renderWithProviders";
import { SalaryEditModal } from "./SalaryEditModal";

const EMPLOYEE: Employee = {
  id: 7,
  first_name: "Ada",
  last_name: "Lovelace",
  email: "ada@example.com",
  job_title: "Engineer",
  department: { id: 1, name: "Engineering" },
  country: { id: 1, code: "US", name: "United States" },
  base_salary: 100_000,
  bonus: 5_000,
  total_compensation: 105_000,
};

let fetchMock: ReturnType<typeof vi.fn>;
const onClose = vi.fn();
const onSaved = vi.fn();

function renderModal(employee: Employee | null = EMPLOYEE) {
  return renderWithProviders(
    <SalaryEditModal employee={employee} onClose={onClose} onSaved={onSaved} />,
  );
}

async function replaceValue(label: string, value: string) {
  const input = await screen.findByLabelText(label);
  await userEvent.clear(input);
  if (value) {
    await userEvent.type(input, value);
  }
}

describe("SalaryEditModal", () => {
  beforeEach(() => {
    onClose.mockReset();
    onSaved.mockReset();
    fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({ ...EMPLOYEE, base_salary: 120_000, total_compensation: 125_000 }),
    }));
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders nothing when no employee is selected", () => {
    renderModal(null);

    expect(screen.queryByLabelText("Base salary")).not.toBeInTheDocument();
  });

  it("pre-fills the employee's current values", async () => {
    renderModal();

    expect(await screen.findByLabelText("Base salary")).toHaveValue("$100,000");
    expect(screen.getByLabelText("Bonus")).toHaveValue("$5,000");
    expect(screen.getByText("Ada Lovelace")).toBeInTheDocument();
    expect(screen.getByText("Total compensation: $105,000")).toBeInTheDocument();
  });

  it("clears a field's error once the value is edited", async () => {
    renderModal();

    await replaceValue("Base salary", "0");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Base salary must be at least $1")).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText("Base salary"), "5");

    expect(screen.queryByText("Base salary must be at least $1")).not.toBeInTheDocument();
  });

  it("updates the total compensation preview as values change", async () => {
    renderModal();

    await replaceValue("Base salary", "120000");

    expect(screen.getByText("Total compensation: $125,000")).toBeInTheDocument();
  });

  it("sends a PATCH with the new values and reports the saved employee", async () => {
    renderModal();
    await replaceValue("Base salary", "120000");
    await replaceValue("Bonus", "0");

    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(onSaved).toHaveBeenCalledOnce());
    const [url, init] = fetchMock.mock.calls[0];
    expect(String(url)).toMatch(/\/employees\/7\/salary$/);
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(init.body)).toEqual({ base_salary: 120_000, bonus: 0 });
    expect(onSaved.mock.calls[0][0].base_salary).toBe(120_000);
  });

  it("shows validation errors and does not call the API", async () => {
    renderModal();
    await replaceValue("Base salary", "");
    await replaceValue("Bonus", "");

    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(await screen.findByText("Base salary is required")).toBeInTheDocument();
    expect(screen.getByText("Bonus is required")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
    expect(onSaved).not.toHaveBeenCalled();
  });

  it("rejects a base salary above the maximum", async () => {
    renderModal();
    await replaceValue("Base salary", "10000001");

    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(
      await screen.findByText("Base salary cannot exceed $10,000,000"),
    ).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("shows the server error and keeps the modal open when saving fails", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ detail: "Employee 7 not found" }),
    });
    renderModal();
    await screen.findByLabelText("Base salary");

    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Employee 7 not found");
    expect(onSaved).not.toHaveBeenCalled();
    expect(screen.getByLabelText("Base salary")).toBeInTheDocument();
  });

  it("calls onClose without saving when Cancel is clicked", async () => {
    renderModal();
    await screen.findByLabelText("Base salary");

    await userEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onClose).toHaveBeenCalledOnce();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
