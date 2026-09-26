const DATA_URL = "/api/data/";

async function getJson(path: string) {
  const res = await fetch(DATA_URL, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch dashboard data");
  const json = await res.json();
  return json[path] ?? [];
}

export const fetchKpi = () => getJson("kpi");
export const fetchRevenue = () => getJson("daily_trend");
export const fetchProperty = () => getJson("properties");
export const fetchFnb = () => getJson("fnb_category");
export const fetchQuality = () => getJson("dq");
export const fetchForecast = () => getJson("forecast");
export const fetchAnomaly = () => getJson("anomalies");
export const fetchInsights = () => getJson("insights");
export const fetchFinance = () => getJson("finance");
export const fetchInventory = () => getJson("inventory");
