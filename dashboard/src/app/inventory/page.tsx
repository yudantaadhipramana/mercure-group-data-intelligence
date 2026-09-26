"use client";
import { useEffect, useState } from "react";
import { fetchInventory } from "@/lib/data";

export default function InventoryPage() {
  const [data, setData] = useState<any>(null);
  useEffect(() => { fetchInventory().then(setData); }, []);
  if (!data) return <div>Loading...</div>;
  return (
    <div className="space-y-6">
      <header className="border-b border-white/10 pb-4">
        <h1 className="text-3xl font-light text-amber-100">Inventory</h1>
        <p className="text-slate-400 text-sm">For Procurement & Stock Controllers.</p>
      </header>
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(data).map(([k, v]) => (<div key={k} className="glass rounded-xl p-5"><div className="text-xs uppercase text-slate-400">{k}</div><div className="text-xl text-amber-100 mt-1">{Number(v).toLocaleString(undefined, { maximumFractionDigits: 0 })}</div></div>))}
      </div>
    </div>
  );
}
