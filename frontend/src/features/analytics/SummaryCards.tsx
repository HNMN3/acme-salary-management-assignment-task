import { Card, SimpleGrid, Text } from "@mantine/core";

import type { Summary } from "../../api/types";
import { formatCurrency } from "../../shared/format";

function StatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Card withBorder>
      <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
        {label}
      </Text>
      <Text size="xl" fw={700}>
        {value}
      </Text>
      {hint && (
        <Text size="xs" c="dimmed">
          {hint}
        </Text>
      )}
    </Card>
  );
}

function money(value: number | null): string {
  return value === null ? "—" : formatCurrency(Math.round(value));
}

export function SummaryCards({ summary }: { summary: Summary }) {
  const country = summary.highest_paid_country;
  return (
    <SimpleGrid cols={{ base: 1, sm: 2, lg: 5 }} mb="md">
      <StatCard label="Headcount" value={summary.headcount.toLocaleString("en-US")} />
      <StatCard label="Total payroll" value={formatCurrency(summary.total_payroll)} />
      <StatCard label="Average base salary" value={money(summary.average_base_salary)} />
      <StatCard
        label="Average total compensation"
        value={money(summary.average_total_compensation)}
      />
      <StatCard
        label="Highest-paid country"
        value={country ? country.name : "—"}
        hint={country ? `${money(country.average_total_compensation)} average` : undefined}
      />
    </SimpleGrid>
  );
}
