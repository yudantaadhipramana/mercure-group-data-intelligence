"use client";

export default function InsightsPanel({ data }: { data: any[] }) {
  if (!data?.length) return null;
  return (
    <div className="card h-full">
      <div className="card-header">
        <h2 className="text-lg font-light text-amber-100">Strategic Insights & Actions</h2>
      </div>
      <div className="card-body space-y-4">
        {data.map((insight: any, i: number) => (
          <div key={i} className="p-4 rounded-lg bg-white/5 border-l-4 border-amber-400">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-amber-100">{insight.metric}</div>
              <div className="text-xs text-slate-400">{insight.period}</div>
            </div>
            <div className="text-xl font-bold text-white mt-1">
              {typeof insight.value === "number" ? `${insight.value} ${insight.unit || ""}` : insight.value}
            </div>
            <div className="text-xs text-slate-300 mt-2">{insight.evidence}</div>
            <div className="text-xs text-slate-400 mt-1">{insight.interpretation}</div>
            <div className="text-xs text-amber-200 mt-2 font-medium">Action: {insight.investigation}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
