import { getRecommendations, chatGemini } from "./api.js";

const inputEl = document.getElementById("anime-input");
const listEl = document.getElementById("autocomplete-list");
const buttonEl = document.getElementById("get-recs");
const chatInputEl = document.getElementById("chat-input");
const chatButtonEl = document.getElementById("send-chat");
const chatLogEl = document.getElementById("chat-log");

let selectedAnimeId = null;
let debounceTimeout = null;
let allRecommendations = [];
let displayedRecommendations = [];
let usedRecommendationIds = new Set();
let removedRecommendationIds = new Set();

// --- Autocomplete feature ---
inputEl.addEventListener("input", async function () {
  const query = this.value.trim();
  selectedAnimeId = null;
  clearTimeout(debounceTimeout);

  if (!query || query.length < 2) {
    listEl.innerHTML = "";
    return;
  }

  debounceTimeout = setTimeout(async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/search?q=${encodeURIComponent(query)}`);
      const results = await response.json();
      renderAutocomplete(results);
    } catch (err) {
      console.error("Autocomplete error:", err);
    }
  }, 300);
});

function renderAutocomplete(results) {
  listEl.innerHTML = "";
  if (!results.length) return;

  results.forEach((anime) => {
    const div = document.createElement("div");
    div.classList.add("autocomplete-item");
    div.innerHTML = `
  <div style="display: flex; align-items: center; gap: 10px;">
    ${anime.image_url
      ? `<img src="${anime.image_url}" alt="${anime.name}" style="width: 30px; height: 45px; object-fit: cover; border-radius: 4px;">`
      : `<div style="width: 30px; height: 45px; background: #eee; border-radius: 4px;"></div>`}
    <span>${anime.name}</span>
  </div>
`;
    div.dataset.id = anime.anime_id;

    div.addEventListener("click", () => {
      inputEl.value = anime.name;
      selectedAnimeId = anime.anime_id;
      listEl.innerHTML = "";
    });

    listEl.appendChild(div);
  });
}

document.addEventListener("click", (e) => {
  if (!e.target.closest(".autocomplete-container")) {
    listEl.innerHTML = "";
  }
});

// --- Get Recommendations ---
buttonEl.addEventListener("click", async () => {
  const query = inputEl.value.trim();
  if (!query) return alert("Please enter an anime name!");

  // If no anime_id is selected from autocomplete, fetch it first
  let animeIds = [];
  if (!selectedAnimeId) {
    const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`);
    const results = await res.json();
    if (results.length) animeIds = [results[0].anime_id];
  } else {
    animeIds = [selectedAnimeId];
  }

  if (!animeIds.length) {
    alert("No anime found matching that name!");
    return;
  }

  const recs = await getRecommendations(animeIds);
  allRecommendations = recs;
  displayedRecommendations = recs.slice(0, 8);
  renderResults(displayedRecommendations);
});


function removeAnime(index) {
  const removed = displayedRecommendations[index];

  // Remove from visible array
  displayedRecommendations.splice(index, 1);

  // Mark it as permanently removed
  removedRecommendationIds.add(removed.anime_id);
  usedRecommendationIds.delete(removed.anime_id); // optional cleanup

  // Find a brand-new unseen and unremoved recommendation
  const nextRec = allRecommendations.find(
    rec =>
      !displayedRecommendations.some(d => d.anime_id === rec.anime_id) &&
      !removedRecommendationIds.has(rec.anime_id)
  );

  if (nextRec) {
    displayedRecommendations.push(nextRec);
    usedRecommendationIds.add(nextRec.anime_id);
  }

  renderResults(displayedRecommendations);
}

// --- Render Recommendations ---
export function renderResults(recommendations) {
  const resultsDiv = document.getElementById("results");
  if (!recommendations.length) {
    resultsDiv.innerHTML = "<p>No results found.</p>";
    return;
  }

  resultsDiv.innerHTML = recommendations
    .map((r, index) => `
        <div class="card" data-index="${index}">
          <a href="${r.anime_url}" target="_blank" rel="noopener noreferrer">
            <img src="${r.image_url}" alt="${r.name}" onerror="this.style.display='none';" />
          </a>
          <div class="info">
            <h3><a href="${r.anime_url}" target="_blank" rel="noopener noreferrer">${r.name}</a></h3>
            ${r.score ? `<div class="anime-score">⭐ ${r.score}</div>` : ''}
          </div>
          <button class="remove-btn" data-index="${index}">❌</button>
        </div>`
    )
    .join("");

  // Add click handlers to remove buttons
  // 🔧 Attach delete handlers after rendering, so CSS layout stays intact
  document.querySelectorAll(".remove-btn").forEach(btn => {
    btn.addEventListener("click", e => {
      const idx = parseInt(e.currentTarget.dataset.index);
      removeAnime(idx);
    });
  });
}

// --- Gemini Chat with "typing" animation ---
chatButtonEl.addEventListener("click", async () => {
  const message = chatInputEl.value.trim();
  if (!message) return;

  // Show user's message
  chatLogEl.innerHTML += `
    <div class="chat-msg user">
      <strong>You:</strong>
      <div class="chat-content">${message}</div>
    </div>
  `;
  chatInputEl.value = "";

  // Create Gemini message container
  const geminiMsg = document.createElement("div");
  geminiMsg.classList.add("chat-msg");
  geminiMsg.innerHTML = `<strong>Gemini:</strong><div class="chat-content typing"></div>`;
  chatLogEl.appendChild(geminiMsg);

  const chatContent = geminiMsg.querySelector(".chat-content");

  // Fetch Gemini response
  const reply = await chatGemini(message);

  // Break into sentences for smoother reveal
  const lines = reply
    .split(/(?<=[.!?])\s+/)
    .filter(line => line.trim().length > 0);

  // Type out each line gradually
  for (const line of lines) {
    const formattedLine = marked.parse(line);
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = formattedLine;

    await appendWithDelay(chatContent, tempDiv.innerHTML, 25); // Adjust speed (ms)
    chatLogEl.scrollTop = chatLogEl.scrollHeight;
  }

  chatContent.classList.remove("typing");
});

// Helper: Append text gradually
async function appendWithDelay(container, html, delay = 50) {
  const span = document.createElement("span");
  container.appendChild(span);

  let i = 0;
  const text = html.replace(/<[^>]+>/g, ""); // Strip tags for timing
  while (i < text.length) {
    span.innerHTML = marked.parse(text.slice(0, i + 1));
    await new Promise(r => setTimeout(r, delay));
    i++;
  }
  span.innerHTML = marked.parse(html); // Finish cleanly
}