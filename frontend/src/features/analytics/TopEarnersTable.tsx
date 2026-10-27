import { Table, Text } from "@mantine/core";

import type { Employee } from "../../api/types";
import { formatCurrency } from "../../shared/format";

export function TopEarnersTable({ employees }: { employees: Employee[] }) {
  return (
    <Table.ScrollContainer minWidth={600}>
      <Table striped>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>#</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Job title</Table.Th>
            <Table.Th>Department</Table.Th>
            <Table.Th>Country</Table.Th>
            <Table.Th ta="right">Total compensation</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {employees.map((employee, index) => (
            <Table.Tr key={employee.id}>
              <Table.Td>{index + 1}</Table.Td>
              <Table.Td>
                <Text size="sm">
                  {employee.first_name} {employee.last_name}
                </Text>
              </Table.Td>
              <Table.Td>{employee.job_title}</Table.Td>
              <Table.Td>{employee.department.name}</Table.Td>
              <Table.Td>{employee.country.name}</Table.Td>
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
