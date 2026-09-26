"use client";
import { useEffect, useState } from "react";
import { fetchForecast, fetchAnomaly } from "@/lib/data";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function ForecastPage() {
  const [fc, setFc] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  useEffect(() => { fetchForecast().then(setFc); fetchAnomaly().then(setAnomalies); }, []);
  return (
    <div className="space-y-6">
      <header className="border-b border-white/10 pb-4">
        <h1 className="text-3xl font-light text-amber-100">Forecast & Anomaly</h1>
        <p className="text-slate-400 text-sm">90-day outlook and detected exceptions.</p>
      </header>
      <div className="glass rounded-xl p-5 h-96">
        <ResponsiveContainer width="100%" height="100%"><LineChart data={fc}><CartesianGrid strokeDasharray="3 3" stroke="#334155" /><XAxis dataKey="date" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip /><Line type="monotone" dataKey="forecast_revenue" stroke="#f59e0b" dot={false} /><Line type="monotone" dataKey="forecast_fnb" stroke="#c084fc" dot={false} /></LineChart></ResponsiveContainer>
      </div>
      <div className="glass rounded-xl p-5">
        <h2 className="text-lg font-light text-amber-100 mb-4">Anomalies</h2>
        <div className="overflow-x-auto"><table className="w-full text-sm text-left text-slate-300"><thead className="text-xs uppercase text-slate-400 border-b border-slate-700"><tr><th className="px-3 py-2">Date</th><th className="px-3 py-2">Property</th><th className="px-3 py-2">Metric</th><th className="px-3 py-2">Severity</th></tr></thead><tbody>{anomalies.map((r, i) => (<tr key={i} className="border-b border-slate-700/50"><td className="px-3 py-2">{String(r.date).slice(0,10)}</td><td className="px-3 py-2">{r.property_name}</td><td className="px-3 py-2">{r.metric}</td><td className="px-3 py-2 capitalize">{r.severity}</td></tr>))}</tbody></table></div>
      </div>
    </div>
  );
}
