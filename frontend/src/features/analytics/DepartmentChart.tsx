import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { DepartmentStats } from "../../api/types";
import { formatCompactCurrency, formatCurrency } from "../../shared/format";

export function DepartmentChart({ stats }: { stats: DepartmentStats[] }) {
  const data = stats.map((s) => ({
    name: s.department.name,
    "Average base salary": s.average_base_salary,
    "Average bonus": s.average_bonus,
  }));

  return (
    <div role="img" aria-label="Average pay by department">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" />
          <YAxis tickFormatter={formatCompactCurrency} />
          <Tooltip formatter={(value) => formatCurrency(Number(value))} />
          <Legend />
          <Bar dataKey="Average base salary" fill="var(--mantine-color-blue-6)" />
          <Bar dataKey="Average bonus" fill="var(--mantine-color-teal-6)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
