const DATA_URL =
  "https://raw.githubusercontent.com/yudantaadhipramana/mercure-group-data-intelligence/main/09_dashboard/dashboard_data.json";

async function getJson(path: string) {
  const res = await fetch(DATA_URL, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch dashboard data");
  const json = await res.json();
  return json[path] ?? [];
}

export const fetchKpi = () => getJson("kpi");
export const fetchRevenue = () => getJson("revenue");
export const fetchProperty = () => getJson("property");
export const fetchFnb = () => getJson("fnb");
export const fetchQuality = () => getJson("quality");
export const fetchForecast = () => Promise.resolve([]);
export const fetchAnomaly = () => Promise.resolve([]);
