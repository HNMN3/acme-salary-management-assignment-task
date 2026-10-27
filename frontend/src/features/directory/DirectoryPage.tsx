import { Group, Pagination, Text } from "@mantine/core";
import { useState } from "react";

import { listEmployees } from "../../api/employees";
import { getFilterOptions } from "../../api/meta";
import type { Employee, EmployeeSortField, SortOrder } from "../../api/types";
import { ErrorState } from "../../shared/components/ErrorState";
import { LoadingState } from "../../shared/components/LoadingState";
import { useAsyncData } from "../../shared/hooks/useAsyncData";
import { useDebouncedValue } from "../../shared/hooks/useDebouncedValue";
import { DirectoryFilters } from "./DirectoryFilters";
import { EmployeeTable } from "./EmployeeTable";
import { SalaryEditModal } from "./SalaryEditModal";

const PAGE_SIZE = 50;
const SEARCH_DEBOUNCE_MS = 300;

export function DirectoryPage() {
  const [search, setSearch] = useState("");
  const [countryId, setCountryId] = useState<number>();
  const [departmentId, setDepartmentId] = useState<number>();
  const [sortBy, setSortBy] = useState<EmployeeSortField>("name");
  const [order, setOrder] = useState<SortOrder>("asc");
  const [page, setPage] = useState(1);
  const [editing, setEditing] = useState<Employee | null>(null);

  const debouncedSearch = useDebouncedValue(search.trim(), SEARCH_DEBOUNCE_MS);

  const options = useAsyncData(getFilterOptions, []);
  const employees = useAsyncData(
    () =>
      listEmployees({
        page,
        page_size: PAGE_SIZE,
        sort_by: sortBy,
        order,
        search: debouncedSearch,
        country_id: countryId,
        department_id: departmentId,
      }),
    [page, sortBy, order, debouncedSearch, countryId, departmentId],
  );

  function changeSearch(value: string) {
    setSearch(value);
    setPage(1);
  }

  function changeCountry(id: number | undefined) {
    setCountryId(id);
    setPage(1);
  }

  function changeDepartment(id: number | undefined) {
    setDepartmentId(id);
    setPage(1);
  }

  function changeSort(field: EmployeeSortField) {
    if (field === sortBy) {
      setOrder(order === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setOrder("asc");
    }
    setPage(1);
  }

  function reset() {
    setSearch("");
    setCountryId(undefined);
    setDepartmentId(undefined);
    setSortBy("name");
    setOrder("asc");
    setPage(1);
  }

  const result = employees.data;
  const totalPages = result ? Math.max(1, Math.ceil(result.total / PAGE_SIZE)) : 1;

  return (
    <>
      <DirectoryFilters
        options={options.data}
        search={search}
        countryId={countryId}
        departmentId={departmentId}
        onSearchChange={changeSearch}
        onCountryChange={changeCountry}
        onDepartmentChange={changeDepartment}
        onReset={reset}
      />

      {employees.error ? (
        <ErrorState message={employees.error.message} onRetry={employees.reload} />
      ) : !result ? (
        <LoadingState label="Loading employees" />
      ) : (
        <>
          <Text size="sm" c="dimmed" mb="xs">
            {result.total.toLocaleString("en-US")}{" "}
            {result.total === 1 ? "employee" : "employees"}
          </Text>
          {result.items.length === 0 ? (
            <Text ta="center" py="xl" c="dimmed">
              No employees match your filters.
            </Text>
          ) : (
            <EmployeeTable
              employees={result.items}
              sortBy={sortBy}
              order={order}
              onSort={changeSort}
              onEdit={setEditing}
            />
          )}
          {result.total > 0 && (
            <Group justify="center" mt="md">
              <Pagination value={page} onChange={setPage} total={totalPages} />
            </Group>
          )}
        </>
      )}

      <SalaryEditModal
        employee={editing}
        onClose={() => setEditing(null)}
        onSaved={() => {
          setEditing(null);
          employees.reload();
        }}
      />
    </>
  );
}
