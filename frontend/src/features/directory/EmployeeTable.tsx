import { Table, Text, UnstyledButton } from "@mantine/core";

import type { Employee, EmployeeSortField, SortOrder } from "../../api/types";
import { formatCurrency } from "../../shared/format";

interface Column {
  field: EmployeeSortField;
  label: string;
  numeric?: boolean;
}

const COLUMNS: Column[] = [
  { field: "name", label: "Name" },
  { field: "job_title", label: "Job title" },
  { field: "department", label: "Department" },
  { field: "country", label: "Country" },
  { field: "base_salary", label: "Base salary", numeric: true },
  { field: "bonus", label: "Bonus", numeric: true },
  { field: "total_compensation", label: "Total compensation", numeric: true },
];

interface EmployeeTableProps {
  employees: Employee[];
  sortBy: EmployeeSortField;
  order: SortOrder;
  onSort: (field: EmployeeSortField) => void;
}

export function EmployeeTable({
  employees,
  sortBy,
  order,
  onSort,
}: EmployeeTableProps) {
  return (
    <Table.ScrollContainer minWidth={900}>
      <Table striped highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            {COLUMNS.map((column) => (
              <Table.Th
                key={column.field}
                ta={column.numeric ? "right" : "left"}
                aria-sort={
                  sortBy === column.field
                    ? order === "asc"
                      ? "ascending"
                      : "descending"
                    : "none"
                }
              >
                <UnstyledButton
                  fw={600}
                  fz="sm"
                  onClick={() => onSort(column.field)}
                >
                  {column.label}
                  {sortBy === column.field && (order === "asc" ? " ▲" : " ▼")}
                </UnstyledButton>
              </Table.Th>
            ))}
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {employees.map((employee) => (
            <Table.Tr key={employee.id}>
              <Table.Td>
                <Text size="sm">
                  {employee.first_name} {employee.last_name}
                </Text>
                <Text size="xs" c="dimmed">
                  {employee.email}
                </Text>
              </Table.Td>
              <Table.Td>{employee.job_title}</Table.Td>
              <Table.Td>{employee.department.name}</Table.Td>
              <Table.Td>{employee.country.name}</Table.Td>
              <Table.Td ta="right">{formatCurrency(employee.base_salary)}</Table.Td>
              <Table.Td ta="right">{formatCurrency(employee.bonus)}</Table.Td>
              <Table.Td ta="right">
                {formatCurrency(employee.total_compensation)}
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </Table.ScrollContainer>
  );
}
