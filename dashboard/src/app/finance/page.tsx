"use client";
import { useEffect, useState } from "react";
import { fetchFinance } from "@/lib/data";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

const colors = ["#f59e0b", "#2e7d5b", "#c084fc"];

export default function FinancePage() {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => { fetchFinance().then(setData); }, []);
  return (
    <div className="space-y-6">
      <header className="border-b border-white/10 pb-4">
        <h1 className="text-3xl font-light text-amber-100">Finance</h1>
        <p className="text-slate-400 text-sm">For Finance Directors & Controllers.</p>
      </header>
      <div className="glass rounded-xl p-5 h-96">
        <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={data} dataKey="amount_bn" nameKey="account_type" outerRadius={120}>{data.map((_, i) => <Cell key={i} fill={colors[i % colors.length]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer>
      </div>
    </div>
  );
}
