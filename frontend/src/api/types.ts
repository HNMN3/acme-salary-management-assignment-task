export interface DepartmentRef {
  id: number;
  name: string;
}

export interface CountryRef {
  id: number;
  code: string;
  name: string;
}

export interface Employee {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  job_title: string;
  department: DepartmentRef;
  country: CountryRef;
  base_salary: number;
  bonus: number;
  total_compensation: number;
}

export interface PaginatedEmployees {
  items: Employee[];
  total: number;
  page: number;
  page_size: number;
}

export type EmployeeSortField =
  | "name"
  | "job_title"
  | "department"
  | "country"
  | "base_salary"
  | "bonus"
  | "total_compensation";

export type SortOrder = "asc" | "desc";

export interface EmployeeListParams {
  page?: number;
  page_size?: number;
  sort_by?: EmployeeSortField;
  order?: SortOrder;
  search?: string;
  country_id?: number;
  department_id?: number;
}

export interface SalaryUpdate {
  base_salary: number;
  bonus: number;
}

export interface FilterOptions {
  countries: CountryRef[];
  departments: DepartmentRef[];
}

export interface AnalyticsFilters {
  country_id?: number;
  department_id?: number;
}

export interface HighestPaidCountry extends CountryRef {
  average_total_compensation: number;
}

export interface Summary {
  headcount: number;
  total_payroll: number;
  average_base_salary: number | null;
  average_total_compensation: number | null;
  min_base_salary: number | null;
  max_base_salary: number | null;
  highest_paid_country: HighestPaidCountry | null;
}

export interface PayStats {
  headcount: number;
  average_base_salary: number;
  average_bonus: number;
  total_payroll: number;
}

export interface DepartmentStats extends PayStats {
  department: DepartmentRef;
}

export interface CountryStats extends PayStats {
  country: CountryRef;
}

export interface SalaryBand {
  label: string;
  min_salary: number;
  max_salary: number | null;
  headcount: number;
}
