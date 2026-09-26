"use client";

import { useEffect, useState } from "react";
import { fetchKpi, fetchRevenue, fetchProperty, fetchFnb, fetchAnomaly, fetchInsights } from "@/lib/data";
import KpiCards from "@/components/KpiCards";
import RevenueChart from "@/components/RevenueChart";
import PropertyChart from "@/components/PropertyChart";
import FnbChart from "@/components/FnbChart";
import InsightsPanel from "@/components/InsightsPanel";
import AnomalyTable from "@/components/AnomalyTable";

export default function ExecutivePage() {
  const [data, setData] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchKpi(), fetchRevenue(), fetchProperty(), fetchFnb(), fetchAnomaly(), fetchInsights()])
      .then(([kpi, revenue, property, fnb, anomaly, insights]) => {
        setData({ kpi, revenue, property, fnb, anomaly, insights });
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-slate-300">Loading executive overview...</div>;

  return (
    <div className="space-y-6">
      <header className="border-b border-white/10 pb-4">
        <h1 className="text-3xl font-light text-amber-100">Executive Overview</h1>
        <p className="text-slate-400 text-sm mt-1">Group performance, pain points, and decision support for BOD / Executive.</p>
      </header>

      <KpiCards data={data.kpi} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart data={data.revenue} />
        <PropertyChart data={data.property} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <FnbChart data={data.fnb} />
        <div className="lg:col-span-2">
          <InsightsPanel data={data.insights} />
        </div>
      </div>

      <AnomalyTable data={data.anomaly} />
    </div>
  );
}
