import { apiGet, apiPatch } from "./client";
import type {
  Employee,
  EmployeeListParams,
  PaginatedEmployees,
  SalaryUpdate,
} from "./types";

export function listEmployees(
  params: EmployeeListParams,
): Promise<PaginatedEmployees> {
  return apiGet<PaginatedEmployees>("/employees", { ...params });
}

export function updateSalary(
  employeeId: number,
  update: SalaryUpdate,
): Promise<Employee> {
  return apiPatch<Employee>(`/employees/${employeeId}/salary`, update);
}
