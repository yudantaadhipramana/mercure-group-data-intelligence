"use client";

export default function AnomalyTable({ data }: { data: any[] }) {
  if (!data?.length) return null;
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-lg font-light text-amber-100">Anomaly Alerts</h2>
      </div>
      <div className="card-body overflow-x-auto">
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
            {data.map((row: any, i: number) => (
              <tr key={i} className="border-b border-slate-700/50 hover:bg-white/5">
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
  );
}
