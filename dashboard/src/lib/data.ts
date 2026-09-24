const SCRIPT_URL =
  "https://script.google.com/macros/s/AKfycbxsPqQh4n3IgslPDrtcAW6Ad8BSiEwtn436oS0frJ0_kQVeDc4ZiHqz7Tv8fD2pb_ehuQ/exec";

async function get(action: string) {
  const res = await fetch(`${SCRIPT_URL}?action=${action}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch ${action}`);
  return res.json();
}

export const fetchKpi = () => get("kpi");
export const fetchRevenue = () => get("revenue");
export const fetchProperty = () => get("property");
export const fetchFnb = () => get("fnb");
export const fetchQuality = () => get("quality");
export const fetchForecast = () => get("forecast");
export const fetchAnomaly = () => get("anomaly");
