import { Button, Group, Select, TextInput } from "@mantine/core";

import type { FilterOptions } from "../../api/types";

interface DirectoryFiltersProps {
  options: FilterOptions | undefined;
  search: string;
  countryId: number | undefined;
  departmentId: number | undefined;
  onSearchChange: (value: string) => void;
  onCountryChange: (id: number | undefined) => void;
  onDepartmentChange: (id: number | undefined) => void;
  onReset: () => void;
}

function toId(value: string | null): number | undefined {
  return value === null ? undefined : Number(value);
}

export function DirectoryFilters({
  options,
  search,
  countryId,
  departmentId,
  onSearchChange,
  onCountryChange,
  onDepartmentChange,
  onReset,
}: DirectoryFiltersProps) {
  return (
    <Group align="flex-end" mb="md">
      <TextInput
        label="Search"
        placeholder="Name or email"
        value={search}
        onChange={(event) => onSearchChange(event.currentTarget.value)}
      />
      <Select
        label="Country"
        placeholder="All countries"
        clearable
        data={(options?.countries ?? []).map((c) => ({
          value: String(c.id),
          label: c.name,
        }))}
        value={countryId === undefined ? null : String(countryId)}
        onChange={(value) => onCountryChange(toId(value))}
      />
      <Select
        label="Department"
        placeholder="All departments"
        clearable
        data={(options?.departments ?? []).map((d) => ({
          value: String(d.id),
          label: d.name,
        }))}
        value={departmentId === undefined ? null : String(departmentId)}
        onChange={(value) => onDepartmentChange(toId(value))}
      />
      <Button variant="default" onClick={onReset}>
        Reset
      </Button>
    </Group>
  );
}
