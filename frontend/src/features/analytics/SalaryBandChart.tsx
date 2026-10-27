import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { SalaryBand } from "../../api/types";

export function SalaryBandChart({ bands }: { bands: SalaryBand[] }) {
  return (
    <div role="img" aria-label="Employees by base salary band">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={bands}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="label" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar
            dataKey="headcount"
            name="Employees"
            fill="var(--mantine-color-indigo-6)"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
