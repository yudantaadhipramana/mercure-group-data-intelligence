export default function QualityTable({ data }: { data: any[] }) {
  if (!data?.length) return null;
  return (
    <div className="rounded-xl bg-slate-800/60 border border-slate-700 p-5">
      <h2 className="text-lg font-light text-amber-100 mb-4">Data Quality</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-slate-300">
          <thead className="text-xs uppercase text-slate-400 border-b border-slate-700">
            <tr>
              {Object.keys(data[0]).map((h) => (
                <th key={h} className="px-3 py-2">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className="border-b border-slate-700/50">
                {Object.values(row).map((v, j) => (
                  <td key={j} className="px-3 py-2">{String(v)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
