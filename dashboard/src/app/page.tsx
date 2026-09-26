"use client";
import { useEffect, useState } from "react";
import { fetchKpi, fetchRevenue, fetchProperty, fetchFnb, fetchAnomaly, fetchInsights } from "@/lib/data";
import KpiCards from "@/components/KpiCards";
import RevenueChart from "@/components/RevenueChart";
import PropertyChart from "@/components/PropertyChart";
import FnbChart from "@/components/FnbChart";

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

  if (loading) return <div className="p-8">Loading executive overview...</div>;

  return (
    <div className="space-y-6">
      <header className="border-b border-white/10 pb-4">
        <h1 className="text-3xl font-light text-amber-100">Executive Overview</h1>
        <p className="text-slate-400 text-sm">Group performance, pain points, and decision support for BOD / Executive.</p>
      </header>

      <KpiCards data={data.kpi} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart data={data.revenue} />
        <PropertyChart data={data.property} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <FnbChart data={data.fnb} />
        <div className="lg:col-span-2 glass rounded-xl p-5">
          <h2 className="text-lg font-light text-amber-100 mb-4">Top Insights & Actions</h2>
          <div className="space-y-3">
            {data.insights?.map((insight: any, i: number) => (
              <div key={i} className="p-4 rounded-lg bg-white/5 border-l-4 border-amber-400">
                <div className="text-sm font-semibold text-amber-100">{insight.metric}</div>
                <div className="text-xs text-slate-300 mt-1">{insight.evidence}</div>
                <div className="text-xs text-slate-400 mt-1">{insight.investigation}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="glass rounded-xl p-5">
        <h2 className="text-lg font-light text-amber-100 mb-4">Anomaly Alerts</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-slate-300">
            <thead className="text-xs uppercase text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-3 py-2">Date</th>
                <th className="px-3 py-2">Property</th>
                <th className="px-3 py-2">Metric</th>
                <th className="px-3 py-2">Actual</th>
                <th className="px-3 py-2">Expected</th>
                <th className="px-3 py-2">Severity</th>
              </tr>
            </thead>
            <tbody>
              {data.anomaly?.map((row: any, i: number) => (
                <tr key={i} className="border-b border-slate-700/50">
                  <td className="px-3 py-2">{String(row.date).slice(0, 10)}</td>
                  <td className="px-3 py-2">{row.property_name}</td>
                  <td className="px-3 py-2">{row.metric}</td>
                  <td className="px-3 py-2">{Number(row.actual).toLocaleString()}</td>
                  <td className="px-3 py-2">{Number(row.expected).toLocaleString()}</td>
                  <td className="px-3 py-2 capitalize">{row.severity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
