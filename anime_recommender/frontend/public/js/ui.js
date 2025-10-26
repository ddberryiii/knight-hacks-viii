import { getRecommendations, chatGemini } from "./api.js";

const inputEl = document.getElementById("anime-input");
const listEl = document.getElementById("autocomplete-list");
const buttonEl = document.getElementById("get-recs");
const chatInputEl = document.getElementById("chat-input");
const chatButtonEl = document.getElementById("send-chat");
const chatLogEl = document.getElementById("chat-log");

let selectedAnimeId = null;
let debounceTimeout = null;

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
    div.textContent = anime.name;
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

  if (!selectedAnimeId) {
    const res = await fetch(`http://127.0.0.1:5000/api/search?q=${encodeURIComponent(query)}`);
    const results = await res.json();
    if (results.length) selectedAnimeId = results[0].anime_id;
  }

  if (!selectedAnimeId) {
    alert("No anime found matching that name!");
    return;
  }

  const recs = await getRecommendations(query);
  renderResults(recs);
});

// --- Render Recommendations ---
export function renderResults(recommendations) {
  const resultsDiv = document.getElementById("results");
  if (!recommendations.length) {
    resultsDiv.innerHTML = "<p>No results found.</p>";
    return;
  }

  resultsDiv.innerHTML = recommendations
    .map(
      (r) => `
        <div class="card">
          <img src="${r.image_url}" alt="${r.name}" onerror="this.style.display='none';" />
          <div class="info">
            <h3>${r.name}</h3>
            <a href="${r.anime_url}" target="_blank">View</a>
          </div>
        </div>`
    )
    .join("");
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
