from flask import Flask, render_template, jsonify
import feedparser

app = Flask(__name__)


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# RISK ENGINE
# ----------------------------
def calculate_risk(title: str):
    t = title.lower()

    high = [
        "war", "crisis", "earthquake", "inflation", "attack",
        "death", "collapse", "recession", "bankrupt", "conflict"
    ]

    medium = [
        "policy", "government", "economy", "market",
        "trade", "business", "finance", "investing"
    ]

    if any(x in t for x in high):
        return "HIGH"
    if any(x in t for x in medium):
        return "MEDIUM"
    return "LOW"


# ----------------------------
# RSS SOURCES
# ----------------------------
RSS_FEEDS = [
    "https://www.tagesschau.de/xml/rss2/",
    "https://www.handelsblatt.com/contentexport/feed/schlagzeilen",
    "https://www.deutschlandfunk.de/rss"
]


# ----------------------------
# FETCH RSS ARTICLES
# ----------------------------
def fetch_articles(limit=10):
    articles = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:limit]:
            title = entry.get("title", "No title")
            link = entry.get("link", "#")
            pubDate = entry.get("published", "")

            articles.append({
                "title": title,
                "link": link,
                "pubDate": pubDate,
                "source": url,
                "risk": calculate_risk(title)
            })

    return articles


# ----------------------------
# API ENDPOINT
# ----------------------------
@app.route("/api/retail-news-page")
def retail_news_page():
    try:
        articles = fetch_articles()

        return jsonify({
            "page": 1,
            "total": len(articles),
            "articles": articles
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "articles": [],
            "total": 0
        })


# ----------------------------
# RUN LOCALLY
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)