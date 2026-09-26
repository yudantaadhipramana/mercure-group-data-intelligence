"use client";

import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function PropertyChart({ data }: { data: any[] }) {
  const chartData = useMemo(() => (data || []).filter((d: any) => d.business_type === "Hotel"), [data]);
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-lg font-light text-amber-100">Hotel Revenue vs EBITDA</h2>
      </div>
      <div className="card-body h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="property_name" stroke="#94a3b8" angle={-20} textAnchor="end" height={60} tickFormatter={(v) => v.replace("Mercure ", "")} />
            <YAxis stroke="#94a3b8" tickFormatter={(v) => `Rp${v}bn`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '0.5rem' }}
              formatter={(value: any, name: any) => [`Rp ${value} bn`, name]}
            />
            <Bar dataKey="revenue_bn" name="Revenue" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            <Bar dataKey="ebitda_bn" name="EBITDA" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
