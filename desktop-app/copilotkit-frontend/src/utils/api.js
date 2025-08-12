export async function fetchAPI(endpoint, options = {}) {
  const baseUrl = process.env.REACT_APP_API_URL || "https://sentinelai-production.up.railway.app/api";
  const url = baseUrl + endpoint;
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
