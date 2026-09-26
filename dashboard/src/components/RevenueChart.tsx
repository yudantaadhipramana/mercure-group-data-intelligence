"use client";

import { useMemo } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area } from "recharts";

export default function RevenueChart({ data }: { data: any[] }) {
  const chartData = useMemo(() => data || [], [data]);
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-lg font-light text-amber-100">Revenue & EBITDA Trend</h2>
      </div>
      <div className="card-body h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="month" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" tickFormatter={(v) => `${(v / 1e9).toFixed(1)}bn`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '0.5rem' }}
              formatter={(value: any) => [`Rp ${(Number(value) / 1e9).toFixed(2)} bn`, '']}
            />
            <Area type="monotone" dataKey="revenue" stroke="#f59e0b" fill="url(#colorRevenue)" />
            <Line type="monotone" dataKey="revenue" name="Revenue" stroke="#f59e0b" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="ebitda" name="EBITDA" stroke="#10b981" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
