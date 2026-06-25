from flask import Flask, jsonify
import requests

app = Flask(__name__)

NODE_URL = "https://retail-ai-backend-1.onrender.com/api/retail-news-page?page=1"

@app.route("/")
def home():
    return "Flask OK"

@app.route("/news")
def news():

    try:
        r = requests.get(NODE_URL, timeout=25)

        # 🔥 DEBUG OUTPUT (IMPORTANT)
        print("STATUS:", r.status_code)
        print("BODY SAMPLE:", r.text[:200])

        # ❌ HARD CHECK 1
        if r.status_code != 200:
            return jsonify({"error": "bad status", "code": r.status_code})

        # ❌ HARD CHECK 2
        if not r.text or len(r.text.strip()) < 10:
            return jsonify({"error": "empty or invalid response"})

        # ❌ SAFE JSON PARSE
        try:
            data = r.json()
        except Exception as e:
            return jsonify({
                "error": "json parse failed",
                "details": str(e),
                "raw": r.text[:200]
            })

        return jsonify(data)

    except requests.exceptions.Timeout:
        return jsonify({"error": "timeout from node"})

    except Exception as e:
        return jsonify({"error": str(e)})