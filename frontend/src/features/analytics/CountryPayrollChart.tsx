import { Group, Stack, Text } from "@mantine/core";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { CountryStats } from "../../api/types";
import { formatCurrency } from "../../shared/format";

const PALETTE = [
  "var(--mantine-color-blue-6)",
  "var(--mantine-color-teal-6)",
  "var(--mantine-color-orange-6)",
  "var(--mantine-color-grape-6)",
  "var(--mantine-color-cyan-6)",
  "var(--mantine-color-lime-6)",
];

function color(index: number): string {
  return PALETTE[index % PALETTE.length];
}

export function CountryPayrollChart({ stats }: { stats: CountryStats[] }) {
  const total = stats.reduce((sum, s) => sum + s.total_payroll, 0);
  const data = stats.map((s) => ({ name: s.country.name, value: s.total_payroll }));

  return (
    <Group align="center" wrap="nowrap">
      <div role="img" aria-label="Payroll share by country" style={{ flex: 1 }}>
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" innerRadius={60} outerRadius={100}>
              {data.map((entry, index) => (
                <Cell key={entry.name} fill={color(index)} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => formatCurrency(Number(value))} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <Stack gap="xs" component="ul" m={0} p={0} style={{ listStyle: "none" }}>
        {stats.map((s, index) => (
          <li key={s.country.id}>
            <Group gap="xs" wrap="nowrap">
              <span
                aria-hidden
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: "50%",
                  background: color(index),
                  flexShrink: 0,
                }}
              />
              <Text size="sm">
                {s.country.name}: {formatCurrency(s.total_payroll)} (
                {total > 0 ? Math.round((s.total_payroll / total) * 100) : 0}%)
              </Text>
            </Group>
          </li>
        ))}
      </Stack>
    </Group>
  );
}
