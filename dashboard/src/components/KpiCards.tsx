export default function KpiCards({ data }: { data: any[] }) {
  if (!data?.length) return null;
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {data.map((k: any, i: number) => (
        <div key={i} className="rounded-xl bg-slate-800/60 border border-slate-700 p-5">
          <div className="text-slate-400 text-xs uppercase tracking-wider">{k.metric}</div>
          <div className="text-2xl font-semibold text-amber-100 mt-1">{k.value}</div>
          <div className="text-xs text-slate-400 mt-2">{k.context}</div>
        </div>
      ))}
    </div>
  );
}
