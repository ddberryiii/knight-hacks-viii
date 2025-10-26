const API_BASE = "http://127.0.0.1:5000";

/**
 * Fetches anime recommendations based on name (via search -> recommend chain)
 */
export async function getRecommendations(animeName) {
  const searchRes = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(animeName)}`);
  const results = await searchRes.json();
  if (!results.length) return [];

  const firstId = results[0].anime_id;
  const recRes = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ anime_ids: [firstId] }),
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
