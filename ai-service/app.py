from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

# -----------------------------
# HOME DASHBOARD
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# API: RETAIL NEWS ENDPOINT
# -----------------------------
@app.route("/api/retail-news-page", methods=["GET"])
def retail_news_page():
    try:
        page = request.args.get("page", 1)

        # If you have a Node API upstream, read it safely
        # IMPORTANT: replace this URL if needed
        NODE_API_URL = "http://localhost:3000/api/news"

        import requests
        r = requests.get(NODE_API_URL, timeout=10)

        # 🔥 FIX: