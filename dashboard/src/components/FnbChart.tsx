"use client";
import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function FnbChart({ data }: { data: any[] }) {
  const chartData = useMemo(() => data || [], [data]);
  return (
    <div className="glass rounded-xl p-5">
      <h2 className="text-lg font-light text-amber-100 mb-4">F&B Net Sales by Category</h2>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="category" stroke="#94a3b8" angle={-30} textAnchor="end" height={60} />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
            <Bar dataKey="sales_bn" fill="#c084fc" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
