"use client";
import { useEffect, useState } from "react";
import { fetchQuality } from "@/lib/data";
import QualityTable from "@/components/QualityTable";

export default function QualityPage() {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => { fetchQuality().then(setData); }, []);
  return (
    <div className="space-y-6">
      <header className="border-b border-white/10 pb-4">
        <h1 className="text-3xl font-light text-amber-100">Data Quality & ETL Monitoring</h1>
        <p className="text-slate-400 text-sm">For Data Engineers & Analysts.</p>
      </header>
      <QualityTable data={data} />
    </div>
  );
}
