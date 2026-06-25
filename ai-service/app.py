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
# RETAIL RISK SCORING ENGINE
# ----------------------------
def calculate_risk(title: str):
    t = title.lower()

    high_keywords = [
        # crisis / emergency
        "war", "attack", "death", "killed", "earthquake", "crisis",
        "collapse", "recession", "bankrupt", "explosion", "fire",
        "accident", "warning", "terror", "conflict", "strike",

        # inflation / economy shock
        "inflation", "price surge", "cost increase", "energy crisis",
        "supply shortage", "shortage", "commodity shock",

        # retail / supermarkets (YOUR FOCUS)
        "aldi", "lidl", "rewe", "edeka", "kaufland",
        "supermarket", "retail", "grocery", "food prices",
        "food inflation", "price war", "discount war",
        "store closure", "product shortage",

        # food essentials
        "milk", "bread", "meat", "coffee", "butter",
        "food crisis", "food shortage", "agriculture crisis"
    ]

    medium_keywords = [
        "policy", "government", "economy", "market",
        "finance", "business", "trade", "tax",
        "company", "merger", "investment", "bank",
        "tesla", "vw", "bayer"
    ]

    score = 0

    for w in high_keywords:
        if w in t:
            score += 3

    for w in medium_keywords:
        if w in t:
            score += 1

    if score >= 3:
        return "HIGH"
    elif score >= 1:
        return "MEDIUM"
    else:
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
# FETCH RSS ARTICLES SAFELY
# ----------------------------
def fetch_articles(limit=10):
    articles = []

    for url in RSS_FEEDS:
        try:
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

        except Exception as e:
            print(f"RSS error for {url}: {e}")

    return articles


# ----------------------------
# API ENDPOINT
# ----------------------------
@app.route("/api/retail-news-page")
def retail_news_page():
    articles = fetch_articles()

    return jsonify({
        "page": 1,
        "total": len(articles),
        "articles": articles
    })


# ----------------------------
# RUN LOCALLY
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)