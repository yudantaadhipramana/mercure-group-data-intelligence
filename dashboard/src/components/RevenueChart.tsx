"use client";
import { useMemo } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function RevenueChart({ data }: { data: any[] }) {
  const chartData = useMemo(() => data || [], [data]);
  return (
    <div className="glass rounded-xl p-5">
      <h2 className="text-lg font-light text-amber-100 mb-4">Revenue & EBITDA Trend</h2>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="month" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
            <Line type="monotone" dataKey="revenue" name="Revenue" stroke="#f59e0b" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="ebitda" name="EBITDA" stroke="#2e7d5b" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
