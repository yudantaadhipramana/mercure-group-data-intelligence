const DATA_URL = "/dashboard_data.json";

let cached: any = null;

export async function fetchDashboardData() {
  if (cached) return cached;
  const res = await fetch(DATA_URL, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch dashboard data");
  cached = await res.json();
  return cached;
}

export async function fetchKpi() {
  return (await fetchDashboardData()).kpi ?? [];
}

export async function fetchRevenue() {
  return (await fetchDashboardData()).daily_trend ?? [];
}

export async function fetchProperty() {
  return (await fetchDashboardData()).properties ?? [];
}

export async function fetchFnb() {
  return (await fetchDashboardData()).fnb_category ?? [];
}

export async function fetchQuality() {
  return (await fetchDashboardData()).dq ?? [];
}

export async function fetchForecast() {
  return (await fetchDashboardData()).forecast ?? [];
}

export async function fetchAnomaly() {
  return (await fetchDashboardData()).anomalies ?? [];
}

export async function fetchInsights() {
  return (await fetchDashboardData()).insights ?? [];
}

export async function fetchFinance() {
  return (await fetchDashboardData()).finance ?? [];
}

export async function fetchInventory() {
  return (await fetchDashboardData()).inventory ?? {};
}
