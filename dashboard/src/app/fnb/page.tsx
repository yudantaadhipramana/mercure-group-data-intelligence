"use client";
import { useEffect, useState } from "react";
import { fetchFnb } from "@/lib/data";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function FnbPage() {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => { fetchFnb().then(setData); }, []);
  return (
    <div className="space-y-6">
      <header className="border-b border-white/10 pb-4">
        <h1 className="text-3xl font-light text-amber-100">F&B Analytics</h1>
        <p className="text-slate-400 text-sm">For F&B Managers & Outlet Supervisors.</p>
      </header>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass rounded-xl p-5 h-80">
          <ResponsiveContainer width="100%" height="100%"><BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#334155" /><XAxis dataKey="category" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip /><Bar dataKey="sales_bn" fill="#c084fc" /></BarChart></ResponsiveContainer>
        </div>
        <div className="glass rounded-xl p-5 h-80">
          <ResponsiveContainer width="100%" height="100%"><BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#334155" /><XAxis dataKey="category" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip /><Bar dataKey="food_cost_pct" fill="#f59e0b" /></BarChart></ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
