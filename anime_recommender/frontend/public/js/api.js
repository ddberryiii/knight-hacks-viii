const API_BASE = "http://127.0.0.1:5000";

/**
 * Fetches anime recommendations based on name (via search -> recommend chain)
 */
export async function getRecommendations(animeIds) {
  const recRes = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ anime_ids: animeIds }),
  });
  const data = await recRes.json();
  return data.recommendations || [];
}

export async function chatGemini(message) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  const data = await res.json();
  return data.reply || data.error || "Error";
}
