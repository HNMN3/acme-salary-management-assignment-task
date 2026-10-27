import { apiGet } from "./client";
import type {
  AnalyticsFilters,
  CountryStats,
  DepartmentStats,
  Employee,
  SalaryBand,
  Summary,
} from "./types";

export function getSummary(filters: AnalyticsFilters): Promise<Summary> {
  return apiGet<Summary>("/analytics/summary", { ...filters });
}

export function getByDepartment(
  filters: AnalyticsFilters,
): Promise<DepartmentStats[]> {
  return apiGet<DepartmentStats[]>("/analytics/by-department", { ...filters });
}

export function getByCountry(
  filters: AnalyticsFilters,
): Promise<CountryStats[]> {
  return apiGet<CountryStats[]>("/analytics/by-country", { ...filters });
}

export function getSalaryBands(
  filters: AnalyticsFilters,
): Promise<SalaryBand[]> {
  return apiGet<SalaryBand[]>("/analytics/salary-bands", { ...filters });
}

export function getTopEarners(
  filters: AnalyticsFilters,
  limit = 10,
): Promise<Employee[]> {
  return apiGet<Employee[]>("/analytics/top-earners", { ...filters, limit });
}
