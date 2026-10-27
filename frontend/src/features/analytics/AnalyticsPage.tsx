import { SimpleGrid, Stack } from "@mantine/core";
import { useState } from "react";

import {
  getByCountry,
  getByDepartment,
  getSalaryBands,
  getSummary,
  getTopEarners,
} from "../../api/analytics";
import { getFilterOptions } from "../../api/meta";
import { useAsyncData } from "../../shared/hooks/useAsyncData";
import { AnalyticsFilters } from "./AnalyticsFilters";
import { AsyncSection } from "./AsyncSection";
import { CountryPayrollChart } from "./CountryPayrollChart";
import { DepartmentChart } from "./DepartmentChart";
import { SalaryBandChart } from "./SalaryBandChart";
import { SummaryCards } from "./SummaryCards";
import { TopEarnersTable } from "./TopEarnersTable";

const TOP_EARNERS_LIMIT = 10;

export function AnalyticsPage() {
  const [countryId, setCountryId] = useState<number>();
  const [departmentId, setDepartmentId] = useState<number>();

  const filters = { country_id: countryId, department_id: departmentId };
  const deps = [countryId, departmentId];

  const options = useAsyncData(getFilterOptions, []);
  const summary = useAsyncData(() => getSummary(filters), deps);
  const byDepartment = useAsyncData(() => getByDepartment(filters), deps);
  const byCountry = useAsyncData(() => getByCountry(filters), deps);
  const bands = useAsyncData(() => getSalaryBands(filters), deps);
  const topEarners = useAsyncData(
    () => getTopEarners(filters, TOP_EARNERS_LIMIT),
    deps,
  );

  function reset() {
    setCountryId(undefined);
    setDepartmentId(undefined);
  }

  return (
    <Stack>
      <AnalyticsFilters
        options={options.data}
        countryId={countryId}
        departmentId={departmentId}
        onCountryChange={setCountryId}
        onDepartmentChange={setDepartmentId}
        onReset={reset}
      />

      <AsyncSection title="Summary" state={summary}>
        {(data) => <SummaryCards summary={data} />}
      </AsyncSection>

      <SimpleGrid cols={{ base: 1, lg: 2 }}>
        <AsyncSection
          title="Average pay by department"
          state={byDepartment}
          isEmpty={(data) => data.length === 0}
        >
          {(data) => <DepartmentChart stats={data} />}
        </AsyncSection>
        <AsyncSection
          title="Payroll by country"
          state={byCountry}
          isEmpty={(data) => data.length === 0}
        >
          {(data) => <CountryPayrollChart stats={data} />}
        </AsyncSection>
      </SimpleGrid>

      <AsyncSection
        title="Salary distribution"
        state={bands}
        isEmpty={(data) => data.every((band) => band.headcount === 0)}
      >
        {(data) => <SalaryBandChart bands={data} />}
      </AsyncSection>

      <AsyncSection
        title="Top earners"
        state={topEarners}
        isEmpty={(data) => data.length === 0}
      >
        {(data) => <TopEarnersTable employees={data} />}
      </AsyncSection>
    </Stack>
  );
}
