from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# RISK SCORING FUNCTION
# ----------------------------
def calculate_risk(title: str):
    title = title.lower()

    high_risk_keywords = [
        "war", "crisis", "earthquake", "attack", "inflation",
        "bankrupt", "collapse", "conflict", "kill", "death",
        "terror", "sanction", "recession"
    ]

    medium_risk_keywords = [
        "policy", "government", "economy", "market",
        "trade", "finance", "investing", "business"
    ]

    if any(word in title for word in high_risk_keywords):
        return "HIGH"
    elif any(word in title for word in medium_risk_keywords):
        return "MEDIUM"
    else:
        return "LOW"


# ----------------------------
# API: RETAIL NEWS + RISK
# ----------------------------
@app.route("/api/retail-news-page", methods=["GET"])
def retail_news_page():

    # demo data (we will replace with RSS later)
    articles = [
        {"title": "Global market falls due to inflation fears", "link": "#", "pubDate": "2026-01-01", "source": "demo"},
        {"title": "New government policy announced", "link": "#", "pubDate": "2026-01-01", "source": "demo"},
        {"title": "Local sports event draws attention", "link": "#", "pubDate": "2026-01-01", "source": "demo"},
        {"title": "Earthquake causes major damage in region", "link": "#", "pubDate": "2026-01-01", "source": "demo"}
    ]

    enriched = []
    for a in articles:
        risk = calculate_risk(a["title"])
        a["risk"] = risk
        enriched.append(a)

    return jsonify({
        "page": 1,
        "total": len(enriched),
        "articles": enriched
    })


# ----------------------------
# RUN LOCALLY
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)