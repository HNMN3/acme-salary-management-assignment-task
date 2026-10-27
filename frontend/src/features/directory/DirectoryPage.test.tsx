import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { Employee, PaginatedEmployees } from "../../api/types";
import { renderWithProviders } from "../../test/renderWithProviders";
import { DirectoryPage } from "./DirectoryPage";

function employee(id: number, overrides: Partial<Employee> = {}): Employee {
  return {
    id,
    first_name: `First${id}`,
    last_name: `Last${id}`,
    email: `person${id}@example.com`,
    job_title: "Engineer",
    department: { id: 1, name: "Engineering" },
    country: { id: 1, code: "US", name: "United States" },
    base_salary: 100_000,
    bonus: 5_000,
    total_compensation: 105_000,
    ...overrides,
  };
}

function page(items: Employee[], total = items.length): PaginatedEmployees {
  return { items, total, page: 1, page_size: 50 };
}

const FILTERS = {
  countries: [
    { id: 1, code: "US", name: "United States" },
    { id: 2, code: "IN", name: "India" },
  ],
  departments: [
    { id: 1, name: "Engineering" },
    { id: 2, name: "Sales" },
  ],
};

let employeeResponse: () => PaginatedEmployees;
let fetchMock: ReturnType<typeof vi.fn>;

function employeeRequests(): URL[] {
  return fetchMock.mock.calls
    .map(([url]) => new URL(String(url)))
    .filter((url) => url.pathname.endsWith("/employees"));
}

function lastEmployeeRequest(): URL {
  return employeeRequests().at(-1)!;
}

describe("DirectoryPage", () => {
  beforeEach(() => {
    employeeResponse = () => page([employee(1), employee(2)]);
    fetchMock = vi.fn(async (url: string) => {
      const body = String(url).includes("/meta/filters")
        ? FILTERS
        : employeeResponse();
      return { ok: true, json: async () => body };
    });
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows a loading state and then the employees", async () => {
    renderWithProviders(<DirectoryPage />);

    expect(screen.getByRole("status", { name: "Loading employees" })).toBeInTheDocument();
    expect(await screen.findByText("First1 Last1")).toBeInTheDocument();
    expect(screen.getByText("First2 Last2")).toBeInTheDocument();
    expect(screen.getByText("2 employees")).toBeInTheDocument();
  });

  it("formats compensation as currency", async () => {
    renderWithProviders(<DirectoryPage />);

    const row = (await screen.findByText("First1 Last1")).closest("tr")!;

    expect(within(row).getByText("$100,000")).toBeInTheDocument();
    expect(within(row).getByText("$5,000")).toBeInTheDocument();
    expect(within(row).getByText("$105,000")).toBeInTheDocument();
  });

  it("requests the first page sorted by name with a page size of 50", async () => {
    renderWithProviders(<DirectoryPage />);
    await screen.findByText("First1 Last1");

    const params = lastEmployeeRequest().searchParams;
    expect(params.get("page")).toBe("1");
    expect(params.get("page_size")).toBe("50");
    expect(params.get("sort_by")).toBe("name");
    expect(params.get("order")).toBe("asc");
    expect(params.has("search")).toBe(false);
  });

  it("shows an empty message when nothing matches", async () => {
    employeeResponse = () => page([]);

    renderWithProviders(<DirectoryPage />);

    expect(await screen.findByText("No employees match your filters.")).toBeInTheDocument();
  });

  describe("editing salary", () => {
    it("opens the modal for the chosen employee", async () => {
      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");

      await userEvent.click(screen.getByRole("button", { name: "Edit salary for First2 Last2" }));

      expect(await screen.findByRole("dialog", { name: "Edit salary" })).toBeInTheDocument();
      expect(screen.getByLabelText("Base salary")).toHaveValue("$100,000");
    });

    it("closes the modal and reloads the list after saving", async () => {
      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");
      await userEvent.click(screen.getByRole("button", { name: "Edit salary for First1 Last1" }));
      const before = employeeRequests().length;
      employeeResponse = () => page([employee(1, { base_salary: 120_000, total_compensation: 125_000 })]);

      await userEvent.click(await screen.findByRole("button", { name: "Save" }));

      expect(await screen.findByText("$125,000")).toBeInTheDocument();
      expect(employeeRequests().length).toBe(before + 1);
      await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
      const patch = fetchMock.mock.calls.find(([, init]) => init?.method === "PATCH");
      expect(String(patch![0])).toMatch(/\/employees\/1\/salary$/);
    });

    it("keeps the list unchanged when the modal is cancelled", async () => {
      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");
      await userEvent.click(screen.getByRole("button", { name: "Edit salary for First1 Last1" }));
      const before = employeeRequests().length;

      await userEvent.click(await screen.findByRole("button", { name: "Cancel" }));

      await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
      expect(employeeRequests().length).toBe(before);
    });
  });

  it("shows an error with a retry that reloads the list", async () => {
    fetchMock.mockImplementation(async (url: string) => {
      if (String(url).includes("/meta/filters")) {
        return { ok: true, json: async () => FILTERS };
      }
      return {
        ok: false,
        status: 500,
        statusText: "Server Error",
        json: async () => ({ detail: "Database unavailable" }),
      };
    });

    renderWithProviders(<DirectoryPage />);
    expect(await screen.findByText("Database unavailable")).toBeInTheDocument();

    fetchMock.mockImplementation(async (url: string) => ({
      ok: true,
      json: async () => (String(url).includes("/meta/filters") ? FILTERS : employeeResponse()),
    }));
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));

    expect(await screen.findByText("First1 Last1")).toBeInTheDocument();
  });

  describe("search", () => {
    it("waits for the debounce before querying and resets to page 1", async () => {
      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");
      const before = employeeRequests().length;

      await userEvent.type(screen.getByLabelText("Search"), "ali");

      expect(employeeRequests()).toHaveLength(before);
      await waitFor(() => expect(lastEmployeeRequest().searchParams.get("search")).toBe("ali"));
      expect(employeeRequests().length - before).toBe(1);
      expect(lastEmployeeRequest().searchParams.get("page")).toBe("1");
    });
  });

  describe("sorting", () => {
    it("sorts ascending on first click and toggles to descending on second", async () => {
      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");

      await userEvent.click(screen.getByRole("button", { name: "Base salary" }));
      await waitFor(() => expect(lastEmployeeRequest().searchParams.get("sort_by")).toBe("base_salary"));
      expect(lastEmployeeRequest().searchParams.get("order")).toBe("asc");

      await userEvent.click(screen.getByRole("button", { name: /Base salary/ }));
      await waitFor(() => expect(lastEmployeeRequest().searchParams.get("order")).toBe("desc"));
    });

    it("marks the sorted column with aria-sort", async () => {
      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");

      expect(screen.getByRole("columnheader", { name: /Name/ })).toHaveAttribute(
        "aria-sort",
        "ascending",
      );
      expect(screen.getByRole("columnheader", { name: /Bonus/ })).toHaveAttribute(
        "aria-sort",
        "none",
      );
    });
  });

  describe("filters", () => {
    it("sends the selected country and department", async () => {
      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");

      await userEvent.click(screen.getByRole("combobox", { name: "Country" }));
      await userEvent.click(await screen.findByRole("option", { name: "India", hidden: true }));
      await waitFor(() => expect(lastEmployeeRequest().searchParams.get("country_id")).toBe("2"));

      await userEvent.click(screen.getByRole("combobox", { name: "Department" }));
      await userEvent.click(await screen.findByRole("option", { name: "Sales", hidden: true }));
      await waitFor(() => expect(lastEmployeeRequest().searchParams.get("department_id")).toBe("2"));
      expect(lastEmployeeRequest().searchParams.get("country_id")).toBe("2");
    });

    it("restores the defaults when Reset is clicked", async () => {
      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");
      await userEvent.click(screen.getByRole("combobox", { name: "Country" }));
      await userEvent.click(await screen.findByRole("option", { name: "India", hidden: true }));
      await userEvent.click(screen.getByRole("button", { name: "Bonus" }));
      await waitFor(() => expect(lastEmployeeRequest().searchParams.get("sort_by")).toBe("bonus"));

      await userEvent.click(screen.getByRole("button", { name: "Reset" }));

      await waitFor(() => expect(lastEmployeeRequest().searchParams.get("sort_by")).toBe("name"));
      const params = lastEmployeeRequest().searchParams;
      expect(params.get("order")).toBe("asc");
      expect(params.has("country_id")).toBe(false);
      expect(params.has("search")).toBe(false);
      expect(screen.getByLabelText("Search")).toHaveValue("");
    });
  });

  describe("pagination", () => {
    it("requests the next page and returns to page 1 when a filter changes", async () => {
      employeeResponse = () => page([employee(1)], 120);
      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");

      await userEvent.click(screen.getByRole("button", { name: "2" }));
      await waitFor(() => expect(lastEmployeeRequest().searchParams.get("page")).toBe("2"));

      await userEvent.click(screen.getByRole("combobox", { name: "Country" }));
      await userEvent.click(await screen.findByRole("option", { name: "India", hidden: true }));
      await waitFor(() => expect(lastEmployeeRequest().searchParams.get("page")).toBe("1"));
    });

    it("renders one page button per 50 employees", async () => {
      employeeResponse = () => page([employee(1)], 120);

      renderWithProviders(<DirectoryPage />);
      await screen.findByText("First1 Last1");

      expect(screen.getByRole("button", { name: "3" })).toBeInTheDocument();
      expect(screen.queryByRole("button", { name: "4" })).not.toBeInTheDocument();
    });
  });
});
