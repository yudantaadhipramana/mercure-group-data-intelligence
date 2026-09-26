"use client";

import { useEffect, useState } from "react";
import { fetchKpi, fetchRevenue, fetchProperty, fetchFnb, fetchQuality } from "@/lib/data";
import KpiCards from "@/components/KpiCards";
import RevenueChart from "@/components/RevenueChart";
import PropertyChart from "@/components/PropertyChart";
import FnbChart from "@/components/FnbChart";
import QualityTable from "@/components/QualityTable";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetchKpi(),
      fetchRevenue(),
      fetchProperty(),
      fetchFnb(),
      fetchQuality(),
    ])
      .then(([kpi, revenue, property, fnb, quality]) => {
        setData({ kpi, revenue, property, fnb, quality });
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-slate-100">Loading dashboard...</div>;
  if (error) return <div className="p-8 text-slate-100">Error: {error}</div>;
  if (!data) return <div className="p-8 text-slate-100">No data</div>;

  return (
    <main className="min-h-screen bg-[#0b1121] text-slate-100 p-6">
      <header className="mb-8 border-b border-slate-700 pb-4">
        <h1 className="text-3xl font-light tracking-wide text-amber-100">Mercure Group Intelligence</h1>
        <p className="text-slate-400 text-sm mt-1">Powered by LensaData — Tajam Melihat, Sigap Bertindak</p>
      </header>
      <KpiCards data={data.kpi} />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <RevenueChart data={data.revenue} />
        <PropertyChart data={data.property} />
        <FnbChart data={data.fnb} />
        <QualityTable data={data.quality} />
      </div>
    </main>
  );
}
