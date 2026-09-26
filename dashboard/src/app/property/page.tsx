"use client";
import { useEffect, useState } from "react";
import { fetchProperty } from "@/lib/data";
import PropertyChart from "@/components/PropertyChart";

export default function PropertyPage() {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => { fetchProperty().then(setData); }, []);
  return (
    <div className="space-y-6">
      <header className="border-b border-white/10 pb-4">
        <h1 className="text-3xl font-light text-amber-100">Property Performance</h1>
        <p className="text-slate-400 text-sm">For Regional Managers & Property GMs.</p>
      </header>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PropertyChart data={data} />
        <div className="glass rounded-xl p-5">
          <h2 className="text-lg font-light text-amber-100 mb-4">Property Ranking</h2>
          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full text-sm text-left text-slate-300">
              <thead className="text-xs uppercase text-slate-400 border-b border-slate-700"><tr><th className="px-3 py-2">Property</th><th className="px-3 py-2">Revenue (bn)</th><th className="px-3 py-2">EBITDA (bn)</th><th className="px-3 py-2">Occ %</th></tr></thead>
              <tbody>{data.map((r, i) => (<tr key={i} className="border-b border-slate-700/50"><td className="px-3 py-2">{r.property_name}</td><td className="px-3 py-2">{r.revenue_bn}</td><td className="px-3 py-2">{r.ebitda_bn}</td><td className="px-3 py-2">{r.occupancy_pct}%</td></tr>))}</tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
