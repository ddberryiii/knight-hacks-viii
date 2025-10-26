from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from recommender_knn import AnimeKNNRecommender
from gemini_client import chat_with_gemini
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend/public', static_url_path='')
CORS(app)

recommender = AnimeKNNRecommender()

# Serve the frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/api/search", methods=["GET"])
def search():
    q = request.args.get("q", "")
    return jsonify(recommender.search(q))

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    anime_ids = data.get("anime_ids", [])
    k = int(data.get("k", 10))
    results = recommender.recommend(anime_ids, k=k)
    return jsonify({"recommendations": results})

@app.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "Message required"}), 400

    try:
        response = chat_with_gemini(user_message)
        return jsonify({"reply": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)