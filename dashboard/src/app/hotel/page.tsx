"use client";
import { useEffect, useState } from "react";
import { fetchProperty } from "@/lib/data";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function HotelPage() {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => { fetchProperty().then(d => { const hotel = d.filter((x: any) => x.business_type === "Hotel"); setData(hotel); }); }, []);
  return (
    <div className="space-y-6">
      <header className="border-b border-white/10 pb-4">
        <h1 className="text-3xl font-light text-amber-100">Hotel Analytics</h1>
        <p className="text-slate-400 text-sm">Occupancy, ADR, RevPAR for Hotel Operations.</p>
      </header>
      <div className="glass rounded-xl p-5 h-96">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="property_name" stroke="#94a3b8" angle={-30} textAnchor="end" height={60} />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
            <Bar dataKey="occupancy_pct" fill="#f59e0b" name="Occupancy %" />
            <Bar dataKey="adr" fill="#2e7d5b" name="ADR" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
