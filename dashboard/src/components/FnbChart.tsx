"use client";

import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";

export default function FnbChart({ data }: { data: any[] }) {
  const chartData = useMemo(() => data || [], [data]);
  const colors = ["#f59e0b", "#06b6d4", "#8b5cf6", "#f43f5e", "#10b981", "#6366f1"];
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-lg font-light text-amber-100">F&B Net Sales by Category</h2>
      </div>
      <div className="card-body h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="category" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" tickFormatter={(v) => `Rp${v}bn`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '0.5rem' }}
              formatter={(value: any) => [`Rp ${(Number(value) / 1e9).toFixed(2)} bn`, 'Net Sales']}
            />
            <Bar dataKey="sales_bn" radius={[4, 4, 0, 0]}>
              {chartData.map((_, i) => (
                <Cell key={`cell-${i}`} fill={colors[i % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
