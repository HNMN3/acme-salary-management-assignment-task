import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { cloneElement } from "react";
import type { ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type {
  CountryStats,
  DepartmentStats,
  Employee,
  SalaryBand,
  Summary,
} from "../../api/types";
import { renderWithProviders } from "../../test/renderWithProviders";
import { AnalyticsPage } from "./AnalyticsPage";

vi.mock("recharts", async (importOriginal) => {
  const actual = await importOriginal<typeof import("recharts")>();
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: ReactElement }) =>
      cloneElement(children, { width: 800, height: 300 } as object),
  };
});

const US = { id: 1, code: "US", name: "United States" };
const INDIA = { id: 2, code: "IN", name: "India" };

const SUMMARY: Summary = {
  headcount: 1234,
  total_payroll: 150_000_000,
  average_base_salary: 80_500.4,
  average_total_compensation: 90_250.6,
  min_base_salary: 20_000,
  max_base_salary: 400_000,
  highest_paid_country: { ...US, average_total_compensation: 120_000.5 },
};

const BY_DEPARTMENT: DepartmentStats[] = [
  {
    department: { id: 1, name: "Engineering" },
    headcount: 10,
    average_base_salary: 120_000,
    average_bonus: 10_000,
    total_payroll: 1_300_000,
  },
  {
    department: { id: 2, name: "Sales" },
    headcount: 5,
    average_base_salary: 80_000,
    average_bonus: 20_000,
    total_payroll: 500_000,
  },
];

const BY_COUNTRY: CountryStats[] = [
  { country: US, headcount: 8, average_base_salary: 1, average_bonus: 1, total_payroll: 75_000_000 },
  { country: INDIA, headcount: 2, average_base_salary: 1, average_bonus: 1, total_payroll: 25_000_000 },
];

const BANDS: SalaryBand[] = [
  { label: "Under 40k", min_salary: 0, max_salary: 40_000, headcount: 3 },
  { label: "40k-60k", min_salary: 40_000, max_salary: 60_000, headcount: 7 },
  { label: "150k+", min_salary: 150_000, max_salary: null, headcount: 1 },
];

const TOP_EARNERS: Employee[] = [
  {
    id: 11,
    first_name: "Grace",
    last_name: "Hopper",
    email: "grace@example.com",
    job_title: "Director",
    department: { id: 1, name: "Engineering" },
    country: US,
    base_salary: 300_000,
    bonus: 100_000,
    total_compensation: 400_000,
  },
  {
    id: 12,
    first_name: "Alan",
    last_name: "Turing",
    email: "alan@example.com",
    job_title: "Principal Engineer",
    department: { id: 1, name: "Engineering" },
    country: INDIA,
    base_salary: 250_000,
    bonus: 50_000,
    total_compensation: 300_000,
  },
];

const FILTERS = {
  countries: [US, INDIA],
  departments: [
    { id: 1, name: "Engineering" },
    { id: 2, name: "Sales" },
  ],
};

let responses: Record<string, () => unknown>;
let failing: Set<string>;
let fetchMock: ReturnType<typeof vi.fn>;

function requestsTo(endpoint: string): URL[] {
  return fetchMock.mock.calls
    .map(([url]) => new URL(String(url)))
    .filter((url) => url.pathname.endsWith(endpoint));
}

describe("AnalyticsPage", () => {
  beforeEach(() => {
    failing = new Set();
    responses = {
      "/meta/filters": () => FILTERS,
      "/analytics/summary": () => SUMMARY,
      "/analytics/by-department": () => BY_DEPARTMENT,
      "/analytics/by-country": () => BY_COUNTRY,
      "/analytics/salary-bands": () => BANDS,
      "/analytics/top-earners": () => TOP_EARNERS,
    };
    fetchMock = vi.fn(async (url: string) => {
      const { pathname } = new URL(String(url));
      const endpoint = Object.keys(responses).find((key) => pathname.endsWith(key))!;
      if (failing.has(endpoint)) {
        return {
          ok: false,
          status: 500,
          statusText: "Server Error",
          json: async () => ({ detail: `${endpoint} failed` }),
        };
      }
      return { ok: true, json: async () => responses[endpoint]() };
    });
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows a loading state per section before data arrives", () => {
    renderWithProviders(<AnalyticsPage />);

    expect(screen.getByRole("status", { name: "Loading Summary" })).toBeInTheDocument();
    expect(screen.getByRole("status", { name: "Loading Top earners" })).toBeInTheDocument();
  });

  it("renders the summary cards", async () => {
    renderWithProviders(<AnalyticsPage />);

    const summary = await screen.findByRole("region", { name: "Summary" });
    await within(summary).findByText("1,234");
    expect(within(summary).getByText("$150,000,000")).toBeInTheDocument();
    expect(within(summary).getByText("$80,500")).toBeInTheDocument();
    expect(within(summary).getByText("$90,251")).toBeInTheDocument();
    expect(within(summary).getByText("United States")).toBeInTheDocument();
    expect(within(summary).getByText("$120,001 average")).toBeInTheDocument();
  });

  it("shows dashes in the summary when there is no data", async () => {
    responses["/analytics/summary"] = () => ({
      headcount: 0,
      total_payroll: 0,
      average_base_salary: null,
      average_total_compensation: null,
      min_base_salary: null,
      max_base_salary: null,
      highest_paid_country: null,
    });

    renderWithProviders(<AnalyticsPage />);

    const summary = await screen.findByRole("region", { name: "Summary" });
    await within(summary).findByText("Headcount");
    expect(within(summary).getAllByText("—")).toHaveLength(3);
  });

  it("renders the department chart with its categories", async () => {
    renderWithProviders(<AnalyticsPage />);

    const section = await screen.findByRole("region", { name: "Average pay by department" });
    expect(await within(section).findByText("Engineering")).toBeInTheDocument();
    expect(within(section).getByText("Sales")).toBeInTheDocument();
  });

  it("lists each country's payroll and share next to the donut", async () => {
    renderWithProviders(<AnalyticsPage />);

    const section = await screen.findByRole("region", { name: "Payroll by country" });
    expect(await within(section).findByText(/United States: \$75,000,000/)).toHaveTextContent("75%");
    expect(within(section).getByText(/India: \$25,000,000/)).toHaveTextContent("25%");
  });

  it("renders the salary band histogram labels", async () => {
    renderWithProviders(<AnalyticsPage />);

    const section = await screen.findByRole("region", { name: "Salary distribution" });
    expect(await within(section).findByText("Under 40k")).toBeInTheDocument();
    expect(within(section).getByText("40k-60k")).toBeInTheDocument();
    expect(within(section).getByText("150k+")).toBeInTheDocument();
  });

  it("lists the top earners in order with their total compensation", async () => {
    renderWithProviders(<AnalyticsPage />);

    const section = await screen.findByRole("region", { name: "Top earners" });
    await within(section).findByText("Grace Hopper");
    const rows = within(section).getAllByRole("row").slice(1);
    expect(rows).toHaveLength(2);
    expect(rows[0]).toHaveTextContent("1Grace HopperDirectorEngineeringUnited States$400,000");
    expect(rows[1]).toHaveTextContent("2Alan Turing");
    expect(requestsTo("/analytics/top-earners")[0].searchParams.get("limit")).toBe("10");
  });

  it("requests every analytics endpoint without filters initially", async () => {
    renderWithProviders(<AnalyticsPage />);
    await screen.findByText("Grace Hopper");

    for (const endpoint of [
      "/analytics/summary",
      "/analytics/by-department",
      "/analytics/by-country",
      "/analytics/salary-bands",
      "/analytics/top-earners",
    ]) {
      const [request] = requestsTo(endpoint);
      expect(request.searchParams.has("country_id")).toBe(false);
      expect(request.searchParams.has("department_id")).toBe(false);
    }
  });

  it("applies the selected filters to every analytics endpoint", async () => {
    renderWithProviders(<AnalyticsPage />);
    await screen.findByText("Grace Hopper");

    await userEvent.click(screen.getByRole("combobox", { name: "Country" }));
    await userEvent.click(await screen.findByRole("option", { name: "India", hidden: true }));
    await userEvent.click(screen.getByRole("combobox", { name: "Department" }));
    await userEvent.click(await screen.findByRole("option", { name: "Sales", hidden: true }));

    await waitFor(() => {
      for (const endpoint of [
        "/analytics/summary",
        "/analytics/by-department",
        "/analytics/by-country",
        "/analytics/salary-bands",
        "/analytics/top-earners",
      ]) {
        const last = requestsTo(endpoint).at(-1)!;
        expect(last.searchParams.get("country_id")).toBe("2");
        expect(last.searchParams.get("department_id")).toBe("2");
      }
    });
  });

  it("clears the filters when Reset is clicked", async () => {
    renderWithProviders(<AnalyticsPage />);
    await screen.findByText("Grace Hopper");
    await userEvent.click(screen.getByRole("combobox", { name: "Country" }));
    await userEvent.click(await screen.findByRole("option", { name: "India", hidden: true }));
    await waitFor(() =>
      expect(requestsTo("/analytics/summary").at(-1)!.searchParams.get("country_id")).toBe("2"),
    );

    await userEvent.click(screen.getByRole("button", { name: "Reset" }));

    await waitFor(() =>
      expect(requestsTo("/analytics/summary").at(-1)!.searchParams.has("country_id")).toBe(false),
    );
  });

  it("shows an empty message for charts when the filters match nobody", async () => {
    responses["/analytics/by-department"] = () => [];
    responses["/analytics/by-country"] = () => [];
    responses["/analytics/salary-bands"] = () => BANDS.map((b) => ({ ...b, headcount: 0 }));
    responses["/analytics/top-earners"] = () => [];

    renderWithProviders(<AnalyticsPage />);

    for (const title of [
      "Average pay by department",
      "Payroll by country",
      "Salary distribution",
      "Top earners",
    ]) {
      const section = await screen.findByRole("region", { name: title });
      expect(
        await within(section).findByText("No data for the selected filters."),
      ).toBeInTheDocument();
    }
  });

  it("isolates a failing section and retries only that section", async () => {
    failing.add("/analytics/salary-bands");

    renderWithProviders(<AnalyticsPage />);

    const bands = await screen.findByRole("region", { name: "Salary distribution" });
    expect(await within(bands).findByText("/analytics/salary-bands failed")).toBeInTheDocument();
    expect(await screen.findByText("Grace Hopper")).toBeInTheDocument();
    expect(await screen.findByText("1,234")).toBeInTheDocument();

    failing.delete("/analytics/salary-bands");
    await userEvent.click(within(bands).getByRole("button", { name: "Retry" }));

    expect(await within(bands).findByText("Under 40k")).toBeInTheDocument();
    expect(requestsTo("/analytics/summary")).toHaveLength(1);
  });
});
