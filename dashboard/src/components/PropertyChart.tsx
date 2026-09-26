"use client";
import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function PropertyChart({ data }: { data: any[] }) {
  const chartData = useMemo(() => data || [], [data]);
  return (
    <div className="glass rounded-xl p-5">
      <h2 className="text-lg font-light text-amber-100 mb-4">Revenue by Property</h2>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="property_name" stroke="#94a3b8" angle={-30} textAnchor="end" height={60} />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} formatter={(v: any) => `Rp ${v} bn`} />
            <Bar dataKey="revenue_bn" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
